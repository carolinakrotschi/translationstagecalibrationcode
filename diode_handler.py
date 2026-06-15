import math
import time
from dataclasses import dataclass


# Single-diode readout uses one NI analog input first.
PHOTODIODE_CHANNEL = "Dev1/ai0"
PHOTODIODE_REF_CHANNEL = "Dev1/ai1"

# Set to True to use reference photodiode (Pl) and measure Pint/Pl ratio.
# Set to False to fall back to a single photodiode measuring Pint raw voltage only.
USE_REFERENCE_DIODE = True

# S1 is treated as cosine, S2 as sine for later quadrature readout.
PHOTODIODE_COS_CHANNEL = "Dev1/ai0"
PHOTODIODE_SIN_CHANNEL = "Dev1/ai1"

LASER_WAVELENGTH_NM = 780.0
PHASE_DIRECTION_SIGN = 1
MIN_SIGNAL_RADIUS = 0.05
CALIBRATION_SECONDS = 5.0
SAMPLE_INTERVAL_S = 0.005


def compute_fringe_distance_mm(wavelength_nm):

    return (wavelength_nm / 2) / 1_000_000


@dataclass
class SingleDiodeCalibration:

    min_voltage: float
    max_voltage: float
    offset_voltage: float
    scale_voltage: float
    sample_count: int


@dataclass
class SingleDiodeSample:

    timestamp: float
    raw_voltage: float
    normalized_voltage: float
    valid: bool


class NISingleDiodeReader:

    def __init__(self, channel=PHOTODIODE_CHANNEL):

        self.channel = channel
        self.task = None

    def connect(self):

        import nidaqmx

        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(
            self.channel
        )

        return True

    def read(self):

        if self.task is None:
            raise RuntimeError("NI diode task is not connected.")

        return float(
            self.task.read()
        )

    def close(self):

        if self.task is not None:
            self.task.close()
            self.task = None


class SingleDiodeCounter:

    def __init__(self):

        self.min_voltage = 0.0
        self.max_voltage = 0.0
        self.offset_voltage = 0.0
        self.scale_voltage = 1.0
        self.calibration = None
        self.sample_count = 0

    def calibrate_from_samples(self, raw_samples):

        if not raw_samples:
            raise ValueError("No diode calibration samples were collected.")

        self.min_voltage = min(raw_samples)
        self.max_voltage = max(raw_samples)
        self.offset_voltage = (
            self.min_voltage + self.max_voltage
        ) / 2
        self.scale_voltage = (
            self.max_voltage - self.min_voltage
        ) / 2

        if self.scale_voltage <= 1e-12:
            self.scale_voltage = 1.0

        self.calibration = SingleDiodeCalibration(
            min_voltage=self.min_voltage,
            max_voltage=self.max_voltage,
            offset_voltage=self.offset_voltage,
            scale_voltage=self.scale_voltage,
            sample_count=len(raw_samples)
        )

        self.reset()

        return self.calibration

    def reset(self):

        self.sample_count = 0

    def normalize(self, raw_voltage):

        return (
            raw_voltage - self.offset_voltage
        ) / self.scale_voltage

    def update(self, raw_voltage):

        self.sample_count += 1

        return SingleDiodeSample(
            timestamp=time.time(),
            raw_voltage=raw_voltage,
            normalized_voltage=self.normalize(raw_voltage),
            valid=True
        )


class SingleDiodeHandler:

    def __init__(self, channel=PHOTODIODE_CHANNEL):

        self.reader = NISingleDiodeReader(
            channel=channel
        )
        self.counter = SingleDiodeCounter()

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

            raw_voltage = self.reader.read()
            samples.append(raw_voltage)

            if sample_callback is not None:
                sample_callback(
                    raw_voltage,
                    time.time() - start_time,
                    seconds
                )

            time.sleep(sample_interval_s)

        if not samples and should_continue is not None and not should_continue():
            return None

        return self.counter.calibrate_from_samples(
            samples
        )

    def read(self):

        return self.counter.update(
            self.reader.read()
        )

    def close(self):

        self.reader.close()


