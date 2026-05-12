import numpy as np
import time
from scipy.signal import find_peaks


class CameraHandler:
    def __init__(self):
        self.camera = None
        self.sdk = None
        self.is_connected = False
        self.simulation_mode = False

        # ROI hier einstellen
        self.roi_x = 754
        self.roi_y = 464
        self.roi_w = 40
        self.roi_h = 40

        # Camera Settings hier einstellen
        self.exposure_us = 100 #in mykrometer
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

    def connect(self):
        if self.simulation_mode:
            self.is_connected = True
            print("Simulated camera connected.")
            return True

        try:
            cameras = self.sdk.discover_available_cameras()

            if len(cameras) == 0:
                raise Exception("No Thorlabs camera found.")

            self.camera = self.sdk.open_camera(cameras[0])

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

            self.camera.arm(2)
            self.camera.issue_software_trigger()

            self.is_connected = True
            print("Camera connected.")
            return True

        except Exception as e:
            print(f"Camera connection failed: {e}")
            print("Using simulation mode.")
            self.simulation_mode = True
            self.is_connected = True
            return True

    def get_frame(self):
        if self.simulation_mode:
            img = np.random.normal(30, 8, (1024, 1280)).astype(np.float32)

            y, x = np.indices(img.shape)
            cx, cy = 760, 460

            spot = 220 * np.exp(
                -(((x - cx) ** 2) / (2 * 150 ** 2) +
                  ((y - cy) ** 2) / (2 * 190 ** 2))
            )

            fringes = 45 * np.sin(0.09 * x + 0.04 * y + time.time() * 3)

            img = img + spot + fringes
            img = np.clip(img, 0, 255).astype(np.uint8)
            return img

        if self.camera is None:
            return None

        try:
            self.camera.issue_software_trigger()

            for _ in range(20):
                frame = self.camera.get_pending_frame_or_null()

                if frame is not None:
                    return np.copy(frame.image_buffer)

                #time.sleep(0.001)

        except Exception as e:
            print("Frame read error:", e)

        return None

    def get_roi(self, img):
        if img is None:
            return None

        h, w = img.shape

        x1 = max(0, min(self.roi_x, w - 1))
        y1 = max(0, min(self.roi_y, h - 1))
        x2 = max(0, min(x1 + self.roi_w, w))
        y2 = max(0, min(y1 + self.roi_h, h))

        roi = img[y1:y2, x1:x2]

        if roi.size == 0:
            return None

        return roi

    def get_contrast_from_frame(self, img):
        roi = self.get_roi(img)

        if roi is None:
            return None

        roi = roi.astype(np.float32)

        roi_min = np.percentile(roi, 5)
        roi_max = np.percentile(roi, 95)

        contrast = (roi_max - roi_min) / (roi_max + roi_min + 1e-6)

        return float(contrast)

    def get_fringe_intensity_from_frame(self, img):
        # bleibt drin, falls alter Code es noch irgendwo nutzt
        roi = self.get_roi(img)

        if roi is None:
            return None

        return float(np.mean(roi))

    def count_visible_fringes_from_frame(self, img):
        roi = self.get_roi(img)

        if roi is None:
            return 0

        roi = roi.astype(np.float32)
        roi -= np.min(roi)

        if np.max(roi) > 0:
            roi /= np.max(roi)

        profile = np.mean(roi, axis=0)

        window = 9
        kernel = np.ones(window) / window
        profile_smooth = np.convolve(profile, kernel, mode="same")

        mean_val = np.mean(profile_smooth)
        std_val = np.std(profile_smooth)

        if std_val == 0:
            return 0

        peaks, _ = find_peaks(
            profile_smooth,
            height=mean_val + 0.25 * std_val,
            distance=8,
            prominence=0.08 * std_val
        )

        return len(peaks)

    def close(self):
        try:
            if self.camera is not None:
                self.camera.disarm()
                self.camera.dispose()
                self.camera = None

            if self.sdk is not None:
                self.sdk.dispose()
                self.sdk = None

        except Exception as e:
            print("Camera close error:", e)

        self.is_connected = False