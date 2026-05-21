import numpy as np
import time


class FringeCounter:

    def __init__(self):

        self.accumulated_fringes = 0

        self.was_dark = False

        self.last_count_time = 0

        self.dark_counter = 0

        self.bright_counter = 0

        self.intensity_history = []

        self.dark_threshold = 8

        self.bright_threshold = 21

        self.required_dark_frames = 2

        self.required_bright_frames = 2

        self.cooldown = 0.03

        self.calibrating = False

        self.calibration_values = []

        self.calibration_start_time = 0

        self.thresholds_ready = False

    def reset(self):

        self.accumulated_fringes = 0

        self.was_dark = False

        self.last_count_time = 0

        self.dark_counter = 0

        self.bright_counter = 0

        self.intensity_history = []

    def set_thresholds(
        self,
        dark_threshold,
        bright_threshold
    ):

        self.dark_threshold = float(
            dark_threshold
        )

        self.bright_threshold = float(
            bright_threshold
        )

        self.thresholds_ready = True

        self.calibrating = False

    def start_calibration(self):

        self.calibrating = True

        self.thresholds_ready = False

        self.calibration_values = []

        self.calibration_start_time = time.time()

    def process_calibration(
        self,
        intensity
    ):

        self.calibration_values.append(
            intensity
        )

        elapsed = (
            time.time()
            - self.calibration_start_time
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

            self.thresholds_ready = True

            return True

        return False

    def update(
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

        if self.dark_counter >= self.required_dark_frames:

            self.was_dark = True

        if smooth_intensity > self.bright_threshold:

            self.bright_counter += 1

        else:

            self.bright_counter = 0

        cooldown_ok = (
            time.time()
            - self.last_count_time
        ) > self.cooldown

        if (
            self.was_dark
            and self.bright_counter
            >= self.required_bright_frames
            and cooldown_ok
        ):

            self.accumulated_fringes += 1

            self.was_dark = False

            self.last_count_time = time.time()

            self.dark_counter = 0

            self.bright_counter = 0

            return True

        return False

    def get_distance_mm(
        self,
        fringe_distance_mm
    ):

        return (
            self.accumulated_fringes
            * fringe_distance_mm
        )

    def get_distance_um(
        self,
        fringe_distance_mm
    ):

        return (
            self.get_distance_mm(
                fringe_distance_mm
            ) * 1000
        )

    def get_delay_ps(
        self,
        fringe_distance_mm,
        speed_of_light_mm_ps
    ):

        distance_mm = (
            self.get_distance_mm(
                fringe_distance_mm
            )
        )

        return (
            2 * distance_mm
        ) / speed_of_light_mm_ps