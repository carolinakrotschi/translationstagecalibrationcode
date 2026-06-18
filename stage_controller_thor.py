import time
import threading
import clr
from System import Decimal

# =============================================================================
# KINESIS DLLs
# =============================================================================

clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.IntegratedStepperMotorsCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage


REQUESTED_ACCELERATION = 0.0
FALLBACK_MOVING_ACCELERATION = 1.0


# =============================================================================
# STAGE CONTROLLER
# =============================================================================

class StageController:

    def __init__(self, serial_no="45517804"):

        self.serial_no = serial_no
        self.device = None
        self.connected = False
        self.last_error = ""

        self.current_position = 0.0
        self.target_position = 0.0

        self.step_size = 0.001
        self.velocity = 0.0006
        self.requested_acceleration = REQUESTED_ACCELERATION
        self.acceleration = FALLBACK_MOVING_ACCELERATION

        self.is_moving = False

        self.min_position = 0.0
        self.max_position = 300.0
        self.home_on_connect = True

    # =============================================================================
    # CONNECT
    # =============================================================================

    def connect(self):

        try:
            self.last_error = ""
            DeviceManagerCLI.BuildDeviceList()

            self.device = LongTravelStage.CreateLongTravelStage(
                self.serial_no
            )

            print("Connect...")
            self.device.Connect(self.serial_no)

            time.sleep(1)

            print("StartPolling...")
            self.device.StartPolling(250)

            time.sleep(0.5)

            print("EnableDevice...")
            self.device.EnableDevice()

            time.sleep(0.5)

            print("Wait settings...")

            if not self.device.IsSettingsInitialized():
                self.device.WaitForSettingsInitialized(10000)

            # =========================================================
            # 🔥 CRITICAL FIX: Motor configuration laden
            # =========================================================

            print("Load motor configuration...")
            self.device.LoadMotorConfiguration(self.serial_no)

            time.sleep(1)

            self._wait_until_ready()

            if self.home_on_connect:
                print("Homing stage...")
                self.device.Home(180000)
                self._wait_until_ready()
                print("Homing complete")
            else:
                print("Homing disabled, skipping homing.")

            self.connected = True
            self.current_position = self.get_position()
            return True

        except Exception as e:
            self.last_error = f"Stage connection error: {e}"
            print(self.last_error)
            self.connected = False
            return False

    # =============================================================================
    # SAFE READY CHECK
    # =============================================================================

    def _wait_until_ready(self):

        time.sleep(2)

        for _ in range(50):
            try:
                _ = self.device.Position
                return True
            except:
                time.sleep(0.1)

        return False

    def needs_homing(self):

        try:
            return bool(self.device.NeedsHoming)
        except Exception as e:
            self.last_error = f"Could not query NeedsHoming: {e}"
            print(self.last_error)
            return False

    # =============================================================================
    # POSITION
    # =============================================================================

    def get_position(self):

        if not self.connected:
            return self.current_position

        for _ in range(5):
            try:
                pos_str = str(self.device.Position).replace(",", ".")
                self.current_position = float(pos_str)
                return self.current_position
            except Exception as e:
                self.last_error = f"get_position error: {e}"
                print(self.last_error)
                time.sleep(0.2)

        return self.current_position

    # =============================================================================
    # LIMITS
    # =============================================================================

    def clamp_position(self, pos):
        return max(self.min_position, min(self.max_position, float(pos)))

    # =============================================================================
    # MOVE ABSOLUTE
    # =============================================================================

    def move_absolute(self, target_mm):

        if not self.connected:
            self.last_error = "Stage not connected"
            return False

        if self.is_moving:
            self.last_error = "Stage is already moving"
            return False

        self.last_error = ""
        target_mm = self.clamp_position(target_mm)
        self.target_position = target_mm
        self.is_moving = True

        def worker():
            try:
                self.device.MoveTo(Decimal(float(target_mm)), 180000)
                self.current_position = self.get_position()

            except Exception as e:
                self.last_error = f"Move error: {e}"
                print(self.last_error)

            finally:
                self.is_moving = False

        threading.Thread(target=worker, daemon=True).start()
        return True

    # =============================================================================
    # MOVE RELATIVE
    # =============================================================================

    def move_relative(self, delta):
        return self.move_absolute(self.get_position() + delta)

    # =============================================================================
    # VELOCITY
    # =============================================================================

    def set_velocity(self, vel=None):

        if vel is None:
            try:
                if self.connected:
                    params = self.device.GetVelocityParams()
                    self.velocity = float(str(params.MaxVelocity).replace(",", "."))
                return self.velocity
            except Exception as e:
                self.last_error = f"Get velocity error: {e}"
                print(self.last_error)
                return self.velocity

        try:
            params = self.device.GetVelocityParams()
            params.MaxVelocity = Decimal(abs(float(vel)))

            # Kinesis move profiles need a positive acceleration to move.
            # A requested value of 0 means "do not force a new ramp"; keep the
            # current controller value if it is valid.
            try:
                current_acceleration = float(
                    str(params.Acceleration).replace(",", ".")
                )
            except Exception:
                current_acceleration = self.acceleration

            if self.requested_acceleration <= 0 and current_acceleration > 0:
                self.acceleration = current_acceleration
            elif self.acceleration <= 0:
                self.acceleration = FALLBACK_MOVING_ACCELERATION

            params.Acceleration = Decimal(self.acceleration)
            self.device.SetVelocityParams(params)
            self.velocity = vel
            return True

        except Exception as e:
            self.last_error = f"Velocity error: {e}"
            print(self.last_error)
            return False

    # =============================================================================
    # STOP
    # =============================================================================

    def stop(self):

        stopped = False

        try:
            if self.connected:
                self.device.StopImmediate()
                stopped = True
        except Exception as e:
            self.last_error = f"Stop error: {e}"
            print(self.last_error)

        if stopped:
            time.sleep(0.05)
            self.is_moving = False
            self.current_position = self.get_position()
            self.target_position = self.current_position

    # =============================================================================
    # CLOSE
    # =============================================================================

    def close(self):

        try:
            if self.device is not None:
                self.device.StopPolling()
                self.device.Disconnect()
                self.connected = False

        except Exception as e:
            self.last_error = f"Close error: {e}"
            print(self.last_error)


# =============================================================================
# EXAMPLE
# =============================================================================

if __name__ == "__main__":

    stage = StageController("45517804")

    if stage.connect():

        print("Position:", stage.get_position())

        stage.set_velocity(20.0)

        stage.move_absolute(150.0)

        while stage.is_moving:
            time.sleep(0.1)

        print("Final position:", stage.get_position())

        stage.close()
