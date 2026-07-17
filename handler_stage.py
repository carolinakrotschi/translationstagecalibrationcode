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

# So that you do not have to understand every line of the code, I will now explain the complete path of a stage command through this file
# 0. What is happening: class in which it is happening : function in the class in which it is happening : what is happening explained in a more precise way
# 1. The stage controller is initialized: StageController : __init__() : initializes the controller, movement parameters, limits, and connection state
# 2. The stage is connected: StageController : connect() : establishes the connection to the first available PI stage and prepares it for motion
# 3. The stage device is selected: StageController : _connect_first_available_device() : searches for connected PI USB devices and connects to the first one
# 4. The axis is prepared for motion: StageController : _prepare_axis_for_motion() : enables the servo and ensures that the axis is referenced
# 5. The servo and reference state are handled: StageController : _set_servo() / _is_referenced() / _define_current_position_as_zero() / _reference_axis() : enables the servo and references the stage if required
# 6. The current position is read: StageController : get_position() : queries the current stage position and stores it for the UI
# 7. The target position is limited: StageController : clamp_position() : restricts movement commands to the physical travel range (0.0 mm to 50.0 mm)
# 8. An absolute movement is started: StageController : move_absolute() : starts a background movement while continuously updating the position
# 9. A blocking movement is executed: StageController : move_absolute_blocking() : moves to a target position while monitoring progress and timeouts
# 10. Relative and manual movements are performed: StageController : move_relative() / step_positive() / step_negative() / move_to_max() / move_to_min() : executes relative, stepwise, and limit movements
# 11. The movement parameters are configured: StageController : set_step_size() / set_velocity() : updates the step size and stage velocity
# 12. The stage is stopped: StageController : stop() : immediately stops the stage and updates the current position
# 13. The connection is closed: StageController : close() : closes the communication with the stage and releases all resources

# -----------------------------------------------------------------------------
# 2. STAGECONTROLLER CLASS
# -----------------------------------------------------------------------------
class StageController:

    # initialize the stage controller
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
        self.acceleration = 0.0
        self.is_moving = False
        self.min_position = 0.0
        self.max_position = 50.0

    # connect to the first available stage
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
            self._prepare_axis_for_motion()  #turn on servo, check zero point
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

    # connect to the first available USB stage
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

    # prepare the axis for motion
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

    # enable or disable the servo
    def _set_servo(self, enabled):
        try:
            self.device.SVO(STAGE_AXIS, bool(enabled))
        except Exception as error:
            print(f"Stage servo warning: {error}")

    # check whether the axis is referenced
    def _is_referenced(self):
        try:
            referenced = self.device.qFRF(STAGE_AXIS)
            return bool(referenced[STAGE_AXIS])
        except Exception as error:
            print(f"Stage reference status warning: {error}")
            return False

    # define the current position as zero
    def _define_current_position_as_zero(self):
        print(f"Defining current PI stage axis {STAGE_AXIS} position as 0.0")
        self.device.RON(STAGE_AXIS, False)
        self.device.POS(STAGE_AXIS, 0.0)

    # reference the stage axis
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

    # read the current stage position and keep it up to date for the UI
    def get_position(self):

        if not self.connected or self.device is None:
            return self.current_position

        try:
            pos = self.device.qPOS(STAGE_AXIS)  #this gives the position
            self.current_position = float(pos[STAGE_AXIS])
        #in case of failure (cable unplugged, ...)
        except Exception as error:
            self.last_error = f"Stage position error: {error}"
            print(self.last_error)

        return self.current_position

    # limit the target position to the physical travel range of the stage (0.0 mm to 50.0 mm)
    def clamp_position(self, pos):
        return max(self.min_position, min(self.max_position, float(pos)))

# -----------------------------------------------------------------------------
# 5. MOTION COMMANDS
# -----------------------------------------------------------------------------

    # move the stage to an absolute position; runs in a background thread so the UI stays responsive
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
                self.device.MOV(STAGE_AXIS, target_mm_clamped)  #start the movement command

                while self.device.IsMoving()[STAGE_AXIS]:
                    self.current_position = self.get_position()
                    time.sleep(0.02)

                self.current_position = self.get_position()  #update the position after arrival

            #in case of failure (cable unplugged, ...)
            except Exception as error:
                self.last_error = f"Stage move error: {error}"
                print(self.last_error)

            finally:
                self.is_moving = False  #movement finished: reset is_moving so the UI knows the stage stopped moving

        threading.Thread(target=worker, daemon=True).start()
        return True

    # move the stage to an absolute position and wait until it arrives
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
            self.device.MOV(STAGE_AXIS, target_mm_clamped)  #start the movement

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

    # move the stage by a relative distance from the current position
    def move_relative(self, distance_mm):
        current = self.get_position()
        target = current + distance_mm
        return self.move_absolute(target)

    # move one step in the positive direction
    def step_positive(self):
        return self.move_relative(self.step_size)

    # move one step in the negative direction
    def step_negative(self):
        return self.move_relative(-self.step_size)

    # move the stage to the maximum position
    def move_to_max(self):
        return self.move_absolute(self.max_position)

    # move the stage to the minimum position
    def move_to_min(self):
        return self.move_absolute(self.min_position)

# -----------------------------------------------------------------------------
# 6. VELOCITY
# -----------------------------------------------------------------------------

    # set the manual step size
    def set_step_size(self, step_size):
        self.step_size = float(step_size)

    # set or read the stage velocity
    def set_velocity(self, vel=None, acceleration_mm_s2=None):
        if vel is not None:
            self.velocity = float(vel)

            if acceleration_mm_s2 is None:
                self.acceleration = 0.0
            else:
                self.acceleration = abs(float(acceleration_mm_s2))

            if self.connected and self.device is not None:
                try:
                    self.device.VEL(STAGE_AXIS, self.velocity)
                #in case of failure (cable unplugged, ...)
                except Exception as error:
                    self.last_error = f"Stage velocity error: {error}"
                    print(self.last_error)
                    return False

            return True

        return self.velocity

    # stop the current stage movement (emergency stop when UI stop button is pressed)
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
        self.current_position = self.get_position()  #reflect the position where the stage actually stopped
        return True

# -----------------------------------------------------------------------------
# 7. CLEANUP
# -----------------------------------------------------------------------------

    # close the stage connection
    def close(self):
        try:
            if self.device is not None:
                self.device.CloseConnection()

        #in case of failure (cable unplugged, ...)
        except Exception as error:
            self.last_error = f"Stage close error: {error}"
            print(self.last_error)

        finally:
            self.connected = False
            self.is_moving = False
            self.connection_description = ""
            self.device = None
