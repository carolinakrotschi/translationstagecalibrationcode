#ganze gui anzeigen aber fringe zaehlen nicht intensity mean
import os
import threading
import time
import numpy as np
import customtkinter as ctk

from PIL import Image
from pipython import GCSDevice, pitools
from camera_handler import CameraHandler


# DLL-Pfad
current_directory = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_directory, "Camera")

if os.path.exists(dll_path):
    os.add_dll_directory(dll_path)
    print(f"Drivers loaded: {dll_path}")


# KONSTANTEN
LASER_WAVELENGTH_NM = 632.8
FRINGE_DISTANCE_MM = (LASER_WAVELENGTH_NM / 2) / 1_000_000
SPEED_OF_LIGHT_MM_PS = 0.299792458


class InterferometerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.is_monitoring = False

        # Kamera
        self.camera_handler = CameraHandler()
        self.camera_connected = self.camera_handler.connect()

        # GUI
        self.title("Interferometer Monitor")
        self.geometry("600x950")
        ctk.set_appearance_mode("light")

        # Titel
        ctk.CTkLabel(
            self,
            text="Interferometer Monitor",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        # Button
        self.btn = ctk.CTkButton(
            self,
            text="START MONITORING",
            command=self.toggle
        )
        self.btn.pack(pady=10)

        # Status
        self.status = ctk.CTkLabel(self, text="Status: Stopped")
        self.status.pack(pady=5)

        # Ergebnisfeld
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="x")

        self.label_mm = ctk.CTkLabel(self.frame, text="Distance: 0.000000 mm")
        self.label_mm.pack(pady=5)

        self.label_um = ctk.CTkLabel(self.frame, text="Distance: 0.000 µm")
        self.label_um.pack(pady=5)

        self.label_ps = ctk.CTkLabel(self.frame, text="Time Delay: 0.0000 ps")
        self.label_ps.pack(pady=5)

        self.label_intensity = ctk.CTkLabel(self.frame, text="Intensity: 0.00")
        self.label_intensity.pack(pady=5)

        # Fringes Count
        self.label_fringes = ctk.CTkLabel(
            self.frame,
            text="Fringes Count: 0",
            font=("Arial", 15, "bold")
        )
        self.label_fringes.pack(pady=5)

        # Livebild
        self.live_size = (520, 360)

        ctk.CTkLabel(
            self,
            text="Live Camera"
        ).pack(pady=(15, 5))

        self.image_label = ctk.CTkLabel(
            self,
            text="No Image",
            width=self.live_size[0],
            height=self.live_size[1]
        )
        self.image_label.pack(pady=10)

    # ----------------------

    def toggle(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.btn.configure(text="STOP MONITORING")
            self.status.configure(text="Status: Running")

            threading.Thread(target=self.loop, daemon=True).start()
        else:
            self.is_monitoring = False
            self.btn.configure(text="START MONITORING")
            self.status.configure(text="Status: Stopped")

    # ----------------------

    def loop(self):
        while self.is_monitoring:
            img = self.camera_handler.get_frame()

            if img is not None:

                # Bild anzeigen
                self.after(0, lambda f=img: self.update_image(f))

                # Intensity
                intensity = self.camera_handler.get_fringe_intensity_from_frame(img)

                if intensity is not None:
                    self.after(
                        0,
                        lambda v=intensity: self.label_intensity.configure(
                            text=f"Intensity: {v:.2f}"
                        )
                    )

                # 🔥 Fringes zählen
                fringes = self.camera_handler.count_fringes_from_frame(img)

                if fringes is not None:
                    self.after(
                        0,
                        lambda v=fringes: self.label_fringes.configure(
                            text=f"Fringes Count: {v}"
                        )
                    )

                    # Distanz berechnen
                    dist_mm = fringes * FRINGE_DISTANCE_MM
                    dist_um = dist_mm * 1000
                    time_ps = (2 * dist_mm) / SPEED_OF_LIGHT_MM_PS

                    self.after(
                        0,
                        lambda d=dist_mm, u=dist_um, t=time_ps:
                        self.update_values(d, u, t)
                    )

            time.sleep(0.05)

    # ----------------------

    def update_image(self, img):
        img = img.astype(np.float32)
        img -= np.min(img)

        if np.max(img) > 0:
            img /= np.max(img)

        img = (img * 255).astype(np.uint8)

        pil = Image.fromarray(img)
        pil = pil.resize(self.live_size)

        ctk_img = ctk.CTkImage(light_image=pil, size=self.live_size)

        self.image_label.configure(image=ctk_img, text="")
        self.image_label.image = ctk_img

    # ----------------------

    def update_values(self, mm, um, ps):
        self.label_mm.configure(text=f"Distance: {mm:.6f} mm")
        self.label_um.configure(text=f"Distance: {um:.3f} µm")
        self.label_ps.configure(text=f"Time Delay: {ps:.4f} ps")

    # ----------------------

    def on_close(self):
        self.is_monitoring = False
        self.camera_handler.close()
        self.destroy()


# ----------------------

if __name__ == "__main__":
    app = InterferometerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()