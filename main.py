#works

# TABLE OF CONTENTS
# 1. "Backup plan"/Basic Setting
# 2. Imports and camera driver path
# 3. Physical constants and colors
# 4. InterferometerApp class
# 5. Monitoring and reset
# 6. Translation stage control
# 7. Calibration 
# 8. Camera loop
# 9. Cleanup and program start

# -----------------------------------------------------------------------------
# 1. BASIC SETTINGS
# -----------------------------------------------------------------------------

# the idea here is, that when the 5s calibration at the beginning doesnt work, the user can observe the intensities of a bright/dark fringe and manually insert them here
MANUAL_THRESHOLDS = False
# this can be manually set to True and then the values can be manually adjusted
MANUAL_DARK_THRESHOLD = 7
MANUAL_BRIGHT_THRESHOLD = 25

# -----------------------------------------------------------------------------
# 2. IMPORTS
# -----------------------------------------------------------------------------


import os #for finding and creating files/paths/etc
import threading #so that camera and stage can run without freezing the UI
import time #for timestamps
import numpy as np #to make computing more efficient with arrays
import customtkinter as ctk #pythons standard UI library

from PIL import Image #for showing the live camera

from camera_handler import CameraHandler #a part of the code got outsourced to other files camera_handler.py and stage_controller.py 
from stage_controller import StageController

current_directory = os.path.dirname(os.path.abspath(__file__)) #finds path of the current file, but without the filename at the end (only dirname)
dll_path = os.path.join(current_directory, "Camera") #the ccd camera needs a certain code from Thorlabs to work, this can be found in the dll files which I added into a folder named "Camera"

if os.path.exists(dll_path): #if the path is there (which it should), windows is going to look there for the dll files
    os.add_dll_directory(dll_path)

# -----------------------------------------------------------------------------
# 3. PHYSICAL CONSTANTS
# -----------------------------------------------------------------------------

LASER_WAVELENGTH_NM = 780.0

#this calculates the fringe distance in mm based on the known formula
FRINGE_DISTANCE_MM = (
    (LASER_WAVELENGTH_NM / 2) / 1_000_000
    #1000000 is from nm to mm
)

SPEED_OF_LIGHT_MM_PS = 0.299792458
DEFAULT_STAGE_SPEED_MM_S = 0.000600
# -----------------------------------------------------------------------------
# 3.1 COLORS AND FILTER TIMINGS
# -----------------------------------------------------------------------------

TEXT_COLOR = "#0A4A51"
GREEN_COLOR = "#1EAD4F"
RED_COLOR = "#C0392B"
ORANGE_COLOR = "#D35400"

#the number of consecutive dark or bright frames required to count a fringe, this is to filter out noise and avoid counting false fringes due to intensity fluctuations
REQUIRED_DARK_FRAMES = 3
REQUIRED_BRIGHT_FRAMES = 3
#after counting a fringe, the system will ignore any new fringes for this amount of time, this is to avoid counting multiple fringes if the intensity fluctuates around the threshold
FRINGE_COOLDOWN = 0.08
#after calibration, 2s cooldown so that no buttons can be pressed immediately
CALIBRATION_BUTTON_COOLDOWN_MS = 2000
#mode for target, distance and center movements: "continuous" or "stepped"
MODE = "continuous"
CALIBRATION_SWEEP_DISTANCE_MM = 0.0006

# -----------------------------------------------------------------------------
# 4. APP CLASS (UI)
# -----------------------------------------------------------------------------

