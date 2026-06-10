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

LASER_WAVELENGTH_NM = 787.3

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
            text="CHECK Stage",
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
        lock_frame.pack(side="left", fill="both", expand=True, padx=(8, 4))

        self.label_phase = self.make_value_label(
            values_frame,
            "Phase",
            "phase_rad = atan2(S2_norm, S1_norm) = 0.00000 rad"
        )
        self.label_s1_norm = self.make_value_label(
            values_frame,
            "S1 norm",
            "S1_norm = (raw_S1 / raw_ref - offset_S1) / scale_S1 = n/a"
        )
        self.label_s2_norm = self.make_value_label(
            values_frame,
            "S2 norm",
            "S2_norm = (raw_S2 / raw_ref - offset_S2) / scale_S2 = n/a"
        )
        self.label_unwrapped_phase = self.make_value_label(
            values_frame,
            "Unwrapped phase",
            "unwrapped_phase_rad += delta_phase_rad = 0.00000 rad"
        )
        self.label_fringe_position = self.make_value_label(
            values_frame,
            "Fringe position",
            "fringe_position = unwrapped_phase_rad / (2*pi) = 0.0000"
        )
        self.label_fringes = self.make_value_label(
            values_frame,
            "Completed fringes",
            "signed_fringes = 0"
        )
        self.label_direction = self.make_value_label(
            values_frame,
            "Direction",
            "direction = none"
        )
        self.label_distance = self.make_value_label(
            values_frame,
            "Distance",
            "distance_mm = fringe_position * fringe_distance_mm = n/a"
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
            self.plot_axes = None
        else:
            self.plot_figure = plt.Figure(figsize=(8, 5.6), dpi=100)
            axes = self.plot_figure.subplots(3, 1, sharex=True)
            self.plot_axis = axes[0]
            self.plot_axes = {
                'S1_raw': axes[0],
                'S2_raw': axes[1],
                'Ref_raw': axes[2]
            }

            plot_specs = {
                'S1_raw': ("S1 raw voltage", 'blue', 'S1'),
                'S2_raw': ("S2 raw voltage", 'green', 'S2'),
                'Ref_raw': ("Reference raw voltage", 'red', 'Ref')
            }

            self.plot_lines = {}
            for key, axis in self.plot_axes.items():
                title, color, label = plot_specs[key]
                axis.set_title(title)
                axis.grid(True, linestyle=':', alpha=0.6)
                axis.set_ylabel("Voltage")
                self.plot_lines[key] = axis.plot(
                    [],
                    [],
                    color=color,
                    label=label
                )[0]
                axis.legend(loc="upper right")

            axes[-1].set_xlabel("Samples")
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
                text=f"Stage position: {p:.6f} mm"
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
                text=f"Stage position: {position_mm:.6f} mm"
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

        self.start_stage_move_by(direction * self.stage_step_mm)

    def manual_stage_move_worker(self):
        while self.stage is not None and self.stage.is_moving:
            position_mm = self.stage.get_position()

            self.root.after(
                0,
                lambda p=position_mm:
                self.label_stage_position.configure(
                    text=f"Stage position: {p:.6f} mm"
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
                text=f"Stage position: {position_mm:.6f} mm"
            )

        self.label_stage_status.configure(
            text="Stage: connected",
            text_color=GREEN_COLOR
        )
        self.status.configure(
            text="Status: stage step done",
            text_color=GREEN_COLOR
        )
        self.finish_stage_command_ui()

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

    def start_stage_move_to(self, target_mm, start_pos=None):
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

        if start_pos is None:
            start_pos = self.stage.get_position()

        target_mm = self.stage.clamp_position(target_mm)

        if abs(target_mm - start_pos) < 1e-12:
            self.status.configure(
                text="Status: stage already at target",
                text_color=TEXT_COLOR
            )
            self.label_stage_position.configure(
                text=f"Stage position: {start_pos:.6f} mm"
            )
            return

        self.stage_command_active = True
        self.set_stage_controls_enabled(False)

        if not self.stage.move_absolute(target_mm):
            self.finish_stage_command_ui()
            self.status.configure(
                text="Status: stage move failed",
                text_color=RED_COLOR
            )
            return

        self.status.configure(
            text=f"Status: stage moving to {target_mm:.6f} mm",
            text_color=TEXT_COLOR
        )
        self.label_stage_status.configure(
            text="Stage: moving",
            text_color=ORANGE_COLOR
        )
        self.label_stage_position.configure(
            text=f"Stage target: {target_mm:.6f} mm"
        )

        threading.Thread(
            target=self.manual_stage_move_worker,
            daemon=True
        ).start()

    def start_stage_move_by(self, move_mm):
        if self.stage is None or not self.stage_connected:
            self.status.configure(
                text="Status: stage not connected",
                text_color=RED_COLOR
            )
            return

        start_pos = self.stage.get_position()
        self.start_stage_move_to(
            start_pos + move_mm,
            start_pos=start_pos
        )

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
                text=f"Stage position: {start_pos:.6f} mm"
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
                text="Status: wait for stage connection, then press CHECK Stage",
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

            # Get current position as starting point
            start_pos = self.stage.get_position()
            
            # Move to minimum position
            min_pos = self.stage.min_position
            self.set_status_from_thread(
                f"Status: stage check moving to minimum ({min_pos:.6f} mm)",
                ORANGE_COLOR
            )
            
            if not self.stage.move_absolute(min_pos):
                self.set_status_from_thread(
                    "Status: stage check move to minimum failed",
                    RED_COLOR
                )
                return

            try:
                min_actual = self.wait_for_stage_motion(timeout_s=STAGE_CHECK_TIMEOUT_S)
            except RuntimeError as error:
                self.set_status_from_thread(
                    f"Status: stage check timeout at minimum: {error}",
                    RED_COLOR
                )
                return

            if min_actual is None:
                self.set_status_from_thread(
                    "Status: could not read stage position at minimum",
                    RED_COLOR
                )
                return

            # Move to maximum position
            max_pos = self.stage.max_position
            self.set_status_from_thread(
                f"Status: stage check moving to maximum ({max_pos:.6f} mm)",
                ORANGE_COLOR
            )
            
            if not self.stage.move_absolute(max_pos):
                self.set_status_from_thread(
                    "Status: stage check move to maximum failed",
                    RED_COLOR
                )
                return

            try:
                max_actual = self.wait_for_stage_motion(timeout_s=STAGE_CHECK_TIMEOUT_S)
            except RuntimeError as error:
                self.set_status_from_thread(
                    f"Status: stage check timeout at maximum: {error}",
                    RED_COLOR
                )
                return

            if max_actual is None:
                self.set_status_from_thread(
                    "Status: could not read stage position at maximum",
                    RED_COLOR
                )
                return

            # Move back to zero position
            zero_pos = 0.0
            self.set_status_from_thread(
                f"Status: stage check returning to zero ({zero_pos:.6f} mm)",
                ORANGE_COLOR
            )
            
            if not self.stage.move_absolute(zero_pos):
                self.set_status_from_thread(
                    "Status: stage check move to zero failed",
                    RED_COLOR
                )
                return

            try:
                final_actual = self.wait_for_stage_motion(timeout_s=STAGE_CHECK_TIMEOUT_S)
            except RuntimeError as error:
                self.set_status_from_thread(
                    f"Status: stage check timeout returning to zero: {error}",
                    RED_COLOR
                )
                return

            if final_actual is None:
                self.set_status_from_thread(
                    "Status: could not read stage position at zero",
                    RED_COLOR
                )
                return

            # Set zero reference on the controller for exact zero positioning
            self.stage.set_zero_position()

            # Verify stage moved sufficiently
            total_travel = abs(max_actual - min_actual)
            expected_travel = abs(max_pos - min_pos)
            
            if expected_travel > 0 and total_travel < expected_travel * 0.5:
                self.set_status_from_thread(
                    (
                        "Status: stage check failed, insufficient travel "
                        f"({total_travel:.6f} mm expected {expected_travel:.6f} mm)"
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
                    f"(min: {min_actual:.6f}, max: {max_actual:.6f}, "
                    f"zero: {final_actual:.6f} mm)"
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
                    text=f"Stage position: {p:.6f} mm"
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

        self.set_status_from_thread(
            (
                f"Status: moving to {target_mm:.6f} mm "
                f"in {step_mm:.6f} mm steps"
            ),
            TEXT_COLOR
        )

        try:
            while remaining > 1e-12:
                next_step = min(step_mm, remaining)
                next_target = self.stage.clamp_position(
                    current_pos + direction * next_step
                )

                if abs(next_target - current_pos) < 1e-12:
                    break

                if not self.stage.move_absolute(next_target):
                    self.set_status_from_thread(
                        "Status: stage move failed",
                        RED_COLOR
                    )
                    return

                while self.stage is not None and self.stage.is_moving:
                    position_mm = self.stage.get_position()
                    self.set_stage_position_from_thread(position_mm)
                    time.sleep(0.05)

                current_pos = next_target
                remaining = abs(target_mm - current_pos)
                self.set_stage_position_from_thread(current_pos)

                if remaining > 1e-12:
                    time.sleep(delay_s)

            if self.stage is not None and self.stage_connected:
                current_pos = self.stage.get_position()
                self.stage_position_mm = current_pos
                self.set_stage_position_from_thread(current_pos)

            self.set_status_from_thread(
                f"Status: reached {current_pos:.6f} mm",
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
            self.label_distance.configure(
                text="distance_mm = fringe_position * fringe_distance_mm = n/a"
            )
        else:
            self.label_distance.configure(
                text=(
                    "distance_mm = fringe_position * fringe_distance_mm = "
                    f"{distance_mm:+.9f} mm"
                )
            )

        self.label_phase.configure(
            text=(
                "phase_rad = atan2(S2_norm, S1_norm) = "
                f"{sample.phase_rad:+.5f} rad"
            ) if sample.valid else "phase_rad = invalid"
        )

        if sample.direction == "reference_low":
            self.label_s1_norm.configure(
                text="S1_norm = raw_ref too low"
            )
            self.label_s2_norm.configure(
                text="S2_norm = raw_ref too low"
            )
        else:
            self.label_s1_norm.configure(
                text=(
                    "S1_norm = (raw_S1 / raw_ref - offset_S1) / scale_S1 = "
                    f"{sample.s1:+.6f}"
                )
            )
            self.label_s2_norm.configure(
                text=(
                    "S2_norm = (raw_S2 / raw_ref - offset_S2) / scale_S2 = "
                    f"{sample.s2:+.6f}"
                )
            )

        self.label_unwrapped_phase.configure(
            text=(
                "unwrapped_phase_rad += delta_phase_rad = "
                f"{sample.unwrapped_phase_rad:+.5f} rad"
            )
        )
        self.label_fringe_position.configure(
            text=(
                "fringe_position = unwrapped_phase_rad / (2*pi) = "
                f"{sample.fringe_position:+.4f}"
            )
        )
        self.label_fringes.configure(
            text=f"signed_fringes = {sample.signed_fringes:+d}"
        )
        self.label_direction.configure(
            text=f"direction = {sample.direction}"
        )

        if sample.fringe_delta != 0:
            self.label_fringes.configure(text_color=GREEN_COLOR)
            self.root.after(
                250,
                lambda:
                self.label_fringes.configure(text_color=TEXT_COLOR)
            )

        self.update_lock_display(sample, distance_mm)

    def reset_calculation_display(self):
        self.label_phase.configure(
            text="phase_rad = atan2(S2_norm, S1_norm) = n/a"
        )
        self.label_s1_norm.configure(
            text="S1_norm = (raw_S1 / raw_ref - offset_S1) / scale_S1 = n/a"
        )
        self.label_s2_norm.configure(
            text="S2_norm = (raw_S2 / raw_ref - offset_S2) / scale_S2 = n/a"
        )
        self.label_unwrapped_phase.configure(
            text="unwrapped_phase_rad += delta_phase_rad = 0.00000 rad"
        )
        self.label_fringe_position.configure(
            text="fringe_position = unwrapped_phase_rad / (2*pi) = 0.0000"
        )
        self.label_fringes.configure(
            text="signed_fringes = 0"
        )
        self.label_direction.configure(
            text="direction = none"
        )
        self.label_distance.configure(
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
            text=f"Stage target: {target_position_mm:.6f} mm"
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
                    text=f"Stage position: {p:.6f} mm"
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
                text=f"Stage position: {position_mm:.6f} mm"
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
        if self.plot_axes is None:
            return

        if reset:
            for key in self.plot_lines:
                self.plot_lines[key].set_data([], [])

            for axis in self.plot_axes.values():
                axis.relim()
                axis.autoscale_view()

            self.plot_canvas.draw_idle()
            return

        x = list(range(len(self.raw_s1_history)))
        plot_data = {
            'S1_raw': self.raw_s1_history,
            'S2_raw': self.raw_s2_history,
            'Ref_raw': self.raw_ref_history
        }

        for key, values in plot_data.items():
            self.plot_lines[key].set_data(x, values)
            self.plot_axes[key].relim()
            self.plot_axes[key].autoscale_view()

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
