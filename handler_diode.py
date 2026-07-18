# TABLE OF CONTENTS
# 1. Imports
# 2. Diode setup constants
# 3. Helper functions
# 4. Dataclasses and Reader/Counter/Handler classes


# -----------------------------------------------------------------------------
# 1. IMPORTS
# -----------------------------------------------------------------------------

import math
import time
from dataclasses import dataclass

# -----------------------------------------------------------------------------
# 2. DIODE SETUP CONSTANTS
# -----------------------------------------------------------------------------

PHOTODIODE_CHANNEL = "Dev1/ai0"
PHOTODIODE_REF_CHANNEL = "Dev1/ai1s"

USE_REFERENCE_DIODE = True

PHOTODIODE_COS_CHANNEL = "Dev1/ai0"
PHOTODIODE_SIN_CHANNEL = "Dev1/ai1"

CALIBRATION_SECONDS = 5.0
SAMPLE_INTERVAL_S = 0.005
LASER_WAVELENGTH_NM = 787.3
PHASE_DIRECTION_SIGN = 1
MIN_SIGNAL_RADIUS = 0.05

# So that you do not have to understand every line of the code, I will now explain the complete path of a diode signal through this file
# 0. What is happening: class in which it is happening : function in the class in which it is happening : what is happening explained in a more precise way
# 1. The diode settings are defined: global constants : module setup : stores the NI channels, calibration time, sampling interval, wavelength, and signal limits
# 2. The fringe distance is calculated: helper function : compute_fringe_distance_mm() : converts the laser wavelength into the distance corresponding to one fringe
# 3. The phase is processed: helper functions : wrap_to_pi() / completed_signed_fringes() : corrects phase jumps and converts phase into a signed fringe count
# 4. The single-diode hardware is connected: NISingleDiodeReader : connect() : creates the NI task for one analog voltage channel
# 5. The single-diode signal is calibrated: SingleDiodeCounter : calibrate_from_samples() : calculates voltage minimum, maximum, offset, and scale
# 6. The single-diode signal is read and normalized: SingleDiodeHandler : read() : reads the raw voltage and returns a processed sample
# 7. The reference diodes are connected: NIReferenceDiodeReader : connect() : creates an NI task for the measurement and reference channels
# 8. The reference signal is calibrated: ReferenceDiodeCounter : calibrate_from_samples() : calculates the offset and scale of the voltage ratio
# 9. The reference ratio is processed: ReferenceDiodeCounter : update() : divides the measurement voltage by the reference voltage and normalizes the result
# 10. Calibration is managed: SingleDiodeHandler / ReferenceDiodeHandler : calibrate() : collects samples for a defined time and applies the calibration
# 11. The hardware connections are closed: reader classes : close() : closes the NI tasks and releases the hardware resources

# -----------------------------------------------------------------------------
# CALCULATE THE FRINGE DISTANCE
# -----------------------------------------------------------------------------
def compute_fringe_distance_mm(wavelength_nm):

    return (wavelength_nm / 2) / 1_000_000

# -----------------------------------------------------------------------------
# WRAP THE PHASE ANGLE TO PI
# -----------------------------------------------------------------------------
def wrap_to_pi(angle_rad):

    return (angle_rad + math.pi) % (2 * math.pi) - math.pi

# -----------------------------------------------------------------------------
# CALCULATE THE COMPLETED SIGNED FRINGES
# -----------------------------------------------------------------------------
def completed_signed_fringes(fringe_position):

    if fringe_position == 0:
        return 0

    sign = 1 if fringe_position > 0 else -1

    return sign * math.floor(
        abs(fringe_position)
    )

# -----------------------------------------------------------------------------
# 4. DATACLASSES AND READER/COUNTER/HANDLER CLASSES
# -----------------------------------------------------------------------------

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

    # -----------------------------------------------------------------------------
    # INITIALIZE THE SINGLE DIODE CHANNEL
    # -----------------------------------------------------------------------------
    def __init__(self, channel=PHOTODIODE_CHANNEL):

        self.channel = channel
        self.task = None

    # -----------------------------------------------------------------------------
    # CONNECT TO THE SINGLE DIODE HARDWARE
    # -----------------------------------------------------------------------------
    def connect(self):

        import nidaqmx

        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(
            self.channel
        )

        return True

    # -----------------------------------------------------------------------------
    # READ THE RAW SINGLE DIODE VOLTAGE
    # -----------------------------------------------------------------------------
    def read(self):

        if self.task is None:
            raise RuntimeError("NI diode task is not connected.")

        return float(
            self.task.read()
        )

    # -----------------------------------------------------------------------------
    # CLOSE THE SINGLE DIODE CONNECTION
    # -----------------------------------------------------------------------------
    def close(self):

        if self.task is not None:
            self.task.close()
            self.task = None