def wrap_to_pi(angle_rad):

    return (angle_rad + math.pi) % (2 * math.pi) - math.pi


def completed_signed_fringes(fringe_position):

    if fringe_position == 0:
        return 0

    sign = 1 if fringe_position > 0 else -1

    return sign * math.floor(
        abs(fringe_position)
    )


@dataclass
class DiodeCalibration:

    cos_min: float
    cos_max: float
    sin_min: float
    sin_max: float
    cos_offset: float
    sin_offset: float
    cos_scale: float
    sin_scale: float
    sample_count: int


@dataclass
class DiodeSample:

    timestamp: float
    raw_cos: float
    raw_sin: float
    cos_value: float
    sin_value: float
    radius: float
    phase_rad: float
    unwrapped_phase_rad: float
    delta_phase_rad: float
    fringe_position: float
    signed_fringes: int
    fringe_delta: int
    total_abs_fringes: int
    direction: str
    valid: bool


class NIDiodeReader:

    def __init__(
        self,
        cos_channel=PHOTODIODE_COS_CHANNEL,
        sin_channel=PHOTODIODE_SIN_CHANNEL
    ):

        self.cos_channel = cos_channel
        self.sin_channel = sin_channel
        self.task = None

    def connect(self):

        import nidaqmx

        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(
            self.cos_channel
        )
        self.task.ai_channels.add_ai_voltage_chan(
            self.sin_channel
        )

        return True

    def read(self):

        if self.task is None:
            raise RuntimeError("NI diode task is not connected.")

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


