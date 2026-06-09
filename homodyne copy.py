import math
import threading
import time
from dataclasses import dataclass

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    plt = None
    FigureCanvasTkAgg = None

try:
    from stage_controller import StageController
except Exception as stage_import_error:
    StageController = None
    STAGE_IMPORT_ERROR = str(stage_import_error)
else:
    STAGE_IMPORT_ERROR = None


# Default NI inputs from NI.py. S1 is the cosine signal, S2 the sine signal.
PHOTODIODE_CHANNEL_S1 = "Dev1/ai0"
PHOTODIODE_CHANNEL_S2 = "Dev1/ai1"
REFERENCE_CHANNEL = "Dev1/ai2"

LASER_WAVELENGTH_NM = 780.0

# If the displayed direction is inverted in the real setup, set this to -1.
PHASE_DIRECTION_SIGN = 1

# Ignore samples close to the circle center. This avoids direction jumps when
# the photodiode signals are weak or disconnected.
MIN_SIGNAL_RADIUS = 0.05
MIN_REFERENCE_SIGNAL = 1e-9

CALIBRATION_SECONDS = 5.0
SAMPLE_INTERVAL_S = 0.005
UI_UPDATE_INTERVAL_S = 0.05

# Lock starts an automatic correction after this much measured drift.
LOCK_TRIGGER_FRINGES = 1.0
LOCK_CORRECTION_COOLDOWN_S = 0.30

# If the stage correction moves in the wrong direction, set this to -1.
STAGE_CORRECTION_SIGN = 1
STAGE_MOVE_TIMEOUT_S = 60.0
STAGE_CHECK_TIMEOUT_S = 180.0
STAGE_POLL_INTERVAL_S = 0.05
STAGE_VERIFY_TOLERANCE_MM = 5e-6

TEXT_COLOR = "#0A4A51"
GREEN_COLOR = "#1EAD4F"
RED_COLOR = "#C0392B"
ORANGE_COLOR = "#D35400"


def compute_fringe_distance_mm(wavelength_nm):
    return (wavelength_nm / 2) / 1_000_000 


def wrap_to_pi(angle_rad):
    return (angle_rad + math.pi) % (2 * math.pi) - math.pi


def completed_signed_fringes(fringe_position):
    if fringe_position == 0:
        return 0

    sign = 1 if fringe_position > 0 else -1
    return sign * math.floor(abs(fringe_position))


@dataclass
class HomodyneSample:
    timestamp: float
    raw_s1: float
    raw_s2: float
    raw_ref: float
    ref_corrected_s1: float
    ref_corrected_s2: float
    s1: float
    s2: float
    radius: float
    phase_rad: float
    unwrapped_phase_rad: float
    delta_phase_rad: float
    fringe_position: float
    signed_fringes: int
    fringe_delta: int
    direction: str
    valid: bool


class NIPhotodiodeReader:
    def __init__(
        self,
        channel_s1=PHOTODIODE_CHANNEL_S1,
        channel_s2=PHOTODIODE_CHANNEL_S2,
        channel_ref=REFERENCE_CHANNEL
    ):
        self.channel_s1 = channel_s1
        self.channel_s2 = channel_s2
        self.channel_ref = channel_ref
        self.task = None
        self.nidaqmx = None

    def connect(self):
        import nidaqmx

        self.nidaqmx = nidaqmx
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(self.channel_s1)
        self.task.ai_channels.add_ai_voltage_chan(self.channel_s2)
        self.task.ai_channels.add_ai_voltage_chan(self.channel_ref)
        return True

    def read(self):
        if self.task is None:
            raise RuntimeError("NI task is not connected.")

        values = self.task.read()

        if len(values) != 3:
            raise RuntimeError(
                "Expected three analog input values from the NI task."
            )

        return float(values[0]), float(values[1]), float(values[2])

    def close(self):
        if self.task is not None:
            self.task.close()
            self.task = None


class HomodyneQuadratureCounter:
    def __init__(
        self,
        phase_direction_sign=PHASE_DIRECTION_SIGN,
        min_signal_radius=MIN_SIGNAL_RADIUS,
        min_reference_signal=MIN_REFERENCE_SIGNAL,
        fringe_distance_mm=None
    ):
        self.phase_direction_sign = 1 if phase_direction_sign >= 0 else -1
        self.min_signal_radius = min_signal_radius
        self.min_reference_signal = min_reference_signal
        self.fringe_distance_mm = fringe_distance_mm

        self.offset_s1 = 0.0
        self.offset_s2 = 0.0
        self.offset_ref = 0.0
        self.scale_s1 = 1.0
        self.scale_s2 = 1.0
        self.scale_ref = 1.0

        self.previous_phase_rad = None
        self.unwrapped_phase_rad = 0.0
        self.signed_fringes = 0
        self.total_abs_fringes = 0

    def calibrate_from_samples(self, raw_samples):
        if not raw_samples:
            raise ValueError("No calibration samples were collected.")

        corrected_samples = [
            self.reference_corrected_values(*sample)
            for sample in raw_samples
            if abs(sample[2]) >= self.min_reference_signal
        ]

        if not corrected_samples:
            raise ValueError("Reference diode signal is too low.")

        s1_values = [sample[0] for sample in corrected_samples]
        s2_values = [sample[1] for sample in corrected_samples]
        ref_values = [sample[2] for sample in raw_samples]

        self.offset_s1 = (min(s1_values) + max(s1_values)) / 2
        self.offset_s2 = (min(s2_values) + max(s2_values)) / 2
        self.offset_ref = (min(ref_values) + max(ref_values)) / 2

        self.scale_s1 = (max(s1_values) - min(s1_values)) / 2
        self.scale_s2 = (max(s2_values) - min(s2_values)) / 2
        self.scale_ref = (max(ref_values) - min(ref_values)) / 2

        if self.scale_s1 <= 1e-12:
            self.scale_s1 = 1.0

        if self.scale_s2 <= 1e-12:
            self.scale_s2 = 1.0

        if self.scale_ref <= 1e-12:
            self.scale_ref = 1.0

        self.reset()

    def reset(self):
        self.previous_phase_rad = None
        self.unwrapped_phase_rad = 0.0
        self.signed_fringes = 0
        self.total_abs_fringes = 0

    def reference_corrected_values(self, raw_s1, raw_s2, raw_ref):
        ref_corrected_s1 = raw_s1 / raw_ref
        ref_corrected_s2 = raw_s2 / raw_ref
        return ref_corrected_s1, ref_corrected_s2

    def normalize(self, raw_s1, raw_s2, raw_ref):
        ref_corrected_s1, ref_corrected_s2 = self.reference_corrected_values(
            raw_s1,
            raw_s2,
            raw_ref
        )
        s1 = (ref_corrected_s1 - self.offset_s1) / self.scale_s1
        s2 = (ref_corrected_s2 - self.offset_s2) / self.scale_s2
        return ref_corrected_s1, ref_corrected_s2, s1, s2

    def update(self, raw_s1, raw_s2, raw_ref):
        timestamp = time.time()

        if abs(raw_ref) < self.min_reference_signal:
            return HomodyneSample(
                timestamp=timestamp,
                raw_s1=raw_s1,
                raw_s2=raw_s2,
                raw_ref=raw_ref,
                ref_corrected_s1=0.0,
                ref_corrected_s2=0.0,
                s1=0.0,
                s2=0.0,
                radius=0.0,
                phase_rad=0.0,
                unwrapped_phase_rad=self.unwrapped_phase_rad,
                delta_phase_rad=0.0,
                fringe_position=self.unwrapped_phase_rad / (2 * math.pi),
                signed_fringes=self.signed_fringes,
                fringe_delta=0,
                direction="reference_low",
                valid=False
            )

        ref_corrected_s1, ref_corrected_s2, s1, s2 = self.normalize(
            raw_s1,
            raw_s2,
            raw_ref
        )
        radius = math.hypot(s1, s2)

        if radius < self.min_signal_radius:
            return HomodyneSample(
                timestamp=timestamp,
                raw_s1=raw_s1,
                raw_s2=raw_s2,
                raw_ref=raw_ref,
                ref_corrected_s1=ref_corrected_s1,
                ref_corrected_s2=ref_corrected_s2,
                s1=s1,
                s2=s2,
                radius=radius,
                phase_rad=0.0,
                unwrapped_phase_rad=self.unwrapped_phase_rad,
                delta_phase_rad=0.0,
                fringe_position=self.unwrapped_phase_rad / (2 * math.pi),
                signed_fringes=self.signed_fringes,
                fringe_delta=0,
                direction="signal_low",
                valid=False
            )

        phase_rad = self.phase_direction_sign * math.atan2(s2, s1)

        if self.previous_phase_rad is None:
            self.previous_phase_rad = phase_rad
            delta_phase_rad = 0.0
        else:
            delta_phase_rad = wrap_to_pi(
                phase_rad - self.previous_phase_rad
            )
            self.unwrapped_phase_rad += delta_phase_rad
            self.previous_phase_rad = phase_rad

        fringe_position = self.unwrapped_phase_rad / (2 * math.pi)
        new_signed_fringes = completed_signed_fringes(fringe_position)
        fringe_delta = new_signed_fringes - self.signed_fringes

        if fringe_delta != 0:
            self.total_abs_fringes += abs(fringe_delta)

        self.signed_fringes = new_signed_fringes

        if delta_phase_rad > 0:
            direction = "forward"
        elif delta_phase_rad < 0:
            direction = "backward"
        else:
            direction = "none"

        return HomodyneSample(
            timestamp=timestamp,
            raw_s1=raw_s1,
            raw_s2=raw_s2,
            raw_ref=raw_ref,
            ref_corrected_s1=ref_corrected_s1,
            ref_corrected_s2=ref_corrected_s2,
            s1=s1,
            s2=s2,
            radius=radius,
            phase_rad=phase_rad,
            unwrapped_phase_rad=self.unwrapped_phase_rad,
            delta_phase_rad=delta_phase_rad,
            fringe_position=fringe_position,
            signed_fringes=self.signed_fringes,
            fringe_delta=fringe_delta,
            direction=direction,
            valid=True
        )

    def signed_distance_mm(self):
        if self.fringe_distance_mm is None:
            return None

        return (
            self.unwrapped_phase_rad
            / (2 * math.pi)
            * self.fringe_distance_mm
        )

    def correction_to_zero_mm(self, stage_direction_sign=1):
        distance_mm = self.signed_distance_mm()

        if distance_mm is None:
            return None

        return -stage_direction_sign * distance_mm


