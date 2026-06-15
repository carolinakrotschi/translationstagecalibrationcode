from pipython import GCSDevice
import threading
import time


STAGE_AXIS = "1"


class StageController:

    def __init__(self):

        self.device = None
        self.connected = False
        self.current_position = 0.0
        self.target_position = 0.0
        self.step_size = 0.020000000
        self.velocity = 0.1
        self.is_moving = False
        self.min_position = -12.5
        self.max_position = 12.5

    def connect(self):

        try:
            self.device = GCSDevice()
            self.device.InterfaceSetupDlg()
            self.connected = True
            self.current_position = self.get_position()
            return True
        except Exception as e:
            print("Stage connection error:", e)
            self.connected = False
            return False

    def get_position(self):

        if not self.connected:
            return self.current_position

        try:
            pos = self.device.qPOS(STAGE_AXIS)
            self.current_position = float(pos[STAGE_AXIS])
            return self.current_position
        except Exception as e:
            print("Position error:", e)
            return self.current_position

    def clamp_position(self, pos):
        return max(self.min_position, min(self.max_position, float(pos)))

    def move_absolute(self, target_mm):

        if not self.connected or self.is_moving:
            return False

        def worker():
            try:
                self.is_moving = True
                target_mm_clamped = self.clamp_position(target_mm)
                self.target_position = target_mm_clamped
                self.device.MOV(STAGE_AXIS, target_mm_clamped)

                while self.device.IsMoving()[STAGE_AXIS]:
                    self.current_position = self.get_position()
                    time.sleep(0.02)

                self.current_position = self.get_position()
            except Exception as e:
                print("Move absolute error:", e)
            finally:
                self.is_moving = False

        threading.Thread(target=worker, daemon=True).start()
        return True

    def move_relative(self, distance_mm):
        current = self.get_position()
        target = current + distance_mm
        return self.move_absolute(target)

    def step_positive(self):
        return self.move_relative(self.step_size)

    def step_negative(self):
        return self.move_relative(-self.step_size)

    def move_to_max(self):
        return self.move_absolute(self.max_position)

    def move_to_min(self):
        return self.move_absolute(self.min_position)

    def set_step_size(self, step_size):
        try:
            self.step_size = float(step_size)
        except:
            pass

    def set_velocity(self, vel=None):
        if vel is not None:
            self.velocity = float(vel)
        return self.velocity

    def stop(self):
        try:
            if self.connected:
                self.device.STP()
        except Exception as e:
            print("Stage stop error:", e)

    def close(self):
        try:
            if self.device is not None:
                self.device.CloseConnection()
        except Exception as e:
            print("Stage close error:", e)