class SingleDiodeCounter:

    # -----------------------------------------------------------------------------
    # INITIALIZE THE COUNTER VARIABLES
    # -----------------------------------------------------------------------------
    def __init__(self):

        self.min_voltage = 0.0
        self.max_voltage = 0.0
        self.offset_voltage = 0.0
        self.scale_voltage = 1.0
        self.calibration = None
        self.sample_count = 0

    # -----------------------------------------------------------------------------
    # CALCULATE CALIBRATION OFFSET AND SCALE
    # -----------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------
    # RESET THE SAMPLE COUNT
    # -----------------------------------------------------------------------------
    def reset(self):

        self.sample_count = 0

    # -----------------------------------------------------------------------------
    # NORMALIZE THE VOLTAGE
    # -----------------------------------------------------------------------------
    def normalize(self, raw_voltage):

        return (
            raw_voltage - self.offset_voltage
        ) / self.scale_voltage

    # -----------------------------------------------------------------------------
    # CREATE A NORMALIZED SAMPLE
    # -----------------------------------------------------------------------------
    def update(self, raw_voltage):

        self.sample_count += 1

        return SingleDiodeSample(
            timestamp=time.time(),
            raw_voltage=raw_voltage,
            normalized_voltage=self.normalize(raw_voltage),
            valid=True
        )

class SingleDiodeHandler:

    # -----------------------------------------------------------------------------
    # INITIALIZE THE SINGLE DIODE HANDLER
    # -----------------------------------------------------------------------------
    def __init__(self, channel=PHOTODIODE_CHANNEL):

        self.reader = NISingleDiodeReader(
            channel=channel
        )
        self.counter = SingleDiodeCounter()

    # -----------------------------------------------------------------------------
    # CONNECT TO THE SINGLE DIODE HARDWARE
    # -----------------------------------------------------------------------------
    def connect(self):

        return self.reader.connect()

    # -----------------------------------------------------------------------------
    # CALIBRATE THE SINGLE DIODE
    # -----------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------
    # READ AND NORMALIZE THE VOLTAGE
    # -----------------------------------------------------------------------------
    def read(self):

        return self.counter.update(
            self.reader.read()
        )

    # -----------------------------------------------------------------------------
    # CLOSE THE SINGLE DIODE CONNECTION
    # -----------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------
    # INITIALIZE THE REFERENCE DIODE CHANNELS
    # -----------------------------------------------------------------------------
    def __init__(self, int_channel=PHOTODIODE_CHANNEL, ref_channel=PHOTODIODE_REF_CHANNEL):

        self.int_channel = int_channel
        self.ref_channel = ref_channel
        self.task = None

    # -----------------------------------------------------------------------------
    # CONNECT TO THE REFERENCE DIODE HARDWARE
    # -----------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------
    # READ THE RAW VOLTAGES
    # -----------------------------------------------------------------------------
    def read(self):

        if self.task is None:
            raise RuntimeError("NI reference diode task is not connected.")

        values = self.task.read()

        if len(values) != 2:
            raise RuntimeError(
                "Expected two analog input values (Pint, Pl) from the NI task."
            )

        return float(values[0]), float(values[1])

    # -----------------------------------------------------------------------------
    # CLOSE THE REFERENCE DIODE CONNECTION
    # -----------------------------------------------------------------------------
    def close(self):

        if self.task is not None:
            self.task.close()
            self.task = None

class ReferenceDiodeCounter:

    # -----------------------------------------------------------------------------
    # INITIALIZE THE COUNTER VARIABLES
    # -----------------------------------------------------------------------------
    def __init__(self):

        self.min_ratio = 0.0
        self.max_ratio = 0.0
        self.offset_ratio = 0.0
        self.scale_ratio = 1.0
        self.calibration = None
        self.sample_count = 0

    # -----------------------------------------------------------------------------
    # CALCULATE CALIBRATION OFFSET AND SCALE
    # -----------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------
    # RESET THE SAMPLE COUNT
    # -----------------------------------------------------------------------------
    def reset(self):

        self.sample_count = 0

    # -----------------------------------------------------------------------------
    # NORMALIZE THE RATIO
    # -----------------------------------------------------------------------------
    def normalize(self, ratio):

        return (
            ratio - self.offset_ratio
        ) / self.scale_ratio

    # -----------------------------------------------------------------------------
    # CALCULATE THE RATIO AND NORMALIZE
    # -----------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------
    # INITIALIZE THE REFERENCE DIODE HANDLER
    # -----------------------------------------------------------------------------
    def __init__(self, int_channel=PHOTODIODE_CHANNEL, ref_channel=PHOTODIODE_REF_CHANNEL):

        self.reader = NIReferenceDiodeReader(
            int_channel=int_channel,
            ref_channel=ref_channel
        )
        self.counter = ReferenceDiodeCounter()

    # -----------------------------------------------------------------------------
    # CONNECT TO THE REFERENCE DIODE HARDWARE
    # -----------------------------------------------------------------------------
    def connect(self):

        return self.reader.connect()

    # -----------------------------------------------------------------------------
    # CALIBRATE THE REFERENCE DIODES
    # -----------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------
    # READ AND PROCESS THE VOLTAGES
    # -----------------------------------------------------------------------------
    def read(self):

        raw_int, raw_ref = self.reader.read()

        return self.counter.update(
            raw_int,
            raw_ref
        )

    # -----------------------------------------------------------------------------
    # CLOSE THE REFERENCE DIODE CONNECTION
    # -----------------------------------------------------------------------------
    def close(self):

        self.reader.close()