class HomodyneMonitor:
    def __init__(
        self,
        channel_s1=PHOTODIODE_CHANNEL_S1,
        channel_s2=PHOTODIODE_CHANNEL_S2,
        channel_ref=REFERENCE_CHANNEL,
        wavelength_nm=LASER_WAVELENGTH_NM,
        phase_direction_sign=PHASE_DIRECTION_SIGN
    ):
        fringe_distance_mm = compute_fringe_distance_mm(wavelength_nm)
        self.reader = NIPhotodiodeReader(channel_s1, channel_s2, channel_ref)
        self.counter = HomodyneQuadratureCounter(
            phase_direction_sign=phase_direction_sign,
            fringe_distance_mm=fringe_distance_mm
        )

    def connect(self):
        return self.reader.connect()

    def calibrate(
        self,
        seconds=CALIBRATION_SECONDS,
        sample_interval_s=SAMPLE_INTERVAL_S,
        should_continue=None
    ):
        samples = []
        start_time = time.time()

        while time.time() - start_time < seconds:
            if should_continue is not None and not should_continue():
                break

            samples.append(self.reader.read())
            time.sleep(sample_interval_s)

        if not samples and should_continue is not None and not should_continue():
            return samples

        self.counter.calibrate_from_samples(samples)
        return samples

    def read(self):
        raw_s1, raw_s2, raw_ref = self.reader.read()
        return self.counter.update(raw_s1, raw_s2, raw_ref)

    def close(self):
        self.reader.close()