class DiodeQuadratureCounter:

    def __init__(
        self,
        wavelength_nm=LASER_WAVELENGTH_NM,
        phase_direction_sign=PHASE_DIRECTION_SIGN,
        min_signal_radius=MIN_SIGNAL_RADIUS
    ):

        self.phase_direction_sign = 1 if phase_direction_sign >= 0 else -1
        self.min_signal_radius = min_signal_radius
        self.fringe_distance_mm = compute_fringe_distance_mm(
            wavelength_nm
        )

        self.cos_offset = 0.0
        self.sin_offset = 0.0
        self.cos_scale = 1.0
        self.sin_scale = 1.0
        self.calibration = None

        self.previous_phase_rad = None
        self.unwrapped_phase_rad = 0.0
        self.signed_fringes = 0
        self.total_abs_fringes = 0

    def calibrate_from_samples(self, raw_samples):

        if not raw_samples:
            raise ValueError("No diode calibration samples were collected.")

        cos_values = [
            sample[0]
            for sample in raw_samples
        ]
        sin_values = [
            sample[1]
            for sample in raw_samples
        ]

        cos_min = min(cos_values)
        cos_max = max(cos_values)
        sin_min = min(sin_values)
        sin_max = max(sin_values)

        self.cos_offset = (cos_min + cos_max) / 2
        self.sin_offset = (sin_min + sin_max) / 2
        self.cos_scale = (cos_max - cos_min) / 2
        self.sin_scale = (sin_max - sin_min) / 2

        if self.cos_scale <= 1e-12:
            self.cos_scale = 1.0

        if self.sin_scale <= 1e-12:
            self.sin_scale = 1.0

        self.calibration = DiodeCalibration(
            cos_min=cos_min,
            cos_max=cos_max,
            sin_min=sin_min,
            sin_max=sin_max,
            cos_offset=self.cos_offset,
            sin_offset=self.sin_offset,
            cos_scale=self.cos_scale,
            sin_scale=self.sin_scale,
            sample_count=len(raw_samples)
        )

        self.reset()

        return self.calibration

    def reset(self):

        self.previous_phase_rad = None
        self.unwrapped_phase_rad = 0.0
        self.signed_fringes = 0
        self.total_abs_fringes = 0

    def normalize(self, raw_cos, raw_sin):

        cos_value = (raw_cos - self.cos_offset) / self.cos_scale
        sin_value = (raw_sin - self.sin_offset) / self.sin_scale

        return cos_value, sin_value

    def update(self, raw_cos, raw_sin):

        timestamp = time.time()
        cos_value, sin_value = self.normalize(
            raw_cos,
            raw_sin
        )
        radius = math.hypot(
            cos_value,
            sin_value
        )

        if radius < self.min_signal_radius:
            return DiodeSample(
                timestamp=timestamp,
                raw_cos=raw_cos,
                raw_sin=raw_sin,
                cos_value=cos_value,
                sin_value=sin_value,
                radius=radius,
                phase_rad=0.0,
                unwrapped_phase_rad=self.unwrapped_phase_rad,
                delta_phase_rad=0.0,
                fringe_position=(
                    self.unwrapped_phase_rad / (2 * math.pi)
                ),
                signed_fringes=self.signed_fringes,
                fringe_delta=0,
                total_abs_fringes=self.total_abs_fringes,
                direction="signal_low",
                valid=False
            )

        phase_rad = self.phase_direction_sign * math.atan2(
            sin_value,
            cos_value
        )

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
        new_signed_fringes = completed_signed_fringes(
            fringe_position
        )
        fringe_delta = new_signed_fringes - self.signed_fringes

        if fringe_delta != 0:
            self.total_abs_fringes += abs(
                fringe_delta
            )

        self.signed_fringes = new_signed_fringes

        if delta_phase_rad > 0:
            direction = "forward"
        elif delta_phase_rad < 0:
            direction = "backward"
        else:
            direction = "none"

        return DiodeSample(
            timestamp=timestamp,
            raw_cos=raw_cos,
            raw_sin=raw_sin,
            cos_value=cos_value,
            sin_value=sin_value,
            radius=radius,
            phase_rad=phase_rad,
            unwrapped_phase_rad=self.unwrapped_phase_rad,
            delta_phase_rad=delta_phase_rad,
            fringe_position=fringe_position,
            signed_fringes=self.signed_fringes,
            fringe_delta=fringe_delta,
            total_abs_fringes=self.total_abs_fringes,
            direction=direction,
            valid=True
        )

    def signed_distance_mm(self):

        return (
            self.unwrapped_phase_rad
            / (2 * math.pi)
            * self.fringe_distance_mm
        )


