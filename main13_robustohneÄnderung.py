# Version: Robuste Fringe-Erkennung mit Hysterese + Glättung + Cooldown

import os
import threading
import time
import numpy as np
import customtkinter as ctk

from PIL import Image, ImageDraw

from camera_handler import CameraHandler


# =========================================================
# DLL / CAMERA
# =========================================================

current_directory = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_directory, "Camera")

if os.path.exists(dll_path):
    os.add_dll_directory(dll_path)
    print(f"Drivers loaded: {dll_path}")


# =========================================================
# PHYSICS
# =========================================================

LASER_WAVELENGTH_NM = 632.8
FRINGE_DISTANCE_MM = (LASER_WAVELENGTH_NM / 2) / 1_000_000
SPEED_OF_LIGHT_MM_PS = 0.299792458


# =========================================================
# COLORS
# =========================================================

TEXT_COLOR = "#0A4A51"
GREEN_COLOR = "#1EAD4F"
RED_COLOR = "#C0392B"


# =========================================================
# APP
# =========================================================

class InterferometerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # -------------------------------------------------
        # STATES
        # -------------------------------------------------

        self.is_monitoring = False

        self.intensity_history = []
        self.history_size = 15

        self.accumulated_fringes = 0

        self.was_dark = False
        self.last_count_time = 0

        # -------------------------------------------------
        # CAMERA
        # -------------------------------------------------

        self.camera_handler = CameraHandler()
        self.camera_connected = self.camera_handler.connect()

        # -------------------------------------------------
        # WINDOW
        # -------------------------------------------------

        self.title("Interferometer Monitor")
        self.geometry("760x1050")

        ctk.set_appearance_mode("light")

        self.configure(fg_color="white")

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        ctk.CTkLabel(
            self,
            text="Interferometer Monitor",
            font=("Arial", 26, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=20)

        # -------------------------------------------------
        # START BUTTON
        # -------------------------------------------------

        self.btn = ctk.CTkButton(
            self,
            text="START MONITORING",
            command=self.toggle,
            height=45,
            width=230,
            font=("Arial", 16, "bold"),
            fg_color=TEXT_COLOR
        )

        self.btn.pack(pady=10)

        # -------------------------------------------------
        # RESET BUTTON
        # -------------------------------------------------

        self.restart_btn = ctk.CTkButton(
            self,
            text="RESTART / RESET",
            command=self.restart,
            height=40,
            width=210,
            font=("Arial", 14, "bold"),
            fg_color="#D35400"
        )

        self.restart_btn.pack(pady=5)

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status = ctk.CTkLabel(
            self,
            text="Status: Stopped",
            font=("Arial", 15),
            text_color=TEXT_COLOR
        )

        self.status.pack(pady=5)

        # -------------------------------------------------
        # INFO FRAME
        # -------------------------------------------------

        self.frame = ctk.CTkFrame(
            self,
            fg_color="#EEEEEE"
        )

        self.frame.pack(
            pady=20,
            padx=25,
            fill="x"
        )

        # -------------------------------------------------
        # DISTANCE MM
        # -------------------------------------------------

        self.label_mm = ctk.CTkLabel(
            self.frame,
            text="Distance: 0.000000 mm",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_mm.pack(pady=5)

        # -------------------------------------------------
        # DISTANCE UM
        # -------------------------------------------------

        self.label_um = ctk.CTkLabel(
            self.frame,
            text="Distance: 0.000 µm",
            font=("Arial", 18, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_um.pack(pady=5)

        # -------------------------------------------------
        # TIME DELAY
        # -------------------------------------------------

        self.label_ps = ctk.CTkLabel(
            self.frame,
            text="Time Delay: 0.0000 ps",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_ps.pack(pady=5)

        # -------------------------------------------------
        # INTENSITY
        # -------------------------------------------------

        self.label_intensity = ctk.CTkLabel(
            self.frame,
            text="Intensity: 0.00",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_intensity.pack(pady=5)

        # -------------------------------------------------
        # FRINGE COUNT
        # -------------------------------------------------

        self.label_accumulated_fringes = ctk.CTkLabel(
            self.frame,
            text="Accumulated Fringes Count: 0",
            font=("Arial", 18, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_accumulated_fringes.pack(pady=10)

        # -------------------------------------------------
        # LIVE IMAGE
        # -------------------------------------------------

        self.live_size = (620, 460)

        ctk.CTkLabel(
            self,
            text="Live Camera Frame",
            font=("Arial", 18, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(20, 8))

        self.image_label = ctk.CTkLabel(
            self,
            text="No Image",
            width=self.live_size[0],
            height=self.live_size[1],
            fg_color="#111111",
            text_color="white"
        )

        self.image_label.pack(pady=10)

        # -------------------------------------------------
        # LOGO
        # -------------------------------------------------

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "assets", "logo.png")

        if os.path.exists(logo_path):

            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                size=(300, 81)
            )

            ctk.CTkLabel(
                self,
                image=self.logo_image,
                text=""
            ).pack(pady=25)

    # =====================================================
    # START / STOP
    # =====================================================

    def toggle(self):

        if not self.is_monitoring:

            if not self.camera_connected:

                self.status.configure(
                    text="Error: Camera not connected",
                    text_color="red"
                )

                return

            self.restart_values_only()

            self.is_monitoring = True

            self.btn.configure(
                text="STOP MONITORING",
                fg_color=RED_COLOR
            )

            self.status.configure(
                text="Status: Running",
                text_color="green"
            )

            threading.Thread(
                target=self.loop,
                daemon=True
            ).start()

        else:

            self.is_monitoring = False

            self.btn.configure(
                text="START MONITORING",
                fg_color=TEXT_COLOR
            )

            self.status.configure(
                text="Status: Stopped",
                text_color=TEXT_COLOR
            )

    # =====================================================
    # RESET
    # =====================================================

    def restart(self):

        self.restart_values_only()

        self.status.configure(
            text="Status: Reset to 0",
            text_color="#D35400"
        )

    # =====================================================
    # RESET VALUES
    # =====================================================

    def restart_values_only(self):

        self.intensity_history = []

        self.accumulated_fringes = 0

        self.was_dark = False

        self.last_count_time = 0

        self.label_mm.configure(
            text="Distance: 0.000000 mm"
        )

        self.label_um.configure(
            text="Distance: 0.000 µm"
        )

        self.label_ps.configure(
            text="Time Delay: 0.0000 ps"
        )

        self.label_intensity.configure(
            text="Intensity: 0.00",
            text_color=TEXT_COLOR
        )

        self.label_accumulated_fringes.configure(
            text="Accumulated Fringes Count: 0"
        )

    # =====================================================
    # MAIN LOOP
    # =====================================================

    def loop(self):

        frame_counter = 0

        while self.is_monitoring:

            img = self.camera_handler.get_frame()

            if img is None:
                continue

            frame_counter += 1

            # -------------------------------------------------
            # IMAGE UPDATE
            # -------------------------------------------------

            if frame_counter % 20 == 0:

                self.after(
                    0,
                    lambda f=img: self.update_image(f)
                )

            # -------------------------------------------------
            # INTENSITY
            # -------------------------------------------------

            intensity = self.camera_handler.get_fringe_intensity_from_frame(img)

            if intensity is not None:

                fringe_counted = self.update_accumulated_fringes(intensity)

                self.after(
                    0,
                    lambda v=intensity, counted=fringe_counted:
                    self.update_intensity_label(v, counted)
                )

            # -------------------------------------------------
            # PHYSICS
            # -------------------------------------------------

            dist_mm = self.accumulated_fringes * FRINGE_DISTANCE_MM

            dist_um = dist_mm * 1000

            time_ps = (2 * dist_mm) / SPEED_OF_LIGHT_MM_PS

            self.after(
                0,
                lambda d=dist_mm, u=dist_um, p=time_ps:
                self.update_values(d, u, p)
            )

            self.after(
                0,
                lambda v=self.accumulated_fringes:
                self.label_accumulated_fringes.configure(
                    text=f"Accumulated Fringes Count: {v}"
                )
            )

    # =====================================================
    # ROBUST FRINGE DETECTION
    # =====================================================

    def update_accumulated_fringes(self, intensity):

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        self.intensity_history.append(intensity)

        if len(self.intensity_history) > self.history_size:
            self.intensity_history.pop(0)

        if len(self.intensity_history) < 20:
            return False

        signal = np.array(self.intensity_history)

        # -------------------------------------------------
        # SMOOTHING
        # -------------------------------------------------

        smooth = np.mean(signal[-5:])

        # -------------------------------------------------
        # DYNAMIC THRESHOLDS
        # -------------------------------------------------

        mean_val = np.mean(signal)

        std_val = np.std(signal)

        if std_val < 20:
            std_val = 20

        dark_threshold = mean_val - 0.25 * std_val

        bright_threshold = mean_val + 0.25 * std_val

        # -------------------------------------------------
        # STABLE DARK
        # -------------------------------------------------

        dark_state = np.mean(signal[-4:]) < dark_threshold

        if dark_state:
            self.was_dark = True
            return False

        # -------------------------------------------------
        # STABLE BRIGHT
        # -------------------------------------------------

        bright_state = np.mean(signal[-4:]) > bright_threshold

        cooldown_ok = (time.time() - self.last_count_time) > 0.12

        if self.was_dark and bright_state and cooldown_ok:

            self.accumulated_fringes += 1

            self.was_dark = False

            self.last_count_time = time.time()

            return True

        return False

    # =====================================================
    # UPDATE INTENSITY LABEL
    # =====================================================

    def update_intensity_label(self, intensity, fringe_counted):

        self.label_intensity.configure(
            text=f"Intensity: {intensity:.2f}"
        )

        if fringe_counted:

            self.label_intensity.configure(
                text_color=GREEN_COLOR
            )

            self.after(
                300,
                lambda:
                self.label_intensity.configure(
                    text_color=TEXT_COLOR
                )
            )

    # =====================================================
    # UPDATE IMAGE
    # =====================================================

    def update_image(self, img):

        display = img.astype(np.float32)

        display -= np.min(display)

        if np.max(display) > 0:
            display /= np.max(display)

        display = (display * 255).astype(np.uint8)

        pil = Image.fromarray(display).convert("RGB")

        original_w, original_h = pil.size

        scale_x = self.live_size[0] / original_w
        scale_y = self.live_size[1] / original_h

        pil = pil.resize(self.live_size)

        draw = ImageDraw.Draw(pil)

        x1 = int(self.camera_handler.roi_x * scale_x)
        y1 = int(self.camera_handler.roi_y * scale_y)

        x2 = int(
            (self.camera_handler.roi_x + self.camera_handler.roi_w)
            * scale_x
        )

        y2 = int(
            (self.camera_handler.roi_y + self.camera_handler.roi_h)
            * scale_y
        )

        draw.rectangle(
            [x1, y1, x2, y2],
            outline="yellow",
            width=3
        )

        ctk_img = ctk.CTkImage(
            light_image=pil,
            size=self.live_size
        )

        self.image_label.configure(
            image=ctk_img,
            text=""
        )

        self.image_label.image = ctk_img

    # =====================================================
    # UPDATE VALUES
    # =====================================================

    def update_values(self, mm, um, ps):

        self.label_mm.configure(
            text=f"Distance: {mm:.6f} mm"
        )

        self.label_um.configure(
            text=f"Distance: {um:.3f} µm"
        )

        self.label_ps.configure(
            text=f"Time Delay: {ps:.4f} ps"
        )

    # =====================================================
    # CLOSE
    # =====================================================

    def on_close(self):

        self.is_monitoring = False

        try:
            self.camera_handler.close()

        except Exception as e:
            print("Camera close error:", e)

        self.destroy()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    app = InterferometerApp()

    app.protocol(
        "WM_DELETE_WINDOW",
        app.on_close
    )

    app.mainloop()