class HomodyneGui:
    def __init__(self):
        if ctk is None:
            raise RuntimeError(
                "customtkinter is not installed. Install requirements.txt first."
            )

        ctk.set_appearance_mode("light")

        self.root = ctk.CTk()
        self.root.title("Homodyne Quadrature Monitor")
        self.root.geometry("700x900")
        self.root.configure(fg_color="white")

        self.scroll = ctk.CTkScrollableFrame(
            self.root,
            fg_color="white"
        )
        self.scroll.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2
        )

        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
        self.fringe_distance_mm = compute_fringe_distance_mm(
            self.laser_wavelength_nm
        )
        self.stage_step_mm = self.fringe_distance_mm / 4

        self.monitor = HomodyneMonitor(
            wavelength_nm=self.laser_wavelength_nm
        )
        self.monitoring = False
        self.measurement_thread = None
        self.raw_s1_history = []
        self.raw_s2_history = []
        self.raw_ref_history = []
        self.sample_display_lock = threading.Lock()
        self.pending_sample = None
        self.pending_distance_mm = None
        self.sample_display_scheduled = False
        self.last_sample_display_time = 0.0

        self.stage = StageController() if StageController is not None else None
        self.stage_connected = False
        self.stage_connecting = False
        self.stage_position_mm = None
        self.stage_command_active = False

        self.latest_sample = None
        self.latest_distance_mm = None
        self.last_error_text = None

        self.lock_active = False
        self.lock_reference_distance_mm = 0.0
        self.lock_reference_phase_rad = 0.0
        self.lock_reference_fringes = 0
        self.lock_correction_active = False
        self.lock_last_correction_time = 0.0
        self.lock_target_position_mm = None

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        ctk.CTkLabel(
            self.scroll,
            text="Homodyne Quadrature Monitor",
            font=("Arial", 23, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(16, 8))

        self.status = ctk.CTkLabel(
            self.scroll,
            text="Status: stopped",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.status.pack(pady=(0, 12))

        control_frame = ctk.CTkFrame(self.scroll, fg_color="#EEEEEE")
        control_frame.pack(fill="x", padx=18, pady=8)

        self.btn_start = ctk.CTkButton(
            control_frame,
            text="START MONITORING",
            width=180,
            command=self.toggle_monitoring,
            fg_color=TEXT_COLOR,
            font=("Arial", 12, "bold")
        )
        self.btn_start.grid(row=0, column=0, padx=12, pady=14)

        self.btn_lock = ctk.CTkButton(
            control_frame,
            text="LOCK",
            width=140,
            command=self.toggle_lock,
            fg_color=TEXT_COLOR,
            font=("Arial", 12, "bold")
        )
        self.btn_lock.grid(row=0, column=1, padx=12, pady=14)

        self.btn_reset = ctk.CTkButton(
            control_frame,
            text="RESET",
            width=140,
            command=self.reset_monitor,
            fg_color=ORANGE_COLOR,
            font=("Arial", 12, "bold")
        )
        self.btn_reset.grid(row=0, column=2, padx=12, pady=14)

        settings_frame = ctk.CTkFrame(self.scroll, fg_color="#EEEEEE")
        settings_frame.pack(fill="x", padx=18, pady=8)

        ctk.CTkLabel(
            settings_frame,
            text="Stage and Interferometer Settings",
            font=("Arial", 16, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(10, 4))

        wavelength_row = ctk.CTkFrame(
            settings_frame,
            fg_color="transparent"
        )
        wavelength_row.pack(fill="x", padx=18, pady=4)

        ctk.CTkLabel(
            wavelength_row,
            text="Laser wavelength in nm:",
            width=180,
            anchor="w",
            font=("Arial", 12, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        self.wavelength_entry = ctk.CTkEntry(
            wavelength_row,
            width=120
        )
        self.wavelength_entry.pack(side="left", padx=(0, 8))
        self.wavelength_entry.insert(
            0,
            f"{self.laser_wavelength_nm:.1f}"
        )

        self.btn_apply_wavelength = ctk.CTkButton(
            wavelength_row,
            text="Set",
            width=70,
            command=self.apply_wavelength,
            fg_color=TEXT_COLOR
        )
        self.btn_apply_wavelength.pack(side="left")

        self.label_fringe_distance = ctk.CTkLabel(
            settings_frame,
            text=self.fringe_distance_text(),
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_fringe_distance.pack(pady=2)

        step_row = ctk.CTkFrame(
            settings_frame,
            fg_color="transparent"
        )
        step_row.pack(fill="x", padx=18, pady=4)

        ctk.CTkLabel(
            step_row,
            text="Stage step size in mm:",
            width=180,
            anchor="w",
            font=("Arial", 12, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        self.step_entry = ctk.CTkEntry(
            step_row,
            width=120
        )
        self.step_entry.pack(side="left", padx=(0, 8))
        self.step_entry.insert(
            0,
            f"{self.stage_step_mm:.9f}"
        )

        self.btn_apply_step_size = ctk.CTkButton(
            step_row,
            text="Set",
            width=70,
            command=self.apply_stage_step_size,
            fg_color=TEXT_COLOR
        )
        self.btn_apply_step_size.pack(side="left")

        step_button_row = ctk.CTkFrame(
            settings_frame,
            fg_color="transparent"
        )
        step_button_row.pack(pady=(4, 10))

        self.btn_stage_step_negative = ctk.CTkButton(
            step_button_row,
            text="STEP -",
            width=90,
            command=lambda: self.move_stage_step(-1),
            fg_color=TEXT_COLOR
        )
        self.btn_stage_step_negative.grid(row=0, column=0, padx=5)

        self.btn_stage_center = ctk.CTkButton(
            step_button_row,
            text="0",
            width=90,
            command=self.move_stage_to_center,
            fg_color=TEXT_COLOR
        )
        self.btn_stage_center.grid(row=0, column=1, padx=5)

        self.btn_stage_step_positive = ctk.CTkButton(
            step_button_row,
            text="STEP +",
            width=90,
            command=lambda: self.move_stage_step(1),
            fg_color=TEXT_COLOR
        )
        self.btn_stage_step_positive.grid(row=0, column=2, padx=5)

        self.btn_stage_check = ctk.CTkButton(
            step_button_row,
            text="CHECK",
            width=90,
            command=self.start_stage_motion_check,
            fg_color=TEXT_COLOR
        )
        self.btn_stage_check.grid(row=0, column=3, padx=5)

        row_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row_frame.pack(fill="x", padx=18, pady=8)

        values_frame = ctk.CTkFrame(row_frame, fg_color="#EEEEEE")
        values_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        lock_frame = ctk.CTkFrame(row_frame, fg_color="#EEEEEE")
        lock_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self.label_phase = self.make_value_label(
            values_frame,
            "Unwrapped phase",
            "0.00000 rad"
        )
        self.label_fringe_position = self.make_value_label(
            values_frame,
            "Fringe position",
            "0.0000"
        )
        self.label_fringes = self.make_value_label(
            values_frame,
            "Completed fringes",
            "0"
        )
        self.label_direction = self.make_value_label(
            values_frame,
            "Direction",
            "none"
        )
        self.label_distance = self.make_value_label(
            values_frame,
            "Distance",
            "0.000000 um / 0.000000000 mm"
        )

        ctk.CTkLabel(
            lock_frame,
            text="Lock",
            font=("Arial", 16, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(10, 4))

        self.label_lock_status = ctk.CTkLabel(
            lock_frame,
            text="Lock: off",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_lock_status.pack(pady=2)

        self.label_lock_reference = ctk.CTkLabel(
            lock_frame,
            text="Reference: n/a",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_lock_reference.pack(pady=2)

        self.label_lock_drift = ctk.CTkLabel(
            lock_frame,
            text="Drift: n/a",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_lock_drift.pack(pady=2)

        self.label_lock_correction = ctk.CTkLabel(
            lock_frame,
            text="Correction to lock: n/a",
            font=("Arial", 12, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_lock_correction.pack(pady=(2, 10))

        self.label_stage_status = ctk.CTkLabel(
            lock_frame,
            text="Stage: not connected",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_stage_status.pack(pady=2)

        self.label_stage_position = ctk.CTkLabel(
            lock_frame,
            text="Stage position: n/a",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_stage_position.pack(pady=(2, 10))

        calculation_frame = ctk.CTkFrame(self.scroll, fg_color="#EEEEEE")
        calculation_frame.pack(fill="x", padx=18, pady=8)

        ctk.CTkLabel(
            calculation_frame,
            text="Live calculations",
            font=("Arial", 16, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(10, 4))

        self.label_calc_s1 = self.make_formula_label(
            calculation_frame,
            (
                "S1_ref = raw_S1 / raw_ref = n/a; "
                "S1_norm = (S1_ref - offset_S1) / scale_S1 = n/a"
            )
        )
        self.label_calc_s2 = self.make_formula_label(
            calculation_frame,
            (
                "S2_ref = raw_S2 / raw_ref = n/a; "
                "S2_norm = (S2_ref - offset_S2) / scale_S2 = n/a"
            )
        )
        self.label_calc_phase = self.make_formula_label(
            calculation_frame,
            "phase_rad = atan2(S2_norm, S1_norm) = n/a"
        )
        self.label_calc_unwrapped = self.make_formula_label(
            calculation_frame,
            "unwrapped_phase_rad += wrap(delta_phase_rad) = 0.00000 rad"
        )
        self.label_calc_fringe = self.make_formula_label(
            calculation_frame,
            "fringe_position = unwrapped_phase_rad / (2*pi) = 0.0000"
        )
        self.label_calc_distance = self.make_formula_label(
            calculation_frame,
            "distance_mm = fringe_position * fringe_distance_mm = n/a"
        )

        channel_text = (
            f"Channels: S1={PHOTODIODE_CHANNEL_S1}, "
            f"S2={PHOTODIODE_CHANNEL_S2}, "
            f"Ref={REFERENCE_CHANNEL}"
        )
        ctk.CTkLabel(
            self.scroll,
            text=channel_text,
            font=("Arial", 10),
            text_color=TEXT_COLOR
        ).pack(pady=(8, 0))

        plot_frame = ctk.CTkFrame(self.scroll, fg_color="#EEEEEE")
        plot_frame.pack(fill="both", padx=18, pady=(8, 16), expand=True)

        ctk.CTkLabel(
            plot_frame,
            text="Live outputs",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(10, 4))

        if plt is None or FigureCanvasTkAgg is None:
            ctk.CTkLabel(
                plot_frame,
                text="Matplotlib is required for live plotting.",
                font=("Arial", 11),
                text_color=RED_COLOR
            ).pack(pady=8)
            self.plot_canvas = None
            self.plot_axis = None
        else:
            self.plot_figure = plt.Figure(figsize=(8, 3.2), dpi=100)
            self.plot_axis = self.plot_figure.add_subplot(111)

            self.plot_axis.set_title("Raw voltage")
            self.plot_axis.grid(True, linestyle=':', alpha=0.6)
            self.plot_axis.set_ylabel("Voltage")
            self.plot_axis.set_xlabel("Samples")

            self.plot_lines = {
                'S1_raw': self.plot_axis.plot([], [], color='blue', label='S1')[0],
                'S2_raw': self.plot_axis.plot([], [], color='green', label='S2')[0],
                'Ref_raw': self.plot_axis.plot([], [], color='red', label='Ref')[0]
            }
            self.plot_axis.legend(loc="upper right")
            self.plot_figure.tight_layout()
            self.plot_canvas = FigureCanvasTkAgg(
                self.plot_figure,
                master=plot_frame
            )
            self.plot_canvas.draw()
            self.plot_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def make_value_label(self, parent, name, initial_value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=5)

        ctk.CTkLabel(
            row,
            text=f"{name}:",
            width=180,
            anchor="w",
            font=("Arial", 12, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        label = ctk.CTkLabel(
            row,
            text=initial_value,
            anchor="w",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        label.pack(side="left", fill="x", expand=True)
        return label

    def make_formula_label(self, parent, text):
        label = ctk.CTkLabel(
            parent,
            text=text,
            anchor="w",
            justify="left",
            wraplength=620,
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        label.pack(fill="x", padx=18, pady=2)
        return label

    def fringe_distance_text(self):
        return (
            f"Fringe distance: {self.fringe_distance_mm:.9f} mm "
            f"({self.fringe_distance_mm * 1000:.6f} um)"
        )

    def parse_entry_float(self, entry):
        return float(entry.get().replace(",", "."))

    def apply_wavelength(self):
        if self.lock_active:
            self.status.configure(
                text="Status: unlock before changing wavelength",
                text_color=ORANGE_COLOR
            )
            return

        try:
            wavelength_nm = self.parse_entry_float(self.wavelength_entry)
        except ValueError:
            self.status.configure(
                text="Status: invalid wavelength value",
                text_color=RED_COLOR
            )
            return

        if wavelength_nm <= 0:
            self.status.configure(
                text="Status: wavelength must be positive",
                text_color=RED_COLOR
            )
            return

        self.laser_wavelength_nm = wavelength_nm
        self.fringe_distance_mm = compute_fringe_distance_mm(
            self.laser_wavelength_nm
        )
        self.stage_step_mm = self.fringe_distance_mm / 4

        self.monitor.counter.fringe_distance_mm = self.fringe_distance_mm

        self.label_fringe_distance.configure(
            text=self.fringe_distance_text()
        )
        self.step_entry.delete(0, "end")
        self.step_entry.insert(
            0,
            f"{self.stage_step_mm:.9f}"
        )

        self.status.configure(
            text=(
                f"Status: wavelength set to "
                f"{self.laser_wavelength_nm:.1f} nm"
            ),
            text_color=GREEN_COLOR
        )

    def apply_stage_step_size(self):
        try:
            step_mm = self.parse_entry_float(self.step_entry)
        except ValueError:
            self.status.configure(
                text="Status: invalid stage step size",
                text_color=RED_COLOR
            )
            return

        step_mm = abs(step_mm)

        if step_mm <= 0:
            self.status.configure(
                text="Status: stage step size must be positive",
                text_color=RED_COLOR
            )
            return

        self.stage_step_mm = step_mm
        self.step_entry.delete(0, "end")
        self.step_entry.insert(
            0,
            f"{self.stage_step_mm:.9f}"
        )

        self.status.configure(
            text=f"Status: stage step set to {self.stage_step_mm:.9f} mm",
            text_color=GREEN_COLOR
        )

    def limited_stage_correction_mm(self, correction_mm):
        if self.stage_step_mm <= 0:
            return correction_mm

        sign = 1 if correction_mm >= 0 else -1
        return sign * min(abs(correction_mm), self.stage_step_mm)

    def set_stage_controls_enabled(self, enabled):
        state = "normal" if enabled else "disabled"

        for button in (
            self.btn_stage_step_negative,
            self.btn_stage_center,
            self.btn_stage_step_positive,
            self.btn_stage_check
        ):
            button.configure(state=state)

    def finish_stage_command_ui(self):
        self.stage_command_active = False
        self.set_stage_controls_enabled(True)

    def queue_sample_display(self, sample, distance_mm, force=False):
        with self.sample_display_lock:
            self.pending_sample = sample
            self.pending_distance_mm = distance_mm

            if self.sample_display_scheduled:
                return

            now = time.monotonic()
            elapsed_s = now - self.last_sample_display_time
            delay_s = 0.0 if force else max(
                0.0,
                UI_UPDATE_INTERVAL_S - elapsed_s
            )
            self.sample_display_scheduled = True

        self.root.after(
            int(delay_s * 1000),
            self.flush_sample_display
        )

    def flush_sample_display(self):
        with self.sample_display_lock:
            sample = self.pending_sample
            distance_mm = self.pending_distance_mm
            self.pending_sample = None
            self.pending_distance_mm = None
            self.sample_display_scheduled = False

        self.last_sample_display_time = time.monotonic()

        if sample is not None:
            self.update_sample_display(sample, distance_mm)

    def set_status_from_thread(self, text, color=TEXT_COLOR):
        self.root.after(
            0,
            lambda:
            self.status.configure(
                text=text,
                text_color=color
            )
        )

    def set_stage_status_from_thread(self, text, color=TEXT_COLOR):
        self.root.after(
            0,
            lambda:
            self.label_stage_status.configure(
                text=text,
                text_color=color
            )
        )

    def set_stage_position_from_thread(self, position_mm):
        self.root.after(
            0,
            lambda p=position_mm:
            self.label_stage_position.configure(
                text=f"Stage position: {p:.9f} mm"
            ) if p is not None else None
        )

    def wait_for_stage_motion(self, timeout_s=STAGE_MOVE_TIMEOUT_S):
        start_time = time.monotonic()
        last_position_update_s = 0.0

        while self.stage is not None and self.stage.is_moving:
            if time.monotonic() - start_time > timeout_s:
                self.stage.stop()
                raise RuntimeError("stage move timeout")

            position_mm = self.stage.current_position
            now = time.monotonic()

            if now - last_position_update_s >= STAGE_POLL_INTERVAL_S:
                self.set_stage_position_from_thread(position_mm)
                last_position_update_s = now

            time.sleep(STAGE_POLL_INTERVAL_S)

        if self.stage is None or not self.stage_connected:
            return None

        position_mm = self.stage.get_position()
        self.set_stage_position_from_thread(position_mm)
        return position_mm

    def stage_move_observed(self, before_mm, after_mm, expected_delta_mm):
        if after_mm is None:
            return False

        actual_delta_mm = after_mm - before_mm
        tolerance_mm = max(
            STAGE_VERIFY_TOLERANCE_MM,
            abs(expected_delta_mm) * 0.2
        )

        if abs(actual_delta_mm) < tolerance_mm:
            return False

        if expected_delta_mm * actual_delta_mm < 0:
            return False

        return True

    def toggle_monitoring(self):
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        if (
            self.measurement_thread is not None
            and self.measurement_thread.is_alive()
        ):
            return

        self.monitor = HomodyneMonitor(
            wavelength_nm=self.laser_wavelength_nm
        )
        self.monitoring = True
        self.latest_sample = None
        self.latest_distance_mm = None
        self.last_error_text = None
        self.raw_s1_history = []
        self.raw_s2_history = []
        self.raw_ref_history = []
        with self.sample_display_lock:
            self.pending_sample = None
            self.pending_distance_mm = None
            self.sample_display_scheduled = False
        self.last_sample_display_time = 0.0
        self.reset_calculation_display()
        self.disable_lock(update_status=False)

        self.btn_start.configure(
            text="STOP MONITORING",
            fg_color=RED_COLOR
        )
        self.status.configure(
            text="Status: connecting NI...",
            text_color=ORANGE_COLOR
        )

        self.start_stage_connection()

        self.measurement_thread = threading.Thread(
            target=self.measurement_loop,
            daemon=True
        )
        self.measurement_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        self.disable_lock(update_status=False)
        self.stop_stage_correction()
        self.status.configure(
            text="Status: stopping...",
            text_color=ORANGE_COLOR
        )

    def start_stage_connection(self):
        if self.stage is None:
            self.label_stage_status.configure(
                text=f"Stage: unavailable ({STAGE_IMPORT_ERROR})",
                text_color=RED_COLOR
            )
            return

        if self.stage_connected or self.stage_connecting:
            return

        self.stage_connecting = True
        self.label_stage_status.configure(
            text="Stage: connecting...",
            text_color=ORANGE_COLOR
        )

        threading.Thread(
            target=self.stage_connection_worker,
            daemon=True
        ).start()

    def stage_connection_worker(self):
        connected = False
        position_mm = None

        try:
            connected = self.stage.connect()

            if connected:
                position_mm = self.stage.get_position()

        except Exception as error:
            self.root.after(
                0,
                lambda e=error:
                self.finish_stage_connection(False, None, str(e))
            )
            return

        self.root.after(
            0,
            lambda c=connected, p=position_mm:
            self.finish_stage_connection(c, p, None)
        )

    def finish_stage_connection(self, connected, position_mm, error_text):
        self.stage_connecting = False
        self.stage_connected = connected
        self.stage_position_mm = position_mm

        if connected:
            self.label_stage_status.configure(
                text="Stage: connected",
                text_color=GREEN_COLOR
            )
            self.label_stage_position.configure(
                text=f"Stage position: {position_mm:.9f} mm"
            )
        else:
            if error_text is None:
                error_text = "no PI stage found"

            self.label_stage_status.configure(
                text=f"Stage: not connected ({error_text})",
                text_color=RED_COLOR
            )
            self.label_stage_position.configure(
                text="Stage position: n/a"
            )

    def move_stage_step(self, direction):
        if self.lock_active:
            self.status.configure(
                text="Status: unlock before manual stage movement",
                text_color=ORANGE_COLOR
            )
            return

        if self.stage is None:
            self.label_stage_status.configure(
                text=f"Stage: unavailable ({STAGE_IMPORT_ERROR})",
                text_color=RED_COLOR
            )
            return

        if not self.stage_connected:
            self.start_stage_connection()
            self.status.configure(
                text="Status: wait for stage connection",
                text_color=ORANGE_COLOR
            )
            return

        if (
            self.stage_command_active
            or self.stage.is_moving
            or self.lock_correction_active
        ):
            self.status.configure(
                text="Status: stage is already moving",
                text_color=ORANGE_COLOR
            )
            return

        self.start_stage_move_by_steps(direction * self.stage_step_mm)

    def manual_stage_move_worker(self):
        while self.stage is not None and self.stage.is_moving:
            position_mm = self.stage.current_position

            self.root.after(
                0,
                lambda p=position_mm:
                self.label_stage_position.configure(
                    text=f"Stage position: {p:.9f} mm"
                )
            )

            time.sleep(0.05)

        position_mm = None

        if self.stage is not None and self.stage_connected:
            position_mm = self.stage.get_position()

        self.root.after(
            0,
            lambda p=position_mm:
            self.finish_manual_stage_move(p)
        )

    def finish_manual_stage_move(self, position_mm):
        if position_mm is not None:
            self.stage_position_mm = position_mm
            self.label_stage_position.configure(
                text=f"Stage position: {position_mm:.9f} mm"
            )

        self.label_stage_status.configure(
            text="Stage: connected",
            text_color=GREEN_COLOR
        )
        self.status.configure(
            text="Status: stage step done",
            text_color=GREEN_COLOR
        )

    def move_stage_to_center(self):
        if self.lock_active:
            self.status.configure(
                text="Status: unlock before manual stage movement",
                text_color=ORANGE_COLOR
            )
            return

        if self.stage is None:
            self.label_stage_status.configure(
                text=f"Stage: unavailable ({STAGE_IMPORT_ERROR})",
                text_color=RED_COLOR
            )
            return

        if not self.stage_connected:
            self.start_stage_connection()
            self.status.configure(
                text="Status: wait for stage connection",
                text_color=ORANGE_COLOR
            )
            return

        if (
            self.stage_command_active
            or self.stage.is_moving
            or self.lock_correction_active
        ):
            self.status.configure(
                text="Status: stage is already moving",
                text_color=ORANGE_COLOR
            )
            return

        self.start_stage_move_to_stepped(0.0)

    def start_stage_move_to_stepped(self, target_mm):
        if self.stage is None or not self.stage_connected:
            self.label_stage_status.configure(
                text=f"Stage: unavailable ({STAGE_IMPORT_ERROR})",
                text_color=RED_COLOR
            )
            self.status.configure(
                text="Status: stage not connected",
                text_color=RED_COLOR
            )
            return

        if self.lock_active:
            self.status.configure(
                text="Status: unlock before manual stage movement",
                text_color=ORANGE_COLOR
            )
            return

        if self.stage_command_active or self.stage.is_moving:
            self.status.configure(
                text="Status: stage is already moving",
                text_color=ORANGE_COLOR
            )
            return

        start_pos = self.stage.get_position()
        target_mm = self.stage.clamp_position(target_mm)

        if abs(target_mm - start_pos) < 1e-12:
            self.status.configure(
                text="Status: stage already at target",
                text_color=TEXT_COLOR
            )
            self.label_stage_position.configure(
                text=f"Stage position: {start_pos:.9f} mm"
            )
            return

        self.stage_command_active = True
        self.set_stage_controls_enabled(False)

        threading.Thread(
            target=self.stage_stepped_move_worker,
            args=(start_pos, target_mm),
            daemon=True
        ).start()

    def start_stage_move_by_steps(self, move_mm):
        if self.stage is None or not self.stage_connected:
            self.status.configure(
                text="Status: stage not connected",
                text_color=RED_COLOR
            )
            return

        self.start_stage_move_to_stepped(
            self.stage.get_position() + move_mm
        )

    def start_stage_motion_check(self):
        if self.monitoring:
            self.status.configure(
                text="Status: stop monitoring before stage check",
                text_color=ORANGE_COLOR
            )
            return

        if self.lock_active:
            self.status.configure(
                text="Status: unlock before stage check",
                text_color=ORANGE_COLOR
            )
            return

        if self.stage is None:
            self.label_stage_status.configure(
                text=f"Stage: unavailable ({STAGE_IMPORT_ERROR})",
                text_color=RED_COLOR
            )
            return

        if not self.stage_connected:
            self.start_stage_connection()
            self.status.configure(
                text="Status: wait for stage connection, then press CHECK",
                text_color=ORANGE_COLOR
            )
            return

        if (
            self.stage_command_active
            or self.lock_correction_active
            or self.stage.is_moving
        ):
            self.status.configure(
                text="Status: stage is already moving",
                text_color=ORANGE_COLOR
            )
            return

        self.stage_command_active = True
        self.set_stage_controls_enabled(False)

        threading.Thread(
            target=self.stage_motion_check_worker,
            daemon=True
        ).start()

    def stage_motion_check_worker(self):
        try:
            self.set_stage_status_from_thread(
                "Stage: checking motion...",
                ORANGE_COLOR
            )

            if not self.stage.update_travel_limits():
                self.set_status_from_thread(
                    "Status: could not read stage limits",
                    RED_COLOR
                )
                return

            min_pos = self.stage.min_position
            max_pos = self.stage.max_position
            zero_pos = self.stage.clamp_position(0.0)
            travel_mm = abs(max_pos - min_pos)
            target_tolerance_mm = max(
                STAGE_VERIFY_TOLERANCE_MM,
                travel_mm * 1e-6
            )

            if travel_mm <= target_tolerance_mm:
                self.set_status_from_thread(
                    "Status: invalid stage travel limits",
                    RED_COLOR
                )
                return

            observed_positions = [self.stage.get_position()]

            for label, target_pos in (
                ("minimum", min_pos),
                ("maximum", max_pos),
                ("zero", zero_pos)
            ):
                before_pos = self.stage.get_position()
                self.set_status_from_thread(
                    (
                        f"Status: stage check moving to {label} "
                        f"({target_pos:.9f} mm)"
                    ),
                    ORANGE_COLOR
                )

                if abs(target_pos - before_pos) > target_tolerance_mm:
                    if not self.stage.move_absolute(target_pos):
                        self.set_status_from_thread(
                            "Status: stage check move failed",
                            RED_COLOR
                        )
                        return

                    try:
                        after_pos = self.wait_for_stage_motion(
                            timeout_s=STAGE_CHECK_TIMEOUT_S
                        )
                    except RuntimeError as error:
                        self.set_status_from_thread(
                            f"Status: {error}",
                            RED_COLOR
                        )
                        return
                else:
                    after_pos = before_pos
                    self.set_stage_position_from_thread(after_pos)

                if after_pos is None:
                    self.set_status_from_thread(
                        "Status: could not read stage position",
                        RED_COLOR
                    )
                    return

                observed_positions.append(after_pos)

                if abs(after_pos - target_pos) > target_tolerance_mm:
                    self.set_status_from_thread(
                        (
                            f"Status: stage did not reach {label} "
                            f"(target {target_pos:.9f} mm, "
                            f"actual {after_pos:.9f} mm)"
                        ),
                        RED_COLOR
                    )
                    return

            observed_travel_mm = max(observed_positions) - min(observed_positions)

            if observed_travel_mm < travel_mm * 0.8:
                self.set_status_from_thread(
                    (
                        "Status: stage check failed, observed travel only "
                        f"{observed_travel_mm:.9f} mm"
                    ),
                    RED_COLOR
                )
                return

            self.set_stage_status_from_thread(
                "Stage: verified",
                GREEN_COLOR
            )
            self.set_status_from_thread(
                (
                    "Status: stage check OK "
                    f"({min_pos:.6f} -> {max_pos:.6f} -> {zero_pos:.6f} mm)"
                ),
                GREEN_COLOR
            )

        finally:
            self.root.after(
                0,
                self.finish_stage_command_ui
            )

    def perform_post_calibration_scan(self, steps=30, pause_s=0.05):
        if self.stage is None or not self.stage_connected:
            self.root.after(
                0,
                lambda:
                self.status.configure(
                    text="Status: stage not available for post-calibration scan",
                    text_color=ORANGE_COLOR
                )
            )
            return

        if (
            self.lock_active
            or self.lock_correction_active
            or self.stage_command_active
            or self.stage.is_moving
        ):
            self.root.after(
                0,
                lambda:
                self.status.configure(
                    text="Status: cannot run post-calibration scan while lock or move is active",
                    text_color=ORANGE_COLOR
                )
            )
            return

        self.root.after(
            0,
            lambda:
            self.status.configure(
                text=f"Status: running {steps} post-calibration steps",
                text_color=TEXT_COLOR
            )
        )

        for step_index in range(steps):
            if not self.monitoring:
                break

            current_pos = self.stage.get_position()
            if current_pos is None:
                break

            target_pos = self.stage.clamp_position(
                current_pos + self.stage_step_mm
            )

            if abs(target_pos - current_pos) < 1e-12:
                break

            if not self.stage.move_absolute(target_pos):
                self.root.after(
                    0,
                    lambda:
                    self.status.configure(
                        text="Status: stage move failed during sweep",
                        text_color=RED_COLOR
                    )
                )
                break

            while self.stage.is_moving and self.monitoring:
                try:
                    sample = self.monitor.read()
                    distance_mm = self.monitor.counter.signed_distance_mm()
                except Exception:
                    sample = None
                    distance_mm = None

                if sample is not None:
                    self.queue_sample_display(sample, distance_mm)

                time.sleep(SAMPLE_INTERVAL_S)

            position_mm = self.stage.get_position()
            self.root.after(
                0,
                lambda p=position_mm:
                self.label_stage_position.configure(
                    text=f"Stage position: {p:.9f} mm"
                ) if p is not None else None
            )

            if not self.monitoring:
                break

            time.sleep(pause_s)

        self.root.after(
            0,
            lambda:
            self.status.configure(
                text="Status: post-calibration scan complete",
                text_color=GREEN_COLOR
            )
        )

    def stage_stepped_move_worker(self, start_pos, target_mm):
        step_mm = abs(self.stage_step_mm)
        if step_mm <= 0:
            step_mm = 1e-6

        delay_s = 0.25
        direction = 1 if target_mm > start_pos else -1
        current_pos = start_pos
        remaining = abs(target_mm - start_pos)
        max_steps = max(1, int(math.ceil(remaining / step_mm)) + 5)

        self.set_status_from_thread(
            (
                f"Status: moving to {target_mm:.9f} mm "
                f"in {step_mm:.9f} mm steps"
            ),
            TEXT_COLOR
        )

        try:
            for _ in range(max_steps):
                if remaining <= STAGE_VERIFY_TOLERANCE_MM:
                    break

                next_step = min(step_mm, remaining)
                next_target = self.stage.clamp_position(
                    current_pos + direction * next_step
                )
                expected_delta = next_target - current_pos

                if abs(expected_delta) <= STAGE_VERIFY_TOLERANCE_MM:
                    break

                if not self.stage.move_absolute(next_target):
                    self.set_status_from_thread(
                        "Status: stage move failed",
                        RED_COLOR
                    )
                    return

                try:
                    actual_pos = self.wait_for_stage_motion()
                except RuntimeError as error:
                    self.set_status_from_thread(
                        f"Status: {error}",
                        RED_COLOR
                    )
                    return

                if actual_pos is None:
                    self.set_status_from_thread(
                        "Status: could not read stage position",
                        RED_COLOR
                    )
                    return

                if not self.stage_move_observed(
                    current_pos,
                    actual_pos,
                    expected_delta
                ):
                    actual_delta = actual_pos - current_pos
                    self.set_status_from_thread(
                        (
                            "Status: stage did not follow command "
                            f"(command {expected_delta:+.9f} mm, "
                            f"actual {actual_delta:+.9f} mm)"
                        ),
                        RED_COLOR
                    )
                    return

                current_pos = actual_pos
                remaining = abs(target_mm - current_pos)

                if remaining > STAGE_VERIFY_TOLERANCE_MM:
                    time.sleep(delay_s)

            if remaining > STAGE_VERIFY_TOLERANCE_MM:
                self.set_status_from_thread(
                    (
                        "Status: stage target not reached "
                        f"(at {current_pos:.9f} mm, "
                        f"target {target_mm:.9f} mm)"
                    ),
                    RED_COLOR
                )
                return

            self.set_status_from_thread(
                f"Status: reached {current_pos:.9f} mm",
                GREEN_COLOR
            )
        finally:
            self.root.after(
                0,
                self.finish_stage_command_ui
            )

    def measurement_loop(self):
        try:
            self.monitor.connect()

            self.root.after(
                0,
                lambda:
                self.status.configure(
                    text=(
                        f"Status: calibrating "
                        f"{CALIBRATION_SECONDS:.1f}s..."
                    ),
                    text_color=ORANGE_COLOR
                )
            )

            self.monitor.calibrate(
                should_continue=lambda: self.monitoring
            )

            if not self.monitoring:
                return

            self.root.after(
                0,
                lambda:
                self.status.configure(
                    text="Status: monitoring running",
                    text_color=GREEN_COLOR
                )
            )

            while self.monitoring:
                sample = self.monitor.read()
                distance_mm = self.monitor.counter.signed_distance_mm()

                self.queue_sample_display(sample, distance_mm)

                time.sleep(SAMPLE_INTERVAL_S)

        except Exception as error:
            self.last_error_text = str(error)
            self.root.after(
                0,
                lambda e=error:
                self.show_error(e)
            )

        finally:
            self.monitoring = False
            self.monitor.close()
            self.root.after(0, self.finish_stopped_ui)

    def update_sample_display(self, sample, distance_mm):
        self.latest_sample = sample
        self.latest_distance_mm = distance_mm

        self.raw_s1_history.append(sample.raw_s1)
        self.raw_s2_history.append(sample.raw_s2)
        self.raw_ref_history.append(sample.raw_ref)

        if len(self.raw_s1_history) > 300:
            self.raw_s1_history.pop(0)
            self.raw_s2_history.pop(0)
            self.raw_ref_history.pop(0)

        self.update_plot()

        self.label_phase.configure(
            text=f"{sample.unwrapped_phase_rad:+.5f} rad"
        )
        self.label_fringe_position.configure(
            text=f"{sample.fringe_position:+.4f}"
        )
        self.label_fringes.configure(
            text=f"{sample.signed_fringes:+d}"
        )
        self.label_direction.configure(
            text=sample.direction
        )

        if distance_mm is None:
            self.label_distance.configure(text="n/a")
        else:
            distance_um = distance_mm * 1000
            self.label_distance.configure(
                text=f"{distance_um:+.6f} um / {distance_mm:+.9f} mm"
            )

        self.update_calculation_display(sample, distance_mm)

        if sample.fringe_delta != 0:
            self.label_fringes.configure(text_color=GREEN_COLOR)
            self.root.after(
                250,
                lambda:
                self.label_fringes.configure(text_color=TEXT_COLOR)
            )

        self.update_lock_display(sample, distance_mm)

    def update_calculation_display(self, sample, distance_mm):
        counter = self.monitor.counter
        phase_formula = "atan2(S2_norm, S1_norm)"

        if counter.phase_direction_sign < 0:
            phase_formula = f"-{phase_formula}"

        if sample.direction == "reference_low":
            self.label_calc_s1.configure(
                text=(
                    "S1_ref = raw_S1 / raw_ref not computed because "
                    f"raw_ref = {sample.raw_ref:+.6f}"
                )
            )
            self.label_calc_s2.configure(
                text=(
                    "S2_ref = raw_S2 / raw_ref not computed because "
                    f"raw_ref = {sample.raw_ref:+.6f}"
                )
            )
        else:
            self.label_calc_s1.configure(
                text=(
                    "S1_ref = "
                    f"{sample.raw_s1:+.6f} / {sample.raw_ref:+.6f} "
                    f"= {sample.ref_corrected_s1:+.6f}; "
                    "S1_norm = "
                    f"({sample.ref_corrected_s1:+.6f} - "
                    f"{counter.offset_s1:+.6f}) "
                    f"/ {counter.scale_s1:.6f} = {sample.s1:+.6f}"
                )
            )
            self.label_calc_s2.configure(
                text=(
                    "S2_ref = "
                    f"{sample.raw_s2:+.6f} / {sample.raw_ref:+.6f} "
                    f"= {sample.ref_corrected_s2:+.6f}; "
                    "S2_norm = "
                    f"({sample.ref_corrected_s2:+.6f} - "
                    f"{counter.offset_s2:+.6f}) "
                    f"/ {counter.scale_s2:.6f} = {sample.s2:+.6f}"
                )
            )

        if sample.valid:
            self.label_calc_phase.configure(
                text=(
                    f"phase_rad = {phase_formula} = "
                    f"{sample.phase_rad:+.6f} rad"
                )
            )
            self.label_calc_unwrapped.configure(
                text=(
                    "unwrapped_phase_rad += "
                    f"delta_phase_rad {sample.delta_phase_rad:+.6f} "
                    f"= {sample.unwrapped_phase_rad:+.6f} rad"
                )
            )
        else:
            if sample.direction == "reference_low":
                invalid_reason = (
                    f"abs(reference) {abs(sample.raw_ref):.3e} "
                    f"< {MIN_REFERENCE_SIGNAL:.1e}"
                )
            else:
                invalid_reason = (
                    f"radius {sample.radius:.6f} < "
                    f"{MIN_SIGNAL_RADIUS:.6f}"
                )

            self.label_calc_phase.configure(
                text=(
                    "phase_rad = not updated because "
                    f"{invalid_reason}"
                )
            )
            self.label_calc_unwrapped.configure(
                text=(
                    "unwrapped_phase_rad unchanged = "
                    f"{sample.unwrapped_phase_rad:+.6f} rad"
                )
            )

        self.label_calc_fringe.configure(
            text=(
                "fringe_position = unwrapped_phase_rad / (2*pi) = "
                f"{sample.fringe_position:+.6f}"
            )
        )

        if distance_mm is None or counter.fringe_distance_mm is None:
            self.label_calc_distance.configure(
                text="distance_mm = fringe_position * fringe_distance_mm = n/a"
            )
        else:
            self.label_calc_distance.configure(
                text=(
                    "distance_mm = "
                    f"{sample.fringe_position:+.6f} * "
                    f"{counter.fringe_distance_mm:.9f} = "
                    f"{distance_mm:+.9f} mm"
                )
            )

    def reset_calculation_display(self):
        self.label_calc_s1.configure(
            text=(
                "S1_ref = raw_S1 / raw_ref = n/a; "
                "S1_norm = (S1_ref - offset_S1) / scale_S1 = n/a"
            )
        )
        self.label_calc_s2.configure(
            text=(
                "S2_ref = raw_S2 / raw_ref = n/a; "
                "S2_norm = (S2_ref - offset_S2) / scale_S2 = n/a"
            )
        )
        self.label_calc_phase.configure(
            text="phase_rad = atan2(S2_norm, S1_norm) = n/a"
        )
        self.label_calc_unwrapped.configure(
            text="unwrapped_phase_rad += wrap(delta_phase_rad) = 0.00000 rad"
        )
        self.label_calc_fringe.configure(
            text="fringe_position = unwrapped_phase_rad / (2*pi) = 0.0000"
        )
        self.label_calc_distance.configure(
            text="distance_mm = fringe_position * fringe_distance_mm = n/a"
        )

    def toggle_lock(self):
        if self.lock_active:
            self.disable_lock()
            return

        if not self.monitoring:
            self.status.configure(
                text="Status: start monitoring before lock",
                text_color=ORANGE_COLOR
            )
            return

        if (
            self.stage_command_active
            or self.lock_correction_active
            or (
                self.stage is not None
                and self.stage_connected
                and self.stage.is_moving
            )
        ):
            self.status.configure(
                text="Status: wait for stage movement before lock",
                text_color=ORANGE_COLOR
            )
            return

        if not self.stage_connected:
            self.start_stage_connection()
            self.status.configure(
                text="Status: wait for stage connection before lock",
                text_color=ORANGE_COLOR
            )
            return

        if self.latest_sample is None or self.latest_distance_mm is None:
            self.status.configure(
                text="Status: wait for a valid homodyne sample",
                text_color=ORANGE_COLOR
            )
            return

        self.lock_active = True
        self.lock_reference_distance_mm = self.latest_distance_mm
        self.lock_reference_phase_rad = (
            self.latest_sample.unwrapped_phase_rad
        )
        self.lock_reference_fringes = self.latest_sample.signed_fringes

        self.btn_lock.configure(
            text="UNLOCK",
            fg_color=GREEN_COLOR
        )
        self.label_lock_status.configure(
            text="Lock: on",
            text_color=GREEN_COLOR
        )
        self.status.configure(
            text="Status: lock reference set",
            text_color=GREEN_COLOR
        )
        self.update_lock_display(
            self.latest_sample,
            self.latest_distance_mm
        )

    def disable_lock(self, update_status=True):
        self.stop_stage_correction()
        self.lock_active = False
        self.btn_lock.configure(
            text="LOCK",
            fg_color=TEXT_COLOR
        )
        self.label_lock_status.configure(
            text="Lock: off",
            text_color=TEXT_COLOR
        )
        self.label_lock_reference.configure(
            text="Reference: n/a"
        )
        self.label_lock_drift.configure(
            text="Drift: n/a"
        )
        self.label_lock_correction.configure(
            text="Correction to lock: n/a",
            text_color=TEXT_COLOR
        )

        if update_status:
            self.status.configure(
                text="Status: lock off",
                text_color=TEXT_COLOR
            )

    def update_lock_display(self, sample, distance_mm):
        if not self.lock_active or distance_mm is None:
            return

        drift_mm = distance_mm - self.lock_reference_distance_mm
        correction_mm = -STAGE_CORRECTION_SIGN * drift_mm
        next_step_mm = self.limited_stage_correction_mm(correction_mm)

        self.label_lock_reference.configure(
            text=(
                f"Reference: "
                f"{self.lock_reference_distance_mm:+.9f} mm, "
                f"{self.lock_reference_fringes:+d} fringes"
            )
        )
        self.label_lock_drift.configure(
            text=f"Drift: {drift_mm:+.9f} mm"
        )
        self.label_lock_correction.configure(
            text=(
                f"Correction to lock: {correction_mm:+.9f} mm "
                f"(next step {next_step_mm:+.9f} mm)"
            ),
            text_color=ORANGE_COLOR if abs(drift_mm) > 0 else GREEN_COLOR
        )

        if sample.fringe_delta != 0:
            self.status.configure(
                text=(
                    f"Status: lock saw fringe "
                    f"{sample.fringe_delta:+d}, "
                    f"correction {correction_mm:+.9f} mm"
                ),
                text_color=ORANGE_COLOR
            )

        self.maybe_start_lock_correction(drift_mm, correction_mm)

    def lock_deadband_mm(self):
        fringe_distance_mm = self.monitor.counter.fringe_distance_mm

        if fringe_distance_mm is None:
            return 1e-7

        return max(
            abs(fringe_distance_mm) * LOCK_TRIGGER_FRINGES,
            1e-7
        )

    def maybe_start_lock_correction(self, drift_mm, correction_mm):
        if not self.lock_active:
            return

        if not self.stage_connected or self.stage is None:
            self.label_stage_status.configure(
                text="Stage: not connected, cannot correct lock",
                text_color=RED_COLOR
            )
            return

        if (
            self.lock_correction_active
            or self.stage_command_active
            or self.stage.is_moving
        ):
            return

        if abs(drift_mm) < self.lock_deadband_mm():
            return

        now = time.time()

        if now - self.lock_last_correction_time < LOCK_CORRECTION_COOLDOWN_S:
            return

        correction_step_mm = self.limited_stage_correction_mm(correction_mm)
        current_position_mm = self.stage.get_position()
        target_position_mm = self.stage.clamp_position(
            current_position_mm + correction_step_mm
        )
        actual_correction_mm = target_position_mm - current_position_mm

        if abs(actual_correction_mm) < 1e-12:
            self.label_lock_status.configure(
                text="Lock: correction blocked by stage limit",
                text_color=RED_COLOR
            )
            return

        self.lock_last_correction_time = now
        self.lock_correction_active = True
        self.lock_target_position_mm = target_position_mm

        if not self.stage.move_absolute(target_position_mm):
            self.lock_correction_active = False
            self.label_lock_status.configure(
                text="Lock: stage correction failed",
                text_color=RED_COLOR
            )
            return

        self.label_lock_status.configure(
            text=f"Lock: correcting {actual_correction_mm:+.9f} mm",
            text_color=ORANGE_COLOR
        )
        self.label_stage_status.configure(
            text="Stage: lock correction running",
            text_color=ORANGE_COLOR
        )
        self.label_stage_position.configure(
            text=f"Stage target: {target_position_mm:.9f} mm"
        )

        threading.Thread(
            target=self.lock_correction_worker,
            daemon=True
        ).start()

    def lock_correction_worker(self):
        while (
            self.lock_correction_active
            and self.stage is not None
            and self.stage.is_moving
        ):
            position_mm = self.stage.current_position

            self.root.after(
                0,
                lambda p=position_mm:
                self.label_stage_position.configure(
                    text=f"Stage position: {p:.9f} mm"
                )
            )

            time.sleep(0.05)

        position_mm = None

        if self.stage is not None and self.stage_connected:
            position_mm = self.stage.get_position()

        self.root.after(
            0,
            lambda p=position_mm:
            self.finish_lock_correction(p)
        )

    def finish_lock_correction(self, position_mm):
        self.lock_correction_active = False

        if position_mm is not None:
            self.stage_position_mm = position_mm
            self.label_stage_position.configure(
                text=f"Stage position: {position_mm:.9f} mm"
            )

        if not self.lock_active:
            return

        self.label_stage_status.configure(
            text="Stage: connected",
            text_color=GREEN_COLOR
        )
        self.label_lock_status.configure(
            text="Lock: correction done",
            text_color=GREEN_COLOR
        )
        self.status.configure(
            text="Status: lock correction done",
            text_color=GREEN_COLOR
        )

    def stop_stage_correction(self):
        was_correcting = self.lock_correction_active
        self.lock_correction_active = False

        if was_correcting and self.stage_connected and self.stage is not None:
            self.stage.stop()

    def show_error(self, error):
        self.status.configure(
            text=f"Status: {error}",
            text_color=RED_COLOR
        )

    def finish_stopped_ui(self):
        self.btn_start.configure(
            text="START MONITORING",
            fg_color=TEXT_COLOR
        )

        if self.last_error_text:
            self.status.configure(
                text=f"Status: {self.last_error_text}",
                text_color=RED_COLOR
            )

        elif not self.lock_active:
            self.status.configure(
                text="Status: stopped",
                text_color=TEXT_COLOR
            )

    def reset_monitor(self):
        self.monitor.counter.reset()
        self.latest_sample = None
        self.latest_distance_mm = None
        self.raw_s1_history = []
        self.raw_s2_history = []
        self.raw_ref_history = []
        with self.sample_display_lock:
            self.pending_sample = None
            self.pending_distance_mm = None

        self.label_phase.configure(text="0.00000 rad")
        self.label_fringe_position.configure(text="0.0000")
        self.label_fringes.configure(text="0")
        self.label_direction.configure(text="none")
        self.label_distance.configure(text="n/a")
        self.reset_calculation_display()
        self.label_lock_status.configure(text="Lock: off", text_color=TEXT_COLOR)
        self.label_lock_reference.configure(text="Reference: n/a")
        self.label_lock_drift.configure(text="Drift: n/a")
        self.label_lock_correction.configure(text="Correction to lock: n/a", text_color=TEXT_COLOR)

        self.disable_lock(update_status=False)
        self.update_plot(reset=True)

        if not self.monitoring:
            self.status.configure(
                text="Status: reset",
                text_color=TEXT_COLOR
            )

    def update_plot(self, reset=False):
        if self.plot_axis is None:
            return

        if reset:
            for key in self.plot_lines:
                self.plot_lines[key].set_data([], [])
            self.plot_axis.relim()
            self.plot_axis.autoscale_view()
            self.plot_canvas.draw_idle()
            return

        x = list(range(len(self.raw_s1_history)))
        self.plot_lines['S1_raw'].set_data(x, self.raw_s1_history)
        self.plot_lines['S2_raw'].set_data(x, self.raw_s2_history)
        self.plot_lines['Ref_raw'].set_data(x, self.raw_ref_history)

        self.plot_axis.relim()
        self.plot_axis.autoscale_view()
        self.plot_canvas.draw_idle()

    def on_close(self):
        self.monitoring = False

        try:
            self.monitor.close()
        except Exception:
            pass

        try:
            if self.stage is not None:
                self.stage.close()
        except Exception:
            pass

        self.root.destroy()

    def run(self):
        self.root.mainloop()


def run_gui():
    gui = HomodyneGui()
    gui.run()


def run_print_loop():
    monitor = HomodyneMonitor()

    try:
        monitor.connect()
        print("NI connected on Dev1/ai0 and Dev1/ai1.")
        print("Calibrating photodiode offsets and amplitudes...")
        print("Move the stage during calibration so the circle is sampled.")
        monitor.calibrate()
        print("Monitoring. Stop with Ctrl+C.")

        while True:
            sample = monitor.read()
            distance_mm = monitor.counter.signed_distance_mm()

            if distance_mm is None:
                distance_text = "n/a"
            else:
                distance_text = f"{distance_mm:+.9f} mm"

            print(
                "phase="
                f"{sample.unwrapped_phase_rad:+.4f} rad, "
                "fringe_position="
                f"{sample.fringe_position:+.4f}, "
                "signed_fringes="
                f"{sample.signed_fringes:+d}, "
                "fringe_delta="
                f"{sample.fringe_delta:+d}, "
                "direction="
                f"{sample.direction}, "
                "distance="
                f"{distance_text}"
            )

            time.sleep(SAMPLE_INTERVAL_S)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        monitor.close()


if __name__ == "__main__":
    run_gui()