class InterferometerApp(ctk.CTk):
    #ctk.CTk is the base class for the customtkinter window, here we inherit our InterferometerApp class from it
    # -----------------------------------------------------------------------------
    # 4.1 INITIALIZATION
    # -----------------------------------------------------------------------------
    
    def __init__(self):
        #init method always gets called to create a new instance of the class

        super().__init__()
        #we inherit the init method from the parent class (which is the ctk Class)
        self.title("Interferometer Monitor")

        self.geometry("900x1000")

        ctk.set_appearance_mode("light")

        self.configure(fg_color="white")

        #creates a scrollable frame inside the window
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="white"
        )
        #the scrollable frame is put into the window
        self.scroll.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2
        )

        #some initialization of values

        #measurement loop is not running at the beginning
        self.is_monitoring = False

        self.accumulated_fringes = 0

        #a bright state only counts after darkness
        self.was_dark = False
        #time of the last counted fringe for the cooldown check
        self.last_count_time = 0
        #number of consecutive dark/bright fringes
        self.dark_counter = 0
        self.bright_counter = 0

        self.intensity_history = []

        #initializes with manual thresholds, but these will be overridden if the automatic calibration works
        self.dark_threshold = MANUAL_DARK_THRESHOLD

        self.bright_threshold = MANUAL_BRIGHT_THRESHOLD

        #for the 5s calibration at the beginning
        self.calibrating = False
        self.calibration_start_time = 0
        self.calibration_values = []

        #initializes the hardware specific camera code of the ccd
        self.camera_handler = CameraHandler()
        #stores the value of the connection result (initially False, will connect in background)
        self.camera_connected = False
        #same for the stage
        self.stage = StageController()
        self.stage.set_velocity(DEFAULT_STAGE_SPEED_MM_S)
        self.stage_connected = False

        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
        self.fringe_distance_mm = self.compute_fringe_distance(
            self.laser_wavelength_nm
        )

        #stores values for all the start positions
        self.stage_start_position = 0.0
        self.stage_reference_position = 0.0
        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        #flags to reset stage movement after calibration
        self.reset_stage_movement_after_move = False #resets after return movement
        self.center_stage_after_calibration_pending = False #stage has to center after calibration
        self.returning_stage_after_calibration = False #return stage after calibration
        self.calibration_motion_started = False #prevents starting the calibration more than once
        self.calibration_stage_stop_done = False
        self.calibration_button_cooldown_active = False
        #header
        ctk.CTkLabel(
            self.scroll, #to separate from the next argument
            text="Interferometer Monitor",
            font=("Arial", 23, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=5)
        
        #now all the buttons, labels etc. (self explanatory)
        self.btn = ctk.CTkButton(
            self.scroll,
            text="START MONITORING",
            command=self.toggle, #which method should run, when you click the button: toggle
            width=180,
            height=30,
            fg_color=TEXT_COLOR,
            font=("Arial", 11, "bold")
        )

        self.btn.pack(pady=2)

        self.restart_btn = ctk.CTkButton(
            self.scroll,
            text="RESET",
            command=self.restart, #which method should run, when you click the button: restart
            width=140,
            height=28,
            fg_color=ORANGE_COLOR
        )

        self.restart_btn.pack(pady=1)
        #label to tell the user the current state
        self.status = ctk.CTkLabel(
            self.scroll,
            text="Status: Stopped", #pre setting
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.status.pack(pady=2)

        #ui group for translation stage controls 
        self.stage_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.stage_frame.pack(
            fill="x", #which direction the frame fills
            padx=5,
            pady=4
        )

        ctk.CTkLabel(
            self.stage_frame,
            text="Electronic Translation Stage",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=2)

        self.wavelength_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Laser wavelength in nm",
            width=250
        )

        self.wavelength_entry.pack(pady=1)
        #writes the default wavelenght into entry field (780nm)
        self.wavelength_entry.insert(0, f"{self.laser_wavelength_nm:.1f}")

        self.wavelength_button = ctk.CTkButton(
            self.stage_frame, #which frame the button is in
            text="Set wavelength",
            width=120,
            command=self.apply_wavelength,
            fg_color=TEXT_COLOR
        )

        self.wavelength_button.pack(pady=1)

        ctk.CTkLabel(
            self.stage_frame,
            text="Step size",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(4, 0))

        self.step_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Step size in mm",
            width=250
        )

        self.step_entry.pack(pady=1)
        self.step_entry.insert(
            0,
            #I found, that the interferometer works best, if the step size is 1/4 of the fringe distance
            f"{(self.fringe_distance_mm / 4):.7f}"
        )

        ctk.CTkLabel(
            self.stage_frame,
            text="Velocity",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(4, 0))

        self.speed_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Velocity in mm/s",
            width=250
        )

        self.speed_entry.pack(pady=1)
        self.speed_entry.insert(
            0,
            f"{DEFAULT_STAGE_SPEED_MM_S:.6f}"
        )

        self.speed_button = ctk.CTkButton(
            self.stage_frame,
            text="Set velocity",
            width=120,
            command=self.apply_stage_speed,
            fg_color=TEXT_COLOR
        )

        self.speed_button.pack(pady=1)

        self.button_frame = ctk.CTkFrame(
            self.stage_frame,
            fg_color="transparent"
        )

        self.button_frame.pack(pady=1)

        ctk.CTkLabel(
            self.stage_frame,
            text="or",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=3)

        self.target_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Target value or distance in mm",
            width=250
        )

        self.target_entry.pack(pady=1)
        self.target_entry.insert(0, "0.0000") #insert(position, text)

        self.target_button_frame = ctk.CTkFrame(
            self.stage_frame,
            fg_color="transparent"
        )

        self.target_button_frame.pack(pady=1)

        self.btn_target_abs = ctk.CTkButton( #button for moving to an absolute target position
            self.target_button_frame,
            text="Go to target",
            width=140,
            command=self.move_to_target_by_steps,
            fg_color=TEXT_COLOR
        )

        self.btn_target_abs.grid( #using grid layout to put the buttons next to each other
            row=0,
            column=0,
            padx=1
        )

        self.btn_target_rel = ctk.CTkButton( #button for moving by a relative distance
            self.target_button_frame,
            text="Move distance",
            width=140,
            command=self.move_distance_by_steps,
            fg_color=TEXT_COLOR
        )

        self.btn_target_rel.grid(
            row=0,
            column=1,
            padx=1
        )

        self.btn_stop = ctk.CTkButton(
            self.target_button_frame,
            text="STOP STAGE",
            width=140,
            command=self.stop_stage,
            fg_color=RED_COLOR,
            font=("Arial", 11, "bold")
        )

        self.btn_stop.grid(
            row=0,
            column=2,
            padx=1
        )

        #buttons for moving to min, center, max and stepping by the defined step size, these are also put next to each other with grid layout
        self.btn_min = ctk.CTkButton(
            self.button_frame,
            text="|<",
            width=60,
            command=self.move_to_min,
            fg_color=TEXT_COLOR
        )

        self.btn_min.grid(
            row=0,
            column=0,
            padx=1
        )

        self.btn_left = ctk.CTkButton(
            self.button_frame,
            text="<",
            width=60,
            command=self.step_negative,
            fg_color=TEXT_COLOR
        )

        self.btn_left.grid(
            row=0,
            column=1,
            padx=1
        )

        self.btn_center = ctk.CTkButton(
            self.button_frame,
            text="0",
            width=60,
            command=self.move_to_center,
            fg_color=TEXT_COLOR
        )

        self.btn_center.grid(
            row=0,
            column=2,
            padx=1
        )

        self.btn_right = ctk.CTkButton(
            self.button_frame,
            text=">",
            width=60,
            command=self.step_positive,
            fg_color=TEXT_COLOR
        )

        self.btn_right.grid(
            row=0,
            column=3,
            padx=1
        )

        self.btn_max = ctk.CTkButton(
            self.button_frame,
            text=">|",
            width=60,
            command=self.move_to_max,
            fg_color=TEXT_COLOR
        )

        self.btn_max.grid(
            row=0,
            column=4,
            padx=1
        )
        #labels. for calculations of stage parameters
        self.label_stage_position = ctk.CTkLabel(
            self.stage_frame,
            text="Stage Position: 0.000000 mm",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )

        self.label_stage_position.pack(pady=0)

        self.label_stage_moved = ctk.CTkLabel(
            self.stage_frame,
            text="Accumulated Movement: 0.000000 mm",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_stage_moved.pack(pady=0)

        self.frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.frame.pack(
            fill="x",
            padx=5,
            pady=4
        )

        self.label_um = ctk.CTkLabel(
            self.frame,
            text="Distance: 0.000 µm",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_um.pack(pady=0)

        self.label_ps = ctk.CTkLabel(
            self.frame,
            text="Time Delay: 0.0000 ps",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.label_ps.pack(pady=0)

        self.label_intensity = ctk.CTkLabel(
            self.frame,
            text="Intensity: 0.00",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_intensity.pack(pady=0)

        self.label_thresholds = ctk.CTkLabel(
            self.frame,
            text="Thresholds: waiting",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )

        self.label_thresholds.pack(pady=0)

        self.label_accumulated_fringes = ctk.CTkLabel(
            self.frame,
            text="Accumulated Fringes Count: 0",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_accumulated_fringes.pack(pady=0)

        self.compare_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.compare_frame.pack(
            fill="x",
            padx=5,
            pady=4
        )
        #comparison
        ctk.CTkLabel(
            self.compare_frame,
            text="Distance Comparison",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=0)

        self.label_compare_driven = ctk.CTkLabel(
            self.compare_frame,
            text="Driven: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.label_compare_driven.pack(pady=0)

        self.label_compare_calculated = ctk.CTkLabel(
            self.compare_frame,
            text="Calculated: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.label_compare_calculated.pack(pady=0)

        self.label_compare_difference = ctk.CTkLabel(
            self.compare_frame,
            text="Difference: 0.000000 mm",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_compare_difference.pack(pady=0)

        self.live_size = (320, 220)

        ctk.CTkLabel(
            self.scroll,
            text="Live Camera",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 2))

        self.image_label = ctk.CTkLabel(
            self.scroll,
            text="No Image",
            width=self.live_size[0],
            height=self.live_size[1],
            fg_color="#111111",
            text_color="white"
        )

        self.image_label.pack(pady=5)

        self.all_buttons = [
            self.btn,
            self.restart_btn,
            self.wavelength_button,
            self.speed_button,
            self.btn_target_abs,
            self.btn_target_rel,
            self.btn_stop,
            self.btn_min,
            self.btn_left,
            self.btn_center,
            self.btn_right,
            self.btn_max
        ]

        self.update_comparison_labels()#renewing the text in the UI matching the initial update of the comparison labels with 0 values using e.g self.current_stage_movement_for_compare which is 0 at the beginning

        self.update_stage_position_once()#reads the current stage position and updates the label, this is important to have the correct position at the beginning

        # The PI stage connection must start from the Tk/main thread.
        # Camera connection can still run in the background afterwards.
        self.status.configure(
            text="Connecting to hardware (camera, stage)...",
            text_color=ORANGE_COLOR
        )
        self.set_buttons_enabled(False)
        self.after(100, self.connect_hardware)
    # -----------------------------------------------------------------------------
    # 4.1.1 HARDWARE CONNECTION WORKER AND CALLBACK
    # -----------------------------------------------------------------------------

    def connect_hardware(self):
        # Connect stage from the main thread, then connect camera in background.
        stage_ok = self.stage.connect()

        threading.Thread(
            target=self.connect_camera_after_stage,
            args=(stage_ok,),
            daemon=True
        ).start()

    def connect_camera_after_stage(self, stage_ok):
        cam_ok = self.camera_handler.connect()

        self.after(0, lambda: self.on_hardware_connected(cam_ok, stage_ok))

    def on_hardware_connected(self, cam_ok, stage_ok):
        self.camera_connected = cam_ok
        self.stage_connected = stage_ok

        if stage_ok:
            self.apply_stage_speed(update_status=False)
        
        self.set_buttons_enabled(True)
        
        # Update stage position and movement tracking once connected
        self.update_stage_position_once()
        self.reset_stage_movement_tracking()
        
        if cam_ok and stage_ok:
            self.status.configure(
                text="Stopped",
                text_color=TEXT_COLOR
            )
        elif not cam_ok and not stage_ok:
            self.status.configure(
                text="Connection failed: Camera and Stage offline",
                text_color=RED_COLOR
            )
        elif not cam_ok:
            self.status.configure(
                text="Connection failed: Camera offline",
                text_color=RED_COLOR
            )
        else:
            self.status.configure(
                text="Connection failed: Stage offline",
                text_color=RED_COLOR
            )
    # -----------------------------------------------------------------------------
    # 4.2 ENABLE OR DISABLE ALL BUTTONS
    # -----------------------------------------------------------------------------

    def set_buttons_enabled(self, enabled):

        state = "normal" if enabled else "disabled"

        for button in self.all_buttons:
            button.configure(state=state)

    def start_calibration_button_cooldown(self):

        self.calibration_button_cooldown_active = True
        self.set_buttons_enabled(False)

        self.status.configure(
            text="Calibration done - buttons locked for 2s",
            text_color=ORANGE_COLOR
        )

        self.after(
            CALIBRATION_BUTTON_COOLDOWN_MS,
            self.finish_calibration_button_cooldown
        )

    def finish_calibration_button_cooldown(self):

        self.calibration_button_cooldown_active = False
        self.set_buttons_enabled(True)

        if self.is_monitoring:

            self.status.configure(
                text="Monitoring running",
                text_color=GREEN_COLOR
            )

        else:

            self.status.configure(
                text="Stopped",
                text_color=TEXT_COLOR
            )
    # -----------------------------------------------------------------------------
    # 5.1 START OR STOP MONITORING
    # -----------------------------------------------------------------------------
    
    def toggle(self): #toggle method
        #if monitoring is off and camera connection is on, start button should start monitoring
        if not self.is_monitoring:

            if not self.camera_connected:

                self.status.configure(
                    text="Camera not connected",
                    text_color=RED_COLOR
                )

                return #stops the method
            if self.stage_connected:
                self.apply_stage_speed(update_status=False)

            self.restart_values_only() #resets all measurement values

            self.is_monitoring = True

            if MANUAL_THRESHOLDS: #if manual thresholds are set

                self.dark_threshold = (
                    MANUAL_DARK_THRESHOLD
                )

                self.bright_threshold = (
                    MANUAL_BRIGHT_THRESHOLD
                )

                self.label_thresholds.configure(
                    text=(
                        f"Manual Dark: "
                        f"{self.dark_threshold:.2f} | "
                        f"Manual Bright: "
                        f"{self.bright_threshold:.2f}"
                    )
                )

                self.status.configure(
                    text="Monitoring running",
                    text_color=GREEN_COLOR
                )

            else:

                self.calibrating = True #starts calibration

                self.calibration_values = []

                self.calibration_start_time = time.time()

                self.status.configure(
                    text="Calibrating thresholds...",
                    text_color=ORANGE_COLOR
                )

            self.btn.configure( #changes button to stop monitoring
                text="STOP MONITORING",
                fg_color=RED_COLOR
            )
            #background thread, so that GUI doesnt stop and can still show the live camera etc.
            threading.Thread(
                target=self.loop, #starts the loop method which reads the camera and counts fringes as background thread
                daemon=True #thread will stop when program ends
            ).start()

        else:

            self.is_monitoring = False

            if self.stage_connected: #are stage commands available? (before stopping it)
                self.stage.stop()
            self.btn.configure(
                text="START MONITORING",
                fg_color=TEXT_COLOR
            )

            self.status.configure(
                text="Stopped",
                text_color=TEXT_COLOR
            )
    # -----------------------------------------------------------------------------
    # 5.2 RESET BUTTON
    # -----------------------------------------------------------------------------
    
    def restart(self):

        self.restart_values_only() #button calls "restart" function, which forwards to "restart_values_only"

    def restart_values_only(self):
        #defines what the values should look like after pressing reset

        self.accumulated_fringes = 0

        self.was_dark = False

        self.last_count_time = 0

        self.dark_counter = 0

        self.bright_counter = 0

        self.intensity_history = []

        self.calibrating = False
        self.calibration_motion_started = False
        self.calibration_stage_stop_done = False

        self.calibration_values = []

        self.reset_stage_movement_tracking() #function defined later

        self.reset_measurement_after_calibration()

        if hasattr(self, "label_compare_driven"): #checks if the label exists, because this method is also called in the init before creating the label, so it would cause an error if we try to update a label that doesnt exist yet

            self.update_comparison_labels(0.0)
    # -----------------------------------------------------------------------------
    # 6.1 MOVE STAGE TO AN ABSOLUTE POSITION
    # -----------------------------------------------------------------------------
    
    def start_stage_move_to(
        self,
        target_mm,
        start_pos=None,
        reset_after_move=False
    ):
        #security checks so the code doesnt crash
        if not self.stage_connected: #translation stage connected?

            if reset_after_move: #if the stage should return after move, we want to reset the stage position even if its not connected, because otherwise the values would be wrong and the user would have to manually move the stage 

                self.reset_stage_after_calibration()

                return

            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )

            return

        if self.stage.is_moving:

            if reset_after_move:

                self.center_stage_after_calibration_pending = True

                self.status.configure(
                    text=(
                        "Calibration done - stage returns to "
                        "0.00000000000 mm after current move"
                    ),
                    text_color=ORANGE_COLOR
                )

            else:

                self.status.configure(
                    text="Stage is already moving",
                    text_color=ORANGE_COLOR
                )

            return

        if not self.apply_stage_speed(update_status=False):

            if reset_after_move:
                self.reset_stage_after_calibration()

            return

        if start_pos is None: #if no start position is given, read the current position from the stage

            start_pos = self.stage.get_position()

        target_mm = self.stage.clamp_position(target_mm) #so that the target position is in range of the stage

        move_mm = target_mm - start_pos
        #safe the values for the stage_ui_loop
        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.reset_stage_movement_after_move = reset_after_move

        if abs(move_mm) < 1e-12: #if stage is at target, dont move

            if reset_after_move:
                #if the movement is a movement back after calibration but stage already at target, the stage shouldnt move
                self.reset_stage_after_calibration(start_pos)

                return

            else:

                self.update_stage_labels(start_pos, 0.0)

            self.status.configure(
                text="Stage already at target",
                text_color=TEXT_COLOR
            )

            return

        if not self.stage.move_absolute(target_mm):
            #if movement successfull, self.stage.move_absolute is False, not False = true, so stage moves
            #if movement failed, there also should be no reset after move
            self.reset_stage_movement_after_move = False

            if reset_after_move:

                self.reset_stage_after_calibration(start_pos)

            return

        self.status.configure(
            text=f"Stage moving to {target_mm:.6f} mm",
            text_color=TEXT_COLOR
        )
        #if none of the above cases stops the stage from moving, create a movement thread and start the movement

        threading.Thread(
            target=self.stage_ui_loop,
            daemon=True
        ).start()
    # -----------------------------------------------------------------------------
    # 6.2 MOVE STAGE BY A RELATIVE DISTANCE
    # -----------------------------------------------------------------------------
    
    def start_stage_move_by(self, move_mm):

        start_pos = self.stage.get_position()

        self.start_stage_move_to(
            start_pos + move_mm,
            start_pos=start_pos
        )
    # -----------------------------------------------------------------------------
    # 6.3 MOVE STAGE TO TARGET IN STEPS
    # -----------------------------------------------------------------------------
    
    def start_stage_move_to_stepped(self, target_mm):
        #stop errors from happening
        if not self.stage_connected:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return

        if self.stage.is_moving:
            self.status.configure(
                text="Stage is already moving",
                text_color=ORANGE_COLOR
            )
            return

        if not self.apply_stage_speed(update_status=False):
            return

        start_pos = self.stage.get_position()
        target_mm = self.stage.clamp_position(target_mm) #clamps target distance by the maximum movement range of the stage

        if abs(target_mm - start_pos) < 1e-12:
            self.status.configure(
                text="Stage already at target",
                text_color=TEXT_COLOR
            )
            return

        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement

        threading.Thread(
            target=self.stage_stepped_move_worker,
            args=(start_pos, target_mm),
            daemon=True
        ).start()
    # -----------------------------------------------------------------------------
    # 6.4 MOVE STAGE RELATIVELY IN STEPS
    # -----------------------------------------------------------------------------
    
    def start_stage_move_by_steps(self, move_mm): 

        start_pos = self.stage.get_position()
        self.start_stage_move_to_stepped( 
            start_pos + move_mm #moves stage by defined distance
        )
    # -----------------------------------------------------------------------------
    # 6.5 WORKER FOR STEPPED MOVEMENT
    # -----------------------------------------------------------------------------
    
    def stage_stepped_move_worker(self, start_pos, target_mm):

        step_mm = self.get_step_size() #step size from UI
        delay_s = 0.25 #delay between steps
        direction = 1 if target_mm > start_pos else -1 #+1 for positiv movement, -1 for negative movement
        current_pos = start_pos
        remaining = abs(target_mm - start_pos)
        moved = 0.0

        self.status.configure(
            text=(
                f"Moving to {target_mm:.6f} mm in {step_mm:.6f} mm steps"
            ),
            text_color=TEXT_COLOR
        )

        while remaining > 1e-12:
            next_step = min(step_mm, remaining)
            next_target = current_pos + direction * next_step

            if not self.stage.move_absolute(next_target): 
                self.status.configure(
                    text="Stage move failed",
                    text_color=RED_COLOR
                )
                return

            while self.stage.is_moving:
                time.sleep(0.01)

            step_distance = abs(next_target - current_pos) #how far did this step move
            moved += step_distance #add this value to step distance
            current_pos = next_target
            remaining = abs(target_mm - current_pos)

            self.total_stage_movement = (
                self.stage_movement_before_move + moved
            )

            self.after( #because background threads are not allowed to access the UI directly, the values have tobe updated
                0, #wait 0 ms
                lambda  p=current_pos, m=moved, b=self.stage_movement_before_move: #lambda=anonymous function because after expects a function that will be called later and not a function output
                self.update_stage_labels(p, m, b)
            )

            if remaining > 1e-12:
                time.sleep(delay_s)

        self.after(
            0,
            lambda:
            self.status.configure(
                text=f"Reached {current_pos:.6f} mm",
                text_color=GREEN_COLOR
            )
        )
    # -----------------------------------------------------------------------------
    # 5.6 READ STEP SIZE FROM THE UI
    # -----------------------------------------------------------------------------
    
    def get_step_size(self):
        #convert the user input from the UI into something readable for the program
        try:
            value = float(
                self.step_entry.get().replace(",", ".")
            )
            return abs(value)
        except ValueError:
            return 0.0001 #safe default size when step size invalid

    def get_stage_speed(self):

        try:
            value = float(
                self.speed_entry.get().replace(",", ".")
            )
            if value <= 0:
                raise ValueError
            return abs(value)

        except ValueError:
            return DEFAULT_STAGE_SPEED_MM_S

    def apply_stage_speed(self, update_status=True):

        speed_mm_s = self.get_stage_speed()

        self.speed_entry.delete(0, "end")
        self.speed_entry.insert(
            0,
            f"{speed_mm_s:.6f}"
        )

        if not self.stage_connected:
            self.stage.set_velocity(speed_mm_s)

            if update_status:
                self.status.configure(
                    text="Stage not connected",
                    text_color=RED_COLOR
                )

            return False

        if not self.stage.set_velocity(speed_mm_s):

            if update_status:
                error_text = (
                    self.stage.last_error
                    or "Could not set stage velocity"
                )
                self.status.configure(
                    text=error_text,
                    text_color=RED_COLOR
                )

            return False

        if update_status:
            self.status.configure(
                text=f"Stage velocity set to {speed_mm_s:.6f} mm/s",
                text_color=GREEN_COLOR
            )

        return True

    def use_continuous_stage_mode(self):

        return MODE.lower().startswith("c")
    # -----------------------------------------------------------------------------
    # 5.7 CALCULATE FRINGE DISTANCE
    # -----------------------------------------------------------------------------
    
    def compute_fringe_distance(self, wavelength_nm):

        return (wavelength_nm / 2) / 1_000_000
    # -----------------------------------------------------------------------------
    # 5.8 APPLY A NEW LASER WAVELENGTH
    # -----------------------------------------------------------------------------
    
    def apply_wavelength(self):
        # get the new laser wavelenght from the UI
        try:
            wavelength_nm = float(
                self.wavelength_entry.get().replace(",", ".")
            )
        except ValueError:
            self.status.configure(
                text="Invalid wavelength value",
                text_color=RED_COLOR
            )
            return

        self.laser_wavelength_nm = wavelength_nm
        self.fringe_distance_mm = self.compute_fringe_distance( #compute fringe distance with new wavelenght
            self.laser_wavelength_nm
        )

        #calculate default step size based on wavelenght
        default_step = self.fringe_distance_mm / 4
        #clear old suggested stepsize
        self.step_entry.delete(0, "end")
        self.step_entry.insert(
            0,
            f"{default_step:.7f}"
        )

        self.status.configure(
            text=f"Wavelength set to {self.laser_wavelength_nm:.1f} nm",
            text_color=GREEN_COLOR
        )
    # -----------------------------------------------------------------------------
    # 5.9 STAGE BUTTON ACTIONS
    # -----------------------------------------------------------------------------
    
    def move_to_min(self):

        self.start_stage_move_to( 
            self.stage.min_position
        )

    def step_negative(self):

        self.start_stage_move_by(
            -self.get_step_size()
        )

    def move_to_center(self):

        if self.use_continuous_stage_mode():
            self.start_stage_move_to(
                0.0
            )

        else:
            self.start_stage_move_to_stepped(
                0.0
            )

    def step_positive(self):

        self.start_stage_move_by(
            self.get_step_size()
        )

    def move_to_max(self):

        self.start_stage_move_to(
            self.stage.max_position
        )

    def move_to_target_by_steps(self):

        try:
            target_mm = float(
                self.target_entry.get().replace(",", ".")
            )
        except ValueError:
            self.status.configure(
                text="Invalid target value",
                text_color=RED_COLOR
            )
            return

        if self.use_continuous_stage_mode():
            self.start_stage_move_to(target_mm)

        else:
            self.start_stage_move_to_stepped(target_mm)

    def move_distance_by_steps(self):

        try:
            distance_mm = float(
                self.target_entry.get().replace(",", ".")
            )
        except ValueError:
            self.status.configure(
                text="Invalid distance value",
                text_color=RED_COLOR
            )
            return

        if self.use_continuous_stage_mode():
            self.start_stage_move_by(distance_mm)

        else:
            self.start_stage_move_by_steps(distance_mm)

    def stop_stage(self):

        if not self.stage_connected:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return

        self.stage.stop()

        self.status.configure(
            text="Stage stopped manually",
            text_color=RED_COLOR
        )

    # -----------------------------------------------------------------------------
    # 7.1 TRACK NORMAL STAGE MOVEMENT
    # -----------------------------------------------------------------------------
    
    def stage_ui_loop(self):
        #how much did the stage move befor the current movement? use this as base
        movement_base = self.stage_movement_before_move

        while self.stage.is_moving:

            pos = self.stage.get_position() #read stage position

            moved = abs(pos - self.stage_start_position) #calculate movement completed

            self.after(
                0,
                lambda p=pos, m=moved, b=movement_base:
                self.update_stage_labels(p, m, b)
            )

            time.sleep(0.05)

        pos = self.stage.get_position()

        moved = abs(pos - self.stage_start_position)
        self.total_stage_movement = (
            movement_base + moved
        )
        #was the recorded movement a movement back after the calibration phase
        if self.reset_stage_movement_after_move:
            
            self.reset_stage_movement_after_move = False

            self.after(
                0,
                lambda p=pos:
                self.reset_stage_after_calibration(p)
            )
        #code runs in background thread, but UI changes should happen in main thread, so "after"
        else:

            self.after(
                0,
                lambda p=pos, m=moved, b=movement_base:
                self.update_stage_labels(p, m, b)
            )
        #start the postponed returned to zero move
        if self.center_stage_after_calibration_pending:

            self.center_stage_after_calibration_pending = False

            self.after(
                0,
                self.move_to_center_after_calibration
            )
    # -----------------------------------------------------------------------------
    # 7.2 SHOW INITIAL STAGE POSITION
    # -----------------------------------------------------------------------------
    #after calibration UI is filled with current stage position
    def update_stage_position_once(self):

        if self.stage_connected:

            pos = self.stage.get_position()

            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )
    # -----------------------------------------------------------------------------
    # 7.3 UPDATE STAGE MOVEMENT DISPLAY
    # -----------------------------------------------------------------------------
    
    def update_stage_labels(self, pos, moved, movement_base=None):

        if movement_base is None:
            movement_base = self.total_stage_movement

        current_total_stage_movement = (
            movement_base + abs(moved) #combine previous and current movement for display
        )
        self.current_stage_movement_for_compare = (
            current_total_stage_movement
        )

        self.label_stage_position.configure(
            text=f"Stage Position: {pos:.6f} mm"
        )

        self.label_stage_moved.configure(
            text=(
                f"Accumulated Movement: "
                f"{current_total_stage_movement:.6f} mm"
            )
        )

        self.update_comparison_labels(
            current_total_stage_movement
        )
    # -----------------------------------------------------------------------------
    # 7.4 RESET STAGE MOVEMENT TRACKING
    # -----------------------------------------------------------------------------
    
    def reset_stage_movement_tracking(self, pos=None):

        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0

        if pos is not None: #use provided position as new reference
            self.stage_reference_position = pos
            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )
        elif self.stage_connected: #if the stage is connected use actual hardware position as reference
            self.stage_reference_position = self.stage.get_position()
        else:
            self.stage_reference_position = 0.0

        self.label_stage_moved.configure(
            text="Accumulated Movement: 0.000000 mm"
        )

        self.update_comparison_labels(0.0)
    # -----------------------------------------------------------------------------
    # 7.5 RESET FRINGE MEASUREMENT DISPLAY
    # -----------------------------------------------------------------------------
    
    def reset_measurement_after_calibration(self):

        self.accumulated_fringes = 0
        self.was_dark = False
        self.last_count_time = 0
        self.dark_counter = 0
        self.bright_counter = 0
        self.intensity_history = []

        self.label_um.configure(
            text="Distance: 0.000 µm"
        )

        self.label_ps.configure(
            text="Time Delay: 0.0000 ps"
        )

        self.label_accumulated_fringes.configure(
            text="Accumulated Fringes Count: 0"
        )

        self.update_comparison_labels(0.0)
    # -----------------------------------------------------------------------------
    # 7.6 STOP STAGE AFTER CALIBRATION
    # -----------------------------------------------------------------------------
    #stop the stage where it is after calibration
    def finish_calibration_stage_reset(self):

        if self.calibration_stage_stop_done:
            return

        self.calibration_stage_stop_done = True
        self.center_stage_after_calibration_pending = False

        if not self.is_monitoring:

            if self.stage_connected and self.stage.is_moving:
                self.stage.stop()

            self.returning_stage_after_calibration = False
            return

        self.returning_stage_after_calibration = True

        pos = None

        if self.stage_connected:

            if self.stage.is_moving:
                self.stage.stop()

            pos = self.stage.get_position()

        self.reset_stage_after_calibration(pos)

        if pos is not None:
            self.status.configure(
                text=(
                    f"Calibration done - stage stopped at {pos:.6f} mm "
                    "(buttons locked for 2s)"
                ),
                text_color=GREEN_COLOR
            )

        else:
            self.status.configure(
                text="Calibration done - stage stopped (buttons locked for 2s)",
                text_color=GREEN_COLOR
            )
    # -----------------------------------------------------------------------------
    # 7.7 MOVE STAGE DURING CALIBRATION
    # -----------------------------------------------------------------------------
    
    def calibration_stage_motion(self):

        try:

            if not self.stage_connected: #refuse movement commands when stage is not connected
                return

            start_pos = self.stage.get_position() #current stage position as movement start
            sweep_target = self.stage.clamp_position(
                start_pos + CALIBRATION_SWEEP_DISTANCE_MM
            )

            if abs(sweep_target - start_pos) < 1e-12:
                sweep_target = self.stage.clamp_position(
                    start_pos - CALIBRATION_SWEEP_DISTANCE_MM
                )

            if abs(sweep_target - start_pos) < 1e-12:
                return

            targets = [
                sweep_target,
                start_pos
            ]

            for target in targets:
                if not self.is_monitoring or not self.calibrating:
                    return

                self.after(
                    0,
                    lambda t=target:
                    self.status.configure(
                        text=f"Calibrating - smooth stage sweep to {t:.6f} mm",
                        text_color=ORANGE_COLOR
                    )
                )

                if not self.stage.move_absolute(target):
                    return

                while (
                    self.stage.is_moving
                    and self.is_monitoring
                    and self.calibrating
                ):
                    pos = self.stage.get_position()
                    moved = abs(pos - start_pos)

                    self.after(
                        0,
                        lambda p=pos, m=moved:
                        self.update_stage_labels(p, m, 0.0)
                    )

                    time.sleep(0.02)

            if self.is_monitoring and self.calibrating:
                self.after(
                    0,
                    lambda:
                    self.status.configure(
                        text="Calibrating - stage sweep done",
                        text_color=ORANGE_COLOR
                    )
                )

        finally:

            if self.stage_connected and self.stage.is_moving:
                self.stage.stop()
    # -----------------------------------------------------------------------------
    # 7.8 START PENDING RETURN AFTER CALIBRATION MOTION
    # -----------------------------------------------------------------------------

    def start_pending_center_after_calibration(self):

        if not self.center_stage_after_calibration_pending:
            return

        if not self.is_monitoring:
            self.center_stage_after_calibration_pending = False
            self.returning_stage_after_calibration = False
            return

        if self.stage_connected and self.stage.is_moving:

            self.after(
                100,
                self.start_pending_center_after_calibration
            )

            return

        self.center_stage_after_calibration_pending = False
        self.move_to_center_after_calibration()
    # -----------------------------------------------------------------------------
    # 7.9 CENTER STAGE AFTER A PENDING CALIBRATION MOVE
    # -----------------------------------------------------------------------------
    
    def move_to_center_after_calibration(self):

        self.returning_stage_after_calibration = True

        self.start_stage_move_to(
            0.0,
            reset_after_move=True
        )
    # -----------------------------------------------------------------------------
    # 7.10 FINISH CALIBRATION RESET
    # -----------------------------------------------------------------------------
    #track the stage movement and reset
    def reset_stage_after_calibration(self, pos=None):

        self.reset_stage_movement_tracking(pos)

        self.reset_measurement_after_calibration()

        self.returning_stage_after_calibration = False

        self.start_calibration_button_cooldown()
    # -----------------------------------------------------------------------------
    # 7.11 UPDATE DRIVEN VS CALCULATED DISTANCE
    # -----------------------------------------------------------------------------
    #stage movement distance is compared with distance calculated from counted fringes
    def update_comparison_labels(self, driven_mm=None):

        if driven_mm is None:

            driven_mm = self.current_stage_movement_for_compare

        driven_distance_mm = abs(driven_mm)

        calculated_fringes = self.accumulated_fringes

        calculated_mm = (
            calculated_fringes
            * self.fringe_distance_mm
        )

        difference_mm = (
            driven_distance_mm
            - calculated_mm
        )

        self.label_compare_driven.configure(
            text=(
                f"Driven: {driven_distance_mm:.6f} mm"
            )
        )

        self.label_compare_calculated.configure(
            text=(
                f"Calculated: {calculated_mm:.6f} mm"
            )
        )

        self.label_compare_difference.configure(
            text=(
                f"Difference: {difference_mm:.6f} mm"
            )
        )
    # -----------------------------------------------------------------------------
    # 8.1 CAMERA AND MEASUREMENT LOOP
    # -----------------------------------------------------------------------------
    
    def loop(self):

        frame_counter = 0

        while self.is_monitoring:

            img = self.camera_handler.get_frame()

            if img is None:
                continue

            frame_counter += 1

            if frame_counter % 20 == 0: #refresh live image after 20 frames to keep UI responsive

                self.after(
                    0,
                    lambda f=img:
                    self.update_image(f)
                )

            intensity = (
                self.camera_handler
                .get_fringe_intensity_from_frame(img)
            )

            if intensity is not None:

                fringe_counted = False

                if self.calibrating:

                    if (not self.calibration_motion_started
                            and self.stage_connected):
                        self.calibration_motion_started = True
                        threading.Thread(
                            target=self.calibration_stage_motion,
                            daemon=True
                        ).start()

                    self.calibration_values.append(
                        intensity
                    )

                    elapsed = (
                        time.time()
                        - self.calibration_start_time
                    )

                    self.after(
                        0,
                        lambda e=elapsed:
                        self.label_thresholds.configure(
                            text=f"Calibrating {e:.1f}/5s"
                        )
                    )

                    if elapsed >= 5: #finish threshold calibration after 5s of frames
                        #use lowest calibration intensity as dark end of the signal
                        min_val = min( 
                            self.calibration_values
                        )
                        #use highest calibration intensity as bright end
                        max_val = max(
                            self.calibration_values
                        )

                        value_range = (
                            max_val - min_val
                        )
                        #these values I found by experimenting with the setup work best for accurate fringe detection
                        self.dark_threshold = (
                            min_val
                            + value_range * 0.125
                        )

                        self.bright_threshold = (
                            max_val
                            - value_range * 0.60
                        )

                        self.calibrating = False

                        self.after(
                            0,
                            lambda:
                            self.label_thresholds.configure(
                                text=(
                                    f"Dark: "
                                    f"{self.dark_threshold:.2f} | "
                                    f"Bright: "
                                    f"{self.bright_threshold:.2f}"
                                )
                            )
                        )

                        self.after(
                            0,
                            lambda:
                            self.status.configure(
                                text="Monitoring running",
                                text_color=GREEN_COLOR
                            )
                        )

                        self.after(
                            0,
                            self.finish_calibration_stage_reset
                        )

                else:

                    if not self.returning_stage_after_calibration:
                        #run fringe detector for current intensity
                        fringe_counted = (
                            self.update_accumulated_fringes(
                                intensity
                            )
                        )
                self.after(
                    0,
                    lambda v=intensity, c=fringe_counted:
                    self.update_intensity_label(v, c)
                )
            #convert counted fringes into distance in mm
            dist_mm = ( 
                self.accumulated_fringes
                * self.fringe_distance_mm
            )

            dist_um = dist_mm * 1000

            time_ps = (
                2 * dist_mm
            ) / SPEED_OF_LIGHT_MM_PS

            self.after(
                0,
                lambda:
                self.update_values(
                    dist_mm,
                    dist_um,
                    time_ps
                )
            )

            self.after(
                0,
                lambda:
                self.label_accumulated_fringes.configure(
                    text=(
                        f"Accumulated Fringes Count: "
                        f"{self.accumulated_fringes}"
                    )
                )
            )
    # -----------------------------------------------------------------------------
    # 8.2 DETECT AND COUNT FRINGES
    # -----------------------------------------------------------------------------
    #a stable dark to bright transition is counted as one fringe
    def update_accumulated_fringes(
        self,
        intensity
    ):

        self.intensity_history.append(
            intensity
        )

        if len(self.intensity_history) > 5:
            self.intensity_history.pop(0)

        smooth_intensity = np.mean( #smooth the intensity with a short moving average
            self.intensity_history
        )

        if smooth_intensity < self.dark_threshold: #smooth signal is dark when below dark threshold

            self.dark_counter += 1

        else:

            self.dark_counter = 0 #reset dark frame streak so a new stable dark phase must be detected from scratch

        if self.dark_counter >= REQUIRED_DARK_FRAMES: #accept dark phase only after enough stable dark frames

            self.was_dark = True

        if smooth_intensity > self.bright_threshold:

            self.bright_counter += 1

        else:

            self.bright_counter = 0

        cooldown_ok = ( #choose whether enough time has passed since last counted fringe
            time.time() - self.last_count_time
        ) > FRINGE_COOLDOWN

        if (
            self.was_dark
            and self.bright_counter
            >= REQUIRED_BRIGHT_FRAMES
            and cooldown_ok
        ):

            self.accumulated_fringes += 1 #count one completed darktobright transition

            self.was_dark = False #clear the remembered dark phase

            self.last_count_time = time.time()

            self.dark_counter = 0

            self.bright_counter = 0

            return True

        return False
    # -----------------------------------------------------------------------------
    # 8.3 SHOW CURRENT INTENSITY
    # -----------------------------------------------------------------------------
    #intensity display updates and briefly turns green when fringe is counted
    def update_intensity_label(
        self,
        intensity,
        fringe_counted
    ):

        self.label_intensity.configure(
            text=f"Intensity: {intensity:.2f}"
        )

        if fringe_counted:

            self.label_intensity.configure(
                text_color=GREEN_COLOR
            )

            self.after(
                250,
                lambda:
                self.label_intensity.configure(
                    text_color=TEXT_COLOR
                )
            )
    # -----------------------------------------------------------------------------
    # 8.4 SHOW DISTANCE AND TIME DELAY
    # -----------------------------------------------------------------------------
    
    def update_values(
        self,
        mm,
        um,
        ps
    ):

        self.label_um.configure(
            text=f"Distance: {um:.3f} µm"
        )

        self.label_ps.configure(
            text=f"Time Delay: {ps:.4f} ps"
        )

        self.update_comparison_labels()
    # -----------------------------------------------------------------------------
    # 8.5 SHOW LIVE CAMERA IMAGE
    # -----------------------------------------------------------------------------
    
    def update_image(self, img):

        display = img.astype(np.float32)

        display -= np.min(display) 

        if np.max(display) > 0: #normalize only when image contains nonzero signal
            display /= np.max(display)

        display = ( #convert normalized image into brightness value 
            display * 255
        ).astype(np.uint8)

        pil = Image.fromarray(display).convert( #convert to rgb image
            "RGB"
        )

        pil = pil.resize(self.live_size) #resize camera image to preview area

        ctk_img = ctk.CTkImage( #convert back into customtkinter image
            light_image=pil,
            size=self.live_size
        )

        self.image_label.configure(
            image=ctk_img,
            text=""
        )

        self.image_label.image = ctk_img
    # -----------------------------------------------------------------------------
    # 9.1 SHUT DOWN HARDWARE CLEANLY
    # -----------------------------------------------------------------------------
    
    def on_close(self):

        self.is_monitoring = False

        try:
            self.camera_handler.close()

        except:
            pass

        try:
            self.stage.close()

        except:
            pass

        self.destroy()
# -----------------------------------------------------------------------------
# 9. PROGRAM START
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    app = InterferometerApp() #create app

    app.protocol(
        "WM_DELETE_WINDOW", #connect window close button to cleanup routine
        app.on_close
    )

    app.mainloop() #start the graphical application loop
