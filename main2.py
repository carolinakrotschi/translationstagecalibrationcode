#version of the code with vertical profile analysis and 2s sleep time
import os
import sys
import threading
import time
from datetime import datetime

import numpy as np
import customtkinter as ctk
from scipy.signal import find_peaks
from PIL import Image
from pipython import GCSDevice, pitools


# === DLL SETUP ===
current_directory = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_directory, 'Camera')

if os.path.exists(dll_path):
    os.add_dll_directory(dll_path)
else:
    print(f"ERROR: Hardware driver folder not found at {dll_path}")

try:
    from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
except Exception as e:
    print(f"SDK Import Warning: {e}")


# === CONFIG ===
LASER_WAVELENGTH_NM = 632.8
FRINGE_DISTANCE_MM = (LASER_WAVELENGTH_NM / 2) / 1_000_000
SPEED_OF_LIGHT_MM_PS = 0.299792458


# === CAMERA ===
class CameraHandler:
    def __init__(self):
        self.camera = None
        self.sdk = None
        self.simulation_mode = False
        self.status = "NOT INITIALIZED"

        try:
            from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
            self.sdk = TLCameraSDK()
            self.status = "SDK LOADED"
        except Exception as e:
            self.simulation_mode = True
            self.status = f"SDK ERROR: {e}"

    def connect(self):
        if self.simulation_mode:
            self.status = "SIMULATION MODE"
            return False

        try:
            devices = self.sdk.discover_available_cameras()

            if len(devices) == 0:
                self.simulation_mode = True
                self.status = "NO CAMERA FOUND → SIMULATION"
                return False

            self.camera = self.sdk.open_camera(devices[0])
            self.camera.arm(frames_to_buffer=10)

            self.camera.issue_software_trigger()
            time.sleep(0.05)
            frame = self.camera.get_pending_frame_or_null()

            if frame is None:
                self.simulation_mode = True
                self.status = "CAMERA NOT STREAMING → SIMULATION"
                return False

            self.status = "CAMERA CONNECTED & WORKING"
            return True

        except Exception as e:
            self.simulation_mode = True
            self.status = f"CAMERA ERROR: {e}"
            return False

    def get_vertical_profile(self):
        if self.simulation_mode:
            y = np.linspace(0, 6 * np.pi, 300)
            return 120 + 50 * np.sin(y + time.time())

        if self.camera:
            self.camera.issue_software_trigger()

            for _ in range(10):
                frame = self.camera.get_pending_frame_or_null()

                if frame is not None:
                    img = frame.image_buffer
                    h, w = img.shape

                    stripe_width = 30
                    x = w // 2

                    stripe = img[:, x - stripe_width:x + stripe_width]
                    profile = np.mean(stripe, axis=1)

                    return profile

                time.sleep(0.001)

        return None


# === APP ===
class InterferometerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.pidevice = GCSDevice('C-663')
        self.stage_connected = False
        self.axis = None
        self.connect_stage()

        self.camera_handler = CameraHandler()
        self.camera_connected = self.camera_handler.connect()

        self.is_monitoring = False

        self.title("Fringe Counter")
        self.geometry("500x600")
        ctk.set_appearance_mode("light")

        self.label_title = ctk.CTkLabel(self, text="Fringe Analyzer", font=("Arial", 22, "bold"))
        self.label_title.pack(pady=20)

        self.label_camera = ctk.CTkLabel(self, text="Camera: checking...", font=("Arial", 14))
        self.label_camera.pack(pady=5)

        if self.camera_connected:
            self.label_camera.configure(text="Camera: CONNECTED", text_color="green")
        else:
            self.label_camera.configure(
                text=f"Camera: {self.camera_handler.status}",
                text_color="red"
            )

        self.btn_start = ctk.CTkButton(self, text="START", command=self.toggle_monitoring)
        self.btn_start.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Idle")
        self.status_label.pack(pady=10)

        self.label_fringe = ctk.CTkLabel(self, text="Fringes: 0", font=("Arial", 18))
        self.label_fringe.pack(pady=10)

        self.label_dist = ctk.CTkLabel(self, text="Distance: 0 µm", font=("Arial", 16))
        self.label_dist.pack(pady=10)

        self.label_time = ctk.CTkLabel(self, text="Delay: 0 ps", font=("Arial", 16))
        self.label_time.pack(pady=10)

    def connect_stage(self):
        try:
            self.pidevice.ConnectUSB(serialnum='0')
            pitools.startup(self.pidevice)
            self.axis = self.pidevice.axes[0]
            self.stage_connected = True
        except Exception:
            self.stage_connected = False

    def toggle_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.btn_start.configure(text="STOP")
            self.status_label.configure(text="Running", text_color="green")
            threading.Thread(target=self.run_monitor, daemon=True).start()
        else:
            self.is_monitoring = False
            self.btn_start.configure(text="START")
            self.status_label.configure(text="Stopped", text_color="black")

    def run_monitor(self):
        while self.is_monitoring:

            profile = self.camera_handler.get_vertical_profile()

            if profile is not None:

                smoothed = np.convolve(profile, np.ones(7)/7, mode='valid')

                mean = np.mean(smoothed)
                std = np.std(smoothed)

                peaks, _ = find_peaks(
                    smoothed,
                    height=mean + 0.3 * std,
                    distance=10,
                    prominence=0.2 * std
                )

                fringe_count = len(peaks)

                dist_mm = fringe_count * FRINGE_DISTANCE_MM
                dist_um = dist_mm * 1000
                time_ps = (2 * dist_mm) / SPEED_OF_LIGHT_MM_PS

                self.after(0, lambda:
                    self.update_ui(fringe_count, dist_um, time_ps)
                )

            time.sleep(2.0)

    def update_ui(self, fringes, dist_um, time_ps):
        self.label_fringe.configure(text=f"Fringes: {fringes}")
        self.label_dist.configure(text=f"Distance: {dist_um:.3f} µm")
        self.label_time.configure(text=f"Delay: {time_ps:.3f} ps")

    def on_close(self):
        self.is_monitoring = False

        if self.stage_connected:
            self.pidevice.CloseConnection()

        self.destroy()


# === MAIN ===
if __name__ == "__main__":
    app = InterferometerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()