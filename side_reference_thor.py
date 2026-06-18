#doesnt work, noise is equal height as interference peaks, so detection fails
import threading
import time

import customtkinter as ctk

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    Figure = None
    FigureCanvasTkAgg = None

from diode_handler import (
    LASER_WAVELENGTH_NM,
    PHOTODIODE_CHANNEL,
    PHOTODIODE_REF_CHANNEL,
    SAMPLE_INTERVAL_S,
    SingleDiodeHandler,
    ReferenceDiodeHandler,
    USE_REFERENCE_DIODE,
    compute_fringe_distance_mm
)
from stage_controller_thor import StageController


TEXT_COLOR = "#0A4A51"
GREEN_COLOR = "#1EAD4F"
RED_COLOR = "#C0392B"
ORANGE_COLOR = "#D35400"

SPEED_OF_LIGHT_MM_PS = 0.299792458
CALIBRATION_SECONDS = 20.0
CALIBRATION_STAGE_DISTANCE_MM = 0.01
CALIBRATION_STAGE_MOTION_SECONDS = CALIBRATION_SECONDS * 0.85
CALIBRATION_STAGE_SPEED_MM_S = (
    2 * CALIBRATION_STAGE_DISTANCE_MM
) / CALIBRATION_STAGE_MOTION_SECONDS
DEFAULT_FRINGE_AMPLITUDE_V = 0.001
MIN_VALID_FRINGE_AMPLITUDE_V = 0.001
MAX_VALID_FRINGE_AMPLITUDE_V = 0.010
FRINGE_RISE_FRACTION = 0.55
FRINGE_REARM_FRACTION = 0.20
DEFAULT_STAGE_SPEED_MM_S = 0.000600
RAW_HISTORY_LENGTH = 300
SMOOTHING_WINDOW_LENGTH = 1
STEP_PAUSE_S = 0.05
REQUIRED_DARK_FRAMES = 1
REQUIRED_BRIGHT_FRAMES = 1
FRINGE_COOLDOWN = SAMPLE_INTERVAL_S
STAGE_STATUS_POLL_MS = 100

# =============================================================================
# STAGE AUTOMATIC MOTION PARAMETERS (similar to movestage.py)
# =============================================================================
# Mode: 'continuous' or 'stepped'
MODE = "continuous"

# For continuous mode:
VELOCITY_MM_S = 0.0006  # Velocity in mm/s
TOTAL_DISTANCE_MM = 13.0  # Total distance to move in mm

# For stepped mode:
VELOCITY_MM_S_STEPPED = 1.00  # Velocity in mm/s
STEP_SIZE_MM = 0.00001  # Step size in mm
STEPS = 100  # Number of steps


def compute_quarter_wavelength_step_mm(wavelength_nm):

    return (wavelength_nm / 4) / 1_000_000


class SideApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        if USE_REFERENCE_DIODE:
            self.title("Reference Photodiode Fringe Monitor")
        else:
            self.title("Single Photodiode Fringe Monitor")
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
        self.measurement_thread = None
        self.calibrating = False
        self.latest_sample = None
        self.latest_voltage = 0.0
        self.last_error_text = None

        self.raw_voltage_history = []
        self.calibration_raw_samples = []
        self.smoothed_voltage_history = []
        self.accumulated_fringes = 0
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0
        self.dark_threshold = 0.0
        self.bright_threshold = 0.0
        default_amp = DEFAULT_FRINGE_AMPLITUDE_V
        self.fringe_amplitude_voltage = default_amp
        self.fringe_rise_threshold_voltage = (
            default_amp * FRINGE_RISE_FRACTION
        )
        self.fringe_rearm_threshold_voltage = (
            default_amp * FRINGE_REARM_FRACTION
        )
        self.fringe_trough_voltage = None
        self.fringe_peak_voltage = None

        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
        self.fringe_distance_mm = compute_fringe_distance_mm(
            self.laser_wavelength_nm
        )
        self.quarter_wavelength_step_mm = compute_quarter_wavelength_step_mm(
            self.laser_wavelength_nm
        )

        if USE_REFERENCE_DIODE:
            self.diode = ReferenceDiodeHandler()
        else:
            self.diode = SingleDiodeHandler()

        self.stage = StageController()
        self.stage_connected = self.stage.connect()

        self.stage_start_position = 0.0
        self.stage_reference_position = 0.0
        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        self.stage_target_position = None
        self.stage_remaining_to_drive = 0.0
        self.stage_remaining_known = True
        self.last_stage_speed_time = None
        self.last_stage_speed_position = None

        self.build_ui()
        self.update_comparison_labels()
        self.update_stage_position_once()

        self.all_buttons = [
            self.restart_btn,
            self.wavelength_button,
            self.speed_button,
            self.btn_target_abs,
            self.btn_target_rel,
            self.btn_stop,
            self.btn_min,
            self.btn_left,
            self.btn_center,
            self.btn_right,
            self.btn_max
        ]

        self.after(
            STAGE_STATUS_POLL_MS,
            self.poll_stage_status
        )

    # -------------------------------------------------------------------------
    # UI
    # -------------------------------------------------------------------------

    def build_ui(self):

        ctk.CTkLabel(
            self.scroll,
            text="Single Photodiode Fringe Monitor",
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
        self.wavelength_entry.insert(
            0,
            f"{self.laser_wavelength_nm:.1f}"
        )

        self.wavelength_button = ctk.CTkButton(
            self.stage_frame,
            text="Set wavelength",
            width=120,
            command=self.apply_wavelength,
            fg_color=TEXT_COLOR
        )
        self.wavelength_button.pack(pady=1)

        ctk.CTkLabel(
            self.stage_frame,
            text="Schrittweite / Step size:",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 0))

        self.step_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Step size in mm",
            width=250
        )
        self.step_entry.pack(pady=1)
        self.step_entry.insert(
            0,
            f"{self.quarter_wavelength_step_mm:.9f}"
        )

        ctk.CTkLabel(
            self.stage_frame,
            text="Geschwindigkeit / Velocity:",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 0))

        self.speed_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Movement speed in mm/s",
            width=250
        )
        self.speed_entry.pack(pady=1)

        stage_velocity = DEFAULT_STAGE_SPEED_MM_S
        if self.stage_connected:
            if not self.stage.set_velocity(stage_velocity):
                stage_velocity = self.stage.set_velocity()

        if stage_velocity is None:
            stage_velocity = DEFAULT_STAGE_SPEED_MM_S

        self.speed_entry.insert(
            0,
            f"{stage_velocity:.6f}"
        )

        self.speed_button = ctk.CTkButton(
            self.stage_frame,
            text="Set speed",
            width=120,
            command=self.apply_stage_speed,
            fg_color=TEXT_COLOR
        )
        self.speed_button.pack(pady=1)

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

        ctk.CTkLabel(
            self.stage_frame,
            text="Zielposition oder Distanz / Target or Distance (mm):",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 0))

        self.target_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Target value or distance in mm",
            width=250
        )
        self.target_entry.pack(pady=1)
        self.target_entry.insert(0, "0.01")

        self.target_button_frame = ctk.CTkFrame(
            self.stage_frame,
            fg_color="transparent"
        )
        self.target_button_frame.pack(pady=1)

        self.btn_target_abs = ctk.CTkButton(
            self.target_button_frame,
            text="Go to target",
            width=140,
            command=self.move_to_target,
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
            command=self.move_distance,
            fg_color=TEXT_COLOR
        )
        self.btn_target_rel.grid(
            row=0,
            column=1,
            padx=1
        )

        self.btn_stop = ctk.CTkButton(
            self.target_button_frame,
            text="STOP STAGE",
            width=140,
            command=self.stop_stage,
            fg_color=RED_COLOR,
            font=("Arial", 11, "bold")
        )
        self.btn_stop.grid(
            row=0,
            column=2,
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

        self.label_stage_speed = ctk.CTkLabel(
            self.stage_frame,
            text="Movement Speed: 0.000000 mm/s",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_stage_speed.pack(pady=0)

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
            text="Distance from Fringes: 0.000 um",
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

        if USE_REFERENCE_DIODE:
            min_text = "Min Ratio: n/a"
            max_text = "Max Ratio: n/a"
            dark_text = "Fringe Rise Threshold Ratio: waiting"
            bright_text = "Fringe Amplitude Ratio: waiting"
            norm_text = "Normalized Ratio: 0.0000"
        else:
            min_text = "Min Voltage: n/a"
            max_text = "Max Voltage: n/a"
            dark_text = "Fringe Rise Threshold: waiting"
            bright_text = "Fringe Amplitude: waiting"
            norm_text = "Normalized Voltage: 0.0000"

        self.label_calibration_offset = ctk.CTkLabel(
            self.frame,
            text=dark_text,
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_calibration_offset.pack(pady=0)

        self.label_calibration_scale = ctk.CTkLabel(
            self.frame,
            text=bright_text,
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_calibration_scale.pack(pady=0)

        self.label_sample_count = ctk.CTkLabel(
            self.frame,
            text="Accumulated Fringes Count: 0",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_sample_count.pack(pady=0)

        self.label_min_voltage = ctk.CTkLabel(
            self.frame,
            text=min_text,
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_min_voltage.pack(pady=0)

        self.label_max_voltage = ctk.CTkLabel(
            self.frame,
            text=max_text,
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_max_voltage.pack(pady=0)

        if USE_REFERENCE_DIODE:
            self.label_raw_pint = ctk.CTkLabel(
                self.frame,
                text="Pint Raw Voltage: 0.000000 V",
                font=("Arial", 10),
                text_color=TEXT_COLOR
            )
            self.label_raw_pint.pack(pady=0)

            self.label_raw_ref = ctk.CTkLabel(
                self.frame,
                text="Pl Raw Voltage: 0.000000 V",
                font=("Arial", 10),
                text_color=TEXT_COLOR
            )
            self.label_raw_ref.pack(pady=0)

            self.label_ratio = ctk.CTkLabel(
                self.frame,
                text="Ratio Pint/Pl: 0.000000",
                font=("Arial", 10),
                text_color=TEXT_COLOR
            )
            self.label_ratio.pack(pady=0)
        else:
            self.label_raw = ctk.CTkLabel(
                self.frame,
                text="Raw Voltage: 0.000000 V",
                font=("Arial", 10),
                text_color=TEXT_COLOR
            )
            self.label_raw.pack(pady=0)

        self.label_norm = ctk.CTkLabel(
            self.frame,
            text=norm_text,
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_norm.pack(pady=0)

        self.label_calibration = ctk.CTkLabel(
            self.frame,
            text="Calibration: waiting",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_calibration.pack(pady=0)

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
            text="Stage Movement",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=0)

        self.compare_driven_frame = ctk.CTkFrame(
            self.compare_frame,
            fg_color="transparent"
        )
        self.compare_driven_frame.pack(pady=0)

        self.label_compare_driven = ctk.CTkLabel(
            self.compare_driven_frame,
            text="Driven: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_compare_driven.grid(
            row=0,
            column=0,
            padx=(0, 14)
        )

        self.label_still_to_drive = ctk.CTkLabel(
            self.compare_driven_frame,
            text="Still to drive: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_still_to_drive.grid(
            row=0,
            column=1,
            padx=(14, 0)
        )

        self.label_compare_calculated = ctk.CTkLabel(
            self.compare_frame,
            text="Calculated from Fringes: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_compare_calculated.pack(pady=0)

        self.label_compare_difference = ctk.CTkLabel(
            self.compare_frame,
            text="Difference: n/a",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_compare_difference.pack(pady=0)

        if USE_REFERENCE_DIODE:
            channel_text = f"Channels: Pint={PHOTODIODE_CHANNEL}, Pl={PHOTODIODE_REF_CHANNEL}"
        else:
            channel_text = f"Channel: photodiode={PHOTODIODE_CHANNEL}"
        ctk.CTkLabel(
            self.scroll,
            text=channel_text,
            font=("Arial", 10),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 2))

        self.plot_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )
        self.plot_frame.pack(
            fill="x",
            expand=False,
            padx=5,
            pady=(4, 10)
        )

        ctk.CTkLabel(
            self.plot_frame,
            text="Live Pint/Pl Ratio" if USE_REFERENCE_DIODE else "Live Raw Voltage",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 2))

        self.build_plot()

    def build_plot(self):

        if Figure is None or FigureCanvasTkAgg is None:
            self.plot_axis = None
            self.plot_canvas = None

            ctk.CTkLabel(
                self.plot_frame,
                text="Matplotlib is required for live voltage plotting.",
                font=("Arial", 11),
                text_color=RED_COLOR
            ).pack(pady=8)

            return

        self.plot_figure = Figure(
            figsize=(8, 2),
            dpi=100
        )
        self.plot_axis = self.plot_figure.add_subplot(111)
        self.plot_axis.set_title("Raw diode voltage", fontsize=9)
        self.plot_axis.set_xlabel("Samples", fontsize=8)
        self.plot_axis.set_ylabel("Voltage", fontsize=8)
        self.plot_axis.tick_params(labelsize=8)
        self.plot_axis.grid(
            True,
            linestyle=":",
            alpha=0.6
        )

        self.plot_line_voltage = self.plot_axis.plot(
            [],
            [],
            color="blue",
            label="Pint/Pl ratio" if USE_REFERENCE_DIODE else "photodiode raw"
        )[0]
        self.plot_axis.legend(loc="upper right", prop={"size": 8})
        self.plot_figure.subplots_adjust(
            left=0.08,
            right=0.98,
            top=0.85,
            bottom=0.22
        )

        self.plot_canvas = FigureCanvasTkAgg(
            self.plot_figure,
            master=self.plot_frame
        )
        self.plot_canvas.draw()
        plot_widget = self.plot_canvas.get_tk_widget()
        plot_widget.configure(height=220)
        plot_widget.pack(
            fill="x",
            expand=False,
            padx=8,
            pady=8
        )

    def set_buttons_enabled(self, enabled):

        state = "normal" if enabled else "disabled"

        for button in self.all_buttons:
            button.configure(state=state)

    # -------------------------------------------------------------------------
    # Monitoring
    # -------------------------------------------------------------------------

    def toggle(self):

        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):

        if (
            self.measurement_thread is not None
            and self.measurement_thread.is_alive()
        ):
            return

        self.restart_values_only()

        if USE_REFERENCE_DIODE:
            self.diode = ReferenceDiodeHandler()
        else:
            self.diode = SingleDiodeHandler()
        self.is_monitoring = True
        self.calibrating = True
        self.last_error_text = None

        self.btn.configure(
            text="STOP MONITORING",
            fg_color=RED_COLOR
        )
        self.status.configure(
            text="Status: connecting NI...",
            text_color=ORANGE_COLOR
        )

        self.set_buttons_enabled(False)

        self.measurement_thread = threading.Thread(
            target=self.loop,
            daemon=True
        )
        self.measurement_thread.start()

    def stop_monitoring(self):

        self.is_monitoring = False
        self.calibrating = False

        if self.stage_connected and self.stage.is_moving:
            self.stage.stop()

        self.status.configure(
            text="Status: stopping...",
            text_color=ORANGE_COLOR
        )

    def loop(self):

        try:
            self.diode.connect()

            self.after(
                0,
                lambda:
                self.status.configure(
                    text=f"Status: calibrating {CALIBRATION_SECONDS:.1f}s...",
                    text_color=ORANGE_COLOR
                )
            )

            # Start stage calibration motion if connected
            if self.stage_connected:
                threading.Thread(
                    target=self.calibration_stage_motion,
                    daemon=True
                ).start()

            calibration = self.diode.calibrate(
                seconds=CALIBRATION_SECONDS,
                sample_interval_s=SAMPLE_INTERVAL_S,
                should_continue=lambda: self.is_monitoring,
                sample_callback=self.handle_calibration_sample
            )

            if not self.is_monitoring:
                return

            self.calibrating = False
            self.stop_calibration_stage_motion()

            if calibration is not None:
                self.after(
                    0,
                    lambda c=calibration:
                    self.finish_calibration_display(c)
                )

            while self.is_monitoring:
                sample = self.diode.read()

                self.after(
                    0,
                    lambda s=sample:
                    self.update_sample_display(s)
                )

                time.sleep(SAMPLE_INTERVAL_S)

        except Exception as error:
            self.last_error_text = str(error)
            self.after(
                0,
                lambda e=error:
                self.show_error(e)
            )

        finally:
            self.is_monitoring = False
            self.calibrating = False

            try:
                self.diode.close()
            except Exception:
                pass

            self.after(
                0,
                self.finish_stopped_ui
            )

    def handle_calibration_sample(self, sample_data, elapsed_s, total_s):

        self.after(
            0,
            lambda s=sample_data, e=elapsed_s, t=total_s:
            self.update_calibration_progress(s, e, t)
        )

    def update_calibration_progress(
        self,
        sample_data,
        elapsed_s,
        total_s
    ):

        if USE_REFERENCE_DIODE:
            raw_int, raw_ref = sample_data
            if abs(raw_ref) < 1e-6:
                denom = 1e-6 if raw_ref >= 0 else -1e-6
            else:
                denom = raw_ref
            val = raw_int / denom
            self.calibration_raw_samples.append(val)
            self.append_raw_history(val)

            self.label_raw_pint.configure(
                text=f"Pint Raw Voltage: {raw_int:+.6f} V"
            )
            self.label_raw_ref.configure(
                text=f"Pl Raw Voltage: {raw_ref:+.6f} V"
            )
            self.label_ratio.configure(
                text=f"Ratio Pint/Pl: {val:.6f}"
            )
        else:
            val = sample_data
            self.calibration_raw_samples.append(val)
            self.append_raw_history(val)

            self.label_raw.configure(
                text=f"Raw Voltage: {val:+.6f} V"
            )

        self.update_plot()

        self.label_calibration.configure(
            text=f"Calibration: {elapsed_s:.1f}/{total_s:.1f}s"
        )

    def finish_calibration_display(self, calibration):

        (
            fringe_min_voltage,
            fringe_max_voltage,
            extrema_count,
            fringe_amplitude_voltage
        ) = (
            self.find_calibration_fringe_extrema(
                self.calibration_raw_samples
            )
        )
        if fringe_min_voltage is None or fringe_max_voltage is None:
            if USE_REFERENCE_DIODE:
                fringe_min_voltage = calibration.min_ratio
                fringe_max_voltage = calibration.max_ratio
                fringe_amplitude_voltage = max((fringe_max_voltage - fringe_min_voltage) / 2, 0.002)
            else:
                fringe_min_voltage = calibration.min_voltage
                fringe_max_voltage = calibration.max_voltage
                fringe_amplitude_voltage = max((fringe_max_voltage - fringe_min_voltage) / 2, 0.0015)

        self.apply_calibration_extrema(
            calibration,
            fringe_min_voltage,
            fringe_max_voltage
        )
        self.configure_fringe_detection(
            fringe_amplitude_voltage
        )

        value_range = fringe_max_voltage - fringe_min_voltage
        self.dark_threshold = (
            fringe_min_voltage
            + value_range * 0.125
        )
        self.bright_threshold = (
            fringe_max_voltage
            - value_range * 0.40
        )

        if USE_REFERENCE_DIODE:
            self.label_calibration.configure(
                text=(
                    f"Fringe calibration min/max: "
                    f"{fringe_min_voltage:.6f}/"
                    f"{fringe_max_voltage:.6f} "
                    f"({extrema_count} extrema, "
                    f"amp {self.fringe_amplitude_voltage:.6f})"
                ),
                text_color=GREEN_COLOR
            )
            self.label_calibration_offset.configure(
                text=(
                    f"Fringe Rise Threshold Ratio: "
                    f"{self.fringe_rise_threshold_voltage:.6f}"
                )
            )
            self.label_calibration_scale.configure(
                text=(
                    f"Fringe Amplitude Ratio: "
                    f"{self.fringe_amplitude_voltage:.6f}"
                )
            )
            self.label_min_voltage.configure(
                text=f"Min Ratio: {fringe_min_voltage:.6f}"
            )
            self.label_max_voltage.configure(
                text=f"Max Ratio: {fringe_max_voltage:.6f}"
            )
        else:
            self.label_calibration.configure(
                text=(
                    f"Fringe calibration min/max: "
                    f"{fringe_min_voltage:+.6f}/"
                    f"{fringe_max_voltage:+.6f} V "
                    f"({extrema_count} extrema, "
                    f"amp {self.fringe_amplitude_voltage:.6f} V)"
                ),
                text_color=GREEN_COLOR
            )
            self.label_calibration_offset.configure(
                text=(
                    f"Fringe Rise Threshold: "
                    f"{self.fringe_rise_threshold_voltage:.6f} V"
                )
            )
            self.label_calibration_scale.configure(
                text=(
                    f"Fringe Amplitude: "
                    f"{self.fringe_amplitude_voltage:.6f} V"
                )
            )
            self.label_min_voltage.configure(
                text=f"Min Voltage: {fringe_min_voltage:+.6f} V"
            )
            self.label_max_voltage.configure(
                text=f"Max Voltage: {fringe_max_voltage:+.6f} V"
            )

        if not self.stage_connected or not self.stage.is_moving:
            self.set_buttons_enabled(True)

        self.status.configure(
            text="Status: monitoring running",
            text_color=GREEN_COLOR
        )

    def find_calibration_fringe_extrema(self, samples):

        if not samples:
            return None, None, 0

        if len(samples) < 5:
            return (
                min(samples),
                max(samples),
                0,
                DEFAULT_FRINGE_AMPLITUDE_V
            )

        smoothed_samples = []

        for index in range(len(samples)):
            start_index = max(
                0,
                index - 2
            )
            end_index = min(
                len(samples),
                index + 3
            )
            window = samples[start_index:end_index]
            smoothed_samples.append(
                sum(window) / len(window)
            )

        minima = []
        maxima = []
        extrema = []

        for index in range(1, len(smoothed_samples) - 1):
            previous_value = smoothed_samples[index - 1]
            current_value = smoothed_samples[index]
            next_value = smoothed_samples[index + 1]

            if (
                (
                    current_value <= previous_value
                    and current_value < next_value
                )
                or (
                    current_value < previous_value
                    and current_value <= next_value
                )
            ):
                minima.append(current_value)
                extrema.append(
                    ("min", current_value)
                )

            if (
                (
                    current_value >= previous_value
                    and current_value > next_value
                )
                or (
                    current_value > previous_value
                    and current_value >= next_value
                )
            ):
                maxima.append(current_value)
                extrema.append(
                    ("max", current_value)
                )

        if minima and maxima:
            fringe_amplitude = self.estimate_fringe_amplitude(
                extrema,
                max(maxima) - min(minima)
            )

            return (
                min(minima),
                max(maxima),
                len(minima) + len(maxima),
                fringe_amplitude
            )

        return (
            min(smoothed_samples),
            max(smoothed_samples),
            0,
            DEFAULT_FRINGE_AMPLITUDE_V
        )

    def estimate_fringe_amplitude(self, extrema, fallback_amplitude):

        compressed_extrema = []

        for kind, value in extrema:
            if (
                compressed_extrema
                and compressed_extrema[-1][0] == kind
            ):
                previous_kind, previous_value = compressed_extrema[-1]

                if (
                    kind == "min"
                    and value < previous_value
                ):
                    compressed_extrema[-1] = (previous_kind, value)

                if (
                    kind == "max"
                    and value > previous_value
                ):
                    compressed_extrema[-1] = (previous_kind, value)

                continue

            compressed_extrema.append(
                (kind, value)
            )

        amplitudes = []

        for index in range(1, len(compressed_extrema)):
            previous_kind, previous_value = compressed_extrema[index - 1]
            current_kind, current_value = compressed_extrema[index]

            if previous_kind == current_kind:
                continue

            amplitude = abs(
                current_value - previous_value
            )

        min_valid = MIN_VALID_FRINGE_AMPLITUDE_V
        max_valid = 0.8 if USE_REFERENCE_DIODE else MAX_VALID_FRINGE_AMPLITUDE_V
        default_amp = DEFAULT_FRINGE_AMPLITUDE_V

        for index in range(1, len(compressed_extrema)):
            previous_kind, previous_value = compressed_extrema[index - 1]
            current_kind, current_value = compressed_extrema[index]

            if previous_kind == current_kind:
                continue

            amplitude = abs(
                current_value - previous_value
            )

            if (
                min_valid
                <= amplitude
                <= max_valid
            ):
                amplitudes.append(amplitude)

        if amplitudes:
            amplitudes.sort()
            upper_half = amplitudes[len(amplitudes) // 2:]

            return self.median_value(
                upper_half
            )

        if (
            min_valid
            <= fallback_amplitude
            <= max_valid
        ):
            return fallback_amplitude

        return default_amp

    def median_value(self, values):

        if not values:
            return DEFAULT_FRINGE_AMPLITUDE_V

        sorted_values = sorted(values)
        middle_index = len(sorted_values) // 2

        if len(sorted_values) % 2:
            return sorted_values[middle_index]

        return (
            sorted_values[middle_index - 1]
            + sorted_values[middle_index]
        ) / 2

    def configure_fringe_detection(self, amplitude_voltage):

        min_valid = MIN_VALID_FRINGE_AMPLITUDE_V
        max_valid = 0.8 if USE_REFERENCE_DIODE else MAX_VALID_FRINGE_AMPLITUDE_V
        default_amp = DEFAULT_FRINGE_AMPLITUDE_V

        if (
            amplitude_voltage is None
            or amplitude_voltage < min_valid
            or amplitude_voltage > max_valid
        ):
            amplitude_voltage = default_amp

        self.fringe_amplitude_voltage = amplitude_voltage
        self.fringe_rise_threshold_voltage = (
            self.fringe_amplitude_voltage
            * FRINGE_RISE_FRACTION
        )
        self.fringe_rearm_threshold_voltage = (
            self.fringe_amplitude_voltage
            * FRINGE_REARM_FRACTION
        )
        self.fringe_trough_voltage = None
        self.fringe_peak_voltage = None
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0

    def apply_calibration_extrema(
        self,
        calibration,
        min_val,
        max_val
    ):

        offset_val = (
            min_val + max_val
        ) / 2
        scale_val = (
            max_val - min_val
        ) / 2

        if scale_val <= 1e-12:
            scale_val = 1.0

        if USE_REFERENCE_DIODE:
            calibration.min_ratio = min_val
            calibration.max_ratio = max_val
            calibration.offset_ratio = offset_val
            calibration.scale_ratio = scale_val

            self.diode.counter.min_ratio = min_val
            self.diode.counter.max_ratio = max_val
            self.diode.counter.offset_ratio = offset_val
            self.diode.counter.scale_ratio = scale_val
        else:
            calibration.min_voltage = min_val
            calibration.max_voltage = max_val
            calibration.offset_voltage = offset_val
            calibration.scale_voltage = scale_val

            self.diode.counter.min_voltage = min_val
            self.diode.counter.max_voltage = max_val
            self.diode.counter.offset_voltage = offset_val
            self.diode.counter.scale_voltage = scale_val

    def update_sample_display(self, sample):

        self.latest_sample = sample

        if USE_REFERENCE_DIODE:
            val = sample.ratio
        else:
            val = sample.raw_voltage

        self.latest_voltage = val
        fringe_counted = self.update_accumulated_fringes(val)

        self.append_raw_history(val)
        self.update_plot()

        distance_mm = self.accumulated_fringes * self.fringe_distance_mm
        distance_um = distance_mm * 1000
        time_ps = (2 * distance_mm) / SPEED_OF_LIGHT_MM_PS

        self.label_um.configure(
            text=f"Distance from Fringes: {distance_um:.6f} um"
        )
        self.label_ps.configure(
            text=f"Time Delay: {time_ps:.4f} ps"
        )
        self.label_sample_count.configure(
            text=f"Accumulated Fringes Count: {self.accumulated_fringes}"
        )

        if USE_REFERENCE_DIODE:
            self.label_raw_pint.configure(
                text=f"Pint Raw Voltage: {sample.raw_int:+.6f} V"
            )
            self.label_raw_ref.configure(
                text=f"Pl Raw Voltage: {sample.raw_ref:+.6f} V"
            )
            self.label_ratio.configure(
                text=f"Ratio Pint/Pl: {sample.ratio:.6f}"
            )
            self.label_norm.configure(
                text=f"Normalized Ratio: {sample.normalized_ratio:+.4f}"
            )
        else:
            self.label_raw.configure(
                text=f"Raw Voltage: {sample.raw_voltage:+.6f} V"
            )
            self.label_norm.configure(
                text=f"Normalized Voltage: {sample.normalized_voltage:+.4f}"
            )

        if fringe_counted:
            self.label_sample_count.configure(
                text_color=GREEN_COLOR
            )
            self.after(
                250,
                lambda:
                self.label_sample_count.configure(
                    text_color=TEXT_COLOR
                )
            )

        self.update_comparison_labels()

    def update_accumulated_fringes(self, voltage):

        self.smoothed_voltage_history.append(
            voltage
        )

        if len(self.smoothed_voltage_history) > SMOOTHING_WINDOW_LENGTH:
            self.smoothed_voltage_history.pop(0)

        smooth_voltage = (
            sum(self.smoothed_voltage_history)
            / len(self.smoothed_voltage_history)
        )

        if self.fringe_trough_voltage is None:
            self.fringe_trough_voltage = smooth_voltage
            self.fringe_peak_voltage = smooth_voltage
            return False

        if self.fringe_peak_voltage is None:
            self.fringe_peak_voltage = smooth_voltage

        cooldown_ok = (
            time.time() - self.last_count_time
        ) > FRINGE_COOLDOWN

        if not self.was_dark:
            if smooth_voltage > self.fringe_peak_voltage:
                self.fringe_peak_voltage = smooth_voltage

            drop_from_peak = (
                self.fringe_peak_voltage
                - smooth_voltage
            )

            if drop_from_peak >= self.fringe_rearm_threshold_voltage:
                self.dark_counter += 1
                self.fringe_trough_voltage = min(
                    self.fringe_trough_voltage,
                    smooth_voltage
                )
            else:
                self.dark_counter = 0

            if self.dark_counter >= REQUIRED_DARK_FRAMES:
                self.was_dark = True
                self.fringe_trough_voltage = smooth_voltage
                self.bright_counter = 0

            return False

        if smooth_voltage < self.fringe_trough_voltage:
            self.fringe_trough_voltage = smooth_voltage
            self.bright_counter = 0
            return False

        rise_from_trough = (
            smooth_voltage
            - self.fringe_trough_voltage
        )

        if rise_from_trough >= self.fringe_rise_threshold_voltage:
            self.bright_counter += 1
        else:
            self.bright_counter = 0

        if (
            self.was_dark
            and self.bright_counter >= REQUIRED_BRIGHT_FRAMES
            and cooldown_ok
        ):
            self.accumulated_fringes += 1
            self.was_dark = False
            self.last_count_time = time.time()
            self.dark_counter = 0
            self.bright_counter = 0
            self.fringe_peak_voltage = smooth_voltage
            self.fringe_trough_voltage = smooth_voltage

            return True

        return False

    def append_raw_history(self, raw_voltage):

        self.raw_voltage_history.append(raw_voltage)

        if len(self.raw_voltage_history) > RAW_HISTORY_LENGTH:
            self.raw_voltage_history.pop(0)

    def update_plot(self, reset=False):

        if self.plot_axis is None:
            return

        if reset:
            self.plot_line_voltage.set_data([], [])
            self.plot_axis.relim()
            self.plot_axis.autoscale_view()
            self.plot_canvas.draw_idle()
            return

        x = list(
            range(len(self.raw_voltage_history))
        )
        self.plot_line_voltage.set_data(
            x,
            self.raw_voltage_history
        )
        self.plot_axis.relim()
        self.plot_axis.autoscale_view()
        self.plot_canvas.draw_idle()

    def show_error(self, error):

        self.status.configure(
            text=f"Status: {error}",
            text_color=RED_COLOR
        )

    def finish_stopped_ui(self):

        self.btn.configure(
            text="START MONITORING",
            fg_color=TEXT_COLOR
        )

        if self.last_error_text:
            self.status.configure(
                text=f"Status: {self.last_error_text}",
                text_color=RED_COLOR
            )
        else:
            self.status.configure(
                text="Status: Stopped",
                text_color=TEXT_COLOR
            )

    def restart(self):

        self.restart_values_only()

    def restart_values_only(self):

        if self.diode is not None:
            self.diode.counter.reset()

        self.latest_sample = None
        self.latest_voltage = 0.0
        self.raw_voltage_history = []
        self.calibration_raw_samples = []
        self.smoothed_voltage_history = []
        self.accumulated_fringes = 0
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0
        self.fringe_trough_voltage = None
        self.fringe_peak_voltage = None

        self.reset_stage_movement_tracking()

        self.label_um.configure(
            text="Distance from Fringes: 0.000 um"
        )
        self.label_ps.configure(
            text="Time Delay: 0.0000 ps"
        )
        if USE_REFERENCE_DIODE:
            self.label_calibration_offset.configure(
                text="Fringe Rise Threshold Ratio: waiting"
            )
            self.label_calibration_scale.configure(
                text="Fringe Amplitude Ratio: waiting"
            )
            self.label_sample_count.configure(
                text="Accumulated Fringes Count: 0",
                text_color=TEXT_COLOR
            )
            self.label_min_voltage.configure(
                text="Min Ratio: n/a"
            )
            self.label_max_voltage.configure(
                text="Max Ratio: n/a"
            )
            self.label_raw_pint.configure(
                text="Pint Raw Voltage: 0.000000 V"
            )
            self.label_raw_ref.configure(
                text="Pl Raw Voltage: 0.000000 V"
            )
            self.label_ratio.configure(
                text="Ratio Pint/Pl: 0.000000"
            )
            self.label_norm.configure(
                text="Normalized Ratio: 0.0000"
            )
        else:
            self.label_calibration_offset.configure(
                text="Fringe Rise Threshold: waiting"
            )
            self.label_calibration_scale.configure(
                text="Fringe Amplitude: waiting"
            )
            self.label_sample_count.configure(
                text="Accumulated Fringes Count: 0",
                text_color=TEXT_COLOR
            )
            self.label_min_voltage.configure(
                text="Min Voltage: n/a"
            )
            self.label_max_voltage.configure(
                text="Max Voltage: n/a"
            )
            self.label_raw.configure(
                text="Raw Voltage: 0.000000 V"
            )
            self.label_norm.configure(
                text="Normalized Voltage: 0.0000"
            )
        self.label_calibration.configure(
            text="Calibration: waiting",
            text_color=TEXT_COLOR
        )
        self.update_plot(reset=True)
        self.update_comparison_labels(0.0)

    # -------------------------------------------------------------------------
    # Stage control
    # -------------------------------------------------------------------------

    def parse_entry_float(self, entry):

        return float(
            entry.get().replace(",", ".")
        )

    def get_step_size(self):

        try:
            value = self.parse_entry_float(
                self.step_entry
            )
            value = abs(value)

            if value <= 0:
                raise ValueError

            return value

        except ValueError:
            self.status.configure(
                text="Status: invalid step size",
                text_color=RED_COLOR
            )
            return 0.0001

    def get_stage_speed(self):

        try:
            value = self.parse_entry_float(
                self.speed_entry
            )
            value = abs(value)

            if value <= 0:
                raise ValueError

            return value

        except ValueError:
            self.status.configure(
                text="Status: invalid movement speed",
                text_color=RED_COLOR
            )
            return None

    def apply_wavelength(self):

        try:
            wavelength_nm = self.parse_entry_float(
                self.wavelength_entry
            )
        except ValueError:
            self.status.configure(
                text="Invalid wavelength value",
                text_color=RED_COLOR
            )
            return

        if wavelength_nm <= 0:
            self.status.configure(
                text="Wavelength must be positive",
                text_color=RED_COLOR
            )
            return

        self.laser_wavelength_nm = wavelength_nm
        self.fringe_distance_mm = compute_fringe_distance_mm(
            self.laser_wavelength_nm
        )
        self.quarter_wavelength_step_mm = compute_quarter_wavelength_step_mm(
            self.laser_wavelength_nm
        )

        self.step_entry.delete(0, "end")
        self.step_entry.insert(
            0,
            f"{self.quarter_wavelength_step_mm:.9f}"
        )

        self.status.configure(
            text=f"Wavelength set to {self.laser_wavelength_nm:.1f} nm",
            text_color=GREEN_COLOR
        )

    def apply_stage_speed(self, update_status=True):

        speed_mm_s = self.get_stage_speed()

        if speed_mm_s is None:
            return False

        self.speed_entry.delete(0, "end")
        self.speed_entry.insert(
            0,
            f"{speed_mm_s:.6f}"
        )

        if not self.stage_connected:
            if update_status:
                self.status.configure(
                    text="Stage not connected",
                    text_color=RED_COLOR
                )
            return False

        if not self.stage.set_velocity(speed_mm_s):
            if update_status:
                self.status.configure(
                    text="Could not set stage speed",
                    text_color=RED_COLOR
                )
            return False

        self.label_stage_speed.configure(
            text=f"Movement Speed: {speed_mm_s:.6f} mm/s"
        )

        if update_status:
            self.status.configure(
                text=f"Stage speed set to {speed_mm_s:.6f} mm/s",
                text_color=GREEN_COLOR
            )

        return True

    def prepare_stage_for_move(self):

        if not self.stage_connected:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return False

        if self.stage.is_moving:
            self.update_still_to_drive_label()

            if self.stage_remaining_known:
                remaining_text = (
                    f"{self.stage_remaining_to_drive:.6f} mm"
                )
            else:
                remaining_text = "target unknown"

            self.status.configure(
                text=(
                    f"Stage is already moving, still to drive "
                    f"{remaining_text}"
                ),
                text_color=ORANGE_COLOR
            )
            return False

        return self.apply_stage_speed(
            update_status=False
        )

    def start_stage_move_to(self, target_mm, start_pos=None):

        if not self.prepare_stage_for_move():
            return

        if start_pos is None:
            start_pos = self.stage.get_position()

        target_mm = self.stage.clamp_position(
            target_mm
        )

        move_mm = target_mm - start_pos

        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.set_stage_target_position(
            target_mm,
            start_pos
        )
        self.reset_stage_speed_tracking(start_pos)

        if abs(move_mm) < 1e-12:
            self.update_stage_labels(
                start_pos,
                0.0,
                self.stage_movement_before_move
            )
            self.status.configure(
                text="Stage already at target",
                text_color=TEXT_COLOR
            )
            self.clear_stage_target_position()
            return

        if not self.stage.move_absolute(target_mm):
            self.status.configure(
                text="Stage move failed",
                text_color=RED_COLOR
            )
            self.clear_stage_target_position()
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

        if not self.stage_connected:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return

        start_pos = self.stage.get_position()

        self.start_stage_move_to(
            start_pos + move_mm,
            start_pos=start_pos
        )

    def start_stage_move_to_stepped(
        self,
        target_mm,
        step_mm=None,
        pause_s=STEP_PAUSE_S,
        label_prefix="Moving"
    ):

        if not self.prepare_stage_for_move():
            return

        start_pos = self.stage.get_position()
        target_mm = self.stage.clamp_position(
            target_mm
        )

        if abs(target_mm - start_pos) < 1e-12:
            self.status.configure(
                text="Stage already at target",
                text_color=TEXT_COLOR
            )
            return

        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.set_stage_target_position(
            target_mm,
            start_pos
        )
        self.reset_stage_speed_tracking(start_pos)

        if step_mm is None:
            step_mm = self.get_step_size()
        else:
            step_mm = abs(
                float(step_mm)
            )

        if step_mm <= 0:
            self.status.configure(
                text="Invalid step size",
                text_color=RED_COLOR
            )
            self.clear_stage_target_position()
            return

        threading.Thread(
            target=self.stage_stepped_move_worker,
            args=(start_pos, target_mm, step_mm, pause_s, label_prefix),
            daemon=True
        ).start()

    def start_stage_move_by_steps(
        self,
        move_mm,
        step_mm=None,
        pause_s=STEP_PAUSE_S,
        label_prefix="Moving"
    ):

        if not self.stage_connected:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return

        start_pos = self.stage.get_position()

        self.start_stage_move_to_stepped(
            start_pos + move_mm,
            step_mm=step_mm,
            pause_s=pause_s,
            label_prefix=label_prefix
        )

    def stage_stepped_move_worker(
        self,
        start_pos,
        target_mm,
        step_mm,
        pause_s,
        label_prefix
    ):

        step_sign = 1 if target_mm > start_pos else -1
        current_pos = start_pos
        remaining = abs(target_mm - start_pos)
        moved = 0.0

        self.after(
            0,
            lambda:
            self.status.configure(
                text=(
                    f"{label_prefix} to {target_mm:.6f} mm in "
                    f"{step_mm:.9f} mm steps"
                ),
                text_color=TEXT_COLOR
            )
        )

        while remaining > 1e-12:
            next_step = min(
                step_mm,
                remaining
            )
            next_target = current_pos + step_sign * next_step

            if not self.stage.move_absolute(next_target):
                self.after(
                    0,
                    lambda:
                    self.status.configure(
                        text="Stage move failed",
                        text_color=RED_COLOR
                    )
                )
                self.after(
                    0,
                    self.clear_stage_target_position
                )
                return

            while self.stage.is_moving:
                time.sleep(0.005 if pause_s <= 0 else 0.01)

            step_distance = abs(
                next_target - current_pos
            )
            moved += step_distance
            current_pos = next_target
            remaining = abs(
                target_mm - current_pos
            )

            self.total_stage_movement = (
                self.stage_movement_before_move + moved
            )

            self.after(
                0,
                lambda p=current_pos, m=moved, b=self.stage_movement_before_move:
                self.update_stage_labels(p, m, b)
            )

            if remaining > 1e-12 and pause_s > 0:
                time.sleep(pause_s)

        self.after(
            0,
            lambda:
            self.finish_stage_move(current_pos)
        )

    def stage_ui_loop(self):

        movement_base = self.stage_movement_before_move

        while self.stage.is_moving:
            pos = self.stage.get_position()
            moved = abs(
                pos - self.stage_start_position
            )

            self.after(
                0,
                lambda p=pos, m=moved, b=movement_base:
                self.update_stage_labels(p, m, b)
            )

            time.sleep(0.05)

        pos = self.stage.get_position()
        moved = abs(
            pos - self.stage_start_position
        )
        self.total_stage_movement = movement_base + moved

        self.after(
            0,
            lambda p=pos:
            self.finish_stage_move(p)
        )

    def finish_stage_move(self, pos):

        moved = abs(
            pos - self.stage_start_position
        )
        self.update_stage_labels(
            pos,
            moved,
            self.stage_movement_before_move
        )
        self.clear_stage_target_position()
        self.label_stage_speed.configure(
            text="Movement Speed: 0.000000 mm/s"
        )
        self.status.configure(
            text=f"Reached {pos:.6f} mm",
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

        self.start_stage_move_to_stepped(
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

    def move_to_target(self):

        try:
            target_mm = self.parse_entry_float(
                self.target_entry
            )
        except ValueError:
            self.status.configure(
                text="Invalid target value",
                text_color=RED_COLOR
            )
            return

        self.start_stage_move_to(
            target_mm
        )

    def move_distance(self):

        try:
            distance_mm = self.parse_entry_float(
                self.target_entry
            )
        except ValueError:
            self.status.configure(
                text="Invalid distance value",
                text_color=RED_COLOR
            )
            return

        self.start_stage_move_by(
            distance_mm
        )

    def stop_stage(self):

        if self.stage_connected:
            self.stage.stop()
        self.after(
            0,
            lambda:
            self.status.configure(
                text="Stage stopped manually",
                text_color=RED_COLOR
            )
        )

    def update_stage_position_once(self):

        if self.stage_connected:
            pos = self.stage.get_position()
            self.stage_reference_position = pos
            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )
        else:
            self.status.configure(
                text="Status: Stage not connected",
                text_color=ORANGE_COLOR
            )

    def poll_stage_status(self):

        try:
            if self.stage_connected:
                pos = self.stage.get_position()

                self.label_stage_position.configure(
                    text=f"Stage Position: {pos:.6f} mm"
                )
                self.update_still_to_drive_label(pos)

                if self.stage.is_moving:
                    self.update_stage_speed_label(pos)
                elif (
                    self.stage_remaining_known
                    and self.stage_remaining_to_drive <= 0
                ):
                    self.label_stage_speed.configure(
                        text="Movement Speed: 0.000000 mm/s"
                    )

        finally:
            self.after(
                STAGE_STATUS_POLL_MS,
                self.poll_stage_status
            )

    def update_stage_labels(self, pos, moved, movement_base=None):

        if movement_base is None:
            movement_base = self.total_stage_movement

        current_total_stage_movement = movement_base + abs(
            moved
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
        self.update_still_to_drive_label(pos)
        self.update_stage_speed_label(pos)
        self.update_comparison_labels(
            current_total_stage_movement
        )

    def set_stage_target_position(self, target_mm, current_pos=None):

        self.stage_target_position = target_mm

        if current_pos is None:
            if self.stage_connected:
                current_pos = self.stage.get_position()
            else:
                current_pos = target_mm

        self.update_still_to_drive_label(current_pos)

    def clear_stage_target_position(self):

        self.stage_target_position = None
        self.stage_remaining_to_drive = 0.0
        self.stage_remaining_known = True

        if hasattr(self, "label_still_to_drive"):
            self.label_still_to_drive.configure(
                text="Still to drive: 0.000000 mm"
            )

    def update_still_to_drive_label(self, pos=None):

        target_position = self.get_active_stage_target_position()

        if target_position is None:
            self.stage_remaining_to_drive = 0.0
            self.stage_remaining_known = (
                not self.stage_connected
                or not self.stage.is_moving
            )
        else:
            self.stage_remaining_known = True

            if pos is None:
                if self.stage_connected:
                    pos = self.stage.get_position()
                else:
                    pos = target_position

            self.stage_remaining_to_drive = abs(
                target_position - pos
            )

            if self.stage_remaining_to_drive < 1e-6:
                self.stage_remaining_to_drive = 0.0

        if hasattr(self, "label_still_to_drive"):
            if self.stage_remaining_known:
                label_text = (
                    f"Still to drive: "
                    f"{self.stage_remaining_to_drive:.6f} mm"
                )
            else:
                label_text = "Still to drive: target unknown"

            self.label_still_to_drive.configure(
                text=label_text
            )

    def get_active_stage_target_position(self):

        if self.stage_target_position is not None:
            return self.stage_target_position

        return None

    def reset_stage_speed_tracking(self, pos):

        self.last_stage_speed_position = pos
        self.last_stage_speed_time = time.time()

    def update_stage_speed_label(self, pos):

        now = time.time()

        if (
            self.last_stage_speed_time is None
            or self.last_stage_speed_position is None
        ):
            self.reset_stage_speed_tracking(pos)
            return

        dt = now - self.last_stage_speed_time

        if dt <= 0:
            return

        speed_mm_s = abs(
            pos - self.last_stage_speed_position
        ) / dt

        self.last_stage_speed_time = now
        self.last_stage_speed_position = pos

        self.label_stage_speed.configure(
            text=f"Movement Speed: {speed_mm_s:.6f} mm/s"
        )

    def reset_stage_movement_tracking(self, pos=None):

        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        self.stage_target_position = None
        self.stage_remaining_to_drive = 0.0
        self.stage_remaining_known = True

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
        self.label_stage_speed.configure(
            text="Movement Speed: 0.000000 mm/s"
        )
        self.clear_stage_target_position()

    def update_comparison_labels(self, driven_mm=None):

        if driven_mm is None:
            driven_mm = self.current_stage_movement_for_compare

        driven_distance_mm = abs(
            driven_mm
        )
        calculated_mm = (
            self.accumulated_fringes
            * self.fringe_distance_mm
        )
        difference_mm = driven_distance_mm - calculated_mm

        self.label_compare_driven.configure(
            text=f"Driven: {driven_distance_mm:.6f} mm"
        )
        self.label_compare_calculated.configure(
            text=f"Calculated from Fringes: {calculated_mm:.6f} mm"
        )
        self.label_compare_difference.configure(
            text=f"Difference: {difference_mm:.6f} mm"
        )

    # -------------------------------------------------------------------------
    # Shutdown
    # -------------------------------------------------------------------------

    def run_stage_motion_by_parameters(self):

        if not self.stage_connected:
            return

        current_position = self.stage.get_position()

        if MODE.lower().startswith("c"):
            self.stage.set_velocity(VELOCITY_MM_S)
            final_target = self.stage.clamp_position(current_position + TOTAL_DISTANCE_MM)

            self.stage_start_position = current_position
            self.stage_movement_before_move = self.total_stage_movement
            self.set_stage_target_position(
                final_target,
                current_position
            )
            self.reset_stage_speed_tracking(current_position)

            self.after(
                0,
                lambda:
                self.status.configure(
                    text=(
                        f"Continuous move to {final_target:.6f} mm "
                        f"at {VELOCITY_MM_S} mm/s"
                    ),
                    text_color=TEXT_COLOR
                )
            )

            if not self.stage.move_absolute(final_target):
                self.after(
                    0,
                    lambda:
                    self.status.configure(
                        text="Stage move failed",
                        text_color=RED_COLOR
                    )
                )
                self.after(
                    0,
                    self.clear_stage_target_position
                )
                return

            while self.stage.is_moving and self.is_monitoring:
                pos = self.stage.get_position()
                moved = abs(pos - self.stage_start_position)
                self.after(
                    0,
                    lambda p=pos, m=moved, b=self.stage_movement_before_move:
                    self.update_stage_labels(p, m, b)
                )
                time.sleep(0.05)

            pos = self.stage.get_position()
            moved = abs(pos - self.stage_start_position)
            self.total_stage_movement = (
                self.stage_movement_before_move + moved
            )
            self.after(
                0,
                lambda p=pos:
                self.finish_stage_move(p)
            )

        else:
            self.stage.set_velocity(VELOCITY_MM_S_STEPPED)

            self.stage_start_position = current_position
            self.stage_movement_before_move = self.total_stage_movement
            stepped_target = self.stage.clamp_position(
                current_position + STEP_SIZE_MM * STEPS
            )
            self.set_stage_target_position(
                stepped_target,
                current_position
            )
            self.reset_stage_speed_tracking(current_position)

            self.after(
                0,
                lambda:
                self.status.configure(
                    text=(
                        f"Stepped move: {STEPS} steps of "
                        f"{STEP_SIZE_MM} mm"
                    ),
                    text_color=TEXT_COLOR
                )
            )

            current_pos = current_position
            moved = 0.0

            for step in range(STEPS):
                if not self.is_monitoring:
                    break

                next_position = self.stage.clamp_position(
                    current_pos + STEP_SIZE_MM
                )

                self.after(
                    0,
                    lambda s=step, n=next_position:
                    self.status.configure(
                        text=(
                            f"Step {s + 1}/{STEPS}: "
                            f"move to {n:.7f} mm"
                        ),
                        text_color=TEXT_COLOR
                    )
                )

                if not self.stage.move_absolute(next_position):
                    self.after(
                        0,
                        lambda:
                        self.status.configure(
                            text="Move command failed",
                            text_color=RED_COLOR
                        )
                    )
                    break

                while self.stage.is_moving and self.is_monitoring:
                    time.sleep(0.01)

                step_distance = abs(next_position - current_pos)
                moved += step_distance
                current_pos = next_position

                self.total_stage_movement = (
                    self.stage_movement_before_move + moved
                )
                self.after(
                    0,
                    lambda p=current_pos, m=moved, b=self.stage_movement_before_move:
                    self.update_stage_labels(p, m, b)
                )

                if step < STEPS - 1:
                    time.sleep(STEP_PAUSE_S)

            self.after(
                0,
                lambda p=current_pos:
                self.finish_stage_move(p)
            )

    def calibration_stage_motion(self):

        previous_velocity = None

        try:
            if not self.stage_connected:
                return

            start_pos = self.stage.get_position()
            zero_target = self.stage.clamp_position(0.0)
            forward_target = self.stage.clamp_position(
                start_pos + CALIBRATION_STAGE_DISTANCE_MM
            )
            sweep_distance_mm = abs(
                forward_target - start_pos
            )

            if sweep_distance_mm <= 1e-12:
                return

            previous_velocity = self.stage.set_velocity()
            calibration_speed_mm_s = CALIBRATION_STAGE_SPEED_MM_S
            calibration_path_mm = (
                abs(forward_target - start_pos)
                + abs(forward_target - zero_target)
            )

            if (
                abs(calibration_path_mm - 2 * CALIBRATION_STAGE_DISTANCE_MM)
                > 1e-12
            ):
                calibration_speed_mm_s = (
                    calibration_path_mm
                    / CALIBRATION_STAGE_MOTION_SECONDS
                )

            if not self.stage.set_velocity(calibration_speed_mm_s):
                return

            self.stage_start_position = start_pos
            self.stage_movement_before_move = 0.0
            self.reset_stage_speed_tracking(start_pos)

            self.after(
                0,
                lambda:
                self.status.configure(
                    text=(
                        f"Calibration sweep then return to 0: "
                        f"{sweep_distance_mm:.5f} mm "
                        f"at {calibration_speed_mm_s:.6f} mm/s"
                    ),
                    text_color=ORANGE_COLOR
                )
            )

            for target in (forward_target, zero_target):
                if not self.is_monitoring or not self.calibrating:
                    return

                self.stage_target_position = target
                self.stage_remaining_known = True

                if not self.stage.move_absolute(target):
                    return

                while (
                    self.stage.is_moving
                    and self.is_monitoring
                    and self.calibrating
                ):
                    current_pos = self.stage.get_position()
                    moved = abs(
                        current_pos - start_pos
                    )
                    self.after(
                        0,
                        lambda p=current_pos, m=moved:
                        self.update_stage_labels(p, m, 0.0)
                    )
                    time.sleep(0.01)

                if not self.is_monitoring or not self.calibrating:
                    return

                current_pos = self.stage.get_position()
                self.after(
                    0,
                    lambda p=current_pos:
                    self.update_still_to_drive_label(p)
                )

        finally:
            if (
                previous_velocity is not None
                and self.stage_connected
                and self.stage.is_moving
            ):
                self.stage.stop()

            if previous_velocity is not None and self.stage_connected:
                self.stage.set_velocity(previous_velocity)

            self.after(0, self.finish_calibration_movement)

    def stop_calibration_stage_motion(self):

        if not self.stage_connected:
            return

        self.clear_stage_target_position()

        if self.stage.is_moving:
            self.stage.stop()

        self.after(
            0,
            lambda:
            self.status.configure(
                text="Calibration ended, stage stopped",
                text_color=ORANGE_COLOR
            )
        )

    def finish_calibration_movement(self):

        if self.stage_connected and self.stage.is_moving:
            self.stage.stop()
            self.status.configure(
                text="Calibration ended, waiting for stage stop",
                text_color=ORANGE_COLOR
            )
            self.after(
                STAGE_STATUS_POLL_MS,
                self.finish_calibration_movement
            )
            return

        if self.stage_connected:
            current_pos = self.stage.get_position()
            self.reset_stage_movement_tracking(current_pos)
        else:
            self.reset_stage_movement_tracking(150.0)

        if self.calibrating:
            self.status.configure(
                text="Calibration sweep finished",
                text_color=ORANGE_COLOR
            )
            return

        self.set_buttons_enabled(True)

        if self.is_monitoring:
            self.status.configure(
                text="Monitoring running",
                text_color=GREEN_COLOR
            )

    def on_close(self):

        self.is_monitoring = False

        try:
            self.diode.close()
        except Exception:
            pass

        try:
            self.stage.close()
        except Exception:
            pass

        self.destroy()


if __name__ == "__main__":

    app = SideApp()
    app.protocol(
        "WM_DELETE_WINDOW",
        app.on_close
    )
    app.mainloop()
