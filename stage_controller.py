import threading
import time

from pipython import GCSError, GCSDevice, gcserror, pitools


STAGE_AXIS = "1"
STAGE_CONTROLLER_NAME = ""
AUTO_REFERENCE_ON_CONNECT = False
DEFINE_POSITION_IF_UNREFERENCED = True
REFERENCE_MODE = "FRF"
REFERENCE_TIMEOUT_S = 180
MOVE_POSITION_TOLERANCE_MM = 0.000002


class StageController:

    def __init__(self, controller_name=STAGE_CONTROLLER_NAME):

        self.controller_name = controller_name
        self.device = None
        self.connected = False
        self.last_error = ""
        self.connection_description = ""
        self.current_position = 0.0
        self.target_position = 0.0
        self.step_size = 0.020000000
        self.velocity = 0.1
        self.is_moving = False
        self.min_position = -12.5
        self.max_position = 12.5

    def connect(self):

        if self.connected:
            return True

        self.last_error = ""

        if threading.current_thread() is not threading.main_thread():
            self.last_error = "Stage connection must be started from the main thread"
            print(self.last_error)
            return False

        try:
            self.device = GCSDevice(self.controller_name)
            self._connect_first_available_device()
            self._prepare_axis_for_motion()
            pos = self.device.qPOS(STAGE_AXIS)
            self.connected = True
            self.current_position = float(pos[STAGE_AXIS])
            self.set_velocity(self.velocity)
            return True

        except Exception as error:
            self.last_error = f"Stage connection error: {error}"
            print(self.last_error)
            self.connected = False
            self.is_moving = False

            try:
                if self.device is not None:
                    self.device.CloseConnection()
            except Exception:
                pass

            self.device = None
            return False

    def _connect_first_available_device(self):
        errors = []

        try:
            usb_devices = list(self.device.EnumerateUSB())
        except Exception as error:
            usb_devices = []
            errors.append(f"USB enumeration failed: {error}")

        if usb_devices:
            self.connection_description = usb_devices[0]
            print(f"Connecting first PI USB stage: {self.connection_description}")
            self.device.ConnectUSB(self.connection_description)
            return

        try:
            tcpip_devices = list(self.device.EnumerateTCPIPDevices())
        except Exception as error:
            tcpip_devices = []
            errors.append(f"TCP/IP enumeration failed: {error}")

        if tcpip_devices:
            self.connection_description = tcpip_devices[0]
            print(f"Connecting first PI TCP/IP stage: {self.connection_description}")
            self.device.ConnectTCPIPByDescription(self.connection_description)
            return

        detail = "; ".join(errors)
        if detail:
            raise RuntimeError(f"No PI stage found via USB or TCP/IP ({detail})")

        raise RuntimeError("No PI stage found via USB or TCP/IP")

    def _prepare_axis_for_motion(self):
        self._set_servo(True)

        if not self._is_referenced():
            if DEFINE_POSITION_IF_UNREFERENCED:
                self._define_current_position_as_zero()
            elif AUTO_REFERENCE_ON_CONNECT:
                self._reference_axis()
            else:
                raise RuntimeError(
                    f"PI stage axis {STAGE_AXIS} is not referenced"
                )

        self._set_servo(True)

    def _set_servo(self, enabled):
        try:
            self.device.SVO(STAGE_AXIS, bool(enabled))
        except Exception as error:
            print(f"Stage servo warning: {error}")

    def _is_referenced(self):
        try:
            referenced = self.device.qFRF(STAGE_AXIS)
            return bool(referenced[STAGE_AXIS])
        except Exception as error:
            print(f"Stage reference status warning: {error}")
            return False

    def _define_current_position_as_zero(self):
        print(f"Defining current PI stage axis {STAGE_AXIS} position as 0.0")
        self.device.RON(STAGE_AXIS, False)
        self.device.POS(STAGE_AXIS, 0.0)

    def _reference_axis(self):
        print(f"Referencing PI stage axis {STAGE_AXIS} with {REFERENCE_MODE}...")

        if REFERENCE_MODE == "FRF":
            self.device.FRF(STAGE_AXIS)
        elif REFERENCE_MODE == "FNL":
            self.device.FNL(STAGE_AXIS)
        elif REFERENCE_MODE == "FPL":
            self.device.FPL(STAGE_AXIS)
        else:
            raise RuntimeError(f"Unsupported PI reference mode: {REFERENCE_MODE}")

        pitools.waitonreferencing(
            self.device,
            STAGE_AXIS,
            timeout=REFERENCE_TIMEOUT_S
        )

        if not self._is_referenced():
            raise RuntimeError(
                f"PI stage axis {STAGE_AXIS} is still unreferenced after "
                f"{REFERENCE_MODE}"
            )

    def get_position(self):

        if not self.connected or self.device is None:
            return self.current_position

        try:
            pos = self.device.qPOS(STAGE_AXIS)
            self.current_position = float(pos[STAGE_AXIS])
        except Exception as error:
            self.last_error = f"Stage position error: {error}"
            print(self.last_error)

        return self.current_position

    def clamp_position(self, pos):
        return max(self.min_position, min(self.max_position, float(pos)))

    def move_absolute(self, target_mm):

        if not self.connected or self.device is None:
            self.last_error = "Stage not connected"
            return False

        if self.is_moving:
            self.last_error = "Stage is already moving"
            return False

        target_mm_clamped = self.clamp_position(target_mm)
        self.target_position = target_mm_clamped
        self.is_moving = True

        def worker():
            try:
                self.device.MOV(STAGE_AXIS, target_mm_clamped)

                while self.device.IsMoving()[STAGE_AXIS]:
                    self.current_position = self.get_position()
                    time.sleep(0.02)

                self.current_position = self.get_position()

            except Exception as error:
                self.last_error = f"Stage move error: {error}"
                print(self.last_error)

            finally:
                self.is_moving = False

        threading.Thread(target=worker, daemon=True).start()
        return True

    def move_absolute_blocking(
        self,
        target_mm,
        timeout_s,
        should_continue=None,
        progress_callback=None,
        poll_s=0.05
    ):

        if not self.connected or self.device is None:
            self.last_error = "Stage not connected"
            return False

        target_mm_clamped = self.clamp_position(target_mm)
        self.target_position = target_mm_clamped
        self.is_moving = True
        deadline_s = time.time() + float(timeout_s)

        try:
            self.device.MOV(STAGE_AXIS, target_mm_clamped)

            while True:
                if should_continue is not None and not should_continue():
                    self.stop()
                    return False

                position_mm = self.get_position()
                if progress_callback is not None:
                    progress_callback(position_mm)

                if abs(position_mm - target_mm_clamped) <= MOVE_POSITION_TOLERANCE_MM:
                    return True

                try:
                    on_target = self.device.qONT(STAGE_AXIS)
                    if bool(on_target[STAGE_AXIS]):
                        self.current_position = self.get_position()
                        if progress_callback is not None:
                            progress_callback(self.current_position)
                        return True
                except Exception:
                    pass

                if time.time() >= deadline_s:
                    self.last_error = (
                        f"Stage move timeout at {position_mm:.6f} mm "
                        f"towards {target_mm_clamped:.6f} mm"
                    )
                    print(self.last_error)
                    self.stop()
                    return False

                time.sleep(poll_s)

        except Exception as error:
            self.last_error = f"Stage move error: {error}"
            print(self.last_error)
            self.stop()
            return False

        finally:
            self.is_moving = False

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
        self.step_size = float(step_size)

    def set_velocity(self, vel=None):
        if vel is not None:
            self.velocity = float(vel)
            if self.connected and self.device is not None:
                try:
                    self.device.VEL(STAGE_AXIS, self.velocity)
                except Exception as error:
                    self.last_error = f"Stage velocity error: {error}"
                    print(self.last_error)
                    return False

            return True

        return self.velocity

    def stop(self):
        if not self.connected or self.device is None:
            return False

        try:
            self.device.STP()
        except GCSError as error:
            if error != gcserror.E10_PI_CNTR_STOP:
                self.last_error = f"Stage stop error: {error}"
                print(self.last_error)
                return False
        except Exception as error:
            self.last_error = f"Stage stop error: {error}"
            print(self.last_error)
            return False

        self.is_moving = False
        self.current_position = self.get_position()
        return True

    def close(self):
        try:
            if self.device is not None:
                self.device.CloseConnection()
        except Exception as error:
            self.last_error = f"Stage close error: {error}"
            print(self.last_error)
        finally:
            self.connected = False
            self.is_moving = False
            self.connection_description = ""
            self.device = None
