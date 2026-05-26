MANUAL_THRESHOLDS = False

MANUAL_DARK_THRESHOLD = 7
MANUAL_BRIGHT_THRESHOLD = 25


import os
import threading
import time
import numpy as np
import customtkinter as ctk

from PIL import Image, ImageDraw
from pipython import GCSDevice

from camera_handler import CameraHandler


current_directory = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_directory, "Camera")

if os.path.exists(dll_path):
    os.add_dll_directory(dll_path)


LASER_WAVELENGTH_NM = 1576.3

FRINGE_DISTANCE_MM = (
    (LASER_WAVELENGTH_NM / 2) / 1_000_000/2 #licht geht ja hin und zurueck, also 0.0004mm translationstage bewegen bedeutet nur ein halber fringe 0.000788
)

SPEED_OF_LIGHT_MM_PS = 0.299792458

TEXT_COLOR = "#0A4A51"
GREEN_COLOR = "#1EAD4F"
RED_COLOR = "#C0392B"
ORANGE_COLOR = "#D35400"

REQUIRED_DARK_FRAMES = 3
REQUIRED_BRIGHT_FRAMES = 3

FRINGE_COOLDOWN = 0.08

STAGE_AXIS = "1"


class TranslationStage:

    def __init__(self):

        self.device = None

        self.connected = False

        self.position_mm = 0.0

        self.start_position_mm = 0.0

        self.target_mm = 0.0

        self.is_moving = False

    def connect(self):

        try:

            self.device = GCSDevice()

            self.device.InterfaceSetupDlg()

            self.connected = True

            self.position_mm = self.get_position()

            return True

        except Exception as e:

            print("Stage connection error:", e)

            return False

    def get_position(self):

        if not self.connected:
            return self.position_mm

        try:

            pos = self.device.qPOS(STAGE_AXIS)

            self.position_mm = float(pos[STAGE_AXIS])

            return self.position_mm

        except Exception as e:

            print("Position error:", e)

            return self.position_mm

    def move_relative(self, distance_mm):

        if not self.connected:
            return

        if self.is_moving:
            return

        def worker():

            try:

                self.is_moving = True

                start_pos = self.get_position()

                self.target_mm = start_pos + distance_mm

                self.device.MOV(
                    STAGE_AXIS,
                    self.target_mm
                )

                while self.device.IsMoving()[STAGE_AXIS]:

                    self.position_mm = self.get_position()

                    time.sleep(0.05)

                self.position_mm = self.get_position()

            except Exception as e:

                print("Move error:", e)

            finally:

                self.is_moving = False

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def stop(self):

        try:

            if self.connected:
                self.device.STP()

        except Exception as e:

            print("Stop error:", e)

    def close(self):

        try:

            if self.device is not None:
                self.device.CloseConnection()

        except Exception as e:

            print("Close error:", e)


class InterferometerApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Interferometer Monitor")

        self.geometry("900x1000")

        ctk.set_appearance_mode("light")

        self.configure(fg_color="white")

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="white"
        )

        self.scroll.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.is_monitoring = False

        self.accumulated_fringes = 0

        self.was_dark = False

        self.last_count_time = 0

        self.dark_counter = 0

        self.bright_counter = 0

        self.intensity_history = []

        self.dark_threshold = MANUAL_DARK_THRESHOLD

        self.bright_threshold = MANUAL_BRIGHT_THRESHOLD

        self.calibrating = False

        self.calibration_start_time = 0

        self.calibration_values = []

        self.camera_handler = CameraHandler()

        self.camera_connected = (
            self.camera_handler.connect()
        )

        self.stage = TranslationStage()

        self.stage_connected = (
            self.stage.connect()
        )

        self.stage_start_position = 0.0

        ctk.CTkLabel(
            self.scroll,
            text="Interferometer Monitor",
            font=("Arial", 28, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=20)

        self.btn = ctk.CTkButton(
            self.scroll,
            text="START MONITORING",
            command=self.toggle,
            width=260,
            height=45,
            fg_color=TEXT_COLOR,
            font=("Arial", 16, "bold")
        )

        self.btn.pack(pady=10)

        self.restart_btn = ctk.CTkButton(
            self.scroll,
            text="RESET",
            command=self.restart,
            width=220,
            height=40,
            fg_color=ORANGE_COLOR
        )

        self.restart_btn.pack(pady=5)

        self.status = ctk.CTkLabel(
            self.scroll,
            text="Status: Stopped",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.status.pack(pady=10)

        self.stage_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.stage_frame.pack(
            fill="x",
            padx=20,
            pady=15
        )

        ctk.CTkLabel(
            self.stage_frame,
            text="Electronic Translation Stage",
            font=("Arial", 20, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=10)

        self.stage_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Move distance in mm",
            width=250
        )

        self.stage_entry.pack(pady=5)

        self.stage_btn = ctk.CTkButton(
            self.stage_frame,
            text="MOVE STAGE",
            command=self.move_stage,
            width=220,
            height=40,
            fg_color=TEXT_COLOR
        )

        self.stage_btn.pack(pady=5)

        self.stop_stage_btn = ctk.CTkButton(
            self.stage_frame,
            text="STOP STAGE",
            command=self.stop_stage,
            width=220,
            height=40,
            fg_color=RED_COLOR
        )

        self.stop_stage_btn.pack(pady=5)

        self.label_stage_position = ctk.CTkLabel(
            self.stage_frame,
            text="Stage Position: 0.000000 mm",
            font=("Arial", 15),
            text_color=TEXT_COLOR
        )

        self.label_stage_position.pack(pady=5)

        self.label_stage_moved = ctk.CTkLabel(
            self.stage_frame,
            text="Moved Already: 0.000000 mm",
            font=("Arial", 16, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_stage_moved.pack(pady=5)

        self.frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.frame.pack(
            fill="x",
            padx=20,
            pady=15
        )

        self.label_mm = ctk.CTkLabel(
            self.frame,
            text="Distance: 0.000000 mm",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_mm.pack(pady=5)

        self.label_um = ctk.CTkLabel(
            self.frame,
            text="Distance: 0.000 µm",
            font=("Arial", 18, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_um.pack(pady=5)

        self.label_ps = ctk.CTkLabel(
            self.frame,
            text="Time Delay: 0.0000 ps",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_ps.pack(pady=5)

        self.label_intensity = ctk.CTkLabel(
            self.frame,
            text="Intensity: 0.00",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_intensity.pack(pady=5)

        self.label_thresholds = ctk.CTkLabel(
            self.frame,
            text="Thresholds: waiting",
            font=("Arial", 15),
            text_color=TEXT_COLOR
        )

        self.label_thresholds.pack(pady=5)

        self.label_accumulated_fringes = ctk.CTkLabel(
            self.frame,
            text="Accumulated Fringes Count: 0",
            font=("Arial", 18, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_accumulated_fringes.pack(pady=10)

        self.live_size = (420, 320)

        ctk.CTkLabel(
            self.scroll,
            text="Live Camera",
            font=("Arial", 20, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(20, 10))

        self.image_label = ctk.CTkLabel(
            self.scroll,
            text="No Image",
            width=self.live_size[0],
            height=self.live_size[1],
            fg_color="#111111",
            text_color="white"
        )

        self.image_label.pack(pady=20)

        self.update_stage_position_once()

    def toggle(self):

        if not self.is_monitoring:

            if not self.camera_connected:

                self.status.configure(
                    text="Camera not connected",
                    text_color=RED_COLOR
                )

                return

            self.restart_values_only()

            self.is_monitoring = True

            if MANUAL_THRESHOLDS:

                self.dark_threshold = (
                    MANUAL_DARK_THRESHOLD
                )

                self.bright_threshold = (
                    MANUAL_BRIGHT_THRESHOLD
                )

                self.label_thresholds.configure(
                    text=(
                        f"Manual Dark: "
                        f"{self.dark_threshold:.2f} | "
                        f"Manual Bright: "
                        f"{self.bright_threshold:.2f}"
                    )
                )

                self.status.configure(
                    text="Monitoring running",
                    text_color=GREEN_COLOR
                )

            else:

                self.calibrating = True

                self.calibration_values = []

                self.calibration_start_time = time.time()

                self.status.configure(
                    text="Calibrating thresholds...",
                    text_color=ORANGE_COLOR
                )

            self.btn.configure(
                text="STOP MONITORING",
                fg_color=RED_COLOR
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
                text="Stopped",
                text_color=TEXT_COLOR
            )

    def restart(self):

        self.restart_values_only()

    def restart_values_only(self):

        self.accumulated_fringes = 0

        self.was_dark = False

        self.last_count_time = 0

        self.dark_counter = 0

        self.bright_counter = 0

        self.intensity_history = []

        self.calibrating = False

        self.calibration_values = []

    def move_stage(self):

        if not self.stage_connected:
            return

        try:

            move_mm = float(
                self.stage_entry.get().replace(",", ".")
            )

        except:
            return

        self.stage_start_position = (
            self.stage.get_position()
        )

        self.stage.move_relative(move_mm)

        threading.Thread(
            target=self.stage_ui_loop,
            daemon=True
        ).start()

    def stop_stage(self):

        self.stage.stop()

    def stage_ui_loop(self):

        while self.stage.is_moving:

            pos = self.stage.get_position()

            moved = pos - self.stage_start_position

            self.after(
                0,
                lambda p=pos, m=moved:
                self.update_stage_labels(p, m)
            )

            time.sleep(0.05)

    def update_stage_position_once(self):

        if self.stage_connected:

            pos = self.stage.get_position()

            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )

    def update_stage_labels(self, pos, moved):

        self.label_stage_position.configure(
            text=f"Stage Position: {pos:.6f} mm"
        )

        self.label_stage_moved.configure(
            text=f"Moved Already: {moved:.6f} mm"
        )

    def loop(self):

        frame_counter = 0

        while self.is_monitoring:

            img = self.camera_handler.get_frame()

            if img is None:
                continue

            frame_counter += 1

            if frame_counter % 20 == 0:

                self.after(
                    0,
                    lambda f=img:
                    self.update_image(f)
                )

            intensity = (
                self.camera_handler
                .get_fringe_intensity_from_frame(img)
            )

            if intensity is not None:

                fringe_counted = False

                if self.calibrating:

                    self.calibration_values.append(
                        intensity
                    )

                    elapsed = (
                        time.time()
                        - self.calibration_start_time
                    )

                    self.after(
                        0,
                        lambda e=elapsed:
                        self.label_thresholds.configure(
                            text=f"Calibrating {e:.1f}/10s"
                        )
                    )

                    if elapsed >= 10:

                        min_val = min(
                            self.calibration_values
                        )

                        max_val = max(
                            self.calibration_values
                        )

                        value_range = (
                            max_val - min_val
                        )

                        self.dark_threshold = (
                            min_val
                            + value_range * 0.125
                        )

                        self.bright_threshold = (
                            max_val
                            - value_range * 0.125
                        )

                        self.calibrating = False

                        self.after(
                            0,
                            lambda:
                            self.label_thresholds.configure(
                                text=(
                                    f"Dark: "
                                    f"{self.dark_threshold:.2f} | "
                                    f"Bright: "
                                    f"{self.bright_threshold:.2f}"
                                )
                            )
                        )

                        self.after(
                            0,
                            lambda:
                            self.status.configure(
                                text="Monitoring running",
                                text_color=GREEN_COLOR
                            )
                        )

                else:

                    fringe_counted = (
                        self.update_accumulated_fringes(
                            intensity
                        )
                    )

                self.after(
                    0,
                    lambda v=intensity, c=fringe_counted:
                    self.update_intensity_label(v, c)
                )

            dist_mm = (
                self.accumulated_fringes
                * FRINGE_DISTANCE_MM
            )

            dist_um = dist_mm * 1000

            time_ps = (
                2 * dist_mm
            ) / SPEED_OF_LIGHT_MM_PS

            self.after(
                0,
                lambda:
                self.update_values(
                    dist_mm,
                    dist_um,
                    time_ps
                )
            )

            self.after(
                0,
                lambda:
                self.label_accumulated_fringes.configure(
                    text=(
                        f"Accumulated Fringes Count: "
                        f"{self.accumulated_fringes}"
                    )
                )
            )

    def update_accumulated_fringes(
        self,
        intensity
    ):

        self.intensity_history.append(
            intensity
        )

        if len(self.intensity_history) > 5:
            self.intensity_history.pop(0)

        smooth_intensity = np.mean(
            self.intensity_history
        )

        if smooth_intensity < self.dark_threshold:

            self.dark_counter += 1

        else:

            self.dark_counter = 0

        if self.dark_counter >= REQUIRED_DARK_FRAMES:

            self.was_dark = True

        if smooth_intensity > self.bright_threshold:

            self.bright_counter += 1

        else:

            self.bright_counter = 0

        cooldown_ok = (
            time.time() - self.last_count_time
        ) > FRINGE_COOLDOWN

        if (
            self.was_dark
            and self.bright_counter
            >= REQUIRED_BRIGHT_FRAMES
            and cooldown_ok
        ):

            self.accumulated_fringes += 1

            self.was_dark = False

            self.last_count_time = time.time()

            self.dark_counter = 0

            self.bright_counter = 0

            return True

        return False

    def update_intensity_label(
        self,
        intensity,
        fringe_counted
    ):

        self.label_intensity.configure(
            text=f"Intensity: {intensity:.2f}"
        )

        if fringe_counted:

            self.label_intensity.configure(
                text_color=GREEN_COLOR
            )

            self.after(
                250,
                lambda:
                self.label_intensity.configure(
                    text_color=TEXT_COLOR
                )
            )

    def update_values(
        self,
        mm,
        um,
        ps
    ):

        self.label_mm.configure(
            text=f"Distance: {mm:.6f} mm"
        )

        self.label_um.configure(
            text=f"Distance: {um:.3f} µm"
        )

        self.label_ps.configure(
            text=f"Time Delay: {ps:.4f} ps"
        )

    def update_image(self, img):

        display = img.astype(np.float32)

        display -= np.min(display)

        if np.max(display) > 0:
            display /= np.max(display)

        display = (
            display * 255
        ).astype(np.uint8)

        pil = Image.fromarray(display).convert(
            "RGB"
        )

        original_w, original_h = pil.size

        scale_x = (
            self.live_size[0] / original_w
        )

        scale_y = (
            self.live_size[1] / original_h
        )

        pil = pil.resize(self.live_size)

        draw = ImageDraw.Draw(pil)

        x1 = int(
            self.camera_handler.roi_x * scale_x
        )

        y1 = int(
            self.camera_handler.roi_y * scale_y
        )

        x2 = int(
            (
                self.camera_handler.roi_x
                + self.camera_handler.roi_w
            ) * scale_x
        )

        y2 = int(
            (
                self.camera_handler.roi_y
                + self.camera_handler.roi_h
            ) * scale_y
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

    def on_close(self):

        self.is_monitoring = False

        try:
            self.camera_handler.close()

        except:
            pass

        try:
            self.stage.close()

        except:
            pass

        self.destroy()


if __name__ == "__main__":

    app = InterferometerApp()

    app.protocol(
        "WM_DELETE_WINDOW",
        app.on_close
    )

    app.mainloop()