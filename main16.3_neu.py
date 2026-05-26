MANUAL_THRESHOLDS = False

MANUAL_DARK_THRESHOLD = 7
MANUAL_BRIGHT_THRESHOLD = 25


import os
import threading
import time
import numpy as np
import customtkinter as ctk

from PIL import Image, ImageDraw

from camera_handler import CameraHandler
from stage_controller import StageController


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

        self.stage = StageController()

        self.stage_connected = (
            self.stage.connect()
        )

        self.stage_start_position = 0.0
        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        self.reset_stage_movement_after_move = False
        self.center_stage_after_calibration_pending = False
        self.returning_stage_after_calibration = False

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

        self.button_frame = ctk.CTkFrame(
            self.stage_frame,
            fg_color="transparent"
        )

        self.button_frame.pack(pady=5)

        self.btn_min = ctk.CTkButton(
            self.button_frame,
            text="|<",
            width=60,
            command=self.move_to_min,
            fg_color=TEXT_COLOR
        )

        self.btn_min.grid(
            row=0,
            column=0,
            padx=5
        )

        self.btn_left = ctk.CTkButton(
            self.button_frame,
            text="<",
            width=60,
            command=self.step_negative,
            fg_color=TEXT_COLOR
        )

        self.btn_left.grid(
            row=0,
            column=1,
            padx=5
        )

        self.btn_center = ctk.CTkButton(
            self.button_frame,
            text="0",
            width=60,
            command=self.move_to_center,
            fg_color=TEXT_COLOR
        )

        self.btn_center.grid(
            row=0,
            column=2,
            padx=5
        )

        self.btn_right = ctk.CTkButton(
            self.button_frame,
            text=">",
            width=60,
            command=self.step_positive,
            fg_color=TEXT_COLOR
        )

        self.btn_right.grid(
            row=0,
            column=3,
            padx=5
        )

        self.btn_max = ctk.CTkButton(
            self.button_frame,
            text=">|",
            width=60,
            command=self.move_to_max,
            fg_color=TEXT_COLOR
        )

        self.btn_max.grid(
            row=0,
            column=4,
            padx=5
        )


        self.label_stage_position = ctk.CTkLabel(
            self.stage_frame,
            text="Stage Position: 0.000000 mm",
            font=("Arial", 15),
            text_color=TEXT_COLOR
        )

        self.label_stage_position.pack(pady=5)

        self.label_stage_moved = ctk.CTkLabel(
            self.stage_frame,
            text="Accumulated Movement: 0.000000 mm",
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

        self.compare_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.compare_frame.pack(
            fill="x",
            padx=20,
            pady=15
        )

        ctk.CTkLabel(
            self.compare_frame,
            text="Vergleich Strecke",
            font=("Arial", 20, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=10)

        self.label_compare_driven = ctk.CTkLabel(
            self.compare_frame,
            text="Gefahren: 0.000000 mm",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_compare_driven.pack(pady=4)

        self.label_compare_calculated = ctk.CTkLabel(
            self.compare_frame,
            text="Berechnet: 0.000000 mm",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_compare_calculated.pack(pady=4)

        self.label_compare_difference = ctk.CTkLabel(
            self.compare_frame,
            text="Differenz: 0.000000 mm",
            font=("Arial", 18, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_compare_difference.pack(pady=8)

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

        self.update_comparison_labels()

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

        if hasattr(self, "label_compare_driven"):

            self.update_comparison_labels()

    def start_stage_move_to(
        self,
        target_mm,
        start_pos=None,
        reset_after_move=False
    ):

        if not self.stage_connected:

            if reset_after_move:

                self.reset_stage_after_calibration()

                return

            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )

            return

        if self.stage.is_moving:

            if reset_after_move:

                self.center_stage_after_calibration_pending = True

                self.status.configure(
                    text=(
                        "Calibration done - stage returns to "
                        "0.00000000000 mm after current move"
                    ),
                    text_color=ORANGE_COLOR
                )

            else:

                self.status.configure(
                    text="Stage is already moving",
                    text_color=ORANGE_COLOR
                )

            return

        if start_pos is None:

            start_pos = self.stage.get_position()

        target_mm = self.stage.clamp_position(target_mm)

        move_mm = target_mm - start_pos

        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.reset_stage_movement_after_move = reset_after_move

        if abs(move_mm) < 1e-12:

            if reset_after_move:

                self.reset_stage_after_calibration(start_pos)

                return

            else:

                self.update_stage_labels(start_pos, 0.0)

            self.status.configure(
                text="Stage already at target",
                text_color=TEXT_COLOR
            )

            return

        if not self.stage.move_absolute(target_mm):

            self.reset_stage_movement_after_move = False

            if reset_after_move:

                self.reset_stage_after_calibration(start_pos)

            return

        self.status.configure(
            text=f"Stage moving to {target_mm:.6f} mm",
            text_color=TEXT_COLOR
        )

        threading.Thread(
            target=self.stage_ui_loop,
            daemon=True
        ).start()

    def start_stage_move_by(self, move_mm):

        start_pos = self.stage.get_position()

        self.start_stage_move_to(
            start_pos + move_mm,
            start_pos=start_pos
        )

    def move_to_min(self):

        self.start_stage_move_to(
            self.stage.min_position
        )

    def step_negative(self):

        self.start_stage_move_by(
            -self.stage.step_size
        )

    def move_to_center(self):

        self.start_stage_move_to(
            0.0
        )

    def step_positive(self):

        self.start_stage_move_by(
            self.stage.step_size
        )

    def move_to_max(self):

        self.start_stage_move_to(
            self.stage.max_position
        )

    def move_stage(self):

        try:
            move_mm = float(
                self.stage_entry.get().replace(",", ".")
            )
        except ValueError:
            return

        self.start_stage_move_by(move_mm)

    def stop_stage(self):

        self.stage.stop()

    def stage_ui_loop(self):

        movement_base = self.stage_movement_before_move

        while self.stage.is_moving:

            pos = self.stage.get_position()

            moved = pos - self.stage_start_position

            self.after(
                0,
                lambda p=pos, m=moved, b=movement_base:
                self.update_stage_labels(p, m, b)
            )

            time.sleep(0.05)

        pos = self.stage.get_position()

        moved = pos - self.stage_start_position
        self.total_stage_movement = movement_base + moved

        if self.reset_stage_movement_after_move:

            self.reset_stage_movement_after_move = False

            self.after(
                0,
                lambda p=pos:
                self.reset_stage_after_calibration(p)
            )

        else:

            self.after(
                0,
                lambda p=pos, m=moved, b=movement_base:
                self.update_stage_labels(p, m, b)
            )

        if self.center_stage_after_calibration_pending:

            self.center_stage_after_calibration_pending = False

            self.after(
                0,
                self.move_to_center_after_calibration
            )

    def update_stage_position_once(self):

        if self.stage_connected:

            pos = self.stage.get_position()

            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )

    def update_stage_labels(self, pos, moved, movement_base=None):

        if movement_base is None:

            movement_base = self.total_stage_movement

        current_total_stage_movement = movement_base + moved
        self.current_stage_movement_for_compare = (
            current_total_stage_movement
        )

        self.label_stage_position.configure(
            text=f"Stage Position: {pos:.6f} mm"
        )

        self.label_stage_moved.configure(
            text=(
                f"Accumulated Movement: "
                f"{current_total_stage_movement:.6f} mm"
            )
        )

        self.update_comparison_labels(
            current_total_stage_movement
        )

    def reset_stage_movement_tracking(self, pos=None):

        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0

        if pos is not None:

            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )

        self.label_stage_moved.configure(
            text="Accumulated Movement: 0.000000 mm"
        )

        self.update_comparison_labels(0.0)

    def reset_measurement_after_calibration(self):

        self.accumulated_fringes = 0
        self.was_dark = False
        self.last_count_time = 0
        self.dark_counter = 0
        self.bright_counter = 0
        self.intensity_history = []

        self.label_mm.configure(
            text="Distance: 0.000000 mm"
        )

        self.label_um.configure(
            text="Distance: 0.000 µm"
        )

        self.label_ps.configure(
            text="Time Delay: 0.0000 ps"
        )

        self.label_accumulated_fringes.configure(
            text="Accumulated Fringes Count: 0"
        )

        self.update_comparison_labels(0.0)

    def finish_calibration_stage_reset(self):

        self.returning_stage_after_calibration = True

        self.status.configure(
            text="Calibration done - stage returning to 0.00000000000 mm",
            text_color=ORANGE_COLOR
        )

        self.start_stage_move_to(
            0.0,
            reset_after_move=True
        )

    def move_to_center_after_calibration(self):

        self.returning_stage_after_calibration = True

        self.start_stage_move_to(
            0.0,
            reset_after_move=True
        )

    def reset_stage_after_calibration(self, pos=None):

        self.reset_stage_movement_tracking(pos)

        self.reset_measurement_after_calibration()

        self.returning_stage_after_calibration = False

        self.status.configure(
            text="Monitoring running",
            text_color=GREEN_COLOR
        )

    def update_comparison_labels(self, driven_mm=None):

        if driven_mm is None:

            driven_mm = self.current_stage_movement_for_compare

        driven_distance_mm = abs(driven_mm)

        calculated_fringes = self.accumulated_fringes

        calculated_mm = (
            calculated_fringes
            * FRINGE_DISTANCE_MM
        )

        difference_mm = (
            driven_distance_mm
            - calculated_mm
        )

        self.label_compare_driven.configure(
            text=(
                f"Gefahren: {driven_distance_mm:.6f} mm"
            )
        )

        self.label_compare_calculated.configure(
            text=(
                f"Berechnet: {calculated_mm:.6f} mm"
            )
        )

        self.label_compare_difference.configure(
            text=(
                f"Differenz: {difference_mm:.6f} mm"
            )
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
                            - value_range * 0.15
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

                        self.after(
                            0,
                            self.finish_calibration_stage_reset
                        )

                else:

                    if not self.returning_stage_after_calibration:

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

        self.update_comparison_labels()

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
