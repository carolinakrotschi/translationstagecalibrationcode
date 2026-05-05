#code mit live gui anzeige von camera aber intensitzt mean
import os
import threading
import time
import numpy as np
import customtkinter as ctk

from PIL import Image
from scipy.signal import find_peaks
from pipython import GCSDevice, pitools

from camera_handler import CameraHandler


# DLL-Pfad
current_directory = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_directory, "Camera")

if os.path.exists(dll_path):
    os.add_dll_directory(dll_path)
    print(f"Successfully loaded drivers from: {dll_path}")
else:
    print(f"WARNING: Camera driver folder not found at {dll_path}")


# KONSTANTEN
LASER_WAVELENGTH_NM = 632.8
FRINGE_DISTANCE_MM = (LASER_WAVELENGTH_NM / 2) / 1_000_000
SPEED_OF_LIGHT_MM_PS = 0.299792458


class InterferometerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Status
        self.is_monitoring = False
        self.stage_connected = False
        self.axis = None
        self.pidevice = None

        # Kamera
        self.camera_handler = CameraHandler()
        self.camera_connected = self.camera_handler.connect()

        # PI Stage
        self.connect_hardware()

        # GUI
        self.title("Precision Interferometer Monitor")
        self.geometry("600x900")
        ctk.set_appearance_mode("light")
        self.configure(fg_color="#FFFFFF")

        self.label_title = ctk.CTkLabel(
            self,
            text="Interferometer Monitor",
            font=("Arial", 22, "bold"),
            text_color="#0A4A51"
        )
        self.label_title.pack(pady=20)

        self.btn_start = ctk.CTkButton(
            self,
            text="START MONITORING",
            command=self.toggle_monitoring,
            font=("Arial", 14, "bold"),
            height=40,
            fg_color="#0A4A51"
        )
        self.btn_start.pack(pady=15)

        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Ready",
            text_color="#0A4A51"
        )
        self.status_label.pack(pady=5)

        self.result_frame = ctk.CTkFrame(self, fg_color="#F0F0F0")
        self.result_frame.pack(pady=20, padx=20, fill="x")

        self.label_dist_mm = ctk.CTkLabel(
            self.result_frame,
            text="Distance: 0.000000 mm",
            font=("Arial", 16)
        )
        self.label_dist_mm.pack(pady=5)

        self.label_dist_um = ctk.CTkLabel(
            self.result_frame,
            text="Distance: 0.000 µm",
            font=("Arial", 16, "bold"),
            text_color="#0A4A51"
        )
        self.label_dist_um.pack(pady=5)

        self.label_time_ps = ctk.CTkLabel(
            self.result_frame,
            text="Time Delay: 0.0000 ps",
            font=("Arial", 16),
            text_color="#D35400"
        )
        self.label_time_ps.pack(pady=5)

        self.label_intensity = ctk.CTkLabel(
            self.result_frame,
            text="Intensity: 0.00",
            font=("Arial", 15),
            text_color="#333333"
        )
        self.label_intensity.pack(pady=5)

        # Logo
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "assets", "logo.png")

        if os.path.exists(logo_path):
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                size=(300, 81)
            )
            ctk.CTkLabel(self, image=self.logo_image, text="").pack(pady=15)

        # Live-Kamerabild unten im GUI
        self.live_image_size = (520, 360)

        self.camera_title = ctk.CTkLabel(
            self,
            text="Live Camera Frame",
            font=("Arial", 16, "bold"),
            text_color="#0A4A51"
        )
        self.camera_title.pack(pady=(15, 5))

        self.camera_image_label = ctk.CTkLabel(
            self,
            text="No camera image yet",
            width=self.live_image_size[0],
            height=self.live_image_size[1],
            fg_color="#222222",
            text_color="white"
        )
        self.camera_image_label.pack(pady=10)

    def connect_hardware(self):
        try:
            self.pidevice = GCSDevice("C-663")
            self.pidevice.ConnectUSB(serialnum="0")
            pitools.startup(self.pidevice)
            self.axis = self.pidevice.axes[0]
            self.stage_connected = True
            print("PI stage connected.")
        except Exception as e:
            self.stage_connected = False
            self.pidevice = None
            print("PI stage not connected:", e)

    def toggle_monitoring(self):
        if not self.is_monitoring:
            if not self.camera_connected:
                self.status_label.configure(
                    text="Error: Camera not connected",
                    text_color="red"
                )
                return

            self.is_monitoring = True
            self.btn_start.configure(
                text="STOP MONITORING",
                fg_color="#C0392B"
            )
            self.status_label.configure(
                text="Status: Live Monitoring...",
                text_color="green"
            )

            thread = threading.Thread(
                target=self.run_live_monitor,
                daemon=True
            )
            thread.start()

        else:
            self.is_monitoring = False
            self.btn_start.configure(
                text="START MONITORING",
                fg_color="#0A4A51"
            )
            self.status_label.configure(
                text="Status: Stopped",
                text_color="#0A4A51"
            )

    def run_live_monitor(self):
        try:
            fringe_count = 0
            intensity_history = []
            history_size = 100
            last_counted_peak_index = -1

            while self.is_monitoring:
                img = self.camera_handler.get_frame()

                if img is not None:
                    intensity = self.camera_handler.get_fringe_intensity_from_frame(img)

                    self.after(
                        0,
                        lambda frame=img: self.update_camera_display(frame)
                    )

                    self.after(
                        0,
                        lambda val=intensity: self.label_intensity.configure(
                            text=f"Intensity: {val:.2f}"
                        )
                    )

                else:
                    intensity = None

                if intensity is not None:
                    intensity_history.append(intensity)

                    if len(intensity_history) > history_size:
                        intensity_history.pop(0)

                    if len(intensity_history) >= history_size:
                        signal = np.array(intensity_history)

                        window = 5
                        smoothed = np.convolve(
                            signal,
                            np.ones(window) / window,
                            mode="valid"
                        )

                        mean_intensity = np.mean(smoothed)
                        std_intensity = np.std(smoothed)

                        threshold = mean_intensity + 0.5 * std_intensity

                        peaks, _ = find_peaks(
                            smoothed,
                            height=threshold,
                            distance=8,
                            prominence=0.3 * std_intensity
                        )

                        if len(peaks) > 0:
                            newest_peak = peaks[-1]

                            if newest_peak > last_counted_peak_index:
                                fringe_count += 1
                                last_counted_peak_index = newest_peak

                                dist_mm = fringe_count * FRINGE_DISTANCE_MM
                                dist_um = dist_mm * 1000
                                time_ps = (2 * dist_mm) / SPEED_OF_LIGHT_MM_PS

                                self.after(
                                    0,
                                    lambda d=dist_mm, u=dist_um, t=time_ps:
                                    self.update_display(d, u, t)
                                )

                time.sleep(0.05)

        except Exception as e:
            self.after(
                0,
                lambda err=e: self.status_label.configure(
                    text=f"Error: {err}",
                    text_color="red"
                )
            )

    def update_camera_display(self, img):
        if img is None:
            return

        img = img.astype(np.float32)
        img = img - np.min(img)

        max_val = np.max(img)

        if max_val > 0:
            img = img / max_val

        img = (img * 255).astype(np.uint8)

        pil_img = Image.fromarray(img)
        pil_img = pil_img.resize(self.live_image_size)

        ctk_img = ctk.CTkImage(
            light_image=pil_img,
            size=self.live_image_size
        )

        self.camera_image_label.configure(
            image=ctk_img,
            text=""
        )
        self.camera_image_label.image = ctk_img

    def update_display(self, mm, um, ps):
        self.label_dist_mm.configure(text=f"Distance: {mm:.6f} mm")
        self.label_dist_um.configure(text=f"Distance: {um:.3f} µm")
        self.label_time_ps.configure(text=f"Time Delay: {ps:.4f} ps")

    def on_closing(self):
        self.is_monitoring = False

        try:
            self.camera_handler.close()
        except Exception as e:
            print("Camera close error:", e)

        try:
            if self.stage_connected and self.pidevice is not None:
                self.pidevice.CloseConnection()
        except Exception as e:
            print("Stage close error:", e)

        self.destroy()


if __name__ == "__main__":
    app = InterferometerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()