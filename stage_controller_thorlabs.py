# =============================================================================
# TABLE OF CONTENTS
# 1. Imports
# 2. StageController setup
# 3. Connection and limits
# 4. Position helpers
# 5. Movement commands
# 6. Cleanup
# =============================================================================


# =============================================================================
# 1. IMPORTS
# =============================================================================

import time
import threading
import clr

clr.AddReference(
    r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI.dll"
)

clr.AddReference(
    r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.GenericMotorCLI.dll"
)

clr.AddReference(
    r"C:\Program Files\Thorlabs\Kinesis\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll"
)

from System import Decimal

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage


# =============================================================================
# 2. STAGE CONTROLLER CLASS
# =============================================================================

class StageController:

    # =========================================================================
    # 2.1 INITIAL STAGE STATE
    # =========================================================================

    def __init__(self, serial_no="45877001"):

        self.serial_no = serial_no

        self.device = None

        self.connected = False

        self.current_position = 0.0

        self.target_position = 0.0

        self.step_size = 0.0001

        self.velocity = 10.0

        self.is_moving = False

        self.min_position = 0.0

        self.max_position = 300.0

    # =========================================================================
    # 3.1 CONNECT TO THE TRANSLATION STAGE
    # =========================================================================

    def connect(self):

        try:

            DeviceManagerCLI.BuildDeviceList()

            self.device = (
                LongTravelStage.CreateLongTravelStage(
                    self.serial_no
                )
            )

            self.device.Connect(
                self.serial_no
            )

            if not self.device.IsSettingsInitialized():

                self.device.WaitForSettingsInitialized(
                    10000
                )

            self.device.StartPolling(
                250
            )

            time.sleep(0.5)

            self.device.EnableDevice()

            time.sleep(0.5)

            print("Homing stage...")

            self.device.Home(
                60000
            )

            print("Homing complete")

            self.current_position = (
                self.read_device_position()
            )

            self.read_travel_limits()

            self.connected = True

            return True

        except Exception as e:

            print(
                "Stage connection error:",
                e
            )

            self.connected = False

            return False

    # =========================================================================
    # 3.2 READ HARDWARE LIMITS
    # =========================================================================

    def read_travel_limits(self):

        self.min_position = 0.0

        self.max_position = 300.0

    def update_travel_limits(self):

        try:

            self.read_travel_limits()

            return True

        except Exception as e:

            print(
                "Stage limit read error:",
                e
            )

            return False

    # =========================================================================
    # 4.1 READ CURRENT POSITION
    # =========================================================================

    def read_device_position(self):

        return float(
            self.device.Position
        )

    def get_position(self):

        if not self.connected:

            return self.current_position

        try:

            self.current_position = (
                self.read_device_position()
            )

            return self.current_position

        except Exception as e:

            print(
                "Position error:",
                e
            )

            return self.current_position

    # =========================================================================
    # 4.2 LIMIT POSITION TO SAFE RANGE
    # =========================================================================

    def clamp_position(self, position_mm):

        return max(
            self.min_position,
            min(
                self.max_position,
                float(position_mm)
            )
        )

    # =========================================================================
    # 5.1 MOVE TO ABSOLUTE POSITION
    # =========================================================================

    def move_absolute(self, target_mm):

        if not self.connected:

            return False

        if self.is_moving:

            return False

        target_mm = self.clamp_position(
            target_mm
        )

        self.target_position = target_mm

        self.is_moving = True

        def worker():

            try:

                self.device.MoveTo(
                    Decimal(target_mm),
                    60000
                )

                self.current_position = (
                    self.get_position()
                )

            except Exception as e:

                print(
                    "Move absolute error:",
                    e
                )

            finally:

                self.is_moving = False

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

        return True

    # =========================================================================
    # 5.2 MOVE RELATIVE
    # =========================================================================

    def move_relative(self, distance_mm):

        current = self.get_position()

        target = current + distance_mm

        return self.move_absolute(
            target
        )

    # =========================================================================
    # 5.3 STEP MOVEMENT
    # =========================================================================

    def step_positive(self):

        return self.move_relative(
            self.step_size
        )

    def step_negative(self):

        return self.move_relative(
            -self.step_size
        )

    # =========================================================================
    # 5.4 MOVE TO LIMITS
    # =========================================================================

    def move_to_max(self):

        return self.move_absolute(
            self.max_position
        )

    def move_to_min(self):

        return self.move_absolute(
            self.min_position
        )

    # =========================================================================
    # 5.5 SET CURRENT POSITION AS ZERO
    # =========================================================================

    def set_zero_position(self):

        try:

            if not self.connected:

                return False

            current = (
                self.get_position()
            )

            print(
                f"Current position = {current:.6f} mm"
            )

            print(
                "Kinesis integrated stages do not "
                "support redefining encoder position "
                "like PI controllers."
            )

            return True

        except Exception as e:

            print(
                "Set zero position error:",
                e
            )

            return False

    # =========================================================================
    # 5.6 STEP SIZE
    # =========================================================================

    def set_step_size(self, step_size):

        try:

            self.step_size = float(
                step_size
            )

        except Exception:

            pass

    # =========================================================================
    # 5.7 READ VELOCITY
    # =========================================================================

    def get_velocity(self):

        if not self.connected:

            return self.velocity

        try:

            params = (
                self.device.GetVelocityParams()
            )

            self.velocity = float(
                params.MaxVelocity
            )

            return self.velocity

        except Exception as e:

            print(
                "Velocity read error:",
                e
            )

            return self.velocity

    # =========================================================================
    # 5.8 SET VELOCITY
    # =========================================================================

    def set_velocity(self, velocity_mm_s):

        if not self.connected:

            return False

        try:

            velocity_mm_s = abs(
                float(velocity_mm_s)
            )

            if velocity_mm_s <= 0:

                return False

            params = (
                self.device.GetVelocityParams()
            )

            params.MaxVelocity = Decimal(
                velocity_mm_s
            )

            self.device.SetVelocityParams(
                params
            )

            self.velocity = velocity_mm_s

            return True

        except Exception as e:

            print(
                "Velocity set error:",
                e
            )

            return False

    # =========================================================================
    # 6.1 STOP MOTION
    # =========================================================================

    def stop(self):

        try:

            if self.connected:

                self.device.StopImmediate()

        except Exception as e:

            print(
                "Stage stop error:",
                e
            )

    # =========================================================================
    # 6.2 CLOSE CONNECTION
    # =========================================================================

    def close(self):

        try:

            if self.device is not None:

                self.device.StopPolling()

                self.device.Disconnect()

                self.connected = False

        except Exception as e:

            print(
                "Stage close error:",
                e
            )


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":

    stage = StageController(
        serial_no="45877001"
    )

    if stage.connect():

        print(
            "Current position:",
            stage.get_position()
        )

        stage.set_velocity(
            20.0
        )

        stage.move_absolute(
            150.0
        )

        while stage.is_moving:

            time.sleep(
                0.1
            )

        print(
            "New position:",
            stage.get_position()
        )

        stage.close()