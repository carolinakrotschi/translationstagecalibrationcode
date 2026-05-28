# TABLE OF CONTENTS FOR CAMERA_HANDLER_EXPL.PY
# 1. Imports: numerical arrays, timing, and peak detection.
# 2. CameraHandler setup: camera state, ROI, exposure, gain, and SDK loading.
# 3. Camera connection: real Thorlabs camera setup or simulation fallback.
# 4. Frame acquisition: simulated frame generation or real camera frame reading.
# 5. ROI extraction: crop the image area used for intensity/fringe analysis.
# 6. Signal analysis: contrast, mean intensity, and visible fringe counting.
# 7. Cleanup: release camera and SDK resources.
# Comments explain what the camera code is doing and why each step is needed.

# -----------------------------------------------------------------------------
# 1. IMPORTS
# -----------------------------------------------------------------------------
import numpy as np
# NumPy is used for camera images, simulation arrays, averages, clipping, and profile calculations.
import time
# Time is used for short camera waits and for animated simulated fringes.
from scipy.signal import find_peaks
# Peak detection is used when the code estimates how many fringes are visible in the ROI.


# -----------------------------------------------------------------------------
# 2. CAMERA HANDLER CLASS
# -----------------------------------------------------------------------------
class CameraHandler:
# This class keeps all camera communication and image-analysis helper functions in one place.

    # -----------------------------------------------------------------------------
    # 2.1 INITIAL CAMERA STATE AND SETTINGS
    # This prepares all camera variables, ROI coordinates, camera settings, and SDK access.
    # -----------------------------------------------------------------------------
    def __init__(self):
        self.camera = None
        # Start without an opened camera; a real camera object is stored here after a successful connection.
        self.sdk = None
        # Start without an SDK object; it is created if the Thorlabs SDK import succeeds.
        self.is_connected = False
        # Start disconnected; this becomes True after real camera setup or simulation setup succeeds.
        self.simulation_mode = False
        # The handler first assumes real hardware will be used; simulation is enabled only if SDK/camera setup fails.

        # ROI setting: choose the image area used for brightness and fringe analysis.
        self.roi_x = 754
        # Set the ROI left edge in camera pixels.
        self.roi_y = 464
        # Set the ROI top edge in camera pixels.
        self.roi_w = 40
        # Set the ROI width to 40 pixels.
        self.roi_h = 40
        # Set the ROI height to 40 pixels.

        # Camera settings: choose exposure, gain, and black level before acquisition starts.
        self.exposure_us = 10 # Exposure time in microseconds.
        # Use a short exposure value that will be sent to the camera during connection setup.
        self.gain = 5
        # Use gain 5 to amplify the camera signal.
        self.black_level = 0
        # Use zero black-level offset so the raw brightness is not shifted upward.

        try:
        # Try to load the Thorlabs SDK; if it is unavailable, the handler will use simulation mode.
            from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
            # Load the Thorlabs camera SDK class; without this package the real camera cannot be controlled.
            self.sdk = TLCameraSDK()
            # Create the SDK object that can discover and open connected Thorlabs cameras.
            print("Thorlabs SDK loaded.")
            # Print a console message confirming that real camera support is available.
        except Exception as e:
        # Handle any failure from the protected camera setup step.
            print(f"SDK not found: {e}")
            # Show why the SDK setup failed.
            print("Using simulation mode.")
            # Tell the console that synthetic camera frames will be used instead of real hardware.
            self.simulation_mode = True
            # Switch to simulation mode so the rest of the program can still run without a real camera.

    # -----------------------------------------------------------------------------
    # 3.1 CONNECT TO CAMERA OR FALL BACK TO SIMULATION
    # This method tries to open the Thorlabs camera and configure it for continuous frame reading.
    # -----------------------------------------------------------------------------
    def connect(self):
        if self.simulation_mode:
        # Use the simulation path when real camera setup is unavailable or intentionally bypassed.
            self.is_connected = True
            # Mark the real camera as connected after configuration and the test frame succeed.
            print("Simulated camera connected.")
            # Show that the simulated camera source is ready.
            return True
            # Report successful camera availability to the main app.

        try:
        # Try the full real-camera setup; if any required step fails, the outer fallback switches to simulation.
            cameras = self.sdk.discover_available_cameras()
            # Ask the SDK for all connected Thorlabs cameras.

            if len(cameras) == 0:
            # Stop real-camera setup if the SDK cannot find any camera.
                raise Exception("No Thorlabs camera found.")
                # Raise a clear error so the outer fallback can switch to simulation mode.

            self.camera = self.sdk.open_camera(cameras[0])
            # Open the first detected camera and store it for later frame reading.

            # -------------------------------------------------
            # HARDWARE ROI
            # -------------------------------------------------

            try:
            # Try to apply the ROI directly on the camera so only the relevant region is delivered.
                roi_x1 = int(self.roi_x)
                roi_y1 = int(self.roi_y)

                roi_x2 = int(self.roi_x + self.roi_w)
                roi_y2 = int(self.roi_y + self.roi_h)

                self.camera.roi = (
                # Send the selected ROI rectangle to the real camera.
                    roi_x1,
                    roi_y1,
                    roi_x2,
                    roi_y2
                )

                print(
                # Print camera setup information for debugging in the console.
                    f"Hardware ROI set: "
                    f"x={roi_x1}, y={roi_y1}, "
                    f"w={self.roi_w}, h={self.roi_h}"
                )

            except Exception as e:
            # Keep going if the camera does not accept the hardware ROI setting.
                print("Could not set hardware ROI:", e)
                # Warn that hardware ROI setup failed; frame reading may still continue without it.

            try:
            # Try to apply exposure; if this optional setting fails, the code keeps setting up the camera.
                self.camera.exposure_time_us = self.exposure_us
                # Apply the configured exposure time to the camera.
            except Exception as e:
            # Keep going if exposure cannot be set.
                print("Could not set exposure:", e)
                # Warn that exposure setup failed, but continue trying other settings.

            try:
            # Try to apply gain; if this optional setting fails, the code keeps setting up the camera.
                self.camera.gain = self.gain
                # Apply the configured camera gain.
            except Exception as e:
            # Keep going if gain cannot be set.
                print("Could not set gain:", e)
                # Warn that gain setup failed, but continue camera setup.

            try:
            # Try to apply black level; if this optional setting fails, the code keeps setting up the camera.
                self.camera.black_level = self.black_level
                # Apply the configured black-level offset.
            except Exception as e:
            # Keep going if black level cannot be set.
                print("Could not set black level:", e)
                # Warn that black-level setup failed, but continue camera setup.

            try:
            # Try to put the camera into continuous acquisition mode.
                self.camera.frames_per_trigger_zero_for_unlimited = 0
                # Configure continuous acquisition so the camera can keep producing frames.
            except Exception as e:
            # Keep going if continuous mode cannot be set, then still try to arm/read the camera.
                print("Could not set continuous mode:", e)
                # Warn that continuous mode setup failed, but still try to arm the camera.

            try:
            # Arm the camera; this step is required before frames can be read.
                self.camera.arm(frames_to_buffer=10)
                # Arm the camera and allocate a small frame buffer for incoming images.
            except Exception as e:
            # Arming is required, so this failure is passed to the outer fallback.
                print("Could not arm camera:", e)
                # Report that camera acquisition could not be prepared.
                raise
                # Propagate this serious setup error to the outer fallback handler.

            try:
            # Test acquisition once so the program knows the camera can actually deliver frames.
                if hasattr(self.camera, "issue_software_trigger"):
                # Only issue a software trigger if this camera object supports that command.
                    self.camera.issue_software_trigger()
                    # Ask the camera to capture or deliver a frame.
                    time.sleep(0.05)
                    # Wait briefly so the camera has time to place a frame into its buffer.
                    frame = self.camera.get_pending_frame_or_null()
                    # Try to read the first pending frame from the camera buffer.
                    if frame is None:
                    # Treat missing first frame as acquisition startup failure.
                        raise Exception("No frame received after software trigger.")
                        # Abort real-camera startup because the camera did not deliver a test frame.
            except Exception as e:
            # Acquisition is required, so this failure is passed to the outer fallback.
                print("Could not start acquisition:", e)
                # Report that the camera could not begin frame acquisition.
                raise
                # Propagate this serious setup error to the outer fallback handler.

            self.is_connected = True
            # Mark the real camera as connected after configuration and the test frame succeed.
            print("Camera connected.")
            # Report that the real camera was configured and tested successfully.
            return True
            # Report successful camera availability to the main app.

        except Exception as e:
        # Handle camera setup failure and switch to the simulation fallback.
            print(f"Camera connection failed: {e}")
            # Show the reason why real-camera connection failed.
            print("Using simulation mode.")
            # Tell the console that synthetic camera frames will be used instead of real hardware.
            self.simulation_mode = True
            # Switch to simulation mode so the rest of the program can still run without a real camera.
            self.is_connected = True
            # Mark the real camera as connected after configuration and the test frame succeed.
            return True
            # Report successful camera availability to the main app.

    # -----------------------------------------------------------------------------
    # 4.1 READ ONE CAMERA FRAME
    # This returns either a simulated frame or a copied image buffer from the real camera.
    # -----------------------------------------------------------------------------
    def get_frame(self):
        if self.simulation_mode:
        # Use the simulation path when real camera setup is unavailable or intentionally bypassed.
            img = np.random.normal(30, 8, (1024, 1280)).astype(np.float32)
            # Create a simulated noisy camera image with realistic size and floating-point brightness values.

            y, x = np.indices(img.shape)
            # Create coordinate grids so the simulated spot and fringes can be calculated per pixel.
            cx, cy = 760, 460
            # Place the simulated bright spot near the same area as the configured ROI.

            spot = 220 * np.exp(
            # Create a broad Gaussian bright spot that imitates the illuminated interferometer signal.
                -(((x - cx) ** 2) / (2 * 150 ** 2) +
                  ((y - cy) ** 2) / (2 * 190 ** 2))
            )

            fringes = 45 * np.sin(0.09 * x + 0.04 * y + time.time() * 3)
            # Add moving sinusoidal fringes so the simulated image changes over time.

            img = img + spot + fringes
            # Combine camera noise, the bright spot, and the fringe pattern into one simulated frame.
            img = np.clip(img, 0, 255).astype(np.uint8)
            # Limit simulated brightness to normal 8-bit camera values.
            return img
            # Return the simulated frame to the main monitoring loop.

        if self.camera is None:
        # If no real camera object exists, no real frame can be read.
            return None
            # Report that this frame request did not produce an image.

        try:
        # Try to request and read one frame from the real camera.
            if hasattr(self.camera, "issue_software_trigger"):
            # Only issue a software trigger if this camera object supports that command.
                self.camera.issue_software_trigger()
                # Ask the camera to capture or deliver a frame.

            for _ in range(20):
            # Try several short reads because the camera frame may not be ready immediately.
                frame = self.camera.get_pending_frame_or_null()
                # Try to read the first pending frame from the camera buffer.

                if frame is not None:
                # Use the frame as soon as the camera delivers one.
                    return np.copy(frame.image_buffer)
                    # Return a safe copy of the camera image buffer so later SDK changes cannot alter it unexpectedly.

                time.sleep(0.001)
                # Wait one millisecond before checking the camera buffer again.

        except Exception as e:
        # Handle frame-read errors and let the main loop continue.
            print("Frame read error:", e)
            # Report frame-read problems without crashing the main app.

        return None
        # Report that this frame request did not produce an image.

    # -----------------------------------------------------------------------------
    # 5.1 EXTRACT THE ANALYSIS ROI
    # This crops the selected image region used for brightness and fringe analysis.
    # -----------------------------------------------------------------------------
    def get_roi(self, img):
        if img is None:
        # Reject missing images before trying to crop or analyze them.
            return None
            # Report that no valid ROI could be extracted.

        h, w = img.shape
        # Read image height and width so the ROI can be clipped to valid pixel coordinates.

        x1 = max(0, min(self.roi_x, w - 1))
        # Clamp the ROI left edge inside the image width.
        y1 = max(0, min(self.roi_y, h - 1))
        # Clamp the ROI top edge inside the image height.
        x2 = max(0, min(x1 + self.roi_w, w))
        # Clamp the ROI right edge so it does not go past the image width.
        y2 = max(0, min(y1 + self.roi_h, h))
        # Clamp the ROI bottom edge so it does not go past the image height.

        roi = img[y1:y2, x1:x2]
        # Cut out the ROI pixels used for intensity and fringe analysis.

        if roi.size == 0:
        # Reject an empty ROI because it cannot produce a meaningful intensity.
            return None
            # Report that no valid ROI could be extracted.

        return roi
        # Return the cropped ROI image region.

    # -----------------------------------------------------------------------------
    # 6.1 CALCULATE ROI CONTRAST
    # This estimates contrast inside the ROI from robust low and high intensity percentiles.
    # -----------------------------------------------------------------------------
    def get_contrast_from_frame(self, img):
        roi = self.get_roi(img)
        # Extract the configured ROI before doing signal analysis.

        if roi is None:
        # Stop analysis when no valid ROI could be extracted.
            return None
            # Report that contrast cannot be calculated without a valid ROI.

        roi = roi.astype(np.float32)
        # Convert ROI pixels to floating point so percentiles and normalization are accurate.

        roi_min = np.percentile(roi, 5)
        # Use the 5th percentile as a robust dark level inside the ROI.
        roi_max = np.percentile(roi, 95)
        # Use the 95th percentile as a robust bright level inside the ROI.

        contrast = (roi_max - roi_min) / (roi_max + roi_min + 1e-6)
        # Calculate normalized contrast while avoiding division by zero with a tiny offset.

        return float(contrast)
        # Return contrast as a normal Python float for the rest of the app.

    # -----------------------------------------------------------------------------
    # 6.2 CALCULATE MEAN ROI INTENSITY
    # This returns the average brightness of the ROI used by the main fringe detector.
    # -----------------------------------------------------------------------------
    def get_fringe_intensity_from_frame(self, img):
        # This helper remains available because the main app still uses mean ROI intensity.
        roi = self.get_roi(img)
        # Extract the configured ROI before doing signal analysis.

        if roi is None:
        # Stop analysis when no valid ROI could be extracted.
            return None
            # Report that intensity cannot be calculated without a valid ROI.

        return float(np.mean(roi))
        # Return the average ROI brightness used as the fringe intensity signal.

    # -----------------------------------------------------------------------------
    # 6.3 COUNT VISIBLE FRINGES IN THE ROI
    # This builds a one-dimensional brightness profile and counts visible peaks.
    # -----------------------------------------------------------------------------
    def count_visible_fringes_from_frame(self, img):
        roi = self.get_roi(img)
        # Extract the configured ROI before doing signal analysis.

        if roi is None:
        # Stop analysis when no valid ROI could be extracted.
            return 0
            # Return zero visible fringes when the ROI is missing or has no usable variation.

        roi = roi.astype(np.float32)
        # Convert ROI pixels to floating point so percentiles and normalization are accurate.
        roi -= np.min(roi)
        # Shift the ROI so the darkest pixel becomes zero before normalization.

        if np.max(roi) > 0:
        # Normalize only if the ROI contains nonzero brightness variation.
            roi /= np.max(roi)
            # Scale the ROI to a 0-to-1 range for peak detection.

        profile = np.mean(roi, axis=0)
        # Average the ROI vertically to create a horizontal intensity profile.

        window = 9
        # Use a 9-pixel smoothing window for the profile.
        kernel = np.ones(window) / window
        # Create a simple averaging kernel for smoothing.
        profile_smooth = np.convolve(profile, kernel, mode="same")

        mean_val = np.mean(profile_smooth)
        # Calculate the average profile level for adaptive peak thresholding.
        std_val = np.std(profile_smooth)
        # Calculate profile variation so the peak threshold scales with signal strength.

        if std_val == 0:
        # If the profile is flat, there are no visible peaks to count.
            return 0
            # Return zero visible fringes when the ROI is missing or has no usable variation.

        peaks, _ = find_peaks(
        # Find bright peaks in the smoothed ROI profile.
            profile_smooth,
            height=mean_val + 0.25 * std_val,
            distance=8,
            prominence=0.08 * std_val
        )

        return len(peaks)
        # Return the number of detected bright fringe peaks.

    # -----------------------------------------------------------------------------
    # 7.1 CLOSE CAMERA RESOURCES
    # This stops camera acquisition and releases SDK resources when the app closes.
    # -----------------------------------------------------------------------------
    def close(self):
        try:
        # Try the hardware-specific action, but keep a fallback path if it fails.
            if self.camera is not None:
            # Only close the camera if a real camera object was opened.
                self.camera.disarm()
                # Stop camera acquisition before disposing of the camera object.
                self.camera.dispose()
                # Release the camera object through the SDK.
                self.camera = None
                # Clear the stored camera object after it has been released.

            if self.sdk is not None:
            # Only dispose of the SDK if it was created.
                self.sdk.dispose()
                # Release SDK resources.
                self.sdk = None
                # Clear the stored SDK object after disposal.

        except Exception as e:
        # Handle cleanup errors during shutdown.
            print("Camera close error:", e)
            # Report cleanup errors without interrupting shutdown.

        self.is_connected = False
        # Start disconnected; this becomes True after real camera setup or simulation setup succeeds.
