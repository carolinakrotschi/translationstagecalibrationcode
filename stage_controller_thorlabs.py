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


# =============================================================================
# STAGE CONTROLLER
# =============================================================================

class StageController:

    def __init__(self, serial_no="45517804"):

        self.serial_no = serial_no
        self.device = None
        self.connected = False

        self.current_position = 0.0
        self.target_position = 0.0

        self.step_size = 0.001
        self.velocity = 10.0

        self.is_moving = False

        self.min_position = 0.0
        self.max_position = 300.0

    # =============================================================================
    # CONNECT
    # =============================================================================

    def connect(self):

        try:
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

            print("Homing stage...")
            self.device.Home(60000)

            self._wait_until_ready()

            print("Homing complete")

            self.connected = True
            return True

        except Exception as e:
            print("Stage connection error:", e)
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

    # =============================================================================
    # POSITION
    # =============================================================================

    def get_position(self):

        if not self.connected:
            return self.current_position

        for _ in range(5):
            try:
                self.current_position = float(str(self.device.Position))
                return self.current_position
            except Exception as e:
                print("get_position error:", e)
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

        if not self.connected or self.is_moving:
            return False

        target_mm = self.clamp_position(target_mm)
        self.target_position = target_mm
        self.is_moving = True

        def worker():
            try:
                self.device.MoveTo(Decimal(target_mm), 60000)
                self.current_position = self.get_position()

            except Exception as e:
                print("Move error:", e)

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

    def set_velocity(self, vel):

        try:
            params = self.device.GetVelocityParams()
            params.MaxVelocity = Decimal(abs(float(vel)))
            self.device.SetVelocityParams(params)
            self.velocity = vel
            return True

        except Exception as e:
            print("Velocity error:", e)
            return False

    # =============================================================================
    # STOP
    # =============================================================================

    def stop(self):

        try:
            if self.connected:
                self.device.StopImmediate()
        except Exception as e:
            print("Stop error:", e)

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
            print("Close error:", e)


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