class DiodeHandler:

    def __init__(
        self,
        cos_channel=PHOTODIODE_COS_CHANNEL,
        sin_channel=PHOTODIODE_SIN_CHANNEL,
        wavelength_nm=LASER_WAVELENGTH_NM,
        phase_direction_sign=PHASE_DIRECTION_SIGN
    ):

        self.reader = NIDiodeReader(
            cos_channel=cos_channel,
            sin_channel=sin_channel
        )
        self.counter = DiodeQuadratureCounter(
            wavelength_nm=wavelength_nm,
            phase_direction_sign=phase_direction_sign
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

            raw_sample = self.reader.read()
            samples.append(raw_sample)

            if sample_callback is not None:
                sample_callback(
                    raw_sample,
                    time.time() - start_time,
                    seconds
                )

            time.sleep(sample_interval_s)

        if not samples and should_continue is not None and not should_continue():
            return None

        return self.counter.calibrate_from_samples(
            samples
        )

    def read(self):

        raw_cos, raw_sin = self.reader.read()

        return self.counter.update(
            raw_cos,
            raw_sin
        )

    def close(self):

        self.reader.close()


@dataclass
class ReferenceDiodeCalibration:

    min_ratio: float
    max_ratio: float
    offset_ratio: float
    scale_ratio: float
    sample_count: int


@dataclass
class ReferenceDiodeSample:

    timestamp: float
    raw_int: float
    raw_ref: float
    ratio: float
    normalized_ratio: float
    valid: bool


class NIReferenceDiodeReader:

    def __init__(self, int_channel=PHOTODIODE_CHANNEL, ref_channel=PHOTODE_REF_CHANNEL if 'PHOTODE_REF_CHANNEL' in globals() else PHOTODIODE_REF_CHANNEL):

        self.int_channel = int_channel
        self.ref_channel = ref_channel
        self.task = None

    def connect(self):

        import nidaqmx

        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(
            self.int_channel
        )
        self.task.ai_channels.add_ai_voltage_chan(
            self.ref_channel
        )

        return True

    def read(self):

        if self.task is None:
            raise RuntimeError("NI reference diode task is not connected.")

        values = self.task.read()

        if len(values) != 2:
            raise RuntimeError(
                "Expected two analog input values (Pint, Pl) from the NI task."
            )

        return float(values[0]), float(values[1])

    def close(self):

        if self.task is not None:
            self.task.close()
            self.task = None


class ReferenceDiodeCounter:

    def __init__(self):

        self.min_ratio = 0.0
        self.max_ratio = 0.0
        self.offset_ratio = 0.0
        self.scale_ratio = 1.0
        self.calibration = None
        self.sample_count = 0

    def calibrate_from_samples(self, raw_samples):

        if not raw_samples:
            raise ValueError("No reference diode calibration samples were collected.")

        ratios = []
        for Pint, Pl in raw_samples:
            if abs(Pl) < 1e-6:
                denom = 1e-6 if Pl >= 0 else -1e-6
            else:
                denom = Pl
            ratios.append(Pint / denom)

        self.min_ratio = min(ratios)
        self.max_ratio = max(ratios)
        self.offset_ratio = (
            self.min_ratio + self.max_ratio
        ) / 2
        self.scale_ratio = (
            self.max_ratio - self.min_ratio
        ) / 2

        if self.scale_ratio <= 1e-12:
            self.scale_ratio = 1.0

        self.calibration = ReferenceDiodeCalibration(
            min_ratio=self.min_ratio,
            max_ratio=self.max_ratio,
            offset_ratio=self.offset_ratio,
            scale_ratio=self.scale_ratio,
            sample_count=len(raw_samples)
        )

        self.reset()

        return self.calibration

    def reset(self):

        self.sample_count = 0

    def normalize(self, ratio):

        return (
            ratio - self.offset_ratio
        ) / self.scale_ratio

    def update(self, raw_int, raw_ref):

        self.sample_count += 1

        if abs(raw_ref) < 1e-6:
            denom = 1e-6 if raw_ref >= 0 else -1e-6
        else:
            denom = raw_ref

        ratio = raw_int / denom

        return ReferenceDiodeSample(
            timestamp=time.time(),
            raw_int=raw_int,
            raw_ref=raw_ref,
            ratio=ratio,
            normalized_ratio=self.normalize(ratio),
            valid=True
        )


class ReferenceDiodeHandler:

    def __init__(self, int_channel=PHOTODIODE_CHANNEL, ref_channel=PHOTODIODE_REF_CHANNEL):

        self.reader = NIReferenceDiodeReader(
            int_channel=int_channel,
            ref_channel=ref_channel
        )
        self.counter = ReferenceDiodeCounter()

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

            raw_int, raw_ref = self.reader.read()
            samples.append((raw_int, raw_ref))

            if sample_callback is not None:
                sample_callback(
                    (raw_int, raw_ref),
                    time.time() - start_time,
                    seconds
                )

            time.sleep(sample_interval_s)

        if not samples and should_continue is not None and not should_continue():
            return None

        return self.counter.calibrate_from_samples(
            samples
        )

    def read(self):

        raw_int, raw_ref = self.reader.read()

        return self.counter.update(
            raw_int,
            raw_ref
        )

    def close(self):

        self.reader.close()

