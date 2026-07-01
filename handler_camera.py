# TABLE OF CONTENTS
# 1. Imports
# 2. Camera setup
# 3. Camera connection
# 4. Frame acquisition
# 5. ROI extraction
# 6. Signal analysis
# 7. Cleanup

# -----------------------------------------------------------------------------
# 1. IMPORTS
# -----------------------------------------------------------------------------
import numpy as np
import time

# -----------------------------------------------------------------------------
# 2. CAMERA HANDLER CLASS
# -----------------------------------------------------------------------------

class CameraHandler:
    # -----------------------------------------------------------------------------
    # 2.1 INITIAL CAMERA STATE AND SETTINGS
    # -----------------------------------------------------------------------------
    
    def __init__(self):
        self.camera = None #start without opened camera
        self.sdk = None #start without SDK (software developement kit from thorlabs)
        self.is_connected = False
        self.simulation_mode = False

        # ROI
        self.roi_x = 557 #748 #exactly the middle of a 1536x1152 px image
        self.roi_y = 608 #556
        self.roi_w = 40
        self.roi_h = 40

        # Camera Settings
        self.exposure_us = 500 #20 #in mykrometer
        self.gain = 5
        self.black_level = 0

        try:
            from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
            self.sdk = TLCameraSDK()
            print("Thorlabs SDK loaded.")
        except Exception as e:
            print(f"SDK not found: {e}")
            print("Using simulation mode.")
            self.simulation_mode = True
    # -----------------------------------------------------------------------------
    # 3.1 CONNECT TO CAMERA OR FALL BACK TO SIMULATION
    # -----------------------------------------------------------------------------
    
    def connect(self):
        #use simulation first then try real camera
        if self.simulation_mode:
            self.is_connected = True
            print("Simulated camera connected.")
            return True

        try:
            cameras = self.sdk.discover_available_cameras()

            if len(cameras) == 0:
                raise Exception("No Thorlabs camera found.")

            self.camera = self.sdk.open_camera(cameras[0]) #open the first detected camera

            # -------------------------------------------------
            # HARDWARE ROI
            # -------------------------------------------------

            try:
                roi_x1 = int(self.roi_x)
                roi_y1 = int(self.roi_y)

                roi_x2 = int(self.roi_x + self.roi_w)
                roi_y2 = int(self.roi_y + self.roi_h)

                self.camera.roi = (
                    roi_x1,
                    roi_y1,
                    roi_x2,
                    roi_y2
                )

                print(
                    f"Hardware ROI set: "
                    f"x={roi_x1}, y={roi_y1}, "
                    f"w={self.roi_w}, h={self.roi_h}"
                )

            except Exception as e:
                print("Could not set hardware ROI:", e)

            try:
                self.camera.exposure_time_us = self.exposure_us
            except Exception as e:
                print("Could not set exposure:", e)

            try:
                self.camera.gain = self.gain
            except Exception as e:
                print("Could not set gain:", e)

            try:
                self.camera.black_level = self.black_level
            except Exception as e:
                print("Could not set black level:", e)

            try: #try to put camera into continous acquisition mode
                self.camera.frames_per_trigger_zero_for_unlimited = 0
            except Exception as e:
                print("Could not set continuous mode:", e)

            try: #arm(start) camera for acquisition
                self.camera.arm(frames_to_buffer=10)
            except Exception as e:
                print("Could not arm camera:", e)
                raise

            try: #test acquirision once so the the program knows, the camera can deliver frames
                if hasattr(self.camera, "issue_software_trigger"):
                    self.camera.issue_software_trigger()
                    time.sleep(0.05)
                    frame = self.camera.get_pending_frame_or_null()
                    if frame is None:
                        raise Exception("No frame received after software trigger.")
            except Exception as e:
                print("Could not start acquisition:", e)
                raise

            self.is_connected = True #mark camera as connected after configuration and test frame succeed
            print("Camera connected.")
            return True

        except Exception as e:
            print(f"Camera connection failed: {e}")
            print("Using simulation mode.")
            self.simulation_mode = True
            self.is_connected = True
            return True
    # -----------------------------------------------------------------------------
    # 4.1 READ ONE CAMERA FRAME
    # -----------------------------------------------------------------------------
    
    def get_frame(self):
        #create the simulation frame
        if self.simulation_mode:
            img = np.random.normal(30, 8, (1024, 1280)).astype(np.float32)

            y, x = np.indices(img.shape)
            cx, cy = 760, 460
            #create bright gaussian spot that imitates illuminated interferometer
            spot = 220 * np.exp(
                -(((x - cx) ** 2) / (2 * 150 ** 2) +
                  ((y - cy) ** 2) / (2 * 190 ** 2))
            )
            #add moving sinoidal fringes
            fringes = 45 * np.sin(0.09 * x + 0.04 * y + time.time() * 3)
            #combine all and limit simulated brightness
            img = img + spot + fringes
            img = np.clip(img, 0, 255).astype(np.uint8)
            return img

        if self.camera is None:
            return None

        try:
            if hasattr(self.camera, "issue_software_trigger"):
                self.camera.issue_software_trigger()

            for _ in range(20):
                frame = self.camera.get_pending_frame_or_null()
                #ask the camera to capture a frame
                if frame is not None:
                    return np.copy(frame.image_buffer)

                time.sleep(0.001)

        except Exception as e:
            print("Frame read error:", e)

        return None
    # -----------------------------------------------------------------------------
    # 5.1 EXTRACT THE ANALYSIS ROI
    # -----------------------------------------------------------------------------
    
    def get_roi(self, img):
        if img is None:
            return None

        h, w = img.shape

        x1 = max(0, min(self.roi_x, w - 1)) #clamp roi inside image 
        y1 = max(0, min(self.roi_y, h - 1))
        x2 = max(0, min(x1 + self.roi_w, w))
        y2 = max(0, min(y1 + self.roi_h, h))

        roi = img[y1:y2, x1:x2]

        if roi.size == 0:
            return None

        return roi
    # -----------------------------------------------------------------------------
    # 6.2 CALCULATE MEAN ROI INTENSITY
    # -----------------------------------------------------------------------------
    
    def get_fringe_intensity_from_frame(self, img):
        # bleibt drin, falls alter Code es noch irgendwo nutzt
        roi = self.get_roi(img)

        if roi is None:
            return None

        return float(np.mean(roi)) #return the roi brightness
     # -----------------------------------------------------------------------------
    # 7.1 CLOSE CAMERA RESOURCES
    # -----------------------------------------------------------------------------
    
    def close(self):
        try:
            if self.camera is not None:
                self.camera.disarm() #stop camera acquisition before disposing of the camera object
                self.camera.dispose() #release camera object through sdk
                self.camera = None

            if self.sdk is not None:
                self.sdk.dispose()
                self.sdk = None

        except Exception as e:
            print("Camera close error:", e)

        self.is_connected = False
