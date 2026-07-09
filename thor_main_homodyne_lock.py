# basically identical to homodyne.py, but we use the Thorlabs stage controller

# TABLE OF CONTENTS
# 1. Basic settings
# 2. Imports
# 3. Physical constants and colors
# 4. HomodyneGui class (UI)
# 5. Monitoring and reset
# 6. Translation stage control
# 7. Calibration
# 8. Diode loop and plotting
# 9. Cleanup and program start


# -----------------------------------------------------------------------------
# 1. BASIC SETTINGS
# -----------------------------------------------------------------------------

PHOTODIODE_CHANNEL_S1 = "Dev1/ai0"
PHOTODIODE_CHANNEL_S2 = "Dev1/ai1"

CALIBRATION_SECONDS = 5.0
CALIBRATION_STAGE_DISTANCE_MM = 0.01
CALIBRATION_STAGE_MOTION_SECONDS = CALIBRATION_SECONDS * 0.85
CALIBRATION_STAGE_SPEED_MM_S = (
    2 * CALIBRATION_STAGE_DISTANCE_MM
) / CALIBRATION_STAGE_MOTION_SECONDS

RAW_HISTORY_LENGTH = 300
STEP_PAUSE_S = 0.05
STAGE_STATUS_POLL_MS = 100

SAMPLE_INTERVAL_S = 0.005

# Threshold for classifying movement direction (reduces tiny jitter being labeled)
DIRECTION_THRESHOLD = 0.004

EXPECTED_FRINGE_AMPLITUDE_V = 0.010
MIN_FRINGE_TO_NOISE_RATIO = 5.0
DEFAULT_NOISE_AMPLITUDE_V = (
    EXPECTED_FRINGE_AMPLITUDE_V / MIN_FRINGE_TO_NOISE_RATIO
)
DEFAULT_FRINGE_AMPLITUDE_V = EXPECTED_FRINGE_AMPLITUDE_V
MIN_VALID_FRINGE_AMPLITUDE_V = 0.005
MAX_VALID_FRINGE_AMPLITUDE_V = 0.020
FRINGE_RISE_FRACTION = 0.50
FRINGE_REARM_FRACTION = 0.25
DARK_LEVEL_FRACTION = 0.30
BRIGHT_LEVEL_FRACTION = 0.55
SMOOTHING_WINDOW_LENGTH = 3
REQUIRED_DARK_FRAMES = 2
REQUIRED_BRIGHT_FRAMES = 2
MAX_FRINGE_WIDTH_FRAMES = 15
FRINGE_COOLDOWN = max(0.04, MAX_FRINGE_WIDTH_FRAMES * SAMPLE_INTERVAL_S)

MODE = "continuous"
VELOCITY_MM_S = 0.0006
TOTAL_DISTANCE_MM = 13.0

VELOCITY_MM_S_STEPPED = 1.00
STEP_SIZE_MM = 0.00001
STEPS = 100

UI_UPDATE_INTERVAL_S = 0.1

LOCK_TRIGGER_FRINGES = 1.0
LOCK_CORRECTION_COOLDOWN_S = 0.30

STAGE_CORRECTION_SIGN = -1
STAGE_MOVE_TIMEOUT_S = 60.0
STAGE_CHECK_TIMEOUT_S = 180.0
STAGE_POLL_INTERVAL_S = 0.05

# -----------------------------------------------------------------------------
# 2. IMPORTS
# -----------------------------------------------------------------------------

import math
import threading # so that camera and stage can run without freezing the UI
import time # for timestamps
from dataclasses import dataclass
import tkinter.simpledialog as sd

try:
    import customtkinter as ctk # pythons standard UI library
except ImportError:
    ctk = None

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    plt = None
    FigureCanvasTkAgg = None

try:
    from thor_handler_stage import StageController
except Exception as stage_import_error:
    StageController = None
    STAGE_IMPORT_ERROR = str(stage_import_error)
else:
    STAGE_IMPORT_ERROR = None

# -----------------------------------------------------------------------------
# 3. PHYSICAL CONSTANTS
# -----------------------------------------------------------------------------

LASER_WAVELENGTH_NM = 787.3
SPEED_OF_LIGHT_MM_PS = 0.299792458

PHASE_DIRECTION_SIGN = 1

MIN_SIGNAL_RADIUS = 0.05
MIN_VISIBLE_FRINGE_AMPLITUDE_V = 0.004
MAX_VISIBLE_FRINGE_AMPLITUDE_V = 0.060

DEFAULT_STAGE_SPEED_MM_S = 0.000600
def compute_fringe_distance_mm(wavelength_nm):
    return (wavelength_nm / 2) / 1_000_000

def wrap_to_pi(angle_rad):
    return (angle_rad + math.pi) % (2 * math.pi) - math.pi

def completed_signed_fringes(fringe_position):
    if fringe_position == 0:
        return 0

    sign = 1 if fringe_position > 0 else -1
    return sign * math.floor(abs(fringe_position))

# -----------------------------------------------------------------------------
# 3.1 COLORS AND FILTER TIMINGS
# -----------------------------------------------------------------------------

TEXT_COLOR = "#0A4A51"
GREEN_COLOR = "#1EAD4F"
RED_COLOR = "#C0392B"
ORANGE_COLOR = "#D35400"

# -----------------------------------------------------------------------------
# 3.2 HELPER CLASSES AND DATACLASSES
# -----------------------------------------------------------------------------

@dataclass
class HomodyneSample:
    timestamp: float
    raw_s1: float
    raw_s2: float
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
    # -----------------------------------------------------------------------------
    # 4.1 INITIALIZATION
    # -----------------------------------------------------------------------------

    def __init__(
        self,
        channel_s1=PHOTODIODE_CHANNEL_S1,
        channel_s2=PHOTODIODE_CHANNEL_S2
    ):
        self.channel_s1 = channel_s1
        self.channel_s2 = channel_s2
        self.task = None
        self.nidaqmx = None

    def connect(self):
        import nidaqmx

        self.nidaqmx = nidaqmx
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(self.channel_s1)
        self.task.ai_channels.add_ai_voltage_chan(self.channel_s2)
        return True

    def read(self):
        if self.task is None:
            raise RuntimeError("NI task is not connected.")

        values = self.task.read()

        if len(values) != 2:
            raise RuntimeError(
                "Expected two analog input values from the NI task."
            )

        return float(values[0]), float(values[1])

    def close(self):
        if self.task is not None:
            self.task.close()
            self.task = None

