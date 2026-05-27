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
LOCK_CORRECTION_COOLDOWN = 0.20


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
            padx=2,
            pady=2
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

        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
        self.fringe_distance_mm = self.compute_fringe_distance(
            self.laser_wavelength_nm
        )
        self.stage_start_position = 0.0
        self.stage_reference_position = 0.0
        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        self.reset_stage_movement_after_move = False
        self.center_stage_after_calibration_pending = False
        self.returning_stage_after_calibration = False
        self.calibration_motion_started = False
        self.lock_active = False
        self.lock_position_mm = 0.0
        self.lock_reference_fringes = 0
        self.lock_correction_active = False
        self.lock_last_correction_time = 0

        ctk.CTkLabel(
            self.scroll,
            text="Interferometer Monitor",
            font=("Arial", 23, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=5)

        self.btn = ctk.CTkButton(
            self.scroll,
            text="START MONITORING",
            command=self.toggle,
            width=180,
            height=30,
            fg_color=TEXT_COLOR,
            font=("Arial", 11, "bold")
        )

        self.btn.pack(pady=2)

        self.restart_btn = ctk.CTkButton(
            self.scroll,
            text="RESET",
            command=self.restart,
            width=140,
            height=28,
            fg_color=ORANGE_COLOR
        )

        self.restart_btn.pack(pady=1)

        self.status = ctk.CTkLabel(
            self.scroll,
            text="Status: Stopped",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.status.pack(pady=2)

        self.stage_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.stage_frame.pack(
            fill="x",
            padx=5,
            pady=4
        )

        ctk.CTkLabel(
            self.stage_frame,
            text="Electronic Translation Stage",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=2)

        self.wavelength_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Laser wavelength in nm",
            width=250
        )

        self.wavelength_entry.pack(pady=1)
        self.wavelength_entry.insert(0, f"{self.laser_wavelength_nm:.1f}")

        self.wavelength_button = ctk.CTkButton(
            self.stage_frame,
            text="Set wavelength",
            width=120,
            command=self.apply_wavelength,
            fg_color=TEXT_COLOR
        )

        self.wavelength_button.pack(pady=1)

        self.step_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Step size in mm",
            width=250
        )

        self.step_entry.pack(pady=1)
        self.step_entry.insert(
            0,
            f"{(self.fringe_distance_mm / 8):.7f}"
        )

        self.button_frame = ctk.CTkFrame(
            self.stage_frame,
            fg_color="transparent"
        )

        self.button_frame.pack(pady=1)

        ctk.CTkLabel(
            self.stage_frame,
            text="or",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=3)

        self.target_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Target value or distance in mm",
            width=250
        )

        self.target_entry.pack(pady=1)
        self.target_entry.insert(0, "0.0000")

        self.target_button_frame = ctk.CTkFrame(
            self.stage_frame,
            fg_color="transparent"
        )

        self.target_button_frame.pack(pady=1)

        self.btn_target_abs = ctk.CTkButton(
            self.target_button_frame,
            text="Go to target",
            width=140,
            command=self.move_to_target_by_steps,
            fg_color=TEXT_COLOR
        )

        self.btn_target_abs.grid(
            row=0,
            column=0,
            padx=1
        )

        self.btn_target_rel = ctk.CTkButton(
            self.target_button_frame,
            text="Move distance",
            width=140,
            command=self.move_distance_by_steps,
            fg_color=TEXT_COLOR
        )

        self.btn_target_rel.grid(
            row=0,
            column=1,
            padx=1
        )

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
            padx=1
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
            padx=1
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
            padx=1
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
            padx=1
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
            padx=1
        )

        self.btn_lock = ctk.CTkButton(
            self.stage_frame,
            text="LOCK",
            width=120,
            command=self.toggle_lock,
            fg_color=TEXT_COLOR
        )

        self.btn_lock.pack(pady=(3, 1))

        self.label_lock_status = ctk.CTkLabel(
            self.stage_frame,
            text="Lock: off",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )

        self.label_lock_status.pack(pady=0)


        self.label_stage_position = ctk.CTkLabel(
            self.stage_frame,
            text="Stage Position: 0.000000 mm",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )

        self.label_stage_position.pack(pady=0)

        self.label_stage_moved = ctk.CTkLabel(
            self.stage_frame,
            text="Accumulated Movement: 0.000000 mm",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_stage_moved.pack(pady=0)

        self.frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.frame.pack(
            fill="x",
            padx=5,
            pady=4
        )

        self.label_um = ctk.CTkLabel(
            self.frame,
            text="Distance: 0.000 µm",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_um.pack(pady=0)

        self.label_ps = ctk.CTkLabel(
            self.frame,
            text="Time Delay: 0.0000 ps",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.label_ps.pack(pady=0)

        self.label_intensity = ctk.CTkLabel(
            self.frame,
            text="Intensity: 0.00",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_intensity.pack(pady=0)

        self.label_thresholds = ctk.CTkLabel(
            self.frame,
            text="Thresholds: waiting",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )

        self.label_thresholds.pack(pady=0)

        self.label_accumulated_fringes = ctk.CTkLabel(
            self.frame,
            text="Accumulated Fringes Count: 0",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_accumulated_fringes.pack(pady=0)

        self.compare_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.compare_frame.pack(
            fill="x",
            padx=5,
            pady=4
        )

        ctk.CTkLabel(
            self.compare_frame,
            text="Distance Comparison",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=0)

        self.label_compare_driven = ctk.CTkLabel(
            self.compare_frame,
            text="Driven: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.label_compare_driven.pack(pady=0)

        self.label_compare_calculated = ctk.CTkLabel(
            self.compare_frame,
            text="Calculated: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.label_compare_calculated.pack(pady=0)

        self.label_compare_difference = ctk.CTkLabel(
            self.compare_frame,
            text="Difference: 0.000000 mm",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_compare_difference.pack(pady=0)

        self.live_size = (320, 220)

        ctk.CTkLabel(
            self.scroll,
            text="Live Camera",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 2))

        self.image_label = ctk.CTkLabel(
            self.scroll,
            text="No Image",
            width=self.live_size[0],
            height=self.live_size[1],
            fg_color="#111111",
            text_color="white"
        )

        self.image_label.pack(pady=5)

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

            self.disable_lock(update_status=False)

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

            if self.stage_connected:
                self.stage.stop()

            self.disable_lock(update_status=False)

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
        self.calibration_motion_started = False

        self.calibration_values = []

        self.reset_stage_movement_tracking()

        self.reset_measurement_after_calibration()

        if hasattr(self, "label_compare_driven"):

            self.update_comparison_labels(0.0)

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

        if self.lock_active and not reset_after_move:

            self.status.configure(
                text="Unlock before moving stage",
                text_color=ORANGE_COLOR
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

    def start_stage_move_to_stepped(self, target_mm):

        if not self.stage_connected:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return

        if self.lock_active:
            self.status.configure(
                text="Unlock before moving stage",
                text_color=ORANGE_COLOR
            )
            return

        if self.stage.is_moving:
            self.status.configure(
                text="Stage is already moving",
                text_color=ORANGE_COLOR
            )
            return

        start_pos = self.stage.get_position()
        target_mm = self.stage.clamp_position(target_mm)

        if abs(target_mm - start_pos) < 1e-12:
            self.status.configure(
                text="Stage already at target",
                text_color=TEXT_COLOR
            )
            return

        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement

        threading.Thread(
            target=self.stage_stepped_move_worker,
            args=(start_pos, target_mm),
            daemon=True
        ).start()

    def start_stage_move_by_steps(self, move_mm):

        start_pos = self.stage.get_position()
        self.start_stage_move_to_stepped(
            start_pos + move_mm
        )

    def stage_stepped_move_worker(self, start_pos, target_mm):

        step_mm = self.get_step_size()
        delay_s = 0.25
        direction = 1 if target_mm > start_pos else -1
        current_pos = start_pos
        remaining = abs(target_mm - start_pos)
        moved = 0.0

        self.status.configure(
            text=(
                f"Moving to {target_mm:.6f} mm in {step_mm:.6f} mm steps"
            ),
            text_color=TEXT_COLOR
        )

        while remaining > 1e-12:
            next_step = min(step_mm, remaining)
            next_target = current_pos + direction * next_step

            if not self.stage.move_absolute(next_target):
                self.status.configure(
                    text="Stage move failed",
                    text_color=RED_COLOR
                )
                return

            while self.stage.is_moving:
                time.sleep(0.01)

            step_distance = abs(next_target - current_pos)
            moved += step_distance
            current_pos = next_target
            remaining = abs(target_mm - current_pos)

            self.total_stage_movement = (
                self.stage_movement_before_move + moved
            )

            self.after(
                0,
                lambda p=current_pos, m=moved, b=self.stage_movement_before_move:
                self.update_stage_labels(p, m, b)
            )

            if remaining > 1e-12:
                time.sleep(delay_s)

        self.after(
            0,
            lambda:
            self.status.configure(
                text=f"Reached {current_pos:.6f} mm",
                text_color=GREEN_COLOR
            )
        )

    def get_step_size(self):

        try:
            value = float(
                self.step_entry.get().replace(",", ".")
            )
            return abs(value)
        except ValueError:
            return 0.0001

    def compute_fringe_distance(self, wavelength_nm):

        return (wavelength_nm / 2) / 1_000_000 / 2

    def apply_wavelength(self):

        try:
            wavelength_nm = float(
                self.wavelength_entry.get().replace(",", ".")
            )
        except ValueError:
            self.status.configure(
                text="Invalid wavelength value",
                text_color=RED_COLOR
            )
            return

        self.laser_wavelength_nm = wavelength_nm
        self.fringe_distance_mm = self.compute_fringe_distance(
            self.laser_wavelength_nm
        )

        default_step = self.fringe_distance_mm / 4
        self.step_entry.delete(0, "end")
        self.step_entry.insert(
            0,
            f"{default_step:.7f}"
        )

        self.status.configure(
            text=f"Wavelength set to {self.laser_wavelength_nm:.1f} nm",
            text_color=GREEN_COLOR
        )

    def move_to_min(self):

        self.start_stage_move_to(
            self.stage.min_position
        )

    def step_negative(self):

        self.start_stage_move_by(
            -self.get_step_size()
        )

    def move_to_center(self):

        self.start_stage_move_to(
            0.0
        )

    def step_positive(self):

        self.start_stage_move_by(
            self.get_step_size()
        )

    def move_to_max(self):

        self.start_stage_move_to(
            self.stage.max_position
        )

    def move_to_target_by_steps(self):

        try:
            target_mm = float(
                self.target_entry.get().replace(",", ".")
            )
        except ValueError:
            self.status.configure(
                text="Invalid target value",
                text_color=RED_COLOR
            )
            return

        self.start_stage_move_to_stepped(target_mm)

    def move_distance_by_steps(self):

        try:
            distance_mm = float(
                self.target_entry.get().replace(",", ".")
            )
        except ValueError:
            self.status.configure(
                text="Invalid distance value",
                text_color=RED_COLOR
            )
            return

        self.start_stage_move_by_steps(distance_mm)

    def stop_stage(self):

        self.stage.stop()

    def toggle_lock(self):

        if self.lock_active:

            self.disable_lock()

            return

        if not self.is_monitoring:

            self.status.configure(
                text="Start monitoring before locking",
                text_color=ORANGE_COLOR
            )

            return

        if not self.stage_connected:

            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )

            return

        if self.calibrating or self.returning_stage_after_calibration:

            self.status.configure(
                text="Wait until calibration is done",
                text_color=ORANGE_COLOR
            )

            return

        if self.stage.is_moving:

            self.status.configure(
                text="Stage is already moving",
                text_color=ORANGE_COLOR
            )

            return

        self.lock_position_mm = self.stage.get_position()
        self.lock_reference_fringes = self.accumulated_fringes
        self.lock_last_correction_time = 0
        self.lock_correction_active = False
        self.lock_active = True
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.intensity_history = []
        self.last_count_time = time.time()

        self.btn_lock.configure(
            text="UNLOCK",
            fg_color=GREEN_COLOR
        )

        self.label_lock_status.configure(
            text=f"Lock: {self.lock_position_mm:.6f} mm",
            text_color=GREEN_COLOR
        )

        self.status.configure(
            text=f"Lock active at {self.lock_position_mm:.6f} mm",
            text_color=GREEN_COLOR
        )

    def disable_lock(self, update_status=True):

        was_correcting = self.lock_correction_active

        self.lock_active = False
        self.lock_correction_active = False

        if was_correcting and self.stage_connected:

            self.stage.stop()

        if hasattr(self, "btn_lock"):

            self.btn_lock.configure(
                text="LOCK",
                fg_color=TEXT_COLOR
            )

        if hasattr(self, "label_lock_status"):

            self.label_lock_status.configure(
                text="Lock: off",
                text_color=TEXT_COLOR
            )

        if update_status:

            self.status.configure(
                text="Lock off",
                text_color=TEXT_COLOR
            )

    def lock_deadband_mm(self):

        return max(
            self.fringe_distance_mm / 8,
            1e-7
        )

    def handle_lock_after_fringe(self):

        if not self.lock_active:
            return

        if (
            not self.stage_connected
            or self.calibrating
            or self.returning_stage_after_calibration
            or self.lock_correction_active
            or self.stage.is_moving
        ):
            return

        now = time.time()

        if (
            now - self.lock_last_correction_time
        ) < LOCK_CORRECTION_COOLDOWN:
            return

        current_pos = self.stage.get_position()
        drift_mm = current_pos - self.lock_position_mm

        if abs(drift_mm) < self.lock_deadband_mm():

            self.after(
                0,
                lambda d=drift_mm:
                self.label_lock_status.configure(
                    text=f"Lock: no qPOS drift ({d:+.6f} mm)",
                    text_color=GREEN_COLOR
                )
            )

            return

        self.lock_last_correction_time = now
        self.lock_correction_active = True

        if not self.stage.move_absolute(self.lock_position_mm):

            self.lock_correction_active = False

            self.after(
                0,
                lambda:
                self.status.configure(
                    text="Lock correction failed",
                    text_color=RED_COLOR
                )
            )

            return

        self.after(
            0,
            lambda d=drift_mm:
            self.label_lock_status.configure(
                text=f"Lock correcting ({d:+.6f} mm)",
                text_color=ORANGE_COLOR
            )
        )

        self.after(
            0,
            lambda d=drift_mm:
            self.status.configure(
                text=f"Lock correcting drift {d:+.6f} mm",
                text_color=ORANGE_COLOR
            )
        )

        threading.Thread(
            target=self.lock_correction_ui_loop,
            daemon=True
        ).start()

    def lock_correction_ui_loop(self):

        while self.stage.is_moving:

            pos = self.stage.get_position()

            self.after(
                0,
                lambda p=pos:
                self.label_stage_position.configure(
                    text=f"Stage Position: {p:.6f} mm"
                )
            )

            time.sleep(0.05)

        pos = self.stage.get_position()
        remaining_mm = pos - self.lock_position_mm
        self.lock_correction_active = False

        self.after(
            0,
            lambda p=pos, r=remaining_mm:
            self.finish_lock_correction(p, r)
        )

    def finish_lock_correction(self, pos, remaining_mm):

        self.label_stage_position.configure(
            text=f"Stage Position: {pos:.6f} mm"
        )

        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.intensity_history = []
        self.last_count_time = time.time()

        if not self.lock_active:
            return

        if abs(remaining_mm) <= self.lock_deadband_mm():

            self.label_lock_status.configure(
                text=f"Lock: {self.lock_position_mm:.6f} mm",
                text_color=GREEN_COLOR
            )

            self.status.configure(
                text="Lock correction done",
                text_color=GREEN_COLOR
            )

        else:

            self.label_lock_status.configure(
                text=f"Lock residual: {remaining_mm:+.6f} mm",
                text_color=ORANGE_COLOR
            )

            self.status.configure(
                text="Lock correction has residual drift",
                text_color=ORANGE_COLOR
            )

    def stage_ui_loop(self):

        movement_base = self.stage_movement_before_move

        while self.stage.is_moving:

            pos = self.stage.get_position()

            moved = abs(pos - self.stage_start_position)

            self.after(
                0,
                lambda p=pos, m=moved, b=movement_base:
                self.update_stage_labels(p, m, b)
            )

            time.sleep(0.05)

        pos = self.stage.get_position()

        moved = abs(pos - self.stage_start_position)
        self.total_stage_movement = (
            movement_base + moved
        )

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

        current_total_stage_movement = (
            movement_base + abs(moved)
        )
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
            self.stage_reference_position = pos
            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )
        elif self.stage_connected:
            self.stage_reference_position = self.stage.get_position()
        else:
            self.stage_reference_position = 0.0

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

    def calibration_stage_motion(self):

        if not self.stage_connected:
            return

        start_pos = self.stage.get_position()
        step_mm = 0.0001
        steps = 4

        # move forward in 4 steps
        for i in range(1, steps + 1):
            if not self.is_monitoring:
                return

            target = start_pos + step_mm * i
            target = self.stage.clamp_position(target)

            if not self.stage.move_absolute(target):
                return

            while self.stage.is_moving and self.is_monitoring:
                time.sleep(0.01)

            time.sleep(0.25)

        # move back in 4 steps
        for i in range(steps - 1, -1, -1):
            if not self.is_monitoring:
                return

            target = start_pos + step_mm * i
            target = self.stage.clamp_position(target)

            if not self.stage.move_absolute(target):
                return

            while self.stage.is_moving and self.is_monitoring:
                time.sleep(0.01)

            time.sleep(0.25)

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
            * self.fringe_distance_mm
        )

        difference_mm = (
            driven_distance_mm
            - calculated_mm
        )

        self.label_compare_driven.configure(
            text=(
                f"Driven: {driven_distance_mm:.6f} mm"
            )
        )

        self.label_compare_calculated.configure(
            text=(
                f"Calculated: {calculated_mm:.6f} mm"
            )
        )

        self.label_compare_difference.configure(
            text=(
                f"Difference: {difference_mm:.6f} mm"
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

                    if (not self.calibration_motion_started
                            and self.stage_connected):
                        self.calibration_motion_started = True
                        threading.Thread(
                            target=self.calibration_stage_motion,
                            daemon=True
                        ).start()

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
                            text=f"Calibrating {e:.1f}/5s"
                        )
                    )

                    if elapsed >= 5:

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
                            - value_range * 0.30
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

                    if (
                        not self.returning_stage_after_calibration
                        and not self.lock_correction_active
                    ):

                        fringe_counted = (
                            self.update_accumulated_fringes(
                                intensity
                            )
                        )

                        if fringe_counted:

                            self.handle_lock_after_fringe()

                self.after(
                    0,
                    lambda v=intensity, c=fringe_counted:
                    self.update_intensity_label(v, c)
                )

            dist_mm = (
                self.accumulated_fringes
                * self.fringe_distance_mm
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
