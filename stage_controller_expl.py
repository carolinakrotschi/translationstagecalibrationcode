# TABLE OF CONTENTS FOR STAGE_CONTROLLER_EXPL.PY
# 1. Imports and stage axis: load the PI stage library and choose the controlled axis.
# 2. StageController setup: store connection state, position state, step size, and travel limits.
# 3. Connection and limits: connect to the controller and read hardware travel limits.
# 4. Position helpers: read current position and clamp requested targets into the safe range.
# 5. Movement commands: absolute moves, relative moves, step moves, and limit moves.
# 6. Safety and cleanup: stop motion and close the controller connection.
# Comments explain what the stage-control code is doing and why each step is needed.

# -----------------------------------------------------------------------------
# 1. IMPORTS AND STAGE AXIS
# -----------------------------------------------------------------------------
from pipython import GCSDevice
# Import the PI Python device class used to talk to the translation-stage controller.
import threading
# Use a background thread so long stage movements do not freeze the GUI.
import time
# Use short sleeps while polling whether the stage is still moving.


# The PI controller uses an axis identifier; this program controls axis 1.
STAGE_AXIS = "1"
# Select axis 1 as the controlled translation-stage axis.


# -----------------------------------------------------------------------------
# 2. STAGE CONTROLLER CLASS
# -----------------------------------------------------------------------------
class StageController:
# This class wraps all direct PI stage commands behind simpler methods for the main app.

    # -----------------------------------------------------------------------------
    # 2.1 INITIAL STAGE STATE
    # This prepares all software-side state before a hardware connection exists.
    # -----------------------------------------------------------------------------
    def __init__(self):

        self.device = None
        # Start without a connected stage device; this is filled after a successful connection.

        self.connected = False
        # Start disconnected; movement commands stay blocked until connect() succeeds.

        self.current_position = 0.0
        # Start the cached position at zero until the real stage position can be read.

        self.target_position = 0.0
        # Prepare storage for the most recent requested target position.

        self.step_size = 0.000100000
        # Use a small default step size for manual positive/negative step moves.

        self.is_moving = False
        # Start with no active movement in progress.

        self.min_position = -13
        # Use a conservative default minimum travel limit before hardware limits are read.

        self.max_position = 13
        # Use a conservative default maximum travel limit before hardware limits are read.

    # -----------------------------------------------------------------------------
    # 3.1 CONNECT TO THE TRANSLATION STAGE
    # This opens the PI controller interface and reads the first position/limit information.
    # -----------------------------------------------------------------------------
    def connect(self):

        try:
        # Try the hardware operation; if it fails, keep the program from crashing and report the problem.

            self.device = GCSDevice()
            # Create the PI controller object that will send commands to the stage.

            self.device.InterfaceSetupDlg()
            # Open the PI connection dialog so the user/system can select the correct controller interface.

            self.connected = True
            # Mark the stage as connected after the interface setup succeeds.

            self.current_position = self.get_position()
            # Read and cache the current physical stage position immediately after connecting.

            self.update_travel_limits()
            # Replace default travel limits with the limits reported by the actual hardware.

            return True
            # Tell the main app that stage connection succeeded.

        except Exception as e:
        # Handle controller errors so the main app can keep running safely.

            print("Stage connection error:", e)
            # Show why the stage connection failed.

            self.connected = False
            # Keep the stage marked as disconnected after connection setup fails.

            return False
            # Tell the main app that stage connection failed.

    # -----------------------------------------------------------------------------
    # 3.2 READ HARDWARE TRAVEL LIMITS
    # This asks the stage controller for the minimum and maximum allowed positions.
    # -----------------------------------------------------------------------------
    def update_travel_limits(self):

        try:
        # Try the hardware operation; if it fails, keep the program from crashing and report the problem.

            min_pos = self.device.qTMN(STAGE_AXIS)
            # Ask the controller for the minimum allowed position of the selected axis.

            max_pos = self.device.qTMX(STAGE_AXIS)
            # Ask the controller for the maximum allowed position of the selected axis.

            self.min_position = float(min_pos[STAGE_AXIS])
            # Store the hardware minimum as a normal float in millimeters.

            self.max_position = float(max_pos[STAGE_AXIS])
            # Store the hardware maximum as a normal float in millimeters.

        except Exception as e:
        # Handle failed limit reads and keep the current default/fallback limits.

            print("Stage limit read error:", e)
            # Report that the hardware limits could not be read and keep the default limits.

    # -----------------------------------------------------------------------------
    # 4.1 READ CURRENT STAGE POSITION
    # This returns the newest known stage position and updates the cached value when connected.
    # -----------------------------------------------------------------------------
    def get_position(self):

        if not self.connected:
        # Use the cached position when the controller is not connected.
            return self.current_position
            # Return the latest known position instead of failing when hardware cannot be queried.

        try:
        # Try the hardware operation; if it fails, keep the program from crashing and report the problem.

            pos = self.device.qPOS(STAGE_AXIS)
            # Ask the controller for the current stage position.

            self.current_position = float(
            # Store the reported hardware position as a normal float.
                pos[STAGE_AXIS]
            )

            return self.current_position
            # Return the latest known position instead of failing when hardware cannot be queried.

        except Exception as e:
        # Handle failed position reads and return the last cached position instead.

            print("Position error:", e)
            # Report a failed position read and keep using the cached position.

            return self.current_position
            # Return the latest known position instead of failing when hardware cannot be queried.

    # -----------------------------------------------------------------------------
    # 4.2 LIMIT A TARGET TO SAFE TRAVEL RANGE
    # This protects movement commands from requesting positions outside the stage limits.
    # -----------------------------------------------------------------------------
    def clamp_position(self, position_mm):

        return max(
        # Return the requested target after limiting it to the safe hardware range.
            self.min_position,
            min(
                self.max_position,
                float(position_mm)
            )
        )

    # -----------------------------------------------------------------------------
    # 5.1 MOVE TO AN ABSOLUTE POSITION
    # This starts a background movement to a target position in millimeters.
    # -----------------------------------------------------------------------------
    def move_absolute(self, target_mm):

        if not self.connected:
        # Refuse an absolute movement when the controller is not connected.
            return False
            # Tell the caller that the movement could not be started.

        if self.is_moving:
        # Refuse a new movement while a previous move is still active.
            return False
            # Tell the caller that the movement could not be started.

        target_mm = self.clamp_position(target_mm)
        # Keep the requested target inside the allowed stage travel limits before moving.

        self.target_position = target_mm
        # Remember the accepted target so other code can know where the stage is being sent.

        self.is_moving = True
        # Mark movement as active before the background worker starts.

        # -----------------------------------------------------------------------------
        # 5.1.1 BACKGROUND ABSOLUTE-MOVE WORKER
        # This sends the move command and follows the stage until motion is finished.
        # -----------------------------------------------------------------------------
        def worker():

            try:
            # Try the hardware operation; if it fails, keep the program from crashing and report the problem.

                self.device.MOV(
                # Send the absolute movement command to the PI controller.
                    STAGE_AXIS,
                    target_mm
                )

                while self.device.IsMoving()[STAGE_AXIS]:
                # Keep polling while the selected axis is still moving.

                    self.current_position = (
                    # Refresh the cached position during or after movement.
                        self.get_position()
                    )

                    time.sleep(0.02)
                    # Wait briefly between motion polls to avoid overloading the controller and CPU.

                self.current_position = (
                # Refresh the cached position during or after movement.
                    self.get_position()
                )

            except Exception as e:
            # Handle controller errors so the main app can keep running safely.

                print("Move absolute error:", e)
                # Report movement errors without leaving the app unaware of the issue.

            finally:
            # Always clear the moving flag after the worker exits, whether the move succeeded or failed.

                self.is_moving = False
                # Mark movement as finished so later movement commands can be accepted.

        threading.Thread(
        # Run the stage movement watcher in the background so the GUI can stay responsive.
            target=worker,
            daemon=True
        ).start()
        # Start the background movement worker.

        return True
        # Tell the main app that this operation succeeded.

    # -----------------------------------------------------------------------------
    # 5.2 MOVE BY A RELATIVE DISTANCE
    # This turns a relative distance into an absolute target and reuses the absolute move routine.
    # -----------------------------------------------------------------------------
    def move_relative(self, distance_mm):

        current = self.get_position()
        # Read the current position so a relative movement can be converted into an absolute target.

        target = current + distance_mm
        # Calculate the absolute target reached by moving the requested relative distance.

        return self.move_absolute(target)
        # Reuse the absolute movement routine so all safety checks and tracking behavior stay consistent.

    # -----------------------------------------------------------------------------
    # 5.3 MOVE ONE POSITIVE STEP
    # This moves the stage by the configured step size in the positive direction.
    # -----------------------------------------------------------------------------
    def step_positive(self):

        return self.move_relative(
        # Reuse relative movement for one-step button actions.
            self.step_size
            # Move one configured step in the positive direction.
        )

    # -----------------------------------------------------------------------------
    # 5.4 MOVE ONE NEGATIVE STEP
    # This moves the stage by the configured step size in the negative direction.
    # -----------------------------------------------------------------------------
    def step_negative(self):

        return self.move_relative(
        # Reuse relative movement for one-step button actions.
            -self.step_size
            # Move one configured step in the negative direction.
        )

    # -----------------------------------------------------------------------------
    # 5.5 MOVE TO MAXIMUM LIMIT
    # This asks the stage to move to its stored maximum travel limit.
    # -----------------------------------------------------------------------------
    def move_to_max(self):

        return self.move_absolute(
        # Reuse the absolute movement routine for limit moves.
            self.max_position
            # Use the stored maximum hardware limit as the movement target.
        )

    # -----------------------------------------------------------------------------
    # 5.6 MOVE TO MINIMUM LIMIT
    # This asks the stage to move to its stored minimum travel limit.
    # -----------------------------------------------------------------------------
    def move_to_min(self):

        return self.move_absolute(
        # Reuse the absolute movement routine for limit moves.
            self.min_position
            # Use the stored minimum hardware limit as the movement target.
        )

    # -----------------------------------------------------------------------------
    # 5.7 UPDATE STEP SIZE
    # This stores the step size used by the positive and negative step buttons.
    # -----------------------------------------------------------------------------
    def set_step_size(self, step_size):

        try:
        # Try to convert the user-provided step size into a number.

            self.step_size = float(step_size)
            # Store a new numeric step size for later manual step movements.

        except:
        # Handle invalid step-size input without interrupting the app.
            pass
            # Keep the previous setting unchanged when the new step size cannot be converted.

    # -----------------------------------------------------------------------------
    # 6.1 STOP THE STAGE
    # This sends a stop command to the controller when motion should be interrupted.
    # -----------------------------------------------------------------------------
    def stop(self):

        try:
        # Try to stop motion through the controller; failed stop commands are reported below.

            if self.connected:
            # Only send a stop command when a controller connection exists.

                self.device.STP()
                # Ask the PI controller to stop current stage motion.

        except Exception as e:
        # Handle failed stop commands during interruption or shutdown.

            print("Stage stop error:", e)
            # Report a failed stop command without crashing the app.

    # -----------------------------------------------------------------------------
    # 6.2 CLOSE THE STAGE CONNECTION
    # This releases the hardware connection when the application exits.
    # -----------------------------------------------------------------------------
    def close(self):

        try:
        # Try to close the controller connection during shutdown.

            if self.device is not None:
            # Only close the connection if a device object exists.

                self.device.CloseConnection()
                # Close the PI controller connection so the hardware is released.

        except Exception as e:
        # Handle close errors during shutdown.

            print("Stage close error:", e)
            # Report close errors during shutdown.