class SingleSignalFringeCounter:
    # -----------------------------------------------------------------------------
    # 4.1 INITIALIZATION
    # -----------------------------------------------------------------------------

    def __init__(self, sample_interval_s=0.005):
        self.sample_interval_s = sample_interval_s
        self.min_voltage = 0.0
        self.max_voltage = 0.0
        self.offset_voltage = 0.0
        self.scale_voltage = 1.0

        self.fringe_amplitude_voltage = DEFAULT_FRINGE_AMPLITUDE_V
        self.fringe_rise_threshold_voltage = (
            DEFAULT_FRINGE_AMPLITUDE_V * FRINGE_RISE_FRACTION
        )
        self.fringe_rearm_threshold_voltage = (
            DEFAULT_FRINGE_AMPLITUDE_V * FRINGE_REARM_FRACTION
        )
        self.fringe_trough_voltage = None
        self.fringe_peak_voltage = None
        self.dark_threshold = 0.0
        self.bright_threshold = 0.0
        self.fringes_visible = False

        self.smoothed_voltage_history = []
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0
        self.accumulated_fringes = 0

    def calibrate(self, s1_values):
        self.fringes_visible = False

        if not s1_values:
            return

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

        amplitude = DEFAULT_FRINGE_AMPLITUDE_V
        visible_amplitude = False
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
                    if (
                        MIN_VISIBLE_FRINGE_AMPLITUDE_V
                        <= amp
                        <= MAX_VISIBLE_FRINGE_AMPLITUDE_V
                    ):
                        amplitudes.append(amp)
            if amplitudes:
                amplitudes.sort()
                upper_half = amplitudes[len(amplitudes) // 2:]
                amplitude = sum(upper_half) / len(upper_half)
                visible_amplitude = True

        self.fringe_amplitude_voltage = amplitude
        detection_amplitude_voltage = min(
            self.fringe_amplitude_voltage,
            EXPECTED_FRINGE_AMPLITUDE_V
        )
        self.fringe_rise_threshold_voltage = (
            detection_amplitude_voltage * 0.98
        )
        self.fringe_rearm_threshold_voltage = (
            detection_amplitude_voltage * 0.98
        )
        self.fringes_visible = visible_amplitude

        value_range = self.max_voltage - self.min_voltage
        self.dark_threshold = self.min_voltage + value_range * DARK_LEVEL_FRACTION
        self.bright_threshold = self.min_voltage + value_range * BRIGHT_LEVEL_FRACTION

        self.reset()

    def reset(self):
        self.fringe_trough_voltage = None
        self.fringe_peak_voltage = None
        self.smoothed_voltage_history = []
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0
        self.accumulated_fringes = 0

    def update(self, voltage):
        self.smoothed_voltage_history.append(voltage)
        if len(self.smoothed_voltage_history) > SMOOTHING_WINDOW_LENGTH:
            self.smoothed_voltage_history.pop(0)
        smooth_voltage = (
            sum(self.smoothed_voltage_history) / len(self.smoothed_voltage_history)
        )

        if self.fringe_trough_voltage is None:
            self.fringe_trough_voltage = smooth_voltage
            self.fringe_peak_voltage = smooth_voltage
            return False

        if self.fringe_peak_voltage is None:
            self.fringe_peak_voltage = smooth_voltage

        cooldown_ok = (time.time() - self.last_count_time) > FRINGE_COOLDOWN

        if not self.was_dark:
            if smooth_voltage > self.fringe_peak_voltage:
                self.fringe_peak_voltage = smooth_voltage

            enough_drop_from_peak = (
                self.fringe_peak_voltage - smooth_voltage
            ) >= self.fringe_rearm_threshold_voltage
            below_dark_level = smooth_voltage <= self.dark_threshold
            started_near_trough = (
                self.fringe_peak_voltage - self.fringe_trough_voltage
            ) < self.fringe_rearm_threshold_voltage

            if (
                enough_drop_from_peak
                or below_dark_level
                or started_near_trough
            ):
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

        rise_from_trough = smooth_voltage - self.fringe_trough_voltage
        peak_is_large_enough = rise_from_trough >= self.fringe_rise_threshold_voltage

        if peak_is_large_enough:
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

class HomodyneQuadratureCounter:
    # -----------------------------------------------------------------------------
    # 4.1 INITIALIZATION
    # -----------------------------------------------------------------------------

    def __init__(
        self,
        phase_direction_sign=PHASE_DIRECTION_SIGN,
        min_signal_radius=MIN_SIGNAL_RADIUS,
        fringe_distance_mm=None
    ):
        self.lock = threading.Lock()
        self.phase_direction_sign = 1 if phase_direction_sign >= 0 else -1
        self.min_signal_radius = min_signal_radius
        self.fringe_distance_mm = fringe_distance_mm

        self.offset_s1 = 0.0
        self.offset_s2 = 0.0
        self.scale_s1 = 1.0
        self.scale_s2 = 1.0

        self.previous_phase_rad = None
        self.unwrapped_phase_rad = 0.0
        self.signed_fringes = 0
        self.total_abs_fringes = 0
        self.s1_fringes_visible = False
        self.s2_fringes_visible = False
        self.current_direction = "none"
        self.center_s1 = 0.0
        self.center_s2 = 0.0

    def calibrate_from_samples(self, raw_samples):
        with self.lock:
            if not raw_samples:
                raise ValueError("No calibration samples were collected.")

            s1_values = [sample[0] for sample in raw_samples]
            s2_values = [sample[1] for sample in raw_samples]

            self.offset_s1 = (min(s1_values) + max(s1_values)) / 2
            self.offset_s2 = (min(s2_values) + max(s2_values)) / 2

            self.scale_s1 = (max(s1_values) - min(s1_values)) / 2
            self.scale_s2 = (max(s2_values) - min(s2_values)) / 2

            if self.scale_s1 <= 1e-12:
                self.scale_s1 = 1.0

            if self.scale_s2 <= 1e-12:
                self.scale_s2 = 1.0

            self.center_s1 = self.offset_s1
            self.center_s2 = self.offset_s2

            self._reset_unlocked()

    def set_signal_visibility(self, s1_visible, s2_visible):
        with self.lock:
            self.s1_fringes_visible = bool(s1_visible)
            self.s2_fringes_visible = bool(s2_visible)

            if not self.signals_visible_unlocked():
                self._reset_unlocked()

    def signals_visible_unlocked(self):
        return self.s1_fringes_visible and self.s2_fringes_visible

    def signals_visible(self):
        with self.lock:
            return self.signals_visible_unlocked()

    def reset(self):
        with self.lock:
            self._reset_unlocked()

    def _reset_unlocked(self):
        self.previous_phase_rad = None
        self.unwrapped_phase_rad = 0.0
        self.signed_fringes = 0
        self.total_abs_fringes = 0
        self.delta_phase_history = []
        self.current_direction = "none"
        self.center_s1 = self.offset_s1
        self.center_s2 = self.offset_s2

    def normalize(self, raw_s1, raw_s2):
        s1 = (raw_s1 - self.offset_s1) / self.scale_s1
        s2 = (raw_s2 - self.offset_s2) / self.scale_s2
        return s1, s2

    def update(self, raw_s1, raw_s2):
        with self.lock:
            timestamp = time.time()

            # Slowly update the center tracking to follow DC drift
            if self.center_s1 is None or self.center_s1 == 0.0:
                self.center_s1 = raw_s1
                self.center_s2 = raw_s2
            else:
                alpha = 0.002  # time constant ~ 500 samples = 2.5 seconds
                self.center_s1 = alpha * raw_s1 + (1 - alpha) * self.center_s1
                self.center_s2 = alpha * raw_s2 + (1 - alpha) * self.center_s2

            s1_centered = (raw_s1 - self.center_s1) / (self.scale_s1 if self.scale_s1 > 1e-12 else 1.0)
            s2_centered = (raw_s2 - self.center_s2) / (self.scale_s2 if self.scale_s2 > 1e-12 else 1.0)
            radius = math.hypot(s1_centered, s2_centered)

            s1, s2 = self.normalize(raw_s1, raw_s2)

            if not self.signals_visible_unlocked():
                return HomodyneSample(
                    timestamp=timestamp,
                    raw_s1=raw_s1,
                    raw_s2=raw_s2,
                    s1=s1,
                    s2=s2,
                    radius=radius,
                    phase_rad=0.0,
                    unwrapped_phase_rad=self.unwrapped_phase_rad,
                    delta_phase_rad=0.0,
                    fringe_position=self.unwrapped_phase_rad / (2 * math.pi),
                    signed_fringes=self.signed_fringes,
                    fringe_delta=0,
                    direction="fringes_not_visible",
                    valid=False
                )

            if radius < self.min_signal_radius:
                return HomodyneSample(
                    timestamp=timestamp,
                    raw_s1=raw_s1,
                    raw_s2=raw_s2,
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

            phase_rad = self.phase_direction_sign * math.atan2(s2_centered, s1_centered)

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
            if len(self.delta_phase_history) > 120:
                self.delta_phase_history.pop(0)

            avg_delta_phase = sum(self.delta_phase_history) / len(self.delta_phase_history)
            
            # Hysteresis parameters for direction detection to avoid jitter
            threshold = 0.003
            release_threshold = 0.001

            if self.current_direction == "none":
                if avg_delta_phase > threshold:
                    self.current_direction = "forward"
                elif avg_delta_phase < -threshold:
                    self.current_direction = "backward"
            elif self.current_direction == "forward":
                if avg_delta_phase < release_threshold:
                    if avg_delta_phase < -threshold:
                        self.current_direction = "backward"
                    else:
                        self.current_direction = "none"
            elif self.current_direction == "backward":
                if avg_delta_phase > -release_threshold:
                    if avg_delta_phase > threshold:
                        self.current_direction = "forward"
                    else:
                        self.current_direction = "none"

            direction = self.current_direction

            return HomodyneSample(
                timestamp=timestamp,
                raw_s1=raw_s1,
                raw_s2=raw_s2,
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
            if (
                self.fringe_distance_mm is None
                or not self.signals_visible_unlocked()
            ):
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
    # -----------------------------------------------------------------------------
    # 4.1 INITIALIZATION
    # -----------------------------------------------------------------------------

    def __init__(
        self,
        channel_s1=PHOTODIODE_CHANNEL_S1,
        channel_s2=PHOTODIODE_CHANNEL_S2,
        wavelength_nm=LASER_WAVELENGTH_NM,
        phase_direction_sign=PHASE_DIRECTION_SIGN
    ):
        fringe_distance_mm = compute_fringe_distance_mm(wavelength_nm)
        self.reader = NIPhotodiodeReader(channel_s1, channel_s2)
        self.counter = HomodyneQuadratureCounter(
            phase_direction_sign=phase_direction_sign,
            fringe_distance_mm=fringe_distance_mm
        )
        self.single_counter = SingleSignalFringeCounter(sample_interval_s=SAMPLE_INTERVAL_S)
        self.s2_visibility_counter = SingleSignalFringeCounter(
            sample_interval_s=SAMPLE_INTERVAL_S
        )

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
            return None

        self.counter.calibrate_from_samples(samples)
        s1_values = [sample[0] for sample in samples]
        s2_values = [sample[1] for sample in samples]
        self.single_counter.calibrate(s1_values)
        self.s2_visibility_counter.calibrate(s2_values)
        self.counter.set_signal_visibility(
            self.single_counter.fringes_visible,
            self.s2_visibility_counter.fringes_visible
        )
        return samples

    def read(self):
        raw_s1, raw_s2 = self.reader.read()
        self.single_counter.update(raw_s2)
        return self.counter.update(raw_s1, raw_s2)

    def close(self):
        self.reader.close()

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

# -----------------------------------------------------------------------------
# 4. APP CLASS (UI)
# -----------------------------------------------------------------------------

class HomodyneGui:
    # -----------------------------------------------------------------------------
    # 4.1 INITIALIZATION
    # -----------------------------------------------------------------------------

    #ctk.CTk is the base class for the customtkinter window, here we inherit our InterferometerApp class from it
    def __init__(self):
        if ctk is None:
            raise RuntimeError(
                "customtkinter is not installed. Install requirements.txt first."
            )

        ctk.set_appearance_mode("light")

        self.root = ctk.CTk()
        self.root.title("Homodyne Quadrature Monitor")
        self.root.geometry("900x850")
        self.root.minsize(760, 650)
        self.root.configure(fg_color="white")

        #creates a scrollable frame inside the window
        self.scroll = ctk.CTkScrollableFrame(
            self.root,
            fg_color="white"
        )
        #the scrollable frame is put into the window
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
        self.sample_display_lock = threading.Lock()
        self.pending_sample = None
        self.pending_distance_mm = None
        self.sample_display_scheduled = False
        self.last_sample_display_time = 0.0

        # Data recording variables
        self.recording = False
        self.recorded_data = []
        self.recording_start_time = None
        
        # Measurement state variables
        self.measuring = False
        self.calibrating = False

        self.stage = StageController() if StageController is not None else None
        if self.stage is not None:
            self.stage.set_velocity(DEFAULT_STAGE_SPEED_MM_S, 0.0)
        self.stage_connected = False
        if self.stage is not None:
            try:
                self.stage_connected = self.stage.connect()
            except Exception as stage_err:
                print("Stage connection error:", stage_err)

        #stores values for all the start positions
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
        self.stage_command_active = False

        self.latest_sample = None
        self.latest_distance_mm = None
        self.last_error_text = None

        #for stage locking
        self.lock_active = False # state of the position lock
        self.lock_reference_distance_mm = 0.0
        self.lock_reference_phase_rad = 0.0
        self.lock_reference_fringes = 0
        self.lock_stage_position_mm = 0.0
        self.lock_ref_single_fringes = 0
        self.stage_position_mm = 0.0
        self.lock_correction_active = False
        self.lock_last_correction_time = 0.0
        self.lock_target_position_mm = None

        self.build_ui()
        self.update_comparison_labels() # renewing the text in the UI matching the initial update of the comparison labels with 0 values using e.g self.current_stage_movement_for_compare which is 0 at the beginning
        self.update_stage_position_once() # reads the current stage position and updates the label, this is important to have the correct position at the beginning
        self.root.after(
            STAGE_STATUS_POLL_MS,
            self.poll_stage_status
        )
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # -----------------------------------------------------------------------------
    # 4.1.2 UI BUILD
    # -----------------------------------------------------------------------------

    def build_ui(self):
        self.status = ctk.CTkLabel(
            self.scroll,
            text="Status: stopped",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.status.pack(pady=(16, 12))

        control_frame = ctk.CTkFrame(self.scroll, fg_color="#EEEEEE")
        control_frame.pack(fill="x", padx=18, pady=8)
        control_frame.grid_columnconfigure(0, weight=2)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)
        control_frame.grid_columnconfigure(3, weight=2)

        self.btn_start = ctk.CTkButton(
            control_frame,
            text="START MONITORING",
            width=150,
            command=self.toggle_monitoring,
            fg_color=TEXT_COLOR,
            font=("Arial", 12, "bold")
        )
        self.btn_start.grid(row=0, column=0, padx=8, pady=14, sticky="ew")

        self.btn_lock = ctk.CTkButton(
            control_frame,
            text="LOCK",
            width=110,
            command=self.toggle_lock,
            fg_color=TEXT_COLOR,
            font=("Arial", 12, "bold")
        )
        self.btn_lock.grid(row=0, column=1, padx=8, pady=14, sticky="ew")

        self.btn_reset = ctk.CTkButton(
            control_frame,
            text="RESET",
            width=110,
            command=self.reset_monitor,
            fg_color=ORANGE_COLOR,
            font=("Arial", 12, "bold")
        )
        self.btn_reset.grid(row=0, column=2, padx=8, pady=14, sticky="ew")

        self.btn_record = ctk.CTkButton(
            control_frame,
            text="START RECORDING",
            width=150,
            command=self.toggle_recording,
            fg_color="#555555",
            font=("Arial", 12, "bold")
        )
        self.btn_record.grid(row=0, column=3, padx=8, pady=14, sticky="ew")

        self.stage_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )
        self.stage_frame.pack(
            fill="x",
            padx=18,
            pady=8
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
            text="Set wavelength (nm)",
            width=120,
            command=self.apply_wavelength,
            fg_color=TEXT_COLOR
        )
        self.wavelength_button.pack(pady=1)

        self.label_fringe_distance = ctk.CTkLabel(
            self.stage_frame,
            text=self.fringe_distance_text(),
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_fringe_distance.pack(pady=2)

        ctk.CTkLabel(
            self.stage_frame,
            text="Step size (mm):",
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
            f"{self.stage_step_mm:.9f}"
        )

        ctk.CTkLabel(
            self.stage_frame,
            text="Velocity (mm):",
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
        if self.stage_connected and self.stage is not None:
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

        self.btn_min = ctk.CTkButton(
            self.button_frame,
            text="|<",
            width=60,
            command=self.move_to_min,
            fg_color=TEXT_COLOR
        )
        self.btn_min.grid(row=0, column=0, padx=1)

        self.btn_left = ctk.CTkButton(
            self.button_frame,
            text="<",
            width=60,
            command=self.step_negative,
            fg_color=TEXT_COLOR
        )
        self.btn_left.grid(row=0, column=1, padx=1)

        self.btn_center = ctk.CTkButton(
            self.button_frame,
            text="0",
            width=60,
            command=self.move_to_center,
            fg_color=TEXT_COLOR
        )
        self.btn_center.grid(row=0, column=2, padx=1)

        self.btn_right = ctk.CTkButton(
            self.button_frame,
            text=">",
            width=60,
            command=self.step_positive,
            fg_color=TEXT_COLOR
        )
        self.btn_right.grid(row=0, column=3, padx=1)

        self.btn_max = ctk.CTkButton(
            self.button_frame,
            text=">|",
            width=60,
            command=self.move_to_max,
            fg_color=TEXT_COLOR
        )
        self.btn_max.grid(row=0, column=4, padx=1)

        ctk.CTkLabel(
            self.stage_frame,
            text="or",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=3)

        ctk.CTkLabel(
            self.stage_frame,
            text="Target or Distance (mm):",
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
        self.target_button_frame.pack(fill="x", padx=12, pady=1)
        self.target_button_frame.grid_columnconfigure(0, weight=1)
        self.target_button_frame.grid_columnconfigure(1, weight=1)
        self.target_button_frame.grid_columnconfigure(2, weight=1)
        self.target_button_frame.grid_columnconfigure(3, weight=1)

        self.btn_target_abs = ctk.CTkButton(
            self.target_button_frame,
            text="Go to target",
            width=120,
            command=self.move_to_target,
            fg_color=TEXT_COLOR
        )
        self.btn_target_abs.grid(row=0, column=0, padx=1, sticky="ew")

        self.btn_target_rel = ctk.CTkButton(
            self.target_button_frame,
            text="Move distance",
            width=120,
            command=self.move_distance,
            fg_color=TEXT_COLOR
        )
        self.btn_target_rel.grid(row=0, column=1, padx=1, sticky="ew")

        self.btn_ref_measurement = ctk.CTkButton(
            self.target_button_frame,
            text="Ref Measurement",
            width=120,
            command=self.start_ref_measurement,
            fg_color=TEXT_COLOR
        )
        self.btn_ref_measurement.grid(row=0, column=2, padx=1, sticky="ew")

        self.btn_stop = ctk.CTkButton(
            self.target_button_frame,
            text="STOP STAGE",
            width=120,
            command=self.stop_stage,
            fg_color=RED_COLOR,
            font=("Arial", 11, "bold")
        )
        self.btn_stop.grid(row=0, column=3, padx=1, sticky="ew")

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

        self.all_buttons = [
            self.btn_reset,
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

        self.cols_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.cols_frame.pack(fill="both", expand=True, padx=18, pady=8)
        self.cols_frame.grid_columnconfigure(0, weight=3, uniform="cols")
        self.cols_frame.grid_columnconfigure(1, weight=2, uniform="cols")
        self.cols_frame.grid_rowconfigure(0, weight=1)

        self.left_col = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.right_col = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        plot_frame = ctk.CTkFrame(self.left_col, fg_color="#EEEEEE")
        plot_frame.pack(fill="x", expand=False, pady=4)

        ctk.CTkLabel(
            plot_frame,
            text="Raw Signal",
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
            self.plot_figure = plt.Figure(figsize=(5.0, 2.6), dpi=100)
            axes = self.plot_figure.subplots(2, 1, sharex=True)
            self.plot_axis = axes[0]
            self.plot_axes = {
                'S1_raw': axes[0],
                'S2_raw': axes[1]
            }

            plot_specs = {
                'S1_raw': ("S1 raw voltage", 'blue', 'S1 raw', 'S1 clean'),
                'S2_raw': ("S2 raw voltage", 'green', 'S2 raw', 'S2 clean')
            }

            self.plot_lines = {}
            for key in ['S1_raw', 'S2_raw']:
                axis = self.plot_axes[key]
                title, color, label_raw, label_clean = plot_specs[key]
                axis.set_title(title, fontsize=9)
                axis.grid(True, linestyle=':', alpha=0.6)
                axis.set_ylabel("Voltage", fontsize=8)
                axis.tick_params(labelsize=8)
                self.plot_lines[key] = axis.plot(
                    [],
                    [],
                    color=color,
                    alpha=0.3,
                    label=label_raw
                )[0]
                self.plot_lines[key + '_clean'] = axis.plot(
                    [],
                    [],
                    color=color,
                    linewidth=1.5,
                    label=label_clean
                )[0]
                self.plot_lines[key + '_fit'] = axis.plot(
                    [],
                    [],
                    color='orange' if key == 'S1_raw' else 'magenta',
                    linestyle='--',
                    label=label_raw.split()[0] + ' fit'
                )[0]
                axis.legend(loc="upper right", prop={"size": 8})

            axes[1].set_xlabel("Samples", fontsize=8)
            self.plot_figure.subplots_adjust(
                left=0.12,
                right=0.98,
                top=0.88,
                bottom=0.18,
                hspace=0.55
            )
            self.plot_canvas = FigureCanvasTkAgg(
                self.plot_figure,
                master=plot_frame
            )
            self.plot_canvas.draw()
            plot_widget = self.plot_canvas.get_tk_widget()
            plot_widget.configure(height=260)
            plot_widget.pack(fill="x", expand=False, padx=8, pady=(4, 8))

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
            text="Signal amplitudes: S1 = n/a, S2 = n/a",
            font=("Arial", 11),
            text_color=TEXT_COLOR,
            wraplength=320
        )
        self.label_single_thresholds.pack(pady=2)

        self.plot_frame_circle = ctk.CTkFrame(self.right_col, fg_color="#EEEEEE")
        self.plot_frame_circle.pack(fill="both", expand=True, pady=4)

        ctk.CTkLabel(
            self.plot_frame_circle,
            text="Lissajous",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(10, 4))

        self.label_lissajous_direction = ctk.CTkLabel(
            self.plot_frame_circle,
            text="STILL",
            font=("Arial", 22, "bold"),
            text_color=ORANGE_COLOR
        )
        self.label_lissajous_direction.pack(pady=(2, 6))

        if plt is None or FigureCanvasTkAgg is None:
            self.plot_canvas_circle = None
            self.axis_circle = None
        else:
            self.plot_figure_circle = plt.Figure(figsize=(4.0, 4.0), dpi=100)
            self.axis_circle = self.plot_figure_circle.add_subplot(111)

            self.axis_circle.set_title("Lissajous Circle (S1 vs S2)")
            self.axis_circle.set_xlabel("S1 (normalized)")
            self.axis_circle.set_ylabel("S2 (normalized)")
            self.axis_circle.grid(True, linestyle=':', alpha=0.6)
            self.axis_circle.set_aspect('equal', adjustable='box')
            self.axis_circle.set_xlim(-1.5, 1.5)
            self.axis_circle.set_ylim(-1.5, 1.5)

            ref_theta = [t * 2 * math.pi / 100 for t in range(101)]
            ref_x = [math.cos(t) for t in ref_theta]
            ref_y = [math.sin(t) for t in ref_theta]
            # keep a handle so we can scale the reference circle when autoscaling axes
            self.plot_lines['ref_circle'] = self.axis_circle.plot(
                ref_x,
                ref_y,
                color='gray',
                linestyle='--',
                alpha=0.5,
                label='Ref Circle'
            )[0]

            self.plot_lines['circle_trace'] = self.axis_circle.plot(
                [],
                [],
                color='purple',
                alpha=0.6,
                label='Trace'
            )[0]

            self.plot_lines['circle_current'] = self.axis_circle.plot(
                [],
                [],
                'ro',
                markersize=8,
                label='Current'
            )[0]

            self.plot_lines['circle_pointer'] = self.axis_circle.plot(
                [],
                [],
                color='orange',
                linestyle='-',
                linewidth=2,
                label='Pointer'
            )[0]

            self.plot_quiver = self.axis_circle.quiver(
                [0], [0], [0], [0],
                angles='xy', scale_units='xy', scale=1,
                color='green', width=0.015, headwidth=4, headlength=5
            )
            self.plot_quiver.set_visible(False)

            # self.axis_circle.legend(loc="upper right")
            self.plot_figure_circle.tight_layout()
            self.plot_canvas_circle = FigureCanvasTkAgg(
                self.plot_figure_circle,
                master=self.plot_frame_circle
            )
            self.plot_canvas_circle.draw()
            self.plot_canvas_circle.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Create dummy labels that are not packed to avoid AttributeError in other methods
        dummy_parent = ctk.CTkFrame(self.right_col)
        self.label_phase = ctk.CTkLabel(dummy_parent)
        self.label_s1_norm = ctk.CTkLabel(dummy_parent)
        self.label_s2_norm = ctk.CTkLabel(dummy_parent)
        self.label_unwrapped_phase = ctk.CTkLabel(dummy_parent)
        self.label_fringe_position = ctk.CTkLabel(dummy_parent)
        self.label_fringes = ctk.CTkLabel(dummy_parent)
        self.label_direction = ctk.CTkLabel(dummy_parent)
        self.label_distance = ctk.CTkLabel(dummy_parent)
        self.label_lock_status = ctk.CTkLabel(dummy_parent)
        self.label_lock_reference = ctk.CTkLabel(dummy_parent)
        self.label_lock_drift = ctk.CTkLabel(dummy_parent)
        self.label_lock_correction = ctk.CTkLabel(dummy_parent)
        self.label_stage_status = ctk.CTkLabel(dummy_parent)
        self.label_stage_position_lock = ctk.CTkLabel(dummy_parent)

        self.compare_frame = ctk.CTkFrame(self.left_col, fg_color="#EEEEEE")
        self.compare_frame.pack(fill="x", pady=4, padx=0)

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

        self.btn_measurement = ctk.CTkButton(
            self.compare_frame,
            text="START MEASUREMENT",
            command=self.toggle_measurement,
            fg_color=TEXT_COLOR,
            font=("Arial", 12, "bold")
        )
        self.btn_measurement.pack(pady=(6, 10))

        # Create Lock Box Frame under start measurement
        self.lock_box_frame = ctk.CTkFrame(self.left_col, fg_color="#EEEEEE")
        self.lock_box_frame.pack(fill="x", pady=8, padx=0)

        ctk.CTkLabel(
            self.lock_box_frame,
            text="Stage Lock",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(8, 4))

        self.label_lock_status_box = ctk.CTkLabel(
            self.lock_box_frame,
            text="Lock Status: off",
            font=("Arial", 12, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_lock_status_box.pack(pady=2)

        self.label_fringes_since_locking = ctk.CTkLabel(
            self.lock_box_frame,
            text="Fringes since locking: n/a",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_fringes_since_locking.pack(pady=2)

        self.label_correction_since_locking = ctk.CTkLabel(
            self.lock_box_frame,
            text="Correction since locking: n/a",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        self.label_correction_since_locking.pack(pady=2)

        self.btn_lock_box = ctk.CTkButton(
            self.lock_box_frame,
            text="LOCK",
            command=self.toggle_lock,
            fg_color=TEXT_COLOR,
            font=("Arial", 12, "bold")
        )
        self.btn_lock_box.pack(pady=(6, 8))

        channel_text = (
            f"Channels: S1={PHOTODIODE_CHANNEL_S1}, "
            f"S2={PHOTODIODE_CHANNEL_S2}"
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

    # -----------------------------------------------------------------------------
    # 5.8 APPLY A NEW LASER WAVELENGTH
    # -----------------------------------------------------------------------------

    def apply_wavelength(self):
        if self.lock_active:
            self.status.configure(
                text="Status: unlock before changing wavelength",
                text_color=ORANGE_COLOR
            )
            return

        # get the new laser wavelenght from the UI
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
        #clear old suggested stepsize
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

    # -----------------------------------------------------------------------------
    # 4.2 ENABLE OR DISABLE ALL BUTTONS
    # -----------------------------------------------------------------------------

    def set_buttons_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        for button in self.all_buttons:
            button.configure(state=state)

    def finish_stage_command_ui(self):
        self.stage_command_active = False
        self.set_buttons_enabled(True)

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
                text=f"Stage Position: {p:.6f} mm"
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

    def toggle_recording(self):
        import time
        from tkinter import messagebox
        
        if self.recording:
            # Stop recording and save
            self.recording = False
            self.btn_record.configure(
                text="START RECORDING",
                fg_color="#555555"
            )
            self.save_recorded_data()
        else:
            # Start recording
            if not self.monitoring:
                messagebox.showwarning(
                    "Aufnahme",
                    "Bitte starten Sie zuerst das Monitoring (START MONITORING)."
                )
                return
            
            self.recorded_data = []
            self.recording_start_time = time.time()
            self.recording = True
            self.btn_record.configure(
                text="REC ● STOP",
                fg_color=RED_COLOR
            )

    def save_recorded_data(self):
        import datetime
        import csv
        from tkinter import filedialog, messagebox

        if not self.recorded_data:
            messagebox.showinfo("Aufnahme", "Keine Messdaten zum Speichern vorhanden.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Messdaten speichern",
            initialfile=f"messung_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if file_path:
            try:
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Relative_Time_s",
                        "Raw_S1_V",
                        "Raw_S2_V",
                        "Norm_S1",
                        "Norm_S2",
                        "Phase_rad",
                        "Unwrapped_Phase_rad",
                        "Lissajous_Distance_mm",
                        "Calculated_Distance_mm",
                        "Fringe_Count",
                        "Stage_Position_mm"
                    ])
                    writer.writerows(self.recorded_data)
                messagebox.showinfo("Erfolg", f"Daten erfolgreich in '{file_path}' gespeichert!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern der Datei:\n{str(e)}")

    def toggle_measurement(self):
        from tkinter import messagebox
        if self.lock_active:
            messagebox.showwarning(
                "Messung",
                "Messung kann nicht gestartet werden, da der Lock aktiv ist."
            )
            return

        if not self.monitoring:
            messagebox.showwarning(
                "Messung",
                "Bitte starten Sie zuerst das Photodioden-Monitoring (START MONITORING)."
            )
            return

        if self.measuring:
            # Stop measurement
            self.stop_measurement()
        else:
            # Start measurement
            self.start_measurement()

    def start_measurement(self):
        self.recorded_data = []  # Clear recorded data if any
        # Reset counters
        if self.monitor is not None:
            self.monitor.counter.reset()
            self.monitor.single_counter.reset()
            self.monitor.s2_visibility_counter.reset()
            
        if hasattr(self, 'lp_s1'):
            del self.lp_s1
        if hasattr(self, 'lp_s2'):
            del self.lp_s2
        if hasattr(self, 'lp_clean_s1'):
            del self.lp_clean_s1
        if hasattr(self, 'lp_clean_s2'):
            del self.lp_clean_s2

        self.clean_s1_history = []
        self.clean_s2_history = []
        self.latest_sample = None
        self.latest_distance_mm = None
        self.reset_calculation_display()
        
        self.measuring = True
        self.calibrating = True
        
        self.btn_measurement.configure(
            text="STOP MEASUREMENT",
            fg_color=RED_COLOR
        )

    def stop_measurement(self):
        self.measuring = False
        self.calibrating = False
        self.stop_calibration_stage_motion()
        
        # Reset UI button
        self.btn_measurement.configure(
            text="START MEASUREMENT",
            fg_color=TEXT_COLOR
        )
        
        # Reset UI status
        self.status.configure(
            text="Status: monitoring running",
            text_color=GREEN_COLOR
        )

    # -----------------------------------------------------------------------------
    # 5.1.1 START MONITORING HELPER
    # -----------------------------------------------------------------------------

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
        self.calibrating = False
        self.measuring = False
        self.latest_sample = None
        self.latest_distance_mm = None
        self.last_error_text = None
        self.raw_s1_history = []
        self.raw_s2_history = []
        self.clean_s1_history = []
        self.clean_s2_history = []
        self.baseline_samples = []
        self.baseline_s1 = 0.0
        self.baseline_s2 = 0.0
        self.baseline_recorded = False
        self.calibration_raw_samples = []
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

        self.set_buttons_enabled(True)

        self.measurement_thread = threading.Thread(
            target=self.measurement_loop,
            daemon=True
        )
        self.measurement_thread.start()

    # -----------------------------------------------------------------------------
    # 5.1.2 STOP MONITORING HELPER
    # -----------------------------------------------------------------------------

    def stop_monitoring(self):
        if self.recording:
            self.toggle_recording()
        if self.measuring:
            self.stop_measurement()
        self.monitoring = False
        self.calibrating = False
        self.disable_lock(update_status=False)
        self.stop_stage_correction()
        self.stop_calibration_stage_motion()
        if self.stage_connected and self.stage is not None and self.stage.is_moving:
            self.stage.stop()
        self.status.configure(
            text="Status: stopping...",
            text_color=ORANGE_COLOR
        )

    # -----------------------------------------------------------------------------
    # 5.6 READ STEP SIZE FROM THE UI
    # -----------------------------------------------------------------------------

    def get_step_size(self):
        #convert the user input from the UI into something readable for the program
        try:
            value = self.parse_entry_float(self.step_entry)
            value = abs(value)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            self.status.configure(
                text="Status: invalid step size",
                text_color=RED_COLOR
            )
            return 0.0001 # safe default size when step size invalid

    # -----------------------------------------------------------------------------
    # 5.6.1 READ STAGE SPEED FROM THE UI
    # -----------------------------------------------------------------------------

    def get_stage_speed(self):
        try:
            value = self.parse_entry_float(self.speed_entry)
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

    # -----------------------------------------------------------------------------
    # 5.6.2 APPLY STAGE SPEED
    # -----------------------------------------------------------------------------

    def apply_stage_speed(self, update_status=True):
        speed_mm_s = self.get_stage_speed()
        if speed_mm_s is None:
            return False

        self.speed_entry.delete(0, "end")
        self.speed_entry.insert(0, f"{speed_mm_s:.6f}")

        if not self.stage_connected or self.stage is None:
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

    # -----------------------------------------------------------------------------
    # 6.6 STAGE CONTROL HELPER
    # -----------------------------------------------------------------------------

    def prepare_stage_for_move(self):
        if self.lock_active:
            self.status.configure(
                text="Stage-Bewegung blockiert: Lock ist aktiv.",
                text_color=RED_COLOR
            )
            return False

        if not self.stage_connected or self.stage is None:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return False

        if self.stage.is_moving:
            self.update_still_to_drive_label()
            if self.stage_remaining_known:
                remaining_text = f"{self.stage_remaining_to_drive:.6f} mm"
            else:
                remaining_text = "target unknown"
            self.status.configure(
                text=f"Stage is already moving, still to drive {remaining_text}",
                text_color=ORANGE_COLOR
            )
            return False

        return self.apply_stage_speed(update_status=False)

    # -----------------------------------------------------------------------------
    # 6.1 MOVE STAGE TO AN ABSOLUTE POSITION
    # -----------------------------------------------------------------------------

    def start_stage_move_to(self, target_mm, start_pos=None):
        if not self.prepare_stage_for_move():
            return

        if start_pos is None:
            start_pos = self.stage.get_position()

        target_mm = self.stage.clamp_position(target_mm)
        move_mm = target_mm - start_pos

        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.set_stage_target_position(target_mm, start_pos)
        self.reset_stage_speed_tracking(start_pos)

        if abs(move_mm) < 1e-12:
            self.update_stage_labels(start_pos, 0.0, self.stage_movement_before_move)
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

    # -----------------------------------------------------------------------------
    # 6.2 MOVE STAGE BY A RELATIVE DISTANCE
    # -----------------------------------------------------------------------------

    def start_stage_move_by(self, move_mm):
        if not self.stage_connected or self.stage is None:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return

        start_pos = self.stage.get_position()
        self.start_stage_move_to(start_pos + move_mm, start_pos=start_pos)

    # -----------------------------------------------------------------------------
    # 6.3 MOVE STAGE TO TARGET IN STEPS
    # -----------------------------------------------------------------------------

    def start_stage_move_to_stepped(self, target_mm, step_mm=None, pause_s=STEP_PAUSE_S, label_prefix="Moving"):
        if not self.prepare_stage_for_move():
            return

        start_pos = self.stage.get_position()
        target_mm = self.stage.clamp_position(target_mm) # clamps target distance by the maximum movement range of the stage

        if abs(target_mm - start_pos) < 1e-12:
            self.status.configure(
                text="Stage already at target",
                text_color=TEXT_COLOR
            )
            return

        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.set_stage_target_position(target_mm, start_pos)
        self.reset_stage_speed_tracking(start_pos)

        if step_mm is None:
            step_mm = self.get_step_size()
        else:
            step_mm = abs(float(step_mm))

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

    # -----------------------------------------------------------------------------
    # 6.4 MOVE STAGE RELATIVELY IN STEPS
    # -----------------------------------------------------------------------------

    def start_stage_move_by_steps(self, move_mm, step_mm=None, pause_s=STEP_PAUSE_S, label_prefix="Moving"):
        if not self.stage_connected or self.stage is None:
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

    # -----------------------------------------------------------------------------
    # 6.5 WORKER FOR STEPPED MOVEMENT
    # -----------------------------------------------------------------------------

    def stage_stepped_move_worker(self, start_pos, target_mm, step_mm, pause_s, label_prefix):
        step_sign = 1 if target_mm > start_pos else -1
        current_pos = start_pos
        remaining = abs(target_mm - start_pos)
        moved = 0.0

        self.root.after(
            0,
            lambda:
            self.status.configure(
                text=f"{label_prefix} to {target_mm:.6f} mm in {step_mm:.9f} mm steps",
                text_color=TEXT_COLOR
            )
        )

        while remaining > 1e-12:
            next_step = min(step_mm, remaining)
            next_target = current_pos + step_sign * next_step

            if not self.stage.move_absolute(next_target):
                self.root.after(
                    0,
                    lambda:
                    self.status.configure(
                        text="Stage move failed",
                        text_color=RED_COLOR
                    )
                )
                self.root.after(0, self.clear_stage_target_position)
                return

            while self.stage.is_moving:
                time.sleep(0.005 if pause_s <= 0 else 0.01)

            step_distance = abs(next_target - current_pos) # how far did this step move
            moved += step_distance # add this value to step distance
            current_pos = next_target
            remaining = abs(target_mm - current_pos)

            self.total_stage_movement = self.stage_movement_before_move + moved
            self.root.after(
                0,
                lambda p=current_pos, m=moved, b=self.stage_movement_before_move: # lambda=anonymous function because after expects a function that will be called later and not a function output
                self.update_stage_labels(p, m, b)
            )

            if remaining > 1e-12 and pause_s > 0:
                time.sleep(pause_s)

        self.root.after(
            0,
            lambda:
            self.finish_stage_move(current_pos)
        )

    # -----------------------------------------------------------------------------
    # 7.1 TRACK NORMAL STAGE MOVEMENT
    # -----------------------------------------------------------------------------

    def stage_ui_loop(self):
        #how much did the stage move befor the current movement? use this as base
        movement_base = self.stage_movement_before_move
        while self.stage.is_moving:
            pos = self.stage.get_position()
            moved = abs(pos - self.stage_start_position)
            self.root.after(
                0,
                lambda p=pos, m=moved, b=movement_base:
                self.update_stage_labels(p, m, b)
            )
            time.sleep(0.05)

        pos = self.stage.get_position()
        moved = abs(pos - self.stage_start_position)
        self.total_stage_movement = movement_base + moved
        self.root.after(
            0,
            lambda p=pos:
            self.finish_stage_move(p)
        )

    # -----------------------------------------------------------------------------
    # 7.1.1 FINISH STAGE MOVE
    # -----------------------------------------------------------------------------

    def finish_stage_move(self, pos):
        moved = abs(pos - self.stage_start_position)
        self.update_stage_labels(pos, moved, self.stage_movement_before_move)
        self.clear_stage_target_position()
        self.label_stage_speed.configure(
            text="Movement Speed: 0.000000 mm/s"
        )
        self.status.configure(
            text=f"Reached {pos:.6f} mm",
            text_color=GREEN_COLOR
        )

    # -----------------------------------------------------------------------------
    # 5.9 STAGE BUTTON ACTIONS
    # -----------------------------------------------------------------------------

    def move_to_min(self):
        if self.stage is not None:
            self.start_stage_move_to(self.stage.min_position)

    # -----------------------------------------------------------------------------
    # 5.9.1 STEP NEGATIVE
    # -----------------------------------------------------------------------------

    def step_negative(self):
        self.start_stage_move_by(-self.get_step_size())

    # -----------------------------------------------------------------------------
    # 5.9.2 MOVE TO CENTER
    # -----------------------------------------------------------------------------

    def move_to_center(self):
        self.start_stage_move_to_stepped(0.0)

    # -----------------------------------------------------------------------------
    # 5.9.3 STEP POSITIVE
    # -----------------------------------------------------------------------------

    def step_positive(self):
        self.start_stage_move_by(self.get_step_size())

    # -----------------------------------------------------------------------------
    # 5.9.4 MOVE TO MAX
    # -----------------------------------------------------------------------------

    def move_to_max(self):
        if self.stage is not None:
            self.start_stage_move_to(self.stage.max_position)

    # -----------------------------------------------------------------------------
    # 5.9.5 MOVE TO TARGET FROM UI
    # -----------------------------------------------------------------------------

    def move_to_target(self):
        try:
            target_mm = self.parse_entry_float(self.target_entry)
            if target_mm < 0:
                raise ValueError("Target position cannot be negative")
        except ValueError:
            self.status.configure(
                text="Invalid target value",
                text_color=RED_COLOR
            )
            return
        self.start_stage_move_to(target_mm)

    # -----------------------------------------------------------------------------
    # 5.9.6 MOVE DISTANCE FROM UI
    # -----------------------------------------------------------------------------

    def move_distance(self):
        try:
            distance_mm = self.parse_entry_float(self.target_entry)
        except ValueError:
            self.status.configure(
                text="Invalid distance value",
                text_color=RED_COLOR
            )
            return
        self.start_stage_move_by(distance_mm)

    def start_ref_measurement(self):
        from tkinter import messagebox
        if not self.monitoring:
            messagebox.showwarning(
                "Messung",
                "Bitte starten Sie zuerst das Photodioden-Monitoring (START MONITORING)."
            )
            return

        if not self.measuring:
            self.start_measurement()

        self.btn_ref_measurement.configure(state="disabled")
        
        import threading
        threading.Thread(target=self.ref_measurement_worker, daemon=True).start()

    def ref_measurement_worker(self):
        import time
        try:
            # 1. Wait for calibration to finish (max 6 seconds)
            start_wait = time.time()
            while self.calibrating and (time.time() - start_wait < 6.0):
                time.sleep(0.1)

            # If measurement was stopped, abort
            if not self.measuring:
                return

            # Stop the stage if it is currently moving (e.g. from calibration phase)
            if self.stage_connected and self.stage is not None and self.stage.is_moving:
                self.root.after(0, lambda: self.stop_stage())
                time.sleep(0.5)
                while self.stage_connected and self.stage is not None and self.stage.is_moving:
                    time.sleep(0.05)

            # 2. Start recording
            self.root.after(0, lambda: self.start_recording_for_ref())
            time.sleep(0.5)

            # 3. Move 0.01 mm forward
            self.root.after(0, lambda: self.start_stage_move_by(0.01))
            time.sleep(0.2)

            # Wait until stage is done moving
            while self.stage_connected and self.stage is not None and self.stage.is_moving:
                time.sleep(0.05)

            time.sleep(0.5)

            # 4. Move 0.01 mm backward
            self.root.after(0, lambda: self.start_stage_move_by(-0.01))
            time.sleep(0.2)

            # Wait until stage is done moving
            while self.stage_connected and self.stage is not None and self.stage.is_moving:
                time.sleep(0.05)

            time.sleep(0.5)

            # 5. Stop recording and save
            self.root.after(0, lambda: self.stop_recording_and_save_for_ref())

        finally:
            self.root.after(0, lambda: self.btn_ref_measurement.configure(state="normal"))

    def start_recording_for_ref(self):
        self.recorded_data = []
        self.recording_start_time = time.time()
        self.recording = True
        self.btn_record.configure(
            text="REC ● STOP",
            fg_color=RED_COLOR
        )

    def stop_recording_and_save_for_ref(self):
        self.recording = False
        self.btn_record.configure(
            text="START RECORDING",
            fg_color="#555555"
        )
        self.save_recorded_data()

    # -----------------------------------------------------------------------------
    # 5.9.7 STOP STAGE ACTION
    # -----------------------------------------------------------------------------

    def stop_stage(self):
        if self.stage_connected and self.stage is not None:
            self.stage.stop()
        self.root.after(
            0,
            lambda:
            self.status.configure(
                text="Stage stopped manually",
                text_color=RED_COLOR
            )
        )

    # -----------------------------------------------------------------------------
    # 7.2 SHOW INITIAL STAGE POSITION
    # -----------------------------------------------------------------------------

    #after calibration UI is filled with current stage position
    def update_stage_position_once(self):
        if self.stage_connected and self.stage is not None:
            pos = self.stage.get_position()
            self.stage_position_mm = pos
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
            if self.stage_connected and self.stage is not None:
                pos = self.stage.get_position()
                self.stage_position_mm = pos
                self.label_stage_position.configure(
                    text=f"Stage Position: {pos:.6f} mm"
                )
                self.update_still_to_drive_label(pos)

                if self.stage.is_moving:
                    self.update_stage_speed_label(pos)
                elif self.stage_remaining_known and self.stage_remaining_to_drive <= 0:
                    self.label_stage_speed.configure(
                        text="Movement Speed: 0.000000 mm/s"
                    )
        finally:
            self.root.after(
                STAGE_STATUS_POLL_MS,
                self.poll_stage_status
            )

    # -----------------------------------------------------------------------------
    # 7.3 UPDATE STAGE MOVEMENT DISPLAY
    # -----------------------------------------------------------------------------

    def update_stage_labels(self, pos, moved, movement_base=None):
        if movement_base is None:
            movement_base = self.total_stage_movement
        current_total_stage_movement = movement_base + abs(moved)
        self.total_stage_movement = max(
            self.total_stage_movement,
            current_total_stage_movement
        )
        self.current_stage_movement_for_compare = current_total_stage_movement

        self.label_stage_position.configure(
            text=f"Stage Position: {pos:.6f} mm"
        )
        self.label_stage_moved.configure(
            text=f"Accumulated Movement: {current_total_stage_movement:.6f} mm"
        )
        self.update_still_to_drive_label(pos)
        self.update_stage_speed_label(pos)
        self.update_comparison_labels(current_total_stage_movement)

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

    def update_still_to_drive_label(self, pos=None):
        target_position = self.get_active_stage_target_position()
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

    def get_active_stage_target_position(self):
        if self.stage_target_position is not None:
            return self.stage_target_position
        return None

    # -----------------------------------------------------------------------------
    # 7.5 RESET STAGE SPEED TRACKING
    # -----------------------------------------------------------------------------

    def reset_stage_speed_tracking(self, pos):
        self.last_stage_speed_position = pos
        self.last_stage_speed_time = time.time()

    # -----------------------------------------------------------------------------
    # 7.6 UPDATE STAGE SPEED DISPLAY
    # -----------------------------------------------------------------------------

    def update_stage_speed_label(self, pos):
        now = time.time()
        if self.last_stage_speed_time is None or self.last_stage_speed_position is None:
            self.reset_stage_speed_tracking(pos)
            return

        dt = now - self.last_stage_speed_time
        if dt <= 0:
            return

        speed_mm_s = abs(pos - self.last_stage_speed_position) / dt
        self.last_stage_speed_time = now
        self.last_stage_speed_position = pos
        self.label_stage_speed.configure(
            text=f"Movement Speed: {speed_mm_s:.6f} mm/s"
        )

    # -----------------------------------------------------------------------------
    # 7.4 RESET STAGE MOVEMENT TRACKING
    # -----------------------------------------------------------------------------

    def reset_stage_movement_tracking(self, pos=None):
        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        self.stage_target_position = None
        self.stage_remaining_to_drive = 0.0
        self.stage_remaining_known = True

        if pos is not None: # use provided position as new reference
            self.stage_reference_position = pos
            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )
        elif self.stage_connected and self.stage is not None:
            self.stage_reference_position = self.stage.get_position()
        else:
            self.stage_reference_position = 0.0

        self.label_stage_moved.configure(text="Accumulated Movement: 0.000000 mm")
        self.label_stage_speed.configure(text="Movement Speed: 0.000000 mm/s")
        self.clear_stage_target_position()

    # -----------------------------------------------------------------------------
    # 7.11 UPDATE DRIVEN VS CALCULATED DISTANCE
    # -----------------------------------------------------------------------------

    #stage movement distance is compared with distance calculated from counted fringes
    def update_comparison_labels(self, driven_mm=None):
        if not self.measuring or self.calibrating:
            self.label_compare_driven.configure(text="Driven: 0.000000 mm")
            self.label_still_to_drive.configure(text="Still to drive: 0.000000 mm")
            self.label_compare_calculated.configure(text="Calculated from Fringes: 0.000000 mm")
            self.label_compare_difference.configure(text="Difference: 0.000000 mm", text_color=TEXT_COLOR)
            return

        if driven_mm is None:
            if self.stage_connected and self.stage is not None:
                current_pos = self.stage.current_position
                start_pos = getattr(self, 'stage_measurement_start_position', current_pos)
                driven_mm = abs(current_pos - start_pos)
            else:
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

    # -----------------------------------------------------------------------------
    # 8.8 RUN STAGE MOTION BY PARAMETERS
    # -----------------------------------------------------------------------------

    def run_stage_motion_by_parameters(self):
        if not self.stage_connected or self.stage is None:
            return

        current_position = self.stage.get_position()
        if MODE.lower().startswith("c"):
            self.stage.set_velocity(VELOCITY_MM_S)
            final_target = self.stage.clamp_position(current_position + TOTAL_DISTANCE_MM)

            self.stage_start_position = current_position
            self.stage_movement_before_move = self.total_stage_movement
            self.set_stage_target_position(final_target, current_position)
            self.reset_stage_speed_tracking(current_position)

            self.root.after(
                0,
                lambda:
                self.status.configure(
                    text=f"Continuous move to {final_target:.6f} mm at {VELOCITY_MM_S} mm/s",
                    text_color=TEXT_COLOR
                )
            )

            if not self.stage.move_absolute(final_target):
                self.root.after(
                    0,
                    lambda:
                    self.status.configure(
                        text="Stage move failed",
                        text_color=RED_COLOR
                    )
                )
                self.root.after(0, self.clear_stage_target_position)
                return

            while self.stage.is_moving and self.monitoring:
                pos = self.stage.get_position()
                moved = abs(pos - self.stage_start_position)
                self.root.after(
                    0,
                    lambda p=pos, m=moved, b=self.stage_movement_before_move:
                    self.update_stage_labels(p, m, b)
                )
                time.sleep(0.05)

            pos = self.stage.get_position()
            moved = abs(pos - self.stage_start_position)
            self.total_stage_movement = self.stage_movement_before_move + moved
            self.root.after(
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
            self.set_stage_target_position(stepped_target, current_position)
            self.reset_stage_speed_tracking(current_position)

            self.root.after(
                0,
                lambda:
                self.status.configure(
                    text=f"Stepped move: {STEPS} steps of {STEP_SIZE_MM} mm",
                    text_color=TEXT_COLOR
                )
            )

            current_pos = current_position
            moved = 0.0

            for step in range(STEPS):
                if not self.monitoring:
                    break

                next_position = self.stage.clamp_position(current_pos + STEP_SIZE_MM)
                self.root.after(
                    0,
                    lambda s=step, n=next_position:
                    self.status.configure(
                        text=f"Step {s + 1}/{STEPS}: move to {n:.7f} mm",
                        text_color=TEXT_COLOR
                    )
                )

                if not self.stage.move_absolute(next_position):
                    self.root.after(
                        0,
                        lambda:
                        self.status.configure(
                            text="Move command failed",
                            text_color=RED_COLOR
                        )
                    )
                    break

                while self.stage.is_moving and self.monitoring:
                    time.sleep(0.01)

                step_distance = abs(next_position - current_pos)
                moved += step_distance
                current_pos = next_position

                self.total_stage_movement = self.stage_movement_before_move + moved
                self.root.after(
                    0,
                    lambda p=current_pos, m=moved, b=self.stage_movement_before_move:
                    self.update_stage_labels(p, m, b)
                )

                if step < STEPS - 1:
                    time.sleep(STEP_PAUSE_S)

            self.root.after(
                0,
                lambda p=current_pos:
                self.finish_stage_move(p)
            )

    # -----------------------------------------------------------------------------
    # 7.7 MOVE STAGE DURING CALIBRATION
    # -----------------------------------------------------------------------------

    def calibration_stage_motion(self):
        previous_velocity = None
        try:
            if not self.stage_connected or self.stage is None:
                return

            start_pos = self.stage.get_position() # current stage position as movement start
            forward_target = self.stage.clamp_position(start_pos + CALIBRATION_STAGE_DISTANCE_MM)
            back_target = self.stage.clamp_position(start_pos)
            sweep_distance_mm = abs(forward_target - start_pos)

            if sweep_distance_mm <= 1e-12:
                return

            previous_velocity = self.stage.set_velocity()
            calibration_speed_mm_s = CALIBRATION_STAGE_SPEED_MM_S

            if not self.stage.set_velocity(calibration_speed_mm_s):
                return

            self.stage_start_position = start_pos
            self.stage_movement_before_move = 0.0
            self.reset_stage_speed_tracking(start_pos)

            self.root.after(
                0,
                lambda:
                self.status.configure(
                    text=f"Calibration sweep: {sweep_distance_mm:.5f} mm at {calibration_speed_mm_s:.6f} mm/s",
                    text_color=ORANGE_COLOR
                )
            )

            accumulated_movement_mm = 0.0

            while self.monitoring and self.calibrating:
                for target in (forward_target, back_target):
                    if not self.monitoring or not self.calibrating:
                        return

                    leg_start_pos = self.stage.get_position()
                    self.stage_target_position = target
                    self.stage_remaining_known = True

                    if not self.stage.move_absolute(target):
                        return

                    while self.stage.is_moving and self.monitoring and self.calibrating:
                        current_pos = self.stage.get_position()
                        moved = accumulated_movement_mm + abs(current_pos - leg_start_pos)
                        self.root.after(
                            0,
                            lambda p=current_pos, m=moved:
                            self.update_stage_labels(p, m, 0.0)
                        )
                        time.sleep(0.01)

                    if not self.monitoring or not self.calibrating:
                        return

                    current_pos = self.stage.get_position()
                    accumulated_movement_mm += abs(current_pos - leg_start_pos)
                    self.total_stage_movement = accumulated_movement_mm
                    self.current_stage_movement_for_compare = accumulated_movement_mm

                    self.root.after(
                        0,
                        lambda p=current_pos, m=accumulated_movement_mm:
                        self.update_stage_labels(p, m, 0.0)
                    )

        finally:
            if self.stage_connected and self.stage is not None and self.stage.is_moving:
                self.stage.stop()

            if previous_velocity is not None and self.stage_connected and self.stage is not None:
                self.stage.set_velocity(previous_velocity)

            pos = self.stage.get_position()
            self.root.after(
                0,
                lambda p=pos, m=accumulated_movement_mm:
                self.finish_calibration_movement(p, m)
            )

    def stop_calibration_stage_motion(self):
        if not self.stage_connected or self.stage is None:
            return
        self.clear_stage_target_position()
        if self.stage.is_moving:
            self.stage.stop()
        self.root.after(
            0,
            lambda:
            self.status.configure(
                text="Calibration ended, stage stopped",
                text_color=ORANGE_COLOR
            )
        )

    # -----------------------------------------------------------------------------
    # 7.10 FINISH CALIBRATION RESET
    # -----------------------------------------------------------------------------

    def finish_calibration_movement(self, pos=None, accumulated_movement_mm=None):
        if self.stage_connected and self.stage is not None and self.stage.is_moving:
            self.stage.stop()
            self.status.configure(
                text="Calibration ended, waiting for stage stop",
                text_color=ORANGE_COLOR
            )
            self.root.after(
                STAGE_STATUS_POLL_MS,
                lambda p=pos, m=accumulated_movement_mm: self.finish_calibration_movement(p, m)
            )
            return

        if pos is None:
            if self.stage_connected and self.stage is not None:
                pos = self.stage.get_position()
            else:
                pos = 0.0

        if accumulated_movement_mm is None:
            self.reset_stage_movement_tracking(pos)
        else:
            self.stage_reference_position = pos
            self.total_stage_movement = accumulated_movement_mm
            self.current_stage_movement_for_compare = accumulated_movement_mm

            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )
            if hasattr(self, "label_stage_position_lock"):
                self.label_stage_position_lock.configure(
                    text=f"Stage Position: {pos:.6f} mm"
                )

            self.label_stage_moved.configure(
                text=f"Accumulated Movement: {accumulated_movement_mm:.6f} mm"
            )
            self.clear_stage_target_position()
            self.update_comparison_labels(accumulated_movement_mm)

        self.set_buttons_enabled(True)
        if self.monitoring:
            self.status.configure(
                text="Status: monitoring running",
                text_color=GREEN_COLOR
            )

    def start_ui_loop(self):

        self.root.after(int(UI_UPDATE_INTERVAL_S * 1000), self.update_ui_loop)

    def update_ui_loop(self):
        if not self.monitoring and not self.calibrating:
            return

        self.label_lissajous_direction.configure(
            text="STILL",
            text_color=ORANGE_COLOR
        )

        with self.sample_display_lock:
            sample = self.latest_sample
            distance_mm = self.latest_distance_mm
            s1_hist = list(self.raw_s1_history)
            s2_hist = list(self.raw_s2_history)

            single_fringes = self.monitor.single_counter.accumulated_fringes
            single_distance = single_fringes * self.fringe_distance_mm
            single_amp = self.monitor.single_counter.fringe_amplitude_voltage
            s2_amp = self.monitor.s2_visibility_counter.fringe_amplitude_voltage
            s1_rise = self.monitor.single_counter.fringe_rise_threshold_voltage
            s2_rise = self.monitor.s2_visibility_counter.fringe_rise_threshold_voltage
            s1_visible = self.monitor.single_counter.fringes_visible
            s2_visible = self.monitor.s2_visibility_counter.fringes_visible
            lissajous_ready = self.monitor.counter.signals_visible()

            calibrating = self.calibrating
            progress_text = getattr(self, 'calibration_progress_text', None)

        if calibrating:
            if progress_text:
                self.status.configure(text=progress_text, text_color=ORANGE_COLOR)
            self.update_plot()
        elif sample is not None:

            self.label_single_fringes.configure(
                text=f"S1 Fringe Count: {single_fringes}"
            )
            self.label_single_distance.configure(
                text=f"S1 Calculated Distance: {single_distance:+.6f} mm"
            )
            lissajous_text = "ready" if lissajous_ready else "blocked"
            self.label_single_thresholds.configure(
                text=(
                    f"S1 amp {single_amp:.6f} V, rise {s1_rise:.6f} V "
                    f"({'visible' if s1_visible else 'not visible'}), "
                    f"S2 amp {s2_amp:.6f} V, rise {s2_rise:.6f} V "
                    f"({'visible' if s2_visible else 'not visible'}), "
                    f"Lissajous {lissajous_text}"
                )
            )

            self.label_phase.configure(
                text=f"phase_rad = atan2(S2_norm, S1_norm) = {sample.phase_rad:+.5f} rad" if sample.valid else "phase_rad = invalid"
            )
            self.label_s1_norm.configure(
                text=f"S1_norm = (raw_S1 - offset_S1) / scale_S1 = {sample.s1:+.6f}"
            )
            self.label_s2_norm.configure(
                text=f"S2_norm = (raw_S2 - offset_S2) / scale_S2 = {sample.s2:+.6f}"
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

            dir_text = "Still"
            dir_color = ORANGE_COLOR
            lissajous_dir_text = "STILL"
            if sample.direction == "forward":
                dir_text = "Forward →"
                dir_color = GREEN_COLOR
                lissajous_dir_text = "FORWARD"
            elif sample.direction == "backward":
                dir_text = "Backward ←"
                dir_color = RED_COLOR
                lissajous_dir_text = "BACKWARD"
            elif sample.direction == "signal_low":
                dir_text = "Signal Low"
                dir_color = RED_COLOR
            elif sample.direction == "fringes_not_visible":
                dir_text = "Fringes Not Visible"
                dir_color = RED_COLOR

            self.label_direction.configure(
                text=f"Direction: {dir_text}",
                text_color=dir_color
            )
            self.label_lissajous_direction.configure(
                text=lissajous_dir_text,
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

            if sample.fringe_delta != 0:
                self.label_fringes.configure(text_color=GREEN_COLOR)
                self.root.after(
                    250,
                    lambda: self.label_fringes.configure(text_color=TEXT_COLOR)
                )

            self.update_lock_display(sample, distance_mm)

            if self.lock_active:
                fringes_diff = sample.signed_fringes if sample is not None else 0
                self.label_fringes_since_locking.configure(
                    text=f"Fringes since locking: {fringes_diff:+d}"
                )
                if self.stage_connected and self.stage is not None:
                    diff_mm = self.stage_position_mm - self.lock_stage_position_mm
                    self.label_correction_since_locking.configure(
                        text=f"Correction since locking: {diff_mm:+.6f} mm"
                    )
                else:
                    self.label_correction_since_locking.configure(
                        text="Correction since locking: n/a"
                    )

            self.update_comparison_labels()

            self.update_plot()
        else:
            self.update_plot()

        self.root.after(int(UI_UPDATE_INTERVAL_S * 1000), self.update_ui_loop)

    def measurement_loop(self):
        try:
            self.monitor.connect()

            self.root.after(
                0,
                lambda:
                self.status.configure(
                    text="Status: monitoring running",
                    text_color=GREEN_COLOR
                )
            )

            self.root.after(0, self.start_ui_loop)

            calibration_samples = []
            calibration_start_time = None

            while self.monitoring:
                raw_s1, raw_s2 = self.monitor.reader.read()

                if not self.baseline_recorded:
                    self.baseline_samples.append((raw_s1, raw_s2))
                    self.root.after(
                        0,
                        lambda: self.status.configure(
                            text="Status: recording baseline noise...",
                            text_color=ORANGE_COLOR
                        )
                    )
                    if len(self.baseline_samples) >= 200:
                        self.baseline_s1 = sum(s[0] for s in self.baseline_samples) / len(self.baseline_samples)
                        self.baseline_s2 = sum(s[1] for s in self.baseline_samples) / len(self.baseline_samples)
                        self.baseline_recorded = True
                        self.root.after(
                            0,
                            lambda: self.status.configure(
                                text="Status: monitoring running",
                                text_color=GREEN_COLOR
                            )
                        )

                clean_s1 = raw_s1 - self.baseline_s1
                clean_s2 = raw_s2 - self.baseline_s2

                alpha = 0.3
                if not hasattr(self, 'lp_clean_s1'):
                    self.lp_clean_s1 = clean_s1
                    self.lp_clean_s2 = clean_s2
                else:
                    self.lp_clean_s1 = alpha * clean_s1 + (1.0 - alpha) * self.lp_clean_s1
                    self.lp_clean_s2 = alpha * clean_s2 + (1.0 - alpha) * self.lp_clean_s2

                with self.sample_display_lock:
                    self.raw_s1_history.append(raw_s1)
                    self.raw_s2_history.append(raw_s2)
                    self.clean_s1_history.append(self.lp_clean_s1)
                    self.clean_s2_history.append(self.lp_clean_s2)
                    if len(self.raw_s1_history) > 300:
                        self.raw_s1_history.pop(0)
                        self.raw_s2_history.pop(0)
                    if len(self.clean_s1_history) > 300:
                        self.clean_s1_history.pop(0)
                        self.clean_s2_history.pop(0)

                if self.measuring or self.lock_active:
                    if self.calibrating:
                        if calibration_start_time is None:
                            # No extra stage motion for calibration
                            calibration_start_time = time.time()
                            calibration_samples = []
                            self.root.after(
                                0,
                                lambda: self.status.configure(
                                    text=f"Status: calibrating {CALIBRATION_SECONDS:.1f}s...",
                                    text_color=ORANGE_COLOR
                                )
                            )

                        calibration_samples.append((clean_s1, clean_s2))
                        elapsed_s = time.time() - calibration_start_time
                        
                        # Set progress text without double-appending raw history
                        self.calibration_progress_text = f"Status: calibrating {elapsed_s:.1f}/{CALIBRATION_SECONDS:.1f}s..."

                        if elapsed_s >= CALIBRATION_SECONDS:
                            # Calibrate the counter from the collected samples
                            self.monitor.counter.calibrate_from_samples(calibration_samples)
                            s1_vals = [s[0] for s in calibration_samples]
                            s2_vals = [s[1] for s in calibration_samples]
                            self.monitor.single_counter.calibrate(s1_vals)
                            self.monitor.s2_visibility_counter.calibrate(s2_vals)
                            self.monitor.counter.set_signal_visibility(
                                self.monitor.single_counter.fringes_visible,
                                self.monitor.s2_visibility_counter.fringes_visible
                            )
                            
                            # Reset fringe counts to 0 starting from the end of calibration
                            self.monitor.single_counter.reset()
                            self.monitor.s2_visibility_counter.reset()
                            self.monitor.counter.reset()

                            # Record stage reference position at the start of measurement
                            if self.stage_connected and self.stage is not None:
                                self.stage_measurement_start_position = self.stage.get_position()

                            self.calibrating = False
                            calibration_start_time = None
                            self.stop_calibration_stage_motion()
                            self.root.after(
                                0,
                                lambda: self.status.configure(
                                    text="Status: measurement running",
                                    text_color=GREEN_COLOR
                                )
                            )
                    else:
                        # Calibration is complete, do normal fringe counting
                        self.monitor.single_counter.update(self.lp_clean_s1)
                        sample = self.monitor.counter.update(self.lp_clean_s1, self.lp_clean_s2)
                        distance_mm = self.monitor.counter.signed_distance_mm()

                        with self.sample_display_lock:
                            self.latest_sample = sample
                            self.latest_distance_mm = distance_mm

                if self.recording:
                    elapsed = time.time() - self.recording_start_time
                    # Non-blocking read of the last queried stage position
                    stage_pos = self.stage.current_position if (self.stage_connected and self.stage is not None) else 0.0
                    s_obj = sample if ('sample' in locals() and sample is not None) else None
                    cur_single_fringes = self.monitor.single_counter.accumulated_fringes if self.monitor else 0
                    cur_single_distance = cur_single_fringes * self.fringe_distance_mm
                    cur_phase_distance = distance_mm if ('distance_mm' in locals() and distance_mm is not None) else 0.0
                    self.recorded_data.append((
                        elapsed,
                        raw_s1,
                        raw_s2,
                        s_obj.s1 if s_obj else 0.0,
                        s_obj.s2 if s_obj else 0.0,
                        s_obj.phase_rad if s_obj else 0.0,
                        s_obj.unwrapped_phase_rad if s_obj else 0.0,
                        cur_phase_distance,
                        cur_single_distance,
                        cur_single_fringes,
                        stage_pos
                    ))

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
            self.stop_calibration_stage_motion()
            try:
                self.monitor.close()
            except Exception:
                pass
            self.root.after(0, self.finish_stopped_ui)

    # -----------------------------------------------------------------------------
    # 7.8 HANDLE CALIBRATION SAMPLE
    # -----------------------------------------------------------------------------

    def handle_calibration_sample(self, raw_sample, elapsed_s, total_s):
        raw_s1, raw_s2 = raw_sample
        with self.sample_display_lock:
            self.calibration_raw_samples.append(raw_sample)
            self.raw_s1_history.append(raw_s1)
            self.raw_s2_history.append(raw_s2)
            if len(self.raw_s1_history) > 300:
                self.raw_s1_history.pop(0)
                self.raw_s2_history.pop(0)
            self.calibration_progress_text = f"Status: calibrating {elapsed_s:.1f}/{total_s:.1f}s..."

    def reset_calculation_display(self):
        self.label_single_fringes.configure(text="S1 Fringe Count: 0")
        self.label_single_distance.configure(text="S1 Calculated Distance: 0.000000 mm")
        self.label_single_thresholds.configure(text="Signal amplitudes: S1 = n/a, S2 = n/a")

        self.label_phase.configure(
            text="phase_rad = atan2(S2_norm, S1_norm) = n/a"
        )
        self.label_s1_norm.configure(
            text="S1_norm = (raw_S1 - offset_S1) / scale_S1 = n/a"
        )
        self.label_s2_norm.configure(
            text="S2_norm = (raw_S2 - offset_S2) / scale_S2 = n/a"
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
        self.label_lissajous_direction.configure(
            text="STILL",
            text_color=ORANGE_COLOR
        )
        self.label_distance.configure(
            text="distance_mm = fringe_position * fringe_distance_mm = n/a"
        )

    def toggle_lock(self):
        #get all errors
        if self.lock_active:
            #refuse manual step movement because lock is active
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
            self.status.configure(
                text="Status: stage not connected, cannot lock",
                text_color=RED_COLOR
            )
            return

        # Check if we have a calibrated fringe amplitude
        if self.monitor is not None and self.monitor.single_counter is not None:
            if not self.monitor.single_counter.fringes_visible:
                # Prompt the user for the default fringe amplitude (V)
                val = sd.askfloat(
                    "Default Fringe Amplitude",
                    "No calibrated fringe value found.\n\nPlease enter the default fringe amplitude in Volts (e.g. 0.010):",
                    parent=self.root,
                    initialvalue=0.010,
                    minvalue=0.0001,
                    maxvalue=2.0
                )
                if val is None:
                    # User cancelled the dialog, abort locking
                    return
                
                # Configure counters with this default value
                self.monitor.single_counter.fringe_amplitude_voltage = val
                self.monitor.single_counter.fringes_visible = True
                
                self.monitor.s2_visibility_counter.fringe_amplitude_voltage = val
                self.monitor.s2_visibility_counter.fringes_visible = True
                
                self.monitor.counter.set_signal_visibility(True, True)

            # In all cases (either reusing the last calibration or setting the default value),
            # enforce the strict 98% rise/rearm thresholds:
            amp = self.monitor.single_counter.fringe_amplitude_voltage
            self.monitor.single_counter.fringe_rise_threshold_voltage = amp * 0.98
            self.monitor.single_counter.fringe_rearm_threshold_voltage = amp * 0.98

            amp_s2 = self.monitor.s2_visibility_counter.fringe_amplitude_voltage
            self.monitor.s2_visibility_counter.fringe_rise_threshold_voltage = amp_s2 * 0.98
            self.monitor.s2_visibility_counter.fringe_rearm_threshold_voltage = amp_s2 * 0.98

        # Keep stage stationary
        if self.stage_connected and self.stage is not None:
            self.stage.stop()
            self.lock_stage_position_mm = self.stage.get_position()
        else:
            self.lock_stage_position_mm = 0.0

        # Reset counters so locking starts at exactly 0
        if self.monitor is not None:
            self.monitor.counter.reset()
            self.monitor.single_counter.reset()
            self.monitor.s2_visibility_counter.reset()

        self.lock_active = True
        self.lock_reference_distance_mm = 0.0
        self.lock_reference_phase_rad = 0.0
        self.lock_reference_fringes = 0
        self.latest_sample = None
        self.latest_distance_mm = 0.0
        self.lock_ref_single_fringes = 0

        self.btn_lock.configure(
            text="UNLOCK",
            fg_color=GREEN_COLOR
        )
        if hasattr(self, 'btn_lock_box'):
            self.btn_lock_box.configure(
                text="UNLOCK",
                fg_color=GREEN_COLOR
            )
        if hasattr(self, 'label_lock_status_box'):
            self.label_lock_status_box.configure(
                text="Lock Status: active",
                text_color=GREEN_COLOR
            )
        self.label_lock_status.configure(
            text="Lock: on",
            text_color=GREEN_COLOR
        )
        self.status.configure(
            text="Status: locked",
            text_color=GREEN_COLOR
        )

    #return everything to unlock state
    def disable_lock(self, update_status=True):
        self.stop_stage_correction()
        self.lock_active = False # disable position lock
        self.btn_lock.configure(
            text="LOCK",
            fg_color=TEXT_COLOR
        )
        if hasattr(self, 'btn_lock_box'):
            self.btn_lock_box.configure(
                text="LOCK",
                fg_color=TEXT_COLOR
            )
            self.label_lock_status_box.configure(
                text="Lock Status: off",
                text_color=TEXT_COLOR
            )
            self.label_fringes_since_locking.configure(
                text="Fringes since locking: n/a"
            )
            self.label_correction_since_locking.configure(
                text="Correction since locking: n/a"
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
        if not self.lock_active or distance_mm is None or sample is None:
            return

        drift_mm = distance_mm - self.lock_reference_distance_mm
        correction_mm = -STAGE_CORRECTION_SIGN * drift_mm

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
                f"(next step {correction_mm:+.9f} mm)"
            ),
            text_color=ORANGE_COLOR if abs(drift_mm) > 0 else GREEN_COLOR
        )

        self.maybe_start_lock_correction(drift_mm, correction_mm, sample)

    #extremely small drift is ignored
    def lock_deadband_mm(self):
        fringe_distance_mm = self.monitor.counter.fringe_distance_mm

        if fringe_distance_mm is None:
            return 1e-7

        return max(
            abs(fringe_distance_mm) * LOCK_TRIGGER_FRINGES,
            1e-7
        )

    def maybe_start_lock_correction(self, drift_mm, correction_mm, sample):
        if not self.lock_active:
            return

        if not self.stage_connected or self.stage is None:
            self.label_stage_status.configure(
                text="Stage: not connected, cannot correct lock",
                text_color=RED_COLOR
            )
            return

        if sample is None or sample.signed_fringes == 0:
            if hasattr(self, 'label_lock_status_box'):
                self.label_lock_status_box.configure(
                    text="Lock Status: active",
                    text_color=GREEN_COLOR
                )
            return

        fringe_distance_mm = self.monitor.counter.fringe_distance_mm
        if fringe_distance_mm is None:
            fringe_distance_mm = 0.000316

        fringes_str = f"+{sample.signed_fringes}" if sample.signed_fringes > 0 else f"{sample.signed_fringes}"

        # 1. Check if deviation is below threshold
        if abs(sample.signed_fringes) < LOCK_TRIGGER_FRINGES:
            msg = f"{fringes_str} fringe, but below threshold so didnt count"
            if hasattr(self, 'label_lock_status_box'):
                self.label_lock_status_box.configure(
                    text=f"Lock Status: {msg}",
                    text_color=ORANGE_COLOR
                )
            return

        # 2. Check invalid direction
        if sample.direction not in ["forward", "backward"]:
            msg = f"{fringes_str} fringe but still, so no correction"
            self.label_lock_status.configure(
                text=f"Lock: {msg}",
                text_color=ORANGE_COLOR
            )
            if hasattr(self, 'label_lock_status_box'):
                self.label_lock_status_box.configure(
                    text=f"Lock Status: {msg}",
                    text_color=ORANGE_COLOR
                )
            return

        # 3. Check busy state
        if (
            self.lock_correction_active
            or self.stage_command_active
            or self.stage.is_moving
        ):
            msg = f"{fringes_str} fringe but still, so no correction"
            if hasattr(self, 'label_lock_status_box'):
                self.label_lock_status_box.configure(
                    text=f"Lock Status: {msg}",
                    text_color=ORANGE_COLOR
                )
            return

        # 4. Check cooldown
        now = time.time()
        if now - self.lock_last_correction_time < LOCK_CORRECTION_COOLDOWN_S:
            msg = f"{fringes_str} fringe but still, so no correction"
            if hasattr(self, 'label_lock_status_box'):
                self.label_lock_status_box.configure(
                    text=f"Lock Status: {msg}",
                    text_color=ORANGE_COLOR
                )
            return

        # Determine the corrective step (opposite to the drift to apply true negative feedback)
        # Drift (+) -> correction (-)
        # Drift (-) -> correction (+)
        correction_step_mm = - (sample.signed_fringes * fringe_distance_mm)
        
        # Clamp the correction step to a maximum of 2 fringes (0.0008 mm) from the lock position
        max_lock_deviation_mm = 0.0008
        if correction_step_mm > max_lock_deviation_mm:
            correction_step_mm = max_lock_deviation_mm
        elif correction_step_mm < -max_lock_deviation_mm:
            correction_step_mm = -max_lock_deviation_mm
        
        # Calculate target relative to the saved lock position reference (not current_position_mm)
        target_position_mm = self.stage.clamp_position(
            self.lock_stage_position_mm + correction_step_mm
        )
        current_position_mm = self.stage.get_position()
        actual_correction_mm = target_position_mm - current_position_mm

        if abs(actual_correction_mm) < 1e-12:
            self.label_lock_status.configure(
                text="Lock: correction blocked by stage limit",
                text_color=RED_COLOR
            )
            if hasattr(self, 'label_lock_status_box'):
                self.label_lock_status_box.configure(
                    text="Lock Status: blocked by limit",
                    text_color=RED_COLOR
                )
            return

        self.lock_correction_active = True
        self.lock_target_position_mm = target_position_mm

        if not self.stage.move_absolute(target_position_mm):
            self.lock_correction_active = False
            self.label_lock_status.configure(
                text="Lock: stage correction failed",
                text_color=RED_COLOR
            )
            if hasattr(self, 'label_lock_status_box'):
                self.label_lock_status_box.configure(
                    text="Lock Status: correction failed",
                    text_color=RED_COLOR
                )
            return

        # Success message format: "+1 fringe corrected by -0.000316 mm"
        msg = f"{fringes_str} fringe corrected by {correction_step_mm:+.6f} mm"

        self.label_lock_status.configure(
            text=f"Lock: {msg}",
            text_color=ORANGE_COLOR
        )
        if hasattr(self, 'label_lock_status_box'):
            self.label_lock_status_box.configure(
                text=f"Lock Status: {msg}",
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
        self.lock_last_correction_time = time.time()

        if position_mm is not None:
            self.stage_position_mm = position_mm
            self.label_stage_position.configure(
                text=f"Stage position: {position_mm:.6f} mm"
            )

        if not self.lock_active:
            return

        # Reset counters to clear any transient/aliased counts during the movement
        if self.monitor is not None:
            self.monitor.counter.reset()
            self.monitor.single_counter.reset()
            self.monitor.s2_visibility_counter.reset()

        self.label_stage_status.configure(
            text="Stage: connected",
            text_color=GREEN_COLOR
        )
        self.label_lock_status.configure(
            text="Lock: correction done",
            text_color=GREEN_COLOR
        )

    def stop_stage_correction(self):
        was_correcting = self.lock_correction_active
        self.lock_correction_active = False

        if was_correcting and self.stage_connected and self.stage is not None:
            self.stage.stop()

    # -----------------------------------------------------------------------------
    # 8.6 SHOW MONITORING ERROR
    # -----------------------------------------------------------------------------

    def show_error(self, error):
        self.status.configure(
            text=f"Status: {error}",
            text_color=RED_COLOR
        )

    # -----------------------------------------------------------------------------
    # 8.7 RESET UI AFTER MONITORING STOPS
    # -----------------------------------------------------------------------------

    def finish_stopped_ui(self):
        if self.recording:
            self.toggle_recording()
        if self.measuring:
            self.stop_measurement()
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
        self.monitor.s2_visibility_counter.reset()
        self.latest_sample = None
        self.latest_distance_mm = None
        self.raw_s1_history = []
        self.raw_s2_history = []
        self.clean_s1_history = []
        self.clean_s2_history = []
        self.baseline_samples = []
        self.baseline_s1 = 0.0
        self.baseline_s2 = 0.0
        self.baseline_recorded = False
        if hasattr(self, 'lp_clean_s1'):
            del self.lp_clean_s1
        if hasattr(self, 'lp_clean_s2'):
            del self.lp_clean_s2
        with self.sample_display_lock:
            self.pending_sample = None
            self.pending_distance_mm = None

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

    # -----------------------------------------------------------------------------
    # 8.5 LIVE VOLTAGE PLOT UPDATE
    # -----------------------------------------------------------------------------

    def update_plot(self, reset=False):
        if self.plot_axes is None or self.axis_circle is None:
            return

        if reset:
            self.plot_lines['S1_raw'].set_data([], [])
            self.plot_lines['S2_raw'].set_data([], [])
            self.plot_lines['S1_raw_clean'].set_data([], [])
            self.plot_lines['S2_raw_clean'].set_data([], [])
            self.plot_lines['S1_raw_fit'].set_data([], [])
            self.plot_lines['S2_raw_fit'].set_data([], [])
            self.plot_lines['S1_raw_fit'].set_visible(False)
            self.plot_lines['S2_raw_fit'].set_visible(False)
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

        self.update_plot_data(s1_hist, s2_hist)

    def update_plot_data(self, s1_hist, s2_hist):
        if self.plot_axes is None or self.axis_circle is None:
            return

        x = list(range(len(s1_hist)))

        self.plot_lines['S1_raw'].set_data(x, s1_hist)
        if len(self.clean_s1_history) == len(x):
            self.plot_lines['S1_raw_clean'].set_data(x, self.clean_s1_history)
        self.plot_axes['S1_raw'].relim()
        self.plot_axes['S1_raw'].autoscale_view()

        self.plot_lines['S2_raw'].set_data(x, s2_hist)
        if len(self.clean_s2_history) == len(x):
            self.plot_lines['S2_raw_clean'].set_data(x, self.clean_s2_history)
        self.plot_axes['S2_raw'].relim()
        self.plot_axes['S2_raw'].autoscale_view()

        if not (self.measuring or self.lock_active) or not self.monitor.counter.signals_visible():
            self.plot_lines['circle_trace'].set_data([], [])
            self.plot_lines['circle_current'].set_data([], [])
            self.plot_lines['circle_pointer'].set_data([], [])
            self.plot_lines['S1_raw_fit'].set_data([], [])
            self.plot_lines['S2_raw_fit'].set_data([], [])
            self.plot_lines['S1_raw_fit'].set_visible(False)
            self.plot_lines['S2_raw_fit'].set_visible(False)
            self.plot_quiver.set_visible(False)
            self.plot_canvas.draw_idle()
            self.plot_canvas_circle.draw_idle()
            return

        s1_norm_history = []
        s2_norm_history = []
        with self.monitor.counter.lock:
            offset_s1 = self.monitor.counter.offset_s1
            scale_s1 = self.monitor.counter.scale_s1
            offset_s2 = self.monitor.counter.offset_s2
            scale_s2 = self.monitor.counter.scale_s2

        # If offsets/scales are default/zero, estimate them dynamically from current history
        # so that the fit line is drawn exactly at the height of the raw signal
        if offset_s1 == 0.0 or scale_s1 == 1.0:
            if s1_hist:
                offset_s1 = sum(s1_hist) / len(s1_hist)
                mean_s1 = offset_s1
                var_s1 = sum((r - mean_s1)**2 for r in s1_hist) / len(s1_hist)
                std_s1 = math.sqrt(var_s1)
                scale_s1 = std_s1 * 1.414
                if scale_s1 < 0.01:
                    scale_s1 = 0.1
        if offset_s2 == 0.0 or scale_s2 == 1.0:
            if s2_hist:
                offset_s2 = sum(s2_hist) / len(s2_hist)
                mean_s2 = offset_s2
                var_s2 = sum((r - mean_s2)**2 for r in s2_hist) / len(s2_hist)
                std_s2 = math.sqrt(var_s2)
                scale_s2 = std_s2 * 1.414
                if scale_s2 < 0.01:
                    scale_s2 = 0.1

        # Determine peak-to-peak variation to check if there is signal activity to fit
        peak_to_peak_s1 = max(s1_hist) - min(s1_hist) if s1_hist else 0.0
        peak_to_peak_s2 = max(s2_hist) - min(s2_hist) if s2_hist else 0.0

        is_measuring = getattr(self, 'measuring', False) or getattr(self, 'calibrating', False)
        if not is_measuring and (peak_to_peak_s1 < 0.05 or peak_to_peak_s2 < 0.05):
            # Draw flat gray lines at raw signal averages
            mean_s1 = sum(s1_hist) / len(s1_hist) if s1_hist else 0.0
            mean_s2 = sum(s2_hist) / len(s2_hist) if s2_hist else 0.0
            fit_s1 = [mean_s1] * len(s1_hist)
            fit_s2 = [mean_s2] * len(s2_hist)

            self.plot_lines['S1_raw_fit'].set_color('gray')
            self.plot_lines['S2_raw_fit'].set_color('gray')
            self.plot_lines['S1_raw_fit'].set_data(x, fit_s1)
            self.plot_lines['S2_raw_fit'].set_data(x, fit_s2)
            self.plot_lines['S1_raw_fit'].set_visible(True)
            self.plot_lines['S2_raw_fit'].set_visible(True)

            # Clear Lissajous circle trace so it doesn't show noise circle
            self.plot_lines['circle_trace'].set_data([], [])
            self.plot_lines['circle_current'].set_data([], [])
            self.plot_lines['circle_pointer'].set_data([], [])
            self.plot_quiver.set_visible(False)
            self.plot_canvas.draw_idle()
            self.plot_canvas_circle.draw_idle()
            return

        for r1, r2 in zip(s1_hist, s2_hist):
            s1 = (r1 - offset_s1) / (scale_s1 if scale_s1 > 1e-12 else 1.0)
            s2 = (r2 - offset_s2) / (scale_s2 if scale_s2 > 1e-12 else 1.0)
            s1_norm_history.append(s1)
            s2_norm_history.append(s2)

        # Compute the phase at each normalized sample
        phases = [math.atan2(y, x) for x, y in zip(s1_norm_history, s2_norm_history)]
        
        # Unwrap the phases to avoid jumps during fitting
        unwrapped_phases = []
        if phases:
            unwrapped_phases.append(phases[0])
            for i in range(1, len(phases)):
                diff = phases[i] - phases[i-1]
                diff = (diff + math.pi) % (2 * math.pi) - math.pi
                unwrapped_phases.append(unwrapped_phases[-1] + diff)
        
        # Fit a line (linear regression) to the phase of the last 20 samples to filter out noise
        fitted_phases = list(unwrapped_phases)
        N = 20
        if len(unwrapped_phases) >= N:
            sum_x = sum(float(j) for j in range(N))
            sum_x2 = sum(float(j)**2 for j in range(N))
            denom = N * sum_x2 - sum_x**2
            
            for i in range(N - 1, len(unwrapped_phases)):
                y = unwrapped_phases[i - N + 1 : i + 1]
                sum_y = sum(y)
                sum_xy = sum(float(j) * y[j] for j in range(N))
                a = (N * sum_xy - sum_x * sum_y) / denom
                b = (sum_y - a * sum_x) / N
                # Value at the end of the window (index N-1)
                fitted_phases[i] = a * (N - 1) + b

        # Reconstruct the smoothed/fitted sine and cosine (perfect unit circle!)
        smoothed_s1 = [math.cos(p) for p in fitted_phases]
        smoothed_s2 = [math.sin(p) for p in fitted_phases]

        # Use unit circle values directly for plotting to keep it perfectly undistorted
        display_s1 = smoothed_s1
        display_s2 = smoothed_s2

        self.plot_lines['circle_trace'].set_data(display_s1, display_s2)

        # Scale fit back to raw voltage levels for raw S1 and S2 plots
        fit_s1 = [s * scale_s1 + offset_s1 for s in smoothed_s1]
        fit_s2 = [s * scale_s2 + offset_s2 for s in smoothed_s2]

        self.plot_lines['S1_raw_fit'].set_color('orange')
        self.plot_lines['S2_raw_fit'].set_color('magenta')
        self.plot_lines['S1_raw_fit'].set_data(x, fit_s1)
        self.plot_lines['S2_raw_fit'].set_data(x, fit_s2)
        self.plot_lines['S1_raw_fit'].set_visible(True)
        self.plot_lines['S2_raw_fit'].set_visible(True)

        if display_s1:
            curr_x = display_s1[-1]
            curr_y = display_s2[-1]
            self.plot_lines['circle_current'].set_data([curr_x], [curr_y])
            self.plot_lines['circle_pointer'].set_data([0, curr_x], [0, curr_y])

            # Ensure the axes limits are always a bit larger than the actual plotted values
            max_extent = 1.0
            if display_s1 and display_s2:
                max_extent = max(max(abs(v) for v in display_s1), max(abs(v) for v in display_s2), 1.0)
            target_limit = max_extent * 1.15
            self.axis_circle.set_xlim(-target_limit, target_limit)
            self.axis_circle.set_ylim(-target_limit, target_limit)

            if 'ref_circle' in self.plot_lines and self.plot_lines['ref_circle'] is not None:
                theta = [t * 2 * math.pi / 100 for t in range(101)]
                ref_r = 1.0
                ref_x = [ref_r * math.cos(t) for t in theta]
                ref_y = [ref_r * math.sin(t) for t in theta]
                try:
                    self.plot_lines['ref_circle'].set_data(ref_x, ref_y)
                except Exception:
                    pass

            if self.latest_sample is not None and self.latest_sample.direction in ["forward", "backward"]:
                phi = math.atan2(curr_y, curr_x)
                if self.latest_sample.direction == "forward":
                    dx, dy = -math.sin(phi), math.cos(phi)
                    color = 'green'
                else:
                    dx, dy = math.sin(phi), -math.cos(phi)
                    color = 'red'

                arrow_len = 0.35
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

    # -----------------------------------------------------------------------------
    # 9.1 SHUT DOWN HARDWARE CLEANLY
    # -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------
# 9. PROGRAM START
# -----------------------------------------------------------------------------

# 9. PROGRAM START
if __name__ == "__main__":
    run_gui()
