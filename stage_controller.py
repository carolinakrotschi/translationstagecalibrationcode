# TABLE OF CONTENTS 
# 1. Imports and stage axis
# 2. StageController setup
# 3. Connection and limits
# 4. Position helpers
# 5. Movement commands
# 6. Safety and cleanup


# -----------------------------------------------------------------------------
# 1. IMPORTS AND STAGE AXIS
# -----------------------------------------------------------------------------

from pipython import GCSDevice #to talk to stage controller
import threading
import time

#pi controller uses axis identifier, this program controls axis 1
STAGE_AXIS = "1"

# -----------------------------------------------------------------------------
# 2. STAGE CONTROLLER CLASS
# -----------------------------------------------------------------------------

class StageController:

    # -----------------------------------------------------------------------------
    # 2.1 INITIAL STAGE STATE
    # -----------------------------------------------------------------------------
    
    def __init__(self):

        self.device = None #start without connected stage device

        self.connected = False

        self.current_position = 0.0

        self.target_position = 0.0

        self.step_size = 0.000100000 #small default step size

        self.is_moving = False

        self.min_position = -13 #minimum travel limit before hardware limits are read in mm

        self.max_position = 13

    # -----------------------------------------------------------------------------
    # 3.1 CONNECT TO THE TRANSLATION STAGE
    # -----------------------------------------------------------------------------
    
    def connect(self):

        try:

            self.device = GCSDevice() #creates PI controller object that will send commands to the stage

            self.device.InterfaceSetupDlg()

            self.connected = True

            self.current_position = self.get_position()

            self.update_travel_limits()

            return True

        except Exception as e:

            print("Stage connection error:", e)

            self.connected = False

            return False

    # -----------------------------------------------------------------------------
    # 3.2 READ HARDWARE TRAVEL LIMITS
    # -----------------------------------------------------------------------------
    
    def update_travel_limits(self):

        try:

            min_pos = self.device.qTMN(STAGE_AXIS)
            #ask controller for minimum allowed position of stage axis

            max_pos = self.device.qTMX(STAGE_AXIS)

            self.min_position = float(min_pos[STAGE_AXIS])

            self.max_position = float(max_pos[STAGE_AXIS])

        except Exception as e:

            print("Stage limit read error:", e)

    # -----------------------------------------------------------------------------
    # 4.1 READ CURRENT STAGE POSITION
    # -----------------------------------------------------------------------------
    
    def get_position(self):

        if not self.connected: #use last known position when controller is not connected
            return self.current_position

        try:

            pos = self.device.qPOS(STAGE_AXIS)
            #ask controller for current stage position

            self.current_position = float(
                pos[STAGE_AXIS]
            )

            return self.current_position

        except Exception as e:

            print("Position error:", e)

            return self.current_position

    # -----------------------------------------------------------------------------
    # 4.2 LIMIT A TARGET TO SAFE TRAVEL RANGE
    # -----------------------------------------------------------------------------
   
    def clamp_position(self, position_mm):

        return max(
            #return requested target position after limiting to the sage hardware range
            self.min_position,
            min(
                self.max_position,
                float(position_mm)
            )
        )
    # -----------------------------------------------------------------------------
    # 5.1 MOVE TO AN ABSOLUTE POSITION
    # -----------------------------------------------------------------------------
    
    def move_absolute(self, target_mm):

        if not self.connected:
            return False

        if self.is_moving:
            return False

        target_mm = self.clamp_position(target_mm)

        self.target_position = target_mm

        self.is_moving = True
        # -----------------------------------------------------------------------------
        # 5.1.1 BACKGROUND ABSOLUTE-MOVE WORKER
        # -----------------------------------------------------------------------------
        #sends move command and follows stage
        def worker():

            try:
                #move command
                self.device.MOV(
                    STAGE_AXIS,
                    target_mm
                )

                while self.device.IsMoving()[STAGE_AXIS]:

                    self.current_position = (
                        self.get_position()
                    )

                    time.sleep(0.02)

                self.current_position = (
                    self.get_position()
                )

            except Exception as e:

                print("Move absolute error:", e)

            finally:

                self.is_moving = False

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

        return True
    # -----------------------------------------------------------------------------
    # 5.2 MOVE BY A RELATIVE DISTANCE
    # -----------------------------------------------------------------------------
    #turns relative distance into absolute target 
    def move_relative(self, distance_mm):

        current = self.get_position()

        target = current + distance_mm

        return self.move_absolute(target)
    # -----------------------------------------------------------------------------
    # 5.3 MOVE ONE POSITIVE/NEGATIVE STEP
    # -----------------------------------------------------------------------------
    #moves stage by configured stepsize in positive direction
    def step_positive(self):

        return self.move_relative(
            self.step_size
        )
    #moves stage by configured stepsize in negative direction
    def step_negative(self):

        return self.move_relative(
            -self.step_size
        )
    # -----------------------------------------------------------------------------
    # 5.4 MOVE TO MAXIMUM/MINIMUM LIMIT
    # -----------------------------------------------------------------------------
    
    def move_to_max(self):

        return self.move_absolute(
            self.max_position
        )

    def move_to_min(self):

        return self.move_absolute(
            self.min_position
        )
    # -----------------------------------------------------------------------------
    # 5.7 UPDATE STEP SIZE
    # -----------------------------------------------------------------------------
    #user provided step size
    def set_step_size(self, step_size):

        try:

            self.step_size = float(step_size)

        except:
            pass
    # -----------------------------------------------------------------------------
    # 6.1 STOP THE STAGE
    # -----------------------------------------------------------------------------
    
    def stop(self):

        try:

            if self.connected:

                self.device.STP() #ask PI controller to stop current stage motion

        except Exception as e:

            print("Stage stop error:", e)

    # -----------------------------------------------------------------------------
    # 6.2 CLOSE THE STAGE CONNECTION
    # -----------------------------------------------------------------------------
    
    def close(self):

        try:

            if self.device is not None:

                self.device.CloseConnection() #close PI controller connection

        except Exception as e:

            print("Stage close error:", e)
