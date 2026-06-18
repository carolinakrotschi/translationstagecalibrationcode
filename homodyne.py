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


class SingleSignalFringeCounter:
    def __init__(self, sample_interval_s=0.005):
        self.sample_interval_s = sample_interval_s
        self.min_voltage = 0.0
        self.max_voltage = 0.0
        self.offset_voltage = 0.0
        self.scale_voltage = 1.0
        
        self.fringe_amplitude_voltage = 0.003
        self.fringe_rise_threshold_voltage = 0.003 * 0.55
        self.fringe_rearm_threshold_voltage = 0.003 * 0.20
        self.fringe_trough_voltage = None
        self.fringe_peak_voltage = None
        
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0
        self.accumulated_fringes = 0

    def calibrate(self, s1_values):
        if not s1_values:
            return
        
        # Smooth values with a small moving average as in side_thor.py
        smoothed_samples = []
        for index in range(len(s1_values)):
            start_index = max(0, index - 2)
            end_index = min(len(s1_values), index + 3)
            window = s1_values[start_index:end_index]
            smoothed_samples.append(sum(window) / len(window))
            
        self.min_voltage = min(smoothed_samples)
        self.max_voltage = max(smoothed_samples)
        self.offset_voltage = (self.min_voltage + self.max_voltage) / 2
        self.scale_voltage = (self.max_voltage - self.min_voltage) / 2
        if self.scale_voltage <= 1e-12:
            self.scale_voltage = 1.0
            
        # Try to find actual extrema/amplitude
        minima = []
        maxima = []
        extrema = []
        for index in range(1, len(smoothed_samples) - 1):
            prev_val = smoothed_samples[index - 1]
            curr_val = smoothed_samples[index]
            next_val = smoothed_samples[index + 1]
            if (curr_val <= prev_val and curr_val < next_val) or (curr_val < prev_val and curr_val <= next_val):
                minima.append(curr_val)
                extrema.append(("min", curr_val))
            if (curr_val >= prev_val and curr_val > next_val) or (curr_val > prev_val and curr_val >= next_val):
                maxima.append(curr_val)
                extrema.append(("max", curr_val))
                
        amplitude = 0.003
        if minima and maxima:
            compressed_extrema = []
            for kind, value in extrema:
                if compressed_extrema and compressed_extrema[-1][0] == kind:
                    prev_kind, prev_val = compressed_extrema[-1]
                    if kind == "min" and value < prev_val:
                        compressed_extrema[-1] = (prev_kind, value)
                    if kind == "max" and value > prev_val:
                        compressed_extrema[-1] = (prev_kind, value)
                    continue
                compressed_extrema.append((kind, value))
                
            amplitudes = []
            for index in range(1, len(compressed_extrema)):
                prev_kind, prev_val = compressed_extrema[index - 1]
                curr_kind, curr_val = compressed_extrema[index]
                if prev_kind != curr_kind:
                    amp = abs(curr_val - prev_val)
                    if 0.001 <= amp <= 0.010:
                        amplitudes.append(amp)
            if amplitudes:
                amplitudes.sort()
                upper_half = amplitudes[len(amplitudes) // 2:]
                amplitude = sum(upper_half) / len(upper_half)
            else:
                fallback_amp = max(maxima) - min(minima)
                if 0.001 <= fallback_amp <= 0.010:
                    amplitude = fallback_amp
                    
        self.fringe_amplitude_voltage = amplitude
        self.fringe_rise_threshold_voltage = amplitude * 0.55
        self.fringe_rearm_threshold_voltage = amplitude * 0.20
        self.reset()

    def reset(self):
        self.fringe_trough_voltage = None
        self.fringe_peak_voltage = None
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0
        self.accumulated_fringes = 0

    def update(self, voltage):
        smooth_voltage = voltage
        
        if self.fringe_trough_voltage is None:
            self.fringe_trough_voltage = smooth_voltage
            self.fringe_peak_voltage = smooth_voltage
            return False
            
        if self.fringe_peak_voltage is None:
            self.fringe_peak_voltage = smooth_voltage
            
        cooldown_ok = (time.time() - self.last_count_time) > self.sample_interval_s
        
        if not self.was_dark:
            if smooth_voltage > self.fringe_peak_voltage:
                self.fringe_peak_voltage = smooth_voltage
                
            drop_from_peak = self.fringe_peak_voltage - smooth_voltage
            if drop_from_peak >= self.fringe_rearm_threshold_voltage:
                self.dark_counter += 1
                self.fringe_trough_voltage = min(self.fringe_trough_voltage, smooth_voltage)
            else:
                self.dark_counter = 0
                
            if self.dark_counter >= 1:
                self.was_dark = True
                self.fringe_trough_voltage = smooth_voltage
                self.bright_counter = 0
            return False
            
        if smooth_voltage < self.fringe_trough_voltage:
            self.fringe_trough_voltage = smooth_voltage
            self.bright_counter = 0
            return False
            
        rise_from_trough = smooth_voltage - self.fringe_trough_voltage
        if rise_from_trough >= self.fringe_rise_threshold_voltage:
            self.bright_counter += 1
        else:
            self.bright_counter = 0
            
        if self.was_dark and self.bright_counter >= 1 and cooldown_ok:
            self.accumulated_fringes += 1
            self.was_dark = False
            self.last_count_time = time.time()
            self.dark_counter = 0
            self.bright_counter = 0
            self.fringe_peak_voltage = smooth_voltage
            self.fringe_trough_voltage = smooth_voltage
            return True
            
        return False


class HomodyneQuadratureCounter:
    def __init__(
        self,
        phase_direction_sign=PHASE_DIRECTION_SIGN,
        min_signal_radius=MIN_SIGNAL_RADIUS,
        min_reference_signal=MIN_REFERENCE_SIGNAL,
        fringe_distance_mm=None
    ):
        self.lock = threading.Lock()
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
        with self.lock:
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

            self._reset_unlocked()

    def reset(self):
        with self.lock:
            self._reset_unlocked()

    def _reset_unlocked(self):
        self.previous_phase_rad = None
        self.unwrapped_phase_rad = 0.0
        self.signed_fringes = 0
        self.total_abs_fringes = 0
        self.delta_phase_history = []

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
        with self.lock:
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

            self.delta_phase_history.append(delta_phase_rad)
            if len(self.delta_phase_history) > 15:
                self.delta_phase_history.pop(0)

            avg_delta_phase = sum(self.delta_phase_history) / len(self.delta_phase_history)
            threshold = 0.001
            if avg_delta_phase > threshold:
                direction = "forward"
            elif avg_delta_phase < -threshold:
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
        with self.lock:
            if self.fringe_distance_mm is None:
                return None

            return (
                self.unwrapped_phase_rad
                / (2 * math.pi)
                * self.fringe_distance_mm
            )

    def correction_to_zero_mm(self, stage_direction_sign=1):
        with self.lock:
            distance_mm = (
                self.unwrapped_phase_rad
                / (2 * math.pi)
                * self.fringe_distance_mm
            ) if self.fringe_distance_mm is not None else None

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
        self.single_counter = SingleSignalFringeCounter(sample_interval_s=SAMPLE_INTERVAL_S)

    def connect(self):
        return self.reader.connect()

    def calibrate(
        self,
        seconds=CALIBRATION_SECONDS,
        sample_interval_s=SAMPLE_INTERVAL_S,
        should_continue=None,
        sample_callback=None
    ):
        samples = []
        start_time = time.time()

        while time.time() - start_time < seconds:
            if should_continue is not None and not should_continue():
                break

            val = self.reader.read()
            samples.append(val)
            if sample_callback is not None:
                sample_callback(
                    val,
                    time.time() - start_time,
                    seconds
                )
            time.sleep(sample_interval_s)

        if not samples and should_continue is not None and not should_continue():
            return samples

        self.counter.calibrate_from_samples(samples)
        s1_corrected = []
        for raw_s1, raw_s2, raw_ref in samples:
            if abs(raw_ref) >= self.counter.min_reference_signal:
                s1_corrected.append(raw_s1 / raw_ref)
        self.single_counter.calibrate(s1_corrected)
        return samples

    def read(self):
        raw_s1, raw_s2, raw_ref = self.reader.read()
        if abs(raw_ref) >= self.counter.min_reference_signal:
            ref_corrected_s1 = raw_s1 / raw_ref
        else:
            ref_corrected_s1 = 0.0
        self.single_counter.update(ref_corrected_s1)
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
        self.root.geometry("1200x950")
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
        self.calibrating = False
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

        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        self.stage_start_position = 0.0
        self.stage_target_position = None
        self.stage_remaining_to_drive = 0.0
        self.stage_remaining_known = True

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

        # Columns layout container
        self.cols_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.cols_frame.pack(fill="both", expand=True, padx=18, pady=8)

        # Left Column for Raw plots
        self.left_col = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Right Column for Displays and Lissajous
        self.right_col = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.right_col.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # Raw Signal Plots Frame (Left Column)
        plot_frame = ctk.CTkFrame(self.left_col, fg_color="#EEEEEE")
        plot_frame.pack(fill="both", expand=True, pady=4)

        ctk.CTkLabel(
            plot_frame,
            text="Raw Signal Time Traces",
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
            self.plot_axes = None
        else:
            self.plot_figure = plt.Figure(figsize=(5.0, 6.0), dpi=100)
            axes = self.plot_figure.subplots(3, 1, sharex=True)
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
            for key in ['S1_raw', 'S2_raw', 'Ref_raw']:
                axis = self.plot_axes[key]
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

        # Single-Signal Fringe Counter Panel (Right Column)
        self.single_fringe_frame = ctk.CTkFrame(self.right_col, fg_color="#EEEEEE")
        self.single_fringe_frame.pack(fill="x", pady=4, padx=8)

        ctk.CTkLabel(
            self.single_fringe_frame,
            text="Single-Signal Fringe Counter (Signal 1)",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(8, 4))

        self.label_single_fringes = ctk.CTkLabel(
            self.single_fringe_frame,
            text="S1 Fringe Count: 0",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_single_fringes.pack(pady=2)

        self.label_single_distance = ctk.CTkLabel(
            self.single_fringe_frame,
            text="S1 Calculated Distance: 0.000000 mm",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_single_distance.pack(pady=2)

        self.label_single_thresholds = ctk.CTkLabel(
            self.single_fringe_frame,
            text="S1 Thresholds: Min/Max = n/a, Amplitude = n/a",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_single_thresholds.pack(pady=2)

        # Lissajous Circle Frame (Right Column)
        self.plot_frame_circle = ctk.CTkFrame(self.right_col, fg_color="#EEEEEE")
        self.plot_frame_circle.pack(fill="both", expand=True, pady=4)

        ctk.CTkLabel(
            self.plot_frame_circle,
            text="Lissajous Circle & Angle Visualizer",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(10, 4))

        if plt is None or FigureCanvasTkAgg is None:
            self.plot_canvas_circle = None
            self.axis_circle = None
        else:
            self.plot_figure_circle = plt.Figure(figsize=(4.0, 4.0), dpi=100)
            self.axis_circle = self.plot_figure_circle.add_subplot(111)

            # Setup the Lissajous circle plot
            self.axis_circle.set_title("Lissajous Circle (S1 vs S2)")
            self.axis_circle.set_xlabel("S1 (normalized)")
            self.axis_circle.set_ylabel("S2 (normalized)")
            self.axis_circle.grid(True, linestyle=':', alpha=0.6)
            self.axis_circle.set_aspect('equal', adjustable='box')
            self.axis_circle.set_xlim(-1.5, 1.5)
            self.axis_circle.set_ylim(-1.5, 1.5)

            # Draw reference unit circle in grey
            ref_theta = [t * 2 * math.pi / 100 for t in range(101)]
            ref_x = [math.cos(t) for t in ref_theta]
            ref_y = [math.sin(t) for t in ref_theta]
            self.axis_circle.plot(ref_x, ref_y, color='gray', linestyle='--', alpha=0.5, label='Ref Circle')

            # Trace line (history of positions on the circle)
            self.plot_lines['circle_trace'] = self.axis_circle.plot(
                [],
                [],
                color='purple',
                alpha=0.6,
                label='Trace'
            )[0]

            # Current position point (large red dot)
            self.plot_lines['circle_current'] = self.axis_circle.plot(
                [],
                [],
                'ro',
                markersize=8,
                label='Current'
            )[0]

            # Pointer line (clock hand)
            self.plot_lines['circle_pointer'] = self.axis_circle.plot(
                [],
                [],
                color='orange',
                linestyle='-',
                linewidth=2,
                label='Pointer'
            )[0]

            # Directional quiver arrow
            self.plot_quiver = self.axis_circle.quiver(
                [0], [0], [0], [0],
                angles='xy', scale_units='xy', scale=1,
                color='green', width=0.015, headwidth=4, headlength=5
            )
            self.plot_quiver.set_visible(False)

            self.axis_circle.legend(loc="upper right")
            self.plot_figure_circle.tight_layout()
            self.plot_canvas_circle = FigureCanvasTkAgg(
                self.plot_figure_circle,
                master=self.plot_frame_circle
            )
            self.plot_canvas_circle.draw()
            self.plot_canvas_circle.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Quadrature Homodyne values frame (Right Column)
        values_frame = ctk.CTkFrame(self.right_col, fg_color="#EEEEEE")
        values_frame.pack(fill="x", pady=4, padx=8)

        ctk.CTkLabel(
            values_frame,
            text="Quadrature Homodyne Monitor",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(8, 4))

        self.label_phase = ctk.CTkLabel(
            values_frame,
            text="phase_rad = atan2(S2_norm, S1_norm) = 0.00000 rad",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_phase.pack(pady=2)

        self.label_s1_norm = ctk.CTkLabel(
            values_frame,
            text="S1_norm = (raw_S1 / raw_ref - offset_S1) / scale_S1 = n/a",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_s1_norm.pack(pady=2)

        self.label_s2_norm = ctk.CTkLabel(
            values_frame,
            text="S2_norm = (raw_S2 / raw_ref - offset_S2) / scale_S2 = n/a",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_s2_norm.pack(pady=2)

        self.label_unwrapped_phase = ctk.CTkLabel(
            values_frame,
            text="unwrapped_phase_rad += delta_phase_rad = 0.00000 rad",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_unwrapped_phase.pack(pady=2)

        self.label_fringe_position = ctk.CTkLabel(
            values_frame,
            text="fringe_position = unwrapped_phase_rad / (2*pi) = 0.0000",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_fringe_position.pack(pady=2)

        self.label_fringes = ctk.CTkLabel(
            values_frame,
            text="signed_fringes = 0",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_fringes.pack(pady=2)

        self.label_direction = ctk.CTkLabel(
            values_frame,
            text="Direction: Still",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_direction.pack(pady=2)

        self.label_distance = ctk.CTkLabel(
            values_frame,
            text="distance_mm = fringe_position * fringe_distance_mm = n/a",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_distance.pack(pady=2)

        # Stage lock and position status frame (Right Column)
        lock_frame = ctk.CTkFrame(self.right_col, fg_color="#EEEEEE")
        lock_frame.pack(fill="x", pady=4, padx=8)

        ctk.CTkLabel(
            lock_frame,
            text="Stage Lock & Status",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(8, 4))

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
        self.label_lock_correction.pack(pady=2)

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
        self.label_stage_position.pack(pady=2)

        # Stage movement comparison frame (Right Column)
        self.compare_frame = ctk.CTkFrame(self.right_col, fg_color="#EEEEEE")
        self.compare_frame.pack(fill="x", pady=4, padx=8)

        ctk.CTkLabel(
            self.compare_frame,
            text="Stage Movement Comparison",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(8, 4))

        self.compare_driven_frame = ctk.CTkFrame(self.compare_frame, fg_color="transparent")
        self.compare_driven_frame.pack(pady=2)

        self.label_compare_driven = ctk.CTkLabel(
            self.compare_driven_frame,
            text="Driven: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_compare_driven.grid(row=0, column=0, padx=14)

        self.label_still_to_drive = ctk.CTkLabel(
            self.compare_driven_frame,
            text="Still to drive: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_still_to_drive.grid(row=0, column=1, padx=14)

        self.label_compare_calculated = ctk.CTkLabel(
            self.compare_frame,
            text="Calculated from Fringes: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_compare_calculated.pack(pady=2)

        self.label_compare_difference = ctk.CTkLabel(
            self.compare_frame,
            text="Difference: n/a",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_compare_difference.pack(pady=2)

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
        ).pack(pady=(8, 8))

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

    def update_stage_ui_from_thread(self, position_mm, total_stage_movement):
        self.label_stage_position.configure(
            text=f"Stage position: {position_mm:.6f} mm"
        )
        self.update_still_to_drive_label(position_mm)
        self.update_comparison_labels(total_stage_movement)

    def update_comparison_labels(self, driven_mm=None):
        if driven_mm is None:
            driven_mm = self.current_stage_movement_for_compare

        driven_distance_mm = abs(driven_mm)
        calculated_mm = 0.0
        if self.monitor is not None and self.monitor.counter is not None:
            dist = self.monitor.counter.signed_distance_mm()
            if dist is not None:
                calculated_mm = abs(dist)

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

    def update_still_to_drive_label(self, pos=None):
        target_position = self.stage_target_position
        if target_position is None:
            self.stage_remaining_to_drive = 0.0
            self.stage_remaining_known = (
                not self.stage_connected
                or self.stage is None
                or not self.stage.is_moving
            )
        else:
            self.stage_remaining_known = True
            if pos is None:
                if self.stage_connected and self.stage is not None:
                    pos = self.stage.get_position()
                else:
                    pos = target_position
            self.stage_remaining_to_drive = abs(target_position - pos)
            if self.stage_remaining_to_drive < 1e-6:
                self.stage_remaining_to_drive = 0.0

        if hasattr(self, "label_still_to_drive"):
            if self.stage_remaining_known:
                label_text = f"Still to drive: {self.stage_remaining_to_drive:.6f} mm"
            else:
                label_text = "Still to drive: target unknown"
            self.label_still_to_drive.configure(text=label_text)

    def set_stage_target_position(self, target_mm, current_pos=None):
        self.stage_target_position = target_mm
        if current_pos is None:
            if self.stage_connected and self.stage is not None:
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
        movement_base = self.stage_movement_before_move
        while self.stage is not None and self.stage.is_moving:
            position_mm = self.stage.get_position()
            moved = abs(position_mm - self.stage_start_position)
            self.total_stage_movement = movement_base + moved
            self.current_stage_movement_for_compare = self.total_stage_movement

            self.root.after(
                0,
                lambda p=position_mm, t=self.total_stage_movement:
                self.update_stage_ui_from_thread(p, t)
            )

            time.sleep(0.05)

        position_mm = None

        if self.stage is not None and self.stage_connected:
            position_mm = self.stage.get_position()
            moved = abs(position_mm - self.stage_start_position)
            self.total_stage_movement = movement_base + moved
            self.current_stage_movement_for_compare = self.total_stage_movement

        self.root.after(
            0,
            lambda p=position_mm:
            self.finish_manual_stage_move(p)
        )

    def finish_manual_stage_move(self, position_mm):
        if position_mm is not None:
            self.stage_position_mm = position_mm
            moved = abs(position_mm - self.stage_start_position)
            self.total_stage_movement = self.stage_movement_before_move + moved
            self.current_stage_movement_for_compare = self.total_stage_movement
            self.update_stage_ui_from_thread(position_mm, self.total_stage_movement)

        self.clear_stage_target_position()

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

        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.set_stage_target_position(target_mm, start_pos)

        if abs(target_mm - start_pos) < 1e-12:
            self.status.configure(
                text="Status: stage already at target",
                text_color=TEXT_COLOR
            )
            self.label_stage_position.configure(
                text=f"Stage position: {start_pos:.6f} mm"
            )
            self.clear_stage_target_position()
            return

        self.stage_command_active = True
        self.set_stage_controls_enabled(False)

        if not self.stage.move_absolute(target_mm):
            self.finish_stage_command_ui()
            self.status.configure(
                text="Status: stage move failed",
                text_color=RED_COLOR
            )
            self.clear_stage_target_position()
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

        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.set_stage_target_position(target_mm, start_pos)

        if abs(target_mm - start_pos) < 1e-12:
            self.status.configure(
                text="Status: stage already at target",
                text_color=TEXT_COLOR
            )
            self.label_stage_position.configure(
                text=f"Stage position: {start_pos:.6f} mm"
            )
            self.clear_stage_target_position()
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

            self.stage_start_position = current_pos
            self.stage_movement_before_move = self.total_stage_movement
            self.set_stage_target_position(target_pos, current_pos)

            if not self.stage.move_absolute(target_pos):
                self.root.after(
                    0,
                    lambda:
                    self.status.configure(
                        text="Status: stage move failed during sweep",
                        text_color=RED_COLOR
                    )
                )
                self.clear_stage_target_position()
                break

            movement_base = self.stage_movement_before_move
            while self.stage.is_moving and self.monitoring:
                try:
                    sample = self.monitor.read()
                    distance_mm = self.monitor.counter.signed_distance_mm()
                except Exception:
                    sample = None
                    distance_mm = None

                position_mm = self.stage.get_position()
                moved = abs(position_mm - self.stage_start_position)
                self.total_stage_movement = movement_base + moved
                self.current_stage_movement_for_compare = self.total_stage_movement

                with self.sample_display_lock:
                    if sample is not None:
                        self.latest_sample = sample
                        self.latest_distance_mm = distance_mm
                        self.raw_s1_history.append(sample.raw_s1)
                        self.raw_s2_history.append(sample.raw_s2)
                        self.raw_ref_history.append(sample.raw_ref)
                        if len(self.raw_s1_history) > 300:
                            self.raw_s1_history.pop(0)
                            self.raw_s2_history.pop(0)
                            self.raw_ref_history.pop(0)

                self.root.after(
                    0,
                    lambda p=position_mm, t=self.total_stage_movement:
                    self.update_stage_ui_from_thread(p, t)
                )

                time.sleep(SAMPLE_INTERVAL_S)

            position_mm = self.stage.get_position()
            moved = abs(position_mm - self.stage_start_position)
            self.total_stage_movement = movement_base + moved
            self.current_stage_movement_for_compare = self.total_stage_movement
            self.root.after(
                0,
                lambda p=position_mm, t=self.total_stage_movement:
                self.update_stage_ui_from_thread(p, t)
            )

            self.clear_stage_target_position()

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
        movement_base = self.stage_movement_before_move

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
                    moved = abs(position_mm - self.stage_start_position)
                    self.total_stage_movement = movement_base + moved
                    self.current_stage_movement_for_compare = self.total_stage_movement
                    self.root.after(
                        0,
                        lambda p=position_mm, t=self.total_stage_movement:
                        self.update_stage_ui_from_thread(p, t)
                    )
                    time.sleep(0.05)

                current_pos = next_target
                remaining = abs(target_mm - current_pos)
                moved = abs(current_pos - self.stage_start_position)
                self.total_stage_movement = movement_base + moved
                self.current_stage_movement_for_compare = self.total_stage_movement
                self.root.after(
                    0,
                    lambda p=current_pos, t=self.total_stage_movement:
                    self.update_stage_ui_from_thread(p, t)
                )

                if remaining > 1e-12:
                    time.sleep(delay_s)

            if self.stage is not None and self.stage_connected:
                current_pos = self.stage.get_position()
                self.stage_position_mm = current_pos
                moved = abs(current_pos - self.stage_start_position)
                self.total_stage_movement = movement_base + moved
                self.current_stage_movement_for_compare = self.total_stage_movement
                self.root.after(
                    0,
                    lambda p=current_pos, t=self.total_stage_movement:
                    self.update_stage_ui_from_thread(p, t)
                )

            self.set_status_from_thread(
                f"Status: reached {current_pos:.6f} mm",
                GREEN_COLOR
            )
        finally:
            self.clear_stage_target_position()
            self.root.after(
                0,
                self.finish_stage_command_ui
            )

    def start_ui_loop(self):
        # Start periodic UI update task
        self.root.after(int(UI_UPDATE_INTERVAL_S * 1000), self.update_ui_loop)

    def update_ui_loop(self):
        if not self.monitoring and not self.calibrating:
            return

        # Retrieve values safely under lock
        with self.sample_display_lock:
            sample = self.latest_sample
            distance_mm = self.latest_distance_mm
            s1_hist = list(self.raw_s1_history)
            s2_hist = list(self.raw_s2_history)
            ref_hist = list(self.raw_ref_history)
            
            # Retrieve single counter state
            single_fringes = self.monitor.single_counter.accumulated_fringes
            single_distance = single_fringes * self.fringe_distance_mm
            single_min = self.monitor.single_counter.min_voltage
            single_max = self.monitor.single_counter.max_voltage
            single_amp = self.monitor.single_counter.fringe_amplitude_voltage
            
            # Progress label if calibrating
            calibrating = self.calibrating
            progress_text = getattr(self, 'calibration_progress_text', None)

        if calibrating:
            if progress_text:
                self.status.configure(text=progress_text, text_color=ORANGE_COLOR)
            self.update_plot()
        elif sample is not None:
            # Update single signal fringe counter labels (strictly English)
            self.label_single_fringes.configure(
                text=f"S1 Fringe Count: {single_fringes}"
            )
            self.label_single_distance.configure(
                text=f"S1 Calculated Distance: {single_distance:+.6f} mm"
            )
            self.label_single_thresholds.configure(
                text=f"S1 Thresholds: Min/Max = {single_min:+.4f}/{single_max:+.4f} V, Amp = {single_amp:.6f} V"
            )

            # Update quadrature homodyne labels (strictly English)
            self.label_phase.configure(
                text=f"phase_rad = atan2(S2_norm, S1_norm) = {sample.phase_rad:+.5f} rad" if sample.valid else "phase_rad = invalid"
            )
            if sample.direction == "reference_low":
                self.label_s1_norm.configure(text="S1_norm = raw_ref too low")
                self.label_s2_norm.configure(text="S2_norm = raw_ref too low")
            else:
                self.label_s1_norm.configure(
                    text=f"S1_norm = (raw_S1 / raw_ref - offset_S1) / scale_S1 = {sample.s1:+.6f}"
                )
                self.label_s2_norm.configure(
                    text=f"S2_norm = (raw_S2 / raw_ref - offset_S2) / scale_S2 = {sample.s2:+.6f}"
                )

            self.label_unwrapped_phase.configure(
                text=f"unwrapped_phase_rad += delta_phase_rad = {sample.unwrapped_phase_rad:+.5f} rad"
            )
            self.label_fringe_position.configure(
                text=f"fringe_position = unwrapped_phase_rad / (2*pi) = {sample.fringe_position:+.4f}"
            )
            self.label_fringes.configure(
                text=f"signed_fringes = {sample.signed_fringes:+d}"
            )
            
            # Format direction label in English
            dir_text = "Still"
            dir_color = ORANGE_COLOR
            if sample.direction == "forward":
                dir_text = "Forward →"
                dir_color = GREEN_COLOR
            elif sample.direction == "backward":
                dir_text = "Backward ←"
                dir_color = RED_COLOR
            elif sample.direction == "signal_low":
                dir_text = "Signal Low"
                dir_color = RED_COLOR
            elif sample.direction == "reference_low":
                dir_text = "Reference Low"
                dir_color = RED_COLOR

            self.label_direction.configure(
                text=f"Direction: {dir_text}",
                text_color=dir_color
            )

            if distance_mm is None:
                self.label_distance.configure(
                    text="distance_mm = fringe_position * fringe_distance_mm = n/a"
                )
            else:
                self.label_distance.configure(
                    text=f"distance_mm = fringe_position * fringe_distance_mm = {distance_mm:+.9f} mm"
                )

            # Update color highlight on fringe detection
            if sample.fringe_delta != 0:
                self.label_fringes.configure(text_color=GREEN_COLOR)
                self.root.after(
                    250,
                    lambda: self.label_fringes.configure(text_color=TEXT_COLOR)
                )

            # Stage lock correction check
            self.update_lock_display(sample, distance_mm)
            self.update_comparison_labels()
            
            # Replot the data
            self.update_plot()

        # Schedule next UI update
        self.root.after(int(UI_UPDATE_INTERVAL_S * 1000), self.update_ui_loop)

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

            # Start the UI update loop
            self.root.after(0, self.start_ui_loop)

            self.monitor.calibrate(
                seconds=CALIBRATION_SECONDS,
                sample_interval_s=SAMPLE_INTERVAL_S,
                should_continue=lambda: self.monitoring,
                sample_callback=self.handle_calibration_sample
            )

            if not self.monitoring:
                return

            self.calibrating = False

            self.root.after(
                0,
                lambda:
                self.status.configure(
                    text="Status: monitoring running",
                    text_color=GREEN_COLOR
                )
            )

            while self.monitoring:
                raw_s1, raw_s2, raw_ref = self.monitor.reader.read()
                
                # Correct S1 for reference fluctuations
                if abs(raw_ref) >= self.monitor.counter.min_reference_signal:
                    ref_corrected_s1 = raw_s1 / raw_ref
                else:
                    ref_corrected_s1 = 0.0
                
                # Run updates in background thread
                self.monitor.single_counter.update(ref_corrected_s1)
                sample = self.monitor.counter.update(raw_s1, raw_s2, raw_ref)
                distance_mm = self.monitor.counter.signed_distance_mm()

                # Lock and update histories
                with self.sample_display_lock:
                    self.latest_sample = sample
                    self.latest_distance_mm = distance_mm
                    self.raw_s1_history.append(raw_s1)
                    self.raw_s2_history.append(raw_s2)
                    self.raw_ref_history.append(raw_ref)
                    if len(self.raw_s1_history) > 300:
                        self.raw_s1_history.pop(0)
                        self.raw_s2_history.pop(0)
                        self.raw_ref_history.pop(0)

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
            self.calibrating = False
            try:
                self.monitor.close()
            except Exception:
                pass
            self.root.after(0, self.finish_stopped_ui)

    def handle_calibration_sample(self, raw_sample, elapsed_s, total_s):
        raw_s1, raw_s2, raw_ref = raw_sample
        with self.sample_display_lock:
            self.raw_s1_history.append(raw_s1)
            self.raw_s2_history.append(raw_s2)
            self.raw_ref_history.append(raw_ref)
            if len(self.raw_s1_history) > 300:
                self.raw_s1_history.pop(0)
                self.raw_s2_history.pop(0)
                self.raw_ref_history.pop(0)
            self.calibration_progress_text = f"Status: calibrating {elapsed_s:.1f}/{total_s:.1f}s..."

    def reset_calculation_display(self):
        self.label_single_fringes.configure(text="S1 Fringe Count: 0")
        self.label_single_distance.configure(text="S1 Calculated Distance: 0.000000 mm")
        self.label_single_thresholds.configure(text="S1 Thresholds: Min/Max = n/a, Amplitude = n/a")

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
            text="Direction: Still"
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
        self.monitor.single_counter.reset()
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
        if self.plot_axes is None or self.axis_circle is None:
            return

        if reset:
            self.plot_lines['S1_raw'].set_data([], [])
            self.plot_lines['S2_raw'].set_data([], [])
            self.plot_lines['Ref_raw'].set_data([], [])
            self.plot_lines['circle_trace'].set_data([], [])
            self.plot_lines['circle_current'].set_data([], [])
            self.plot_lines['circle_pointer'].set_data([], [])
            self.plot_quiver.set_visible(False)
            self.plot_canvas.draw_idle()
            self.plot_canvas_circle.draw_idle()
            return

        with self.sample_display_lock:
            s1_hist = list(self.raw_s1_history)
            s2_hist = list(self.raw_s2_history)
            ref_hist = list(self.raw_ref_history)

        self.update_plot_data(s1_hist, s2_hist, ref_hist)

    def update_plot_data(self, s1_hist, s2_hist, ref_hist):
        if self.plot_axes is None or self.axis_circle is None:
            return

        x = list(range(len(s1_hist)))
        
        # Update raw voltage plots
        self.plot_lines['S1_raw'].set_data(x, s1_hist)
        self.plot_axes['S1_raw'].relim()
        self.plot_axes['S1_raw'].autoscale_view()

        self.plot_lines['S2_raw'].set_data(x, s2_hist)
        self.plot_axes['S2_raw'].relim()
        self.plot_axes['S2_raw'].autoscale_view()

        self.plot_lines['Ref_raw'].set_data(x, ref_hist)
        self.plot_axes['Ref_raw'].relim()
        self.plot_axes['Ref_raw'].autoscale_view()

        # Update circle plot
        s1_norm_history = []
        s2_norm_history = []
        with self.monitor.counter.lock:
            offset_s1 = self.monitor.counter.offset_s1
            scale_s1 = self.monitor.counter.scale_s1
            offset_s2 = self.monitor.counter.offset_s2
            scale_s2 = self.monitor.counter.scale_s2
            min_reference_signal = self.monitor.counter.min_reference_signal

        for r1, r2, ref in zip(s1_hist, s2_hist, ref_hist):
            if abs(ref) >= min_reference_signal:
                ref_corrected_s1 = r1 / ref
                ref_corrected_s2 = r2 / ref
            else:
                ref_corrected_s1 = 0.0
                ref_corrected_s2 = 0.0
            
            s1 = (ref_corrected_s1 - offset_s1) / (scale_s1 if scale_s1 > 1e-12 else 1.0)
            s2 = (ref_corrected_s2 - offset_s2) / (scale_s2 if scale_s2 > 1e-12 else 1.0)
            s1_norm_history.append(s1)
            s2_norm_history.append(s2)

        # Smooth circle trace to reduce noise and triangular/jagged appearance
        smoothed_s1 = []
        smoothed_s2 = []
        window_size = 5
        for i in range(len(s1_norm_history)):
            start = max(0, i - window_size + 1)
            end = i + 1
            w1 = s1_norm_history[start:end]
            w2 = s2_norm_history[start:end]
            smoothed_s1.append(sum(w1) / len(w1))
            smoothed_s2.append(sum(w2) / len(w2))

        self.plot_lines['circle_trace'].set_data(smoothed_s1, smoothed_s2)
        
        if smoothed_s1:
            curr_x = smoothed_s1[-1]
            curr_y = smoothed_s2[-1]
            self.plot_lines['circle_current'].set_data([curr_x], [curr_y])
            self.plot_lines['circle_pointer'].set_data([0, curr_x], [0, curr_y])
            
            # Update tangent quiver arrow
            if self.latest_sample is not None and self.latest_sample.direction in ["forward", "backward"]:
                phi = math.atan2(curr_y, curr_x)
                if self.latest_sample.direction == "forward":
                    dx, dy = -math.sin(phi), math.cos(phi)
                    color = 'green'
                else:
                    dx, dy = math.sin(phi), -math.cos(phi)
                    color = 'red'
                
                arrow_len = 0.3
                self.plot_quiver.set_offsets([[curr_x, curr_y]])
                self.plot_quiver.set_UVC([arrow_len * dx], [arrow_len * dy])
                self.plot_quiver.set_color(color)
                self.plot_quiver.set_visible(True)
            else:
                self.plot_quiver.set_visible(False)
        else:
            self.plot_lines['circle_current'].set_data([], [])
            self.plot_lines['circle_pointer'].set_data([], [])
            self.plot_quiver.set_visible(False)

        self.plot_canvas.draw_idle()
        self.plot_canvas_circle.draw_idle()

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
