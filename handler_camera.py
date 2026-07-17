# -----------------------------------------------------------------------------
# 1. IMPORTS
# -----------------------------------------------------------------------------
import numpy as np
import time

# So that you do not have to understand every line of the code, I will now explain the complete path of a camera signal through this file
# 0. What is happening: class in which it is happening : function in the class in which it is happening : what is happening explained in a more precise way
# 1. The camera handler is initialized: CameraHandler : __init__() : initializes the camera, ROI, camera settings, and loads the Thorlabs SDK
# 2. The camera is connected: CameraHandler : connect() : connects to the camera, configures the ROI and acquisition settings, or switches to simulation mode
# 3. A camera frame is acquired: CameraHandler : get_frame() : reads a new image from the camera or generates a simulated frame
# 4. The region of interest is extracted: CameraHandler : get_roi() : extracts the selected ROI from the acquired image
# 5. The fringe intensity is calculated: CameraHandler : get_fringe_intensity_from_frame() : computes the mean intensity inside the ROI
# 6. The camera connection is closed: CameraHandler : close() : stops image acquisition, releases the camera, and closes the SDK

# -----------------------------------------------------------------------------
# 2. CAMERA HANDLER CLASS
# -----------------------------------------------------------------------------

class CameraHandler:

    # initialize the camera state and settings
    def __init__(self):
        self.camera = None  # start without opened camera
        self.sdk = None  # start without SDK (software development kit from Thorlabs)
        self.is_connected = False
        self.simulation_mode = False

        # ROI
        self.roi_x = 557
        self.roi_y = 608
        self.roi_w = 40
        self.roi_h = 40

        # Camera Settings
        self.exposure_us = 80
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

    # connect to the camera or fall back to simulation
    def connect(self):

        # use simulation first then try real camera
        if self.simulation_mode:
            self.is_connected = True
            print("Simulated camera connected.")
            return True

        try:
            cameras = self.sdk.discover_available_cameras()

            if len(cameras) == 0:
                raise Exception("No Thorlabs camera found.")

            self.camera = self.sdk.open_camera(cameras[0])  # open the first detected camera

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

            try:
                self.camera.frames_per_trigger_zero_for_unlimited = 0
            except Exception as e:
                print("Could not set continuous mode:", e)

            try:
                self.camera.arm(frames_to_buffer=10)
            except Exception as e:
                print("Could not arm camera:", e)
                raise

            try:
                if hasattr(self.camera, "issue_software_trigger"):
                    self.camera.issue_software_trigger()
                    time.sleep(0.05)
                    frame = self.camera.get_pending_frame_or_null()
                    if frame is None:
                        raise Exception("No frame received after software trigger.")
            except Exception as e:
                print("Could not start acquisition:", e)
                raise

            self.is_connected = True
            print("Camera connected.")
            return True

        except Exception as e:
            print(f"Camera connection failed: {e}")
            print("Using simulation mode.")
            self.simulation_mode = True
            self.is_connected = True
            return True
    # acquire one camera frame
    def get_frame(self):

        # create the simulation frame
        if self.simulation_mode:
            img = np.random.normal(30, 8, (1024, 1280)).astype(np.float32)

            y, x = np.indices(img.shape)
            cx, cy = 760, 460

            # create bright Gaussian spot that imitates the illuminated interferometer
            spot = 220 * np.exp(
                -(((x - cx) ** 2) / (2 * 150 ** 2) +
                  ((y - cy) ** 2) / (2 * 190 ** 2))
            )

            # add moving sinusoidal fringes
            fringes = 45 * np.sin(0.09 * x + 0.04 * y + time.time() * 3)

            # combine all components and limit the simulated brightness
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

                # request a frame from the camera
                if frame is not None:
                    return np.copy(frame.image_buffer)

                time.sleep(0.001)

        except Exception as e:
            print("Frame read error:", e)

        return None

    # extract the analysis region of interest
    def get_roi(self, img):

        if img is None:
            return None

        h, w = img.shape

        # keep the ROI inside the image boundaries
        x1 = max(0, min(self.roi_x, w - 1))
        y1 = max(0, min(self.roi_y, h - 1))
        x2 = max(0, min(x1 + self.roi_w, w))
        y2 = max(0, min(y1 + self.roi_h, h))

        roi = img[y1:y2, x1:x2]

        if roi.size == 0:
            return None

        return roi

    # calculate the mean fringe intensity
    def get_fringe_intensity_from_frame(self, img):

        # kept for compatibility with older code
        roi = self.get_roi(img)

        if roi is None:
            return None

        # return the mean brightness inside the ROI
        return float(np.mean(roi))
        # close the camera and release all resources
    def close(self):

        try:
            if self.camera is not None:
                # stop image acquisition before releasing the camera
                self.camera.disarm()

                # release the camera object
                self.camera.dispose()
                self.camera = None

            if self.sdk is not None:
                # release the Thorlabs SDK
                self.sdk.dispose()
                self.sdk = None

        except Exception as e:
            print("Camera close error:", e)

        # mark the camera as disconnected
        self.is_connected = False