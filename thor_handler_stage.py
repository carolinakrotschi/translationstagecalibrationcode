# TABLE OF CONTENTS
# 1. Imports and CLR bindings
# 2. StageController class and connection
# 3. Reference and homing helpers
# 4. Position querying and limits
# 5. Motion commands (absolute, relative)
# 6. Velocity and parameter configurations
# 7. Cleanup and connection close

# -----------------------------------------------------------------------------
# 1. IMPORTS AND CLR BINDINGS
# -----------------------------------------------------------------------------
import time
import threading
import clr
from System import Decimal

clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.IntegratedStepperMotorsCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage

REQUESTED_ACCELERATION = 1.0
FALLBACK_MOVING_ACCELERATION = 1.0
MIN_ACCELERATION = 0.5

# -----------------------------------------------------------------------------
# 2. STAGECONTROLLER CLASS AND CONNECTION
# -----------------------------------------------------------------------------
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
        self.acceleration = 0.0

        self.is_moving = False

        self.min_position = 0.0
        self.max_position = 300.0
        self.home_on_connect = True

    def _get_discovered_serial_numbers(self):

        try:
            DeviceManagerCLI.BuildDeviceList()
            device_list = DeviceManagerCLI.GetDeviceList()

            if device_list is None:
                return []

            try:
                count = int(getattr(device_list, "Count", 0))
            except Exception:
                count = None

            if count is not None:
                return [
                    str(device_list[i])
                    for i in range(count)
                    if str(device_list[i]).strip()
                ]

            return [str(item) for item in list(device_list) if str(item).strip()]

        except Exception as e:
            self.last_error = f"Could not enumerate Thorlabs devices: {e}"
            print(self.last_error)
            return []

    def _resolve_serial_number(self):

        configured_serial = str(self.serial_no or "").strip()
        discovered_serials = self._get_discovered_serial_numbers()

        if configured_serial and configured_serial in discovered_serials:
            return configured_serial

        if discovered_serials:
            return discovered_serials[0]

        if configured_serial:
            return configured_serial

        raise RuntimeError("No Thorlabs stage serial number available")

    #connects the actual motor to the software
    def connect(self):

        try:
            self.last_error = ""
            resolved_serial = self._resolve_serial_number()
            self.serial_no = resolved_serial

            self.device = LongTravelStage.CreateLongTravelStage(
                resolved_serial
            )

            print(f"Connect to Thorlabs stage {resolved_serial}...")
            self.device.Connect(resolved_serial)

            if not bool(getattr(self.device, "IsConnected", False)):
                raise RuntimeError("Device is not connected after Connect()")

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

            print("Load motor configuration...")
            self.device.LoadMotorConfiguration(resolved_serial)

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

        #in case of failure (cable unplugged, ...)
        except Exception as e:
            self.last_error = f"Stage connection error: {e}"
            print(self.last_error)
            self.connected = False
            return False

# -----------------------------------------------------------------------------
# 3. REFERENCE AND HOMING HELPERS
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 4. POSITION QUERYING AND LIMITS
# -----------------------------------------------------------------------------
    #for the UI it is essential, that the current position is always available
    def get_position(self):

        if not self.connected:
            return self.current_position

        for _ in range(5):
            try:
                pos_str = str(self.device.Position).replace(",", ".") #this gives the position
                self.current_position = float(pos_str)
                return self.current_position
            #in case of failure (cable unplugged, ...)
            except Exception as e:
                self.last_error = f"get_position error: {e}"
                print(self.last_error)
                time.sleep(0.2)

        return self.current_position

    #limits the position to the physical limits of the stage (0.0 mm to 300.0 mm)
    def clamp_position(self, pos):
        return max(self.min_position, min(self.max_position, float(pos)))

# -----------------------------------------------------------------------------
# 5. MOTION COMMANDS
# -----------------------------------------------------------------------------
    #for driving to an absolute position, does that in the background, so that the UI is still usable
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
                self.device.MoveTo(Decimal(float(target_mm)), 180000) #scan the motion command
                self.current_position = self.get_position() #after arrival, question the position again

            #in case of failure (cable unplugged, ...)
            except Exception as e:
                self.last_error = f"Move error: {e}"
                print(self.last_error)

            finally:
                self.is_moving = False #at the end, when the stage is not moving anymore, set is_moving to false, so that the UI knows that the stage is not moving anymore

        threading.Thread(target=worker, daemon=True).start()
        return True

    #moves stage by relative distance
    def move_relative(self, delta):
        return self.move_absolute(self.get_position() + delta)

# -----------------------------------------------------------------------------
# 6. VELOCITY AND PARAMETER CONFIGURATIONS
# -----------------------------------------------------------------------------
    def set_velocity(self, vel=None, acceleration_mm_s2=None):

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

        if not self.connected:
            self.velocity = abs(float(vel))
            if acceleration_mm_s2 is None:
                requested_acceleration = self.requested_acceleration
            else:
                requested_acceleration = abs(float(acceleration_mm_s2))
            self.requested_acceleration = requested_acceleration
            self.acceleration = requested_acceleration
            return True

        try:
            params = self.device.GetVelocityParams()
            params.MaxVelocity = Decimal(abs(float(vel)))

            if acceleration_mm_s2 is None:
                requested_acceleration = self.requested_acceleration
            else:
                requested_acceleration = abs(float(acceleration_mm_s2))

            # Ensure minimum acceleration for Thorlabs hardware
            if requested_acceleration < MIN_ACCELERATION:
                requested_acceleration = MIN_ACCELERATION

            self.requested_acceleration = requested_acceleration
            self.acceleration = requested_acceleration
            params.Acceleration = Decimal(self.acceleration)
            self.device.SetVelocityParams(params) #send velocity command to hardware
            self.velocity = vel
            return True

        #in case of failure (cable unplugged, ...)
        except Exception as e:
            self.last_error = f"Velocity error: {e}"
            print(self.last_error)
            return False

    #stops the stage (emergency stop when UI stop button is pressed)
    def stop(self):

        stopped = False

        try:
            if self.connected:
                self.device.StopImmediate()
                stopped = True
        #in case of failure (cable unplugged, ...)
        except Exception as e:
            self.last_error = f"Stop error: {e}"
            print(self.last_error)

        if stopped:
            time.sleep(0.05)
            self.is_moving = False #adjusts the position to the point where the stage stopped
            self.current_position = self.get_position()
            self.target_position = self.current_position

# -----------------------------------------------------------------------------
# 7. CLEANUP AND CONNECTION CLOSE
# -----------------------------------------------------------------------------
    def close(self):

        try:
            if self.device is not None:
                self.device.StopPolling()
                self.device.Disconnect()
                self.connected = False

        #in case of failure (cable unplugged, ...)
        except Exception as e:
            self.last_error = f"Close error: {e}"
            print(self.last_error)

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
