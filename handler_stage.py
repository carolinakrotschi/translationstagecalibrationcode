# TABLE OF CONTENTS
# 1. Imports
# 2. StageController class
# 3. Axis referencing
# 4. Position querying
# 5. Motion commands
# 6. Velocity and step size
# 7. Cleanup

# -----------------------------------------------------------------------------
# 1. IMPORTS
# -----------------------------------------------------------------------------
import threading
import time

from pipython import GCSError, GCSDevice, gcserror, pitools


STAGE_AXIS = "1"
STAGE_CONTROLLER_NAME = "" #is found automatically, thats why its empty
AUTO_REFERENCE_ON_CONNECT = False
DEFINE_POSITION_IF_UNREFERENCED = True
REFERENCE_MODE = "FRF" #frf is the standard reference drive of the PI stage
REFERENCE_TIMEOUT_S = 180
MOVE_POSITION_TOLERANCE_MM = 0.000002


# -----------------------------------------------------------------------------
# 2. STAGECONTROLLER CLASS  
# -----------------------------------------------------------------------------
class StageController:

    def __init__(self, controller_name=STAGE_CONTROLLER_NAME):
        #initialize all the variables
        self.controller_name = controller_name
        self.device = None
        self.connected = False
        self.last_error = ""
        self.connection_description = ""
        self.current_position = 0.0
        self.target_position = 0.0
        self.step_size = 0.020000000
        self.velocity = 0.0006
        self.is_moving = False
        self.min_position = 0
        self.max_position = 50
    #connects the actual motor to the software
    def connect(self):

        if self.connected:
            return True

        self.last_error = ""
        #the connection of the motor has to run in the main thread
        if threading.current_thread() is not threading.main_thread():
            self.last_error = "Stage connection must be started from the main thread"
            print(self.last_error)
            return False

        try:
            self.device = GCSDevice(self.controller_name)
            self._connect_first_available_device()
            self._prepare_axis_for_motion() #turn on servo, check zero point
            pos = self.device.qPOS(STAGE_AXIS)
            self.connected = True
            self.current_position = float(pos[STAGE_AXIS])
            self.set_velocity(self.velocity)
            return True
        #in case of failure (cable unplugged, ...)
        except Exception as error:
            self.last_error = f"Stage connection error: {error}"
            print(self.last_error)
            self.connected = False
            self.is_moving = False
            #close the communication channel, if there is an error
            try:
                if self.device is not None:
                    self.device.CloseConnection()
            except Exception:
                pass

            self.device = None
            return False

    def _connect_first_available_device(self):
        errors = []
        #search for usb devices
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
    

        detail = "; ".join(errors)
        if detail:
            raise RuntimeError(f"No PI stage found via USB ({detail})")

        raise RuntimeError("No PI stage found via USB")

# -----------------------------------------------------------------------------
# 3. AXIS REFERENCING 
# -----------------------------------------------------------------------------
    def _prepare_axis_for_motion(self):
        #turn on servo (motor current) --> only when servo is on, the motor can hold its position
        self._set_servo(True)
        #does the motor know, where it stands at? this is calibrated here
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
    #enables servo
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
    #for now we define the current position as zero, for quick tests (e.g. when starting the code 10 times in a row...)
    def _define_current_position_as_zero(self):
        print(f"Defining current PI stage axis {STAGE_AXIS} position as 0.0")
        self.device.RON(STAGE_AXIS, False)
        self.device.POS(STAGE_AXIS, 0.0)
    #then we properly reference the axis by moving the stage to zero
    def _reference_axis(self):
        print(f"Referencing PI stage axis {STAGE_AXIS} with {REFERENCE_MODE}...")
        #reference the axis depending on the mode that was selected
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

# -----------------------------------------------------------------------------
# 4. POSITION QUERYING 
# -----------------------------------------------------------------------------
    #for the UI it is essential, that the current position is always available
    def get_position(self):

        if not self.connected or self.device is None:
            return self.current_position

        try:
            pos = self.device.qPOS(STAGE_AXIS) #this gibes the position
            self.current_position = float(pos[STAGE_AXIS])
        except Exception as error:
            self.last_error = f"Stage position error: {error}"
            print(self.last_error)

        return self.current_position
    #limits the position to the physical limits of the stage (0mm to 50 mm)
    def clamp_position(self, pos):
        return max(self.min_position, min(self.max_position, float(pos)))

# -----------------------------------------------------------------------------
# 5. MOTION COMMANDS
# -----------------------------------------------------------------------------
    #for driving to an absolute position, does that in the background, so that the UI is still usable
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
                self.device.MOV(STAGE_AXIS, target_mm_clamped) #scan the motion command

                while self.device.IsMoving()[STAGE_AXIS]:
                    self.current_position = self.get_position()
                    time.sleep(0.02)

                self.current_position = self.get_position() #after arrival, question the position again

            except Exception as error:
                self.last_error = f"Stage move error: {error}"
                print(self.last_error)

            finally:
                self.is_moving = False #at the end, when the stage is not moving anymore, set is_moving to false, so that the UI knows that the stage is not moving anymore

        threading.Thread(target=worker, daemon=True).start()
        return True
    #this is used for calibration, when the stage gets moving to one position, but all the commands in the UI should be blocked
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
            self.device.MOV(STAGE_AXIS, target_mm_clamped) #starting the movement

            while True:
                if should_continue is not None and not should_continue(): #if the ui signals, the movement should be stopped, stop
                    self.stop()
                    return False

                position_mm = self.get_position()
                if progress_callback is not None:
                    progress_callback(position_mm)

                if abs(position_mm - target_mm_clamped) <= MOVE_POSITION_TOLERANCE_MM: #if the position is reached within the tolerance, stop
                    return True

                try:
                    on_target = self.device.qONT(STAGE_AXIS) #check if the stage is on target
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
    #moves stage by relative distance
    def move_relative(self, distance_mm):
        current = self.get_position()
        target = current + distance_mm
        return self.move_absolute(target)
    #single steps
    def step_positive(self):
        return self.move_relative(self.step_size)

    def step_negative(self):
        return self.move_relative(-self.step_size)

    def move_to_max(self):
        return self.move_absolute(self.max_position)

    def move_to_min(self):
        return self.move_absolute(self.min_position)

# -----------------------------------------------------------------------------
# 6. VELOCITY 
# -----------------------------------------------------------------------------
    #sets step size for the manual buttons
    def set_step_size(self, step_size):
        self.step_size = float(step_size)

    def set_velocity(self, vel=None):
        if vel is not None:
            self.velocity = float(vel)
            if self.connected and self.device is not None:
                try:
                    self.device.VEL(STAGE_AXIS, self.velocity) #send velocity command to hardware
                except Exception as error:
                    self.last_error = f"Stage velocity error: {error}"
                    print(self.last_error)
                    return False

            return True

        return self.velocity
    #stops the stage (emergency stop when UI stop button is pressed)
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

        self.is_moving = False #adjusts the position to the point where the stage stopped
        self.current_position = self.get_position()
        return True

# -----------------------------------------------------------------------------
# 7. CLEANUP
# -----------------------------------------------------------------------------
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
