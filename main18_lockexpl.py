# TABLE OF CONTENTS FOR MAIN18_LOCKEXPL.PY
# 1. Settings and constants for thresholding, optics, colors, and timing.
# 2. Hardware setup for camera and translation stage access.
# 3. Window construction with controls, live image, and measurement labels.
# 4. Monitoring start/stop logic and measurement reset logic.
# 5. Translation-stage movement commands and movement tracking.
# 6. Position lock logic for correcting stage drift.
# 7. Calibration reset, stage return, and distance comparison.
# 8. Camera loop, fringe detection, value updates, and live image display.
# 9. Shutdown and program start.
# Comments describe what the interferometer program is doing, not Python syntax mechanics.

# -----------------------------------------------------------------------------
# 1. SETTINGS AND CONSTANTS
# -----------------------------------------------------------------------------
MANUAL_THRESHOLDS = False
# Use automatic threshold calibration by default.

MANUAL_DARK_THRESHOLD = 7
# Fallback dark threshold if manual thresholds are enabled.
MANUAL_BRIGHT_THRESHOLD = 25
# Fallback bright threshold if manual thresholds are enabled.


# -----------------------------------------------------------------------------
# 2. HARDWARE AND LIBRARY SETUP
# -----------------------------------------------------------------------------
import os
# Path handling is needed to locate camera driver files.
import threading
# Background threads keep the UI responsive during camera and stage work.
import time
# Timestamps and short pauses are used for calibration, cooldowns, and movement polling.
import numpy as np
# Camera frames and intensity smoothing are handled as numeric arrays.
import customtkinter as ctk
# The graphical interface is built with CustomTkinter widgets.

from PIL import Image, ImageDraw
# Live camera frames are converted and annotated before display.

from camera_handler import CameraHandler
# Camera communication is handled by the local camera wrapper.
from stage_controller import StageController
# Translation-stage communication is handled by the local stage wrapper.


# Camera driver files are loaded relative to this script location.
current_directory = os.path.dirname(os.path.abspath(__file__))
# Find the folder containing this script.
dll_path = os.path.join(current_directory, "Camera")
# Build the expected path to the camera driver folder.

if os.path.exists(dll_path):
# Only register the driver folder when it actually exists.
    os.add_dll_directory(dll_path)
    # Make the camera driver folder available to the camera library.


# Optical constants convert counted fringes into distance and time delay.
LASER_WAVELENGTH_NM = 1576.3
# Start with the default laser wavelength used for distance calculations.

FRINGE_DISTANCE_MM = (
# Calculate the stage distance represented by one counted fringe.
    (LASER_WAVELENGTH_NM / 2) / 1_000_000/2 # Light travels to the mirror and back, so stage travel maps to half of the optical path change.
)

SPEED_OF_LIGHT_MM_PS = 0.299792458
# Use light speed in mm/ps to convert distance into optical delay.

# Shared UI colors keep status messages visually consistent.
TEXT_COLOR = "#0A4A51"
# Main color for neutral text and controls.
GREEN_COLOR = "#1EAD4F"
# Green marks active or successful states.
RED_COLOR = "#C0392B"
# Red marks stop states or errors.
ORANGE_COLOR = "#D35400"
# Orange marks calibration, waiting, or warning states.

REQUIRED_DARK_FRAMES = 3
# Require several dark frames before the detector accepts a dark phase.
REQUIRED_BRIGHT_FRAMES = 3
# Require several bright frames before the detector accepts a bright phase.

FRINGE_COOLDOWN = 0.08
# Prevent one physical fringe from being counted multiple times too quickly.
LOCK_CORRECTION_COOLDOWN = 0.20
# Prevent the lock controller from sending correction moves too often.


# -----------------------------------------------------------------------------
# 3. MAIN APPLICATION WINDOW AND MEASUREMENT CONTROL
# -----------------------------------------------------------------------------
class InterferometerApp(ctk.CTk):
# The application object combines UI, camera handling, stage movement, and measurement logic.

    # -----------------------------------------------------------------------------
    # 3.1 BUILD THE APP STATE AND USER INTERFACE
    # All start values, hardware objects, buttons, labels, and image areas are prepared here.
    # -----------------------------------------------------------------------------
    def __init__(self):

        super().__init__()
        # Initialize the window before adding app-specific widgets.

        self.title("Interferometer Monitor")
        # Show the application name in the window title.

        self.geometry("900x1000")
        # Start with enough window space for controls, values, and live image.

        ctk.set_appearance_mode("light")
        # Use a light UI appearance for the monitor window.

        self.configure(fg_color="white")
        # Use a white background for the main window.

        self.scroll = ctk.CTkScrollableFrame(
        # Create the main scrollable area for all controls and displays.
            self,
            fg_color="white"
        )

        self.scroll.pack(
        # Place the scroll area so it fills the window.
            fill="both",
            expand=True,
            padx=2,
            pady=2
        )

        self.is_monitoring = False
        # Start with the camera measurement loop stopped.

        self.accumulated_fringes = 0
        # Clear the fringe counter.

        self.was_dark = False
        # Clear the remembered dark phase so the next fringe count requires a fresh dark-to-bright transition.

        self.last_count_time = 0
        # Start with no previous fringe timestamp.

        self.dark_counter = 0
        # Reset the dark-frame streak so a new stable dark phase must be detected from scratch.

        self.bright_counter = 0
        # Reset the bright-frame streak so a new stable bright phase must be detected from scratch.

        self.intensity_history = []
        # Clear old intensity samples so smoothing starts from the current measurement state.

        self.dark_threshold = MANUAL_DARK_THRESHOLD
        # Initialize the dark threshold with the manual fallback value.

        self.bright_threshold = MANUAL_BRIGHT_THRESHOLD
        # Initialize the bright threshold with the manual fallback value.

        self.calibrating = False
        # Leave calibration mode and begin normal fringe counting.

        self.calibration_start_time = 0
        # Start with no calibration start time recorded.

        self.calibration_values = []
        # Start collecting fresh calibration intensities.

        self.camera_handler = CameraHandler()
        # Prepare the camera interface object.

        self.camera_connected = (
        # Store whether the camera connection succeeds.
            self.camera_handler.connect()
            # Try to connect to the camera.
        )

        self.stage = StageController()
        # Prepare the translation-stage interface object.

        self.stage_connected = (
        # Store whether the stage connection succeeds.
            self.stage.connect()
            # Try to connect to the translation stage.
        )

        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
        # Use the default wavelength as the current wavelength.
        self.fringe_distance_mm = self.compute_fringe_distance(
        # Calculate the current distance per fringe from the wavelength.
            self.laser_wavelength_nm
        )
        self.stage_start_position = 0.0
        # Prepare a place to remember where a stage movement starts.
        self.stage_reference_position = 0.0
        # Prepare the reference position used for movement tracking.
        self.total_stage_movement = 0.0
        # Start accumulated stage travel at zero.
        self.stage_movement_before_move = 0.0
        # Start the movement baseline at zero.
        self.current_stage_movement_for_compare = 0.0
        # Start the driven-distance comparison value at zero.
        self.reset_stage_movement_after_move = False
        # Cancel the planned after-move reset because there will be no stage-ui loop completion event for a failed move.
        self.center_stage_after_calibration_pending = False
        # Start without a postponed centering move.
        self.returning_stage_after_calibration = False
        # Mark that the calibration return is finished.
        self.calibration_motion_started = False
        # Allow calibration movement to start again on the next run.
        self.lock_active = False
        # Disable the position lock.
        self.lock_position_mm = 0.0
        # Prepare the stored lock position.
        self.lock_reference_fringes = 0
        # Prepare the fringe count captured when lock starts.
        self.lock_correction_active = False
        # Mark that no lock correction is currently running, so future correction checks can start a new one if needed.
        self.lock_last_correction_time = 0
        # Allow the first lock correction immediately after lock starts.

        ctk.CTkLabel(
        # Add a visible text label to the current UI section.
            self.scroll,
            text="Interferometer Monitor",
            font=("Arial", 23, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=5)
        # Place this UI element in the window layout.

        self.btn = ctk.CTkButton(
        # Create the button that starts and stops monitoring.
            self.scroll,
            text="START MONITORING",
            command=self.toggle,
            width=180,
            height=30,
            fg_color=TEXT_COLOR,
            font=("Arial", 11, "bold")
        )

        self.btn.pack(pady=2)
        # Place the monitoring button below the title.

        self.restart_btn = ctk.CTkButton(
        # Create the button that resets measurement values.
            self.scroll,
            text="RESET",
            command=self.restart,
            width=140,
            height=28,
            fg_color=ORANGE_COLOR
        )

        self.restart_btn.pack(pady=1)
        # Place the reset button near the monitoring control.

        self.status = ctk.CTkLabel(
        # Create the status line for user feedback.
            self.scroll,
            text="Status: Stopped",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.status.pack(pady=2)
        # Place the status line below the main buttons.

        self.stage_frame = ctk.CTkFrame(
        # Create the UI section for translation-stage controls.
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.stage_frame.pack(
        # Place the stage-control section in the scroll area.
            fill="x",
            padx=5,
            pady=4
        )

        ctk.CTkLabel(
        # Add a visible text label to the current UI section.
            self.stage_frame,
            text="Electronic Translation Stage",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=2)
        # Place this UI element in the window layout.

        self.wavelength_entry = ctk.CTkEntry(
        # Create the wavelength input field.
            self.stage_frame,
            placeholder_text="Laser wavelength in nm",
            width=250
        )

        self.wavelength_entry.pack(pady=1)
        # Place the wavelength input in the stage section.
        self.wavelength_entry.insert(0, f"{self.laser_wavelength_nm:.1f}")
        # Show the default wavelength in the input field.

        self.wavelength_button = ctk.CTkButton(
        # Create the button that applies the wavelength input.
            self.stage_frame,
            text="Set wavelength",
            width=120,
            command=self.apply_wavelength,
            fg_color=TEXT_COLOR
        )

        self.wavelength_button.pack(pady=1)
        # Place the wavelength button under the wavelength input.

        self.step_entry = ctk.CTkEntry(
        # Create the input for the movement step size.
            self.stage_frame,
            placeholder_text="Step size in mm",
            width=250
        )

        self.step_entry.pack(pady=1)
        # Place the step-size input in the stage section.
        self.step_entry.insert(
        # Show the new suggested step size.
            0,
            f"{(self.fringe_distance_mm / 8):.7f}"
        )

        self.button_frame = ctk.CTkFrame(
        # Create a row container for stage movement buttons.
            self.stage_frame,
            fg_color="transparent"
        )

        self.button_frame.pack(pady=1)
        # Place the movement-button row in the stage section.

        ctk.CTkLabel(
        # Add a visible text label to the current UI section.
            self.stage_frame,
            text="or",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=3)
        # Place this UI element in the window layout.

        self.target_entry = ctk.CTkEntry(
        # Create the input for target position or travel distance.
            self.stage_frame,
            placeholder_text="Target value or distance in mm",
            width=250
        )

        self.target_entry.pack(pady=1)
        # Place the target input below the manual step controls.
        self.target_entry.insert(0, "0.0000")
        # Start the target input at zero.

        self.target_button_frame = ctk.CTkFrame(
        # Create a small row for target and distance buttons.
            self.stage_frame,
            fg_color="transparent"
        )

        self.target_button_frame.pack(pady=1)
        # Place the target-button row below the target input.

        self.btn_target_abs = ctk.CTkButton(
        # Create the button for absolute target movement.
            self.target_button_frame,
            text="Go to target",
            width=140,
            command=self.move_to_target_by_steps,
            fg_color=TEXT_COLOR
        )

        self.btn_target_abs.grid(
        # Place the absolute target button in the target row.
            row=0,
            column=0,
            padx=1
        )

        self.btn_target_rel = ctk.CTkButton(
        # Create the button for relative distance movement.
            self.target_button_frame,
            text="Move distance",
            width=140,
            command=self.move_distance_by_steps,
            fg_color=TEXT_COLOR
        )

        self.btn_target_rel.grid(
        # Place the relative distance button next to the target button.
            row=0,
            column=1,
            padx=1
        )

        self.btn_min = ctk.CTkButton(
        # Create the button that moves to the minimum stage limit.
            self.button_frame,
            text="|<",
            width=60,
            command=self.move_to_min,
            fg_color=TEXT_COLOR
        )

        self.btn_min.grid(
        # Place the minimum button in the movement row.
            row=0,
            column=0,
            padx=1
        )

        self.btn_left = ctk.CTkButton(
        # Create the button for one negative step.
            self.button_frame,
            text="<",
            width=60,
            command=self.step_negative,
            fg_color=TEXT_COLOR
        )

        self.btn_left.grid(
        # Place the negative-step button in the movement row.
            row=0,
            column=1,
            padx=1
        )

        self.btn_center = ctk.CTkButton(
        # Create the button that moves to zero.
            self.button_frame,
            text="0",
            width=60,
            command=self.move_to_center,
            fg_color=TEXT_COLOR
        )

        self.btn_center.grid(
        # Place the center button in the movement row.
            row=0,
            column=2,
            padx=1
        )

        self.btn_right = ctk.CTkButton(
        # Create the button for one positive step.
            self.button_frame,
            text=">",
            width=60,
            command=self.step_positive,
            fg_color=TEXT_COLOR
        )

        self.btn_right.grid(
        # Place the positive-step button in the movement row.
            row=0,
            column=3,
            padx=1
        )

        self.btn_max = ctk.CTkButton(
        # Create the button that moves to the maximum stage limit.
            self.button_frame,
            text=">|",
            width=60,
            command=self.move_to_max,
            fg_color=TEXT_COLOR
        )

        self.btn_max.grid(
        # Place the maximum button in the movement row.
            row=0,
            column=4,
            padx=1
        )

        self.btn_lock = ctk.CTkButton(
        # Create the lock button for holding the current stage position.
            self.stage_frame,
            text="LOCK",
            width=120,
            command=self.toggle_lock,
            fg_color=TEXT_COLOR
        )

        self.btn_lock.pack(pady=(3, 1))
        # Place the lock button in the stage section.

        self.label_lock_status = ctk.CTkLabel(
        # Create the display that shows whether the lock is active.
            self.stage_frame,
            text="Lock: off",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )

        self.label_lock_status.pack(pady=0)
        # Place the lock-status display under the lock button.


        self.label_stage_position = ctk.CTkLabel(
        # Create the display for the current stage position.
            self.stage_frame,
            text="Stage Position: 0.000000 mm",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )

        self.label_stage_position.pack(pady=0)
        # Place the stage-position display in the stage section.

        self.label_stage_moved = ctk.CTkLabel(
        # Create the display for accumulated stage travel.
            self.stage_frame,
            text="Accumulated Movement: 0.000000 mm",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_stage_moved.pack(pady=0)
        # Place the accumulated-movement display near the position display.

        self.frame = ctk.CTkFrame(
        # Create the measurement-value display section.
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.frame.pack(
        # Place the measurement-value section in the scroll area.
            fill="x",
            padx=5,
            pady=4
        )

        self.label_um = ctk.CTkLabel(
        # Create the distance display in micrometers.
            self.frame,
            text="Distance: 0.000 µm",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_um.pack(pady=0)
        # Place the distance display in the measurement section.

        self.label_ps = ctk.CTkLabel(
        # Create the optical time-delay display.
            self.frame,
            text="Time Delay: 0.0000 ps",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.label_ps.pack(pady=0)
        # Place the time-delay display under the distance display.

        self.label_intensity = ctk.CTkLabel(
        # Create the live intensity display.
            self.frame,
            text="Intensity: 0.00",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_intensity.pack(pady=0)
        # Place the intensity display with the measurement values.

        self.label_thresholds = ctk.CTkLabel(
        # Create the display for dark and bright thresholds.
            self.frame,
            text="Thresholds: waiting",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )

        self.label_thresholds.pack(pady=0)
        # Place the threshold display under the intensity display.

        self.label_accumulated_fringes = ctk.CTkLabel(
        # Create the accumulated fringe-count display.
            self.frame,
            text="Accumulated Fringes Count: 0",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_accumulated_fringes.pack(pady=0)
        # Place the fringe-count display in the measurement section.

        self.compare_frame = ctk.CTkFrame(
        # Create the distance-comparison section.
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.compare_frame.pack(
        # Place the comparison section in the scroll area.
            fill="x",
            padx=5,
            pady=4
        )

        ctk.CTkLabel(
        # Add a visible text label to the current UI section.
            self.compare_frame,
            text="Distance Comparison",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=0)
        # Place this UI element in the window layout.

        self.label_compare_driven = ctk.CTkLabel(
        # Create the display for physically driven stage distance.
            self.compare_frame,
            text="Driven: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.label_compare_driven.pack(pady=0)
        # Place the driven-distance display in the comparison section.

        self.label_compare_calculated = ctk.CTkLabel(
        # Create the display for fringe-calculated distance.
            self.compare_frame,
            text="Calculated: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )

        self.label_compare_calculated.pack(pady=0)
        # Place the calculated-distance display below the driven distance.

        self.label_compare_difference = ctk.CTkLabel(
        # Create the display for the distance difference.
            self.compare_frame,
            text="Difference: 0.000000 mm",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_compare_difference.pack(pady=0)
        # Place the difference display below the two compared distances.

        self.live_size = (320, 220)
        # Set the size used for the live camera preview.

        ctk.CTkLabel(
        # Add a visible text label to the current UI section.
            self.scroll,
            text="Live Camera",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 2))
        # Place this UI element in the window layout.

        self.image_label = ctk.CTkLabel(
        # Create the placeholder area for the live camera image.
            self.scroll,
            text="No Image",
            width=self.live_size[0],
            height=self.live_size[1],
            fg_color="#111111",
            text_color="white"
        )

        self.image_label.pack(pady=5)
        # Place the live camera image area in the window.

        self.update_comparison_labels()
        # Fill the comparison display with the current start values.

        self.update_stage_position_once()
        # Show the current stage position immediately after startup.

    # -----------------------------------------------------------------------------
    # 4.1 START OR STOP MONITORING
    # The monitoring button either starts calibration/measurement or stops the running system.
    # -----------------------------------------------------------------------------
    def toggle(self):

        if not self.is_monitoring:
        # Stop calibration movement if monitoring was stopped.

            if not self.camera_connected:
            # Stop the start process if no camera is available.

                self.status.configure(
                # Tell the user what the program is currently doing or why an action was refused.
                    text="Camera not connected",
                    text_color=RED_COLOR
                )

                return
                # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

            self.disable_lock(update_status=False)
            # Clear any previous lock state before starting a fresh measurement.

            self.restart_values_only()
            # Clear old measurement values before the new run begins.

            self.is_monitoring = True
            # Start the camera-processing loop; the background measurement loop below will keep running while this value stays True.

            if MANUAL_THRESHOLDS:
            # Use fixed threshold values when manual mode is enabled.

                self.dark_threshold = (
                # Place the dark threshold near the low end of the calibrated signal.
                    MANUAL_DARK_THRESHOLD
                )

                self.bright_threshold = (
                # Place the bright threshold below the high end of the calibrated signal.
                    MANUAL_BRIGHT_THRESHOLD
                )

                self.label_thresholds.configure(
                # Update the displayed calibration thresholds.
                    text=(
                        f"Manual Dark: "
                        f"{self.dark_threshold:.2f} | "
                        f"Manual Bright: "
                        f"{self.bright_threshold:.2f}"
                    )
                )

                self.status.configure(
                # Tell the user what the program is currently doing or why an action was refused.
                    text="Monitoring running",
                    text_color=GREEN_COLOR
                )

            else:
            # Continue with the normal path for this case because the special case above does not apply.

                self.calibrating = True
                # Enter calibration mode to collect threshold data.

                self.calibration_values = []
                # Start collecting fresh calibration intensities.

                self.calibration_start_time = time.time()
                # Remember when threshold calibration started.

                self.status.configure(
                # Tell the user what the program is currently doing or why an action was refused.
                    text="Calibrating thresholds...",
                    text_color=ORANGE_COLOR
                )

            self.btn.configure(
            # Update the monitoring button to match the current monitoring state.
                text="STOP MONITORING",
                fg_color=RED_COLOR
            )

            threading.Thread(
            # Start the long-running movement or camera work in the background so the window can still update and react.
                target=self.loop,
                daemon=True
            ).start()
            # Begin the background worker that will monitor movement or process frames while the UI stays responsive.

        else:
        # Continue with the normal path for this case because the special case above does not apply.

            self.is_monitoring = False
            # Start with the camera measurement loop stopped.

            if self.stage_connected:
            # Handle this state before continuing so the measurement and stage control stay consistent.
                self.stage.stop()
                # Stop any current stage motion.

            self.disable_lock(update_status=False)
            # Clear any previous lock state before starting a fresh measurement.

            self.btn.configure(
            # Update the monitoring button to match the current monitoring state.
                text="START MONITORING",
                fg_color=TEXT_COLOR
            )

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Stopped",
                text_color=TEXT_COLOR
            )

    # -----------------------------------------------------------------------------
    # 4.2 RESET BUTTON ENTRY POINT
    # The visible reset button is routed to the measurement-value reset routine.
    # -----------------------------------------------------------------------------
    def restart(self):

        self.restart_values_only()
        # Clear old measurement values before the new run begins.

    # -----------------------------------------------------------------------------
    # 4.3 RESET MEASUREMENT STATE
    # Fringe counters, detector state, calibration data, and comparison values are cleared.
    # -----------------------------------------------------------------------------
    def restart_values_only(self):

        self.accumulated_fringes = 0
        # Clear the fringe counter.

        self.was_dark = False
        # Clear the remembered dark phase so the next fringe count requires a fresh dark-to-bright transition.

        self.last_count_time = 0
        # Start with no previous fringe timestamp.

        self.dark_counter = 0
        # Reset the dark-frame streak so a new stable dark phase must be detected from scratch.

        self.bright_counter = 0
        # Reset the bright-frame streak so a new stable bright phase must be detected from scratch.

        self.intensity_history = []
        # Clear old intensity samples so smoothing starts from the current measurement state.

        self.calibrating = False
        # Leave calibration mode and begin normal fringe counting.
        self.calibration_motion_started = False
        # Allow calibration movement to start again on the next run.

        self.calibration_values = []
        # Start collecting fresh calibration intensities.

        self.reset_stage_movement_tracking()
        # Reset the software counter for driven stage travel.

        self.reset_measurement_after_calibration()
        # Reset fringe-based distance and delay displays.

        if hasattr(self, "label_compare_driven"):
        # Update comparison labels only after the comparison UI exists.

            self.update_comparison_labels(0.0)
            # Show zero driven distance in the comparison display.

    # -----------------------------------------------------------------------------
    # 5.1 MOVE STAGE TO AN ABSOLUTE POSITION
    # This is the central direct stage movement routine.
    # -----------------------------------------------------------------------------
    def start_stage_move_to(
        self,
        target_mm,
        start_pos=None,
        reset_after_move=False
    ):

        if not self.stage_connected:
        # Refuse movement commands when the stage connection failed, because the program cannot safely control hardware.

            if reset_after_move:
            # Handle the special return-after-calibration case.

                self.reset_stage_after_calibration()
                # Finish the calibration reset in software when no stage movement can happen.

                return
                # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Stage not connected",
                text_color=RED_COLOR
            )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if self.lock_active and not reset_after_move:
        # Block user stage moves while the position lock is active.

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Unlock before moving stage",
                text_color=ORANGE_COLOR
            )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if self.stage.is_moving:
        # Refuse a new movement while the stage is busy so two commands do not fight each other.

            if reset_after_move:
            # Handle the special return-after-calibration case.

                self.center_stage_after_calibration_pending = True
                # Remember that the stage should return to zero after the current movement finishes.

                self.status.configure(
                # Tell the user what the program is currently doing or why an action was refused.
                    text=(
                        "Calibration done - stage returns to "
                        "0.00000000000 mm after current move"
                    ),
                    text_color=ORANGE_COLOR
                )

            else:
            # Continue with the normal path for this case because the special case above does not apply.

                self.status.configure(
                # Tell the user what the program is currently doing or why an action was refused.
                    text="Stage is already moving",
                    text_color=ORANGE_COLOR
                )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if start_pos is None:
        # Use the current hardware position when no start position was provided.

            start_pos = self.stage.get_position()
            # Read the current stage position so it can be used as the movement start, reference, or drift value.

        target_mm = self.stage.clamp_position(target_mm)
        # Limit the target to the allowed travel range before any movement command is sent to the stage.

        move_mm = target_mm - start_pos
        # Calculate the requested travel distance; this decides whether a physical movement is needed at all.

        self.stage_start_position = start_pos
        # Save the start position so live movement tracking can measure how far this move has traveled.
        self.stage_movement_before_move = self.total_stage_movement
        # Save the movement total from before this move so the UI can add the new travel on top of it.
        self.reset_stage_movement_after_move = reset_after_move
        # Save whether this movement is a calibration-return move so the stage UI loop can reset values afterward.

        if abs(move_mm) < 1e-12:
        # Treat tiny calculated movement as zero so floating-point rounding does not trigger unnecessary stage motion.

            if reset_after_move:
            # Handle the special return-after-calibration case.

                self.reset_stage_after_calibration(start_pos)
                # Complete the calibration-reset cleanup immediately because the stage is already at the return position.

                return
                # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

            else:
            # Continue with the normal path for this case because the special case above does not apply.

                self.update_stage_labels(start_pos, 0.0)
                # Refresh the stage display while recording zero new travel because the stage was already at the target.

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Stage already at target",
                text_color=TEXT_COLOR
            )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if not self.stage.move_absolute(target_mm):
        # Send the actual movement command to the stage; if the controller rejects it, clean up the pending movement state.

            self.reset_stage_movement_after_move = False
            # Cancel the planned after-move reset because there will be no stage-ui loop completion event for a failed move.

            if reset_after_move:
            # Handle the special return-after-calibration case.

                self.reset_stage_after_calibration(start_pos)
                # Complete the calibration-reset cleanup immediately because the stage is already at the return position.

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        self.status.configure(
        # Tell the user what the program is currently doing or why an action was refused.
            text=f"Stage moving to {target_mm:.6f} mm",
            text_color=TEXT_COLOR
        )

        threading.Thread(
        # Start the long-running movement or camera work in the background so the window can still update and react.
            target=self.stage_ui_loop,
            daemon=True
        ).start()
        # Begin the background worker that will monitor movement or process frames while the UI stays responsive.

    # -----------------------------------------------------------------------------
    # 5.2 MOVE STAGE BY A RELATIVE DISTANCE
    # A relative distance is converted into an absolute target.
    # -----------------------------------------------------------------------------
    def start_stage_move_by(self, move_mm):

        start_pos = self.stage.get_position()
        # Read the current stage position so it can be used as the movement start, reference, or drift value.

        self.start_stage_move_to(
        # Reuse the central movement routine so all safety checks and tracking updates happen the same way.
            start_pos + move_mm,
            start_pos=start_pos
        )

    # -----------------------------------------------------------------------------
    # 5.3 PREPARE STEPPED MOVEMENT TO A TARGET
    # The target is checked and then a background worker performs small steps.
    # -----------------------------------------------------------------------------
    def start_stage_move_to_stepped(self, target_mm):

        if not self.stage_connected:
        # Refuse movement commands when the stage connection failed, because the program cannot safely control hardware.
            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if self.lock_active:
        # Refuse manual stepped movement while lock is active, because the lock is supposed to hold one position.
            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Unlock before moving stage",
                text_color=ORANGE_COLOR
            )
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if self.stage.is_moving:
        # Refuse a new movement while the stage is busy so two commands do not fight each other.
            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Stage is already moving",
                text_color=ORANGE_COLOR
            )
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        start_pos = self.stage.get_position()
        # Read the current stage position so it can be used as the movement start, reference, or drift value.
        target_mm = self.stage.clamp_position(target_mm)
        # Limit the target to the allowed travel range before any movement command is sent to the stage.

        if abs(target_mm - start_pos) < 1e-12:
        # Skip the step worker when the current position already matches the requested target.
            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Stage already at target",
                text_color=TEXT_COLOR
            )
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        self.stage_start_position = start_pos
        # Save the start position so live movement tracking can measure how far this move has traveled.
        self.stage_movement_before_move = self.total_stage_movement
        # Save the movement total from before this move so the UI can add the new travel on top of it.

        threading.Thread(
        # Start the long-running movement or camera work in the background so the window can still update and react.
            target=self.stage_stepped_move_worker,
            args=(start_pos, target_mm),
            daemon=True
        ).start()
        # Begin the background worker that will monitor movement or process frames while the UI stays responsive.

    # -----------------------------------------------------------------------------
    # 5.4 PREPARE RELATIVE STEPPED MOVEMENT
    # A relative stepped movement is converted into a stepped target movement.
    # -----------------------------------------------------------------------------
    def start_stage_move_by_steps(self, move_mm):

        start_pos = self.stage.get_position()
        # Read the current stage position so it can be used as the movement start, reference, or drift value.
        self.start_stage_move_to_stepped(
        # Reuse the stepped movement routine so relative and absolute step moves share the same safety checks.
            start_pos + move_mm
        )

    # -----------------------------------------------------------------------------
    # 5.5 EXECUTE STEPPED MOVEMENT
    # The stage is moved step by step with short pauses between steps.
    # -----------------------------------------------------------------------------
    def stage_stepped_move_worker(self, start_pos, target_mm):

        step_mm = self.get_step_size()
        # Use the step size selected in the UI.
        delay_s = 0.25
        # Pause briefly between individual stage steps.
        direction = 1 if target_mm > start_pos else -1
        # Choose the movement direction toward the target.
        current_pos = start_pos
        # Track the current position inside the step loop.
        remaining = abs(target_mm - start_pos)
        # Track the distance still left to move.
        moved = 0.0
        # Start the moved-distance counter for this stepped move.

        self.status.configure(
        # Tell the user what the program is currently doing or why an action was refused.
            text=(
                f"Moving to {target_mm:.6f} mm in {step_mm:.6f} mm steps"
            ),
            text_color=TEXT_COLOR
        )

        while remaining > 1e-12:
        # Continue stepping until the target is reached within numerical tolerance.
            next_step = min(step_mm, remaining)
            # Use a full step unless only a smaller final step remains.
            next_target = current_pos + direction * next_step
            # Calculate the next intermediate stage position.

            if not self.stage.move_absolute(next_target):
            # Move to the next intermediate target and stop if that command fails.
                self.status.configure(
                # Tell the user what the program is currently doing or why an action was refused.
                    text="Stage move failed",
                    text_color=RED_COLOR
                )
                return
                # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

            while self.stage.is_moving:
            # Wait until the current stage step has finished.
                time.sleep(0.01)
                # Pause briefly so hardware state can settle before checking again.

            step_distance = abs(next_target - current_pos)
            # Measure how far this step moved.
            moved += step_distance
            # Add this step to the movement total for the stepped move.
            current_pos = next_target
            # Use the reached intermediate target as the new current position.
            remaining = abs(target_mm - current_pos)
            # Recalculate how much distance is still left.

            self.total_stage_movement = (
            # Store the final accumulated movement after the stage stops.
                self.stage_movement_before_move + moved
            )

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                lambda p=current_pos, m=moved, b=self.stage_movement_before_move: # Use the captured value for the scheduled UI update.
                self.update_stage_labels(p, m, b)
            )

            if remaining > 1e-12:
            # Handle this state before continuing so the measurement and stage control stay consistent.
                time.sleep(delay_s)
                # Wait before the next step so motion and measurement remain stable.

        self.after(
        # Queue the display update safely from background work so the visible UI reflects the newest state.
            0,
            lambda: # Use the captured value for the scheduled UI update.
            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text=f"Reached {current_pos:.6f} mm",
                text_color=GREEN_COLOR
            )
        )

    # -----------------------------------------------------------------------------
    # 5.6 READ STEP SIZE FROM THE UI
    # The stage step size is read from the input field and made usable for movement.
    # -----------------------------------------------------------------------------
    def get_step_size(self):

        try:
        # Try to parse the user input as a number; invalid text is handled by the ValueError branch below.
            value = float(
            # Convert the step-size input into a number.
                self.step_entry.get().replace(",", ".")
            )
            return abs(value)
            # Use a positive step size even if the user entered a negative value.
        except ValueError:
            return 0.0001
            # Use a safe default step size when the input is invalid.

    # -----------------------------------------------------------------------------
    # 5.7 CALCULATE FRINGE DISTANCE
    # The selected wavelength determines how much stage movement corresponds to one fringe.
    # -----------------------------------------------------------------------------
    def compute_fringe_distance(self, wavelength_nm):

        return (wavelength_nm / 2) / 1_000_000 / 2
        # Convert the wavelength into the stage distance represented by one fringe.

    # -----------------------------------------------------------------------------
    # 5.8 APPLY A NEW LASER WAVELENGTH
    # A changed wavelength updates the fringe distance and the suggested step size.
    # -----------------------------------------------------------------------------
    def apply_wavelength(self):

        try:
        # Try to parse the user input as a number; invalid text is handled by the ValueError branch below.
            wavelength_nm = float(
            # Convert the wavelength input into a number.
                self.wavelength_entry.get().replace(",", ".")
            )
        except ValueError:
            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Invalid wavelength value",
                text_color=RED_COLOR
            )
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        self.laser_wavelength_nm = wavelength_nm
        # Store the newly selected laser wavelength.
        self.fringe_distance_mm = self.compute_fringe_distance(
        # Calculate the current distance per fringe from the wavelength.
            self.laser_wavelength_nm
        )

        default_step = self.fringe_distance_mm / 4
        # Suggest a step size based on the updated fringe distance.
        self.step_entry.delete(0, "end")
        # Clear the old suggested step size.
        self.step_entry.insert(
        # Show the new suggested step size.
            0,
            f"{default_step:.7f}"
        )

        self.status.configure(
        # Tell the user what the program is currently doing or why an action was refused.
            text=f"Wavelength set to {self.laser_wavelength_nm:.1f} nm",
            text_color=GREEN_COLOR
        )

    # -----------------------------------------------------------------------------
    # 5.9 STAGE BUTTON ACTIONS
    # Small helper methods connect UI buttons to stage movement routines.
    # -----------------------------------------------------------------------------
    def move_to_min(self):

        self.start_stage_move_to(
        # Reuse the central movement routine so all safety checks and tracking updates happen the same way.
            self.stage.min_position
        )

    def step_negative(self):

        self.start_stage_move_by(
            -self.get_step_size()
        )

    def move_to_center(self):

        self.start_stage_move_to(
        # Reuse the central movement routine so all safety checks and tracking updates happen the same way.
            0.0
        )

    def step_positive(self):

        self.start_stage_move_by(
            self.get_step_size()
        )

    def move_to_max(self):

        self.start_stage_move_to(
        # Reuse the central movement routine so all safety checks and tracking updates happen the same way.
            self.stage.max_position
        )

    def move_to_target_by_steps(self):

        try:
        # Try to parse the user input as a number; invalid text is handled by the ValueError branch below.
            target_mm = float(
            # Read the target position from the input field as a number; commas are accepted as decimal separators before conversion.
                self.target_entry.get().replace(",", ".")
            )
        except ValueError:
            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Invalid target value",
                text_color=RED_COLOR
            )
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        self.start_stage_move_to_stepped(target_mm)

    def move_distance_by_steps(self):

        try:
        # Try to parse the user input as a number; invalid text is handled by the ValueError branch below.
            distance_mm = float(
            # Read the relative movement distance from the input field as a number; this becomes a signed stage travel command.
                self.target_entry.get().replace(",", ".")
            )
        except ValueError:
            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Invalid distance value",
                text_color=RED_COLOR
            )
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        self.start_stage_move_by_steps(distance_mm)

    def stop_stage(self):

        self.stage.stop()
        # Stop any current stage motion.

    # -----------------------------------------------------------------------------
    # 6.1 ENABLE OR DISABLE POSITION LOCK
    # The current stage position can be stored as the position that should be held.
    # -----------------------------------------------------------------------------
    def toggle_lock(self):

        if self.lock_active:
        # Refuse manual stepped movement while lock is active, because the lock is supposed to hold one position.

            self.disable_lock()

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if not self.is_monitoring:
        # Stop calibration movement if monitoring was stopped.

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Start monitoring before locking",
                text_color=ORANGE_COLOR
            )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if not self.stage_connected:
        # Refuse movement commands when the stage connection failed, because the program cannot safely control hardware.

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Stage not connected",
                text_color=RED_COLOR
            )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if self.calibrating or self.returning_stage_after_calibration:
        # Do not enable the lock while threshold calibration is active or while the stage is returning after calibration.

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Wait until calibration is done",
                text_color=ORANGE_COLOR
            )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if self.stage.is_moving:
        # Refuse a new movement while the stage is busy so two commands do not fight each other.

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Stage is already moving",
                text_color=ORANGE_COLOR
            )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        self.lock_position_mm = self.stage.get_position()
        # Store the current stage position as the lock target.
        self.lock_reference_fringes = self.accumulated_fringes
        # Remember the fringe count at the moment lock starts.
        self.lock_last_correction_time = 0
        # Allow the first lock correction immediately after lock starts.
        self.lock_correction_active = False
        # Mark that no lock correction is currently running, so future correction checks can start a new one if needed.
        self.lock_active = True
        # Enable the position lock.
        self.was_dark = False
        # Clear the remembered dark phase so the next fringe count requires a fresh dark-to-bright transition.
        self.dark_counter = 0
        # Reset the dark-frame streak so a new stable dark phase must be detected from scratch.
        self.bright_counter = 0
        # Reset the bright-frame streak so a new stable bright phase must be detected from scratch.
        self.intensity_history = []
        # Clear old intensity samples so smoothing starts from the current measurement state.
        self.last_count_time = time.time()
        # Restart the fringe cooldown timer after changing lock state.

        self.btn_lock.configure(
        # Update the lock button to match the current lock state.
            text="UNLOCK",
            fg_color=GREEN_COLOR
        )

        self.label_lock_status.configure(
        # Update the lock status display.
            text=f"Lock: {self.lock_position_mm:.6f} mm",
            text_color=GREEN_COLOR
        )

        self.status.configure(
        # Tell the user what the program is currently doing or why an action was refused.
            text=f"Lock active at {self.lock_position_mm:.6f} mm",
            text_color=GREEN_COLOR
        )

    # -----------------------------------------------------------------------------
    # 6.2 CLEAR POSITION LOCK
    # Lock state, correction state, and lock UI are returned to the unlocked state.
    # -----------------------------------------------------------------------------
    def disable_lock(self, update_status=True):

        was_correcting = self.lock_correction_active
        # Remember whether a lock correction is being interrupted.

        self.lock_active = False
        # Disable the position lock.
        self.lock_correction_active = False
        # Mark that no lock correction is currently running, so future correction checks can start a new one if needed.

        if was_correcting and self.stage_connected:
        # Stop the stage if unlocking interrupts an active correction.

            self.stage.stop()
            # Stop any current stage motion.

        if hasattr(self, "btn_lock"):
        # Update the lock button only after it exists; this avoids errors during early startup or reset calls.

            self.btn_lock.configure(
            # Update the lock button to match the current lock state.
                text="LOCK",
                fg_color=TEXT_COLOR
            )

        if hasattr(self, "label_lock_status"):
        # Update the lock status label only after it exists in the UI.

            self.label_lock_status.configure(
            # Update the lock status display.
                text="Lock: off",
                text_color=TEXT_COLOR
            )

        if update_status:
        # Show the "Lock off" message only when the caller wants a visible status update.

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Lock off",
                text_color=TEXT_COLOR
            )

    # -----------------------------------------------------------------------------
    # 6.3 LOCK TOLERANCE
    # Very small drift is ignored so the stage is not constantly corrected.
    # -----------------------------------------------------------------------------
    def lock_deadband_mm(self):

        return max(
        # Use the larger of fringe-based tolerance and a small absolute minimum.
            self.fringe_distance_mm / 8,
            1e-7
        )

    # -----------------------------------------------------------------------------
    # 6.4 CHECK WHETHER LOCK CORRECTION IS NEEDED
    # After a counted fringe, the current stage position is compared to the lock position.
    # -----------------------------------------------------------------------------
    def handle_lock_after_fringe(self):

        if not self.lock_active:
        # Skip lock correction logic when lock is off.
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if (
        # Skip correction while hardware or measurement state is busy; lock correction should only run in a stable state.
            not self.stage_connected
            # Do not correct lock drift without stage access.
            or self.calibrating
            # Do not correct lock drift during threshold calibration.
            or self.returning_stage_after_calibration
            # Do not correct lock drift while the stage is returning after calibration.
            or self.lock_correction_active
            # Do not start another correction while one is already running.
            or self.stage.is_moving
            # Do not start lock correction while another movement is active.
        ):
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        now = time.time()
        # Read the current time for the lock correction cooldown.

        if (
        # Skip correction while hardware or measurement state is busy; lock correction should only run in a stable state.
            now - self.lock_last_correction_time
            # Measure time since the last lock correction.
        ) < LOCK_CORRECTION_COOLDOWN:
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        current_pos = self.stage.get_position()
        # Read the actual stage position for drift detection.
        drift_mm = current_pos - self.lock_position_mm
        # Calculate how far the stage is from the locked position.

        if abs(drift_mm) < self.lock_deadband_mm():
        # Treat tiny drift as acceptable and avoid moving the stage.

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                lambda d=drift_mm: # Use the captured value for the scheduled UI update.
                self.label_lock_status.configure(
                # Update the lock status display.
                    text=f"Lock: no qPOS drift ({d:+.6f} mm)",
                    text_color=GREEN_COLOR
                )
            )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        self.lock_last_correction_time = now
        # Record when this lock correction starts.
        self.lock_correction_active = True
        # Mark that a lock correction is now in progress.

        if not self.stage.move_absolute(self.lock_position_mm):
        # Send the stage back to the locked position and handle failure.

            self.lock_correction_active = False
            # Mark that no lock correction is currently running, so future correction checks can start a new one if needed.

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                lambda: # Use the captured value for the scheduled UI update.
                self.status.configure(
                # Tell the user what the program is currently doing or why an action was refused.
                    text="Lock correction failed",
                    text_color=RED_COLOR
                )
            )

            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        self.after(
        # Queue the display update safely from background work so the visible UI reflects the newest state.
            0,
            lambda d=drift_mm: # Use the captured value for the scheduled UI update.
            self.label_lock_status.configure(
            # Update the lock status display.
                text=f"Lock correcting ({d:+.6f} mm)",
                text_color=ORANGE_COLOR
            )
        )

        self.after(
        # Queue the display update safely from background work so the visible UI reflects the newest state.
            0,
            lambda d=drift_mm: # Use the captured value for the scheduled UI update.
            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text=f"Lock correcting drift {d:+.6f} mm",
                text_color=ORANGE_COLOR
            )
        )

        threading.Thread(
        # Start the long-running movement or camera work in the background so the window can still update and react.
            target=self.lock_correction_ui_loop,
            daemon=True
        ).start()
        # Begin the background worker that will monitor movement or process frames while the UI stays responsive.

    # -----------------------------------------------------------------------------
    # 6.5 FOLLOW THE LOCK CORRECTION MOVEMENT
    # The position display is updated while the stage returns to the lock position.
    # -----------------------------------------------------------------------------
    def lock_correction_ui_loop(self):

        while self.stage.is_moving:
        # Wait until the current stage step has finished.

            pos = self.stage.get_position()
            # Read the stage position for display or completion checks.

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                lambda p=pos: # Use the captured value for the scheduled UI update.
                self.label_stage_position.configure(
                # Update the displayed stage position.
                    text=f"Stage Position: {p:.6f} mm"
                )
            )

            time.sleep(0.05)
            # Pause briefly so hardware state can settle before checking again.

        pos = self.stage.get_position()
        # Read the stage position for display or completion checks.
        remaining_mm = pos - self.lock_position_mm
        # Measure remaining error after the lock correction finished.
        self.lock_correction_active = False
        # Mark that no lock correction is currently running, so future correction checks can start a new one if needed.

        self.after(
        # Queue the display update safely from background work so the visible UI reflects the newest state.
            0,
            lambda p=pos, r=remaining_mm: # Use the captured value for the scheduled UI update.
            self.finish_lock_correction(p, r)
        )

    # -----------------------------------------------------------------------------
    # 6.6 FINISH LOCK CORRECTION
    # The lock display is updated and the fringe detector is reset after correction.
    # -----------------------------------------------------------------------------
    def finish_lock_correction(self, pos, remaining_mm):

        self.label_stage_position.configure(
        # Update the displayed stage position.
            text=f"Stage Position: {pos:.6f} mm"
        )

        self.was_dark = False
        # Clear the remembered dark phase so the next fringe count requires a fresh dark-to-bright transition.
        self.dark_counter = 0
        # Reset the dark-frame streak so a new stable dark phase must be detected from scratch.
        self.bright_counter = 0
        # Reset the bright-frame streak so a new stable bright phase must be detected from scratch.
        self.intensity_history = []
        # Clear old intensity samples so smoothing starts from the current measurement state.
        self.last_count_time = time.time()
        # Restart the fringe cooldown timer after changing lock state.

        if not self.lock_active:
        # Skip lock correction logic when lock is off.
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        if abs(remaining_mm) <= self.lock_deadband_mm():
        # Treat the lock correction as successful when the remaining error is within tolerance.

            self.label_lock_status.configure(
            # Update the lock status display.
                text=f"Lock: {self.lock_position_mm:.6f} mm",
                text_color=GREEN_COLOR
            )

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Lock correction done",
                text_color=GREEN_COLOR
            )

        else:
        # Continue with the normal path for this case because the special case above does not apply.

            self.label_lock_status.configure(
            # Update the lock status display.
                text=f"Lock residual: {remaining_mm:+.6f} mm",
                text_color=ORANGE_COLOR
            )

            self.status.configure(
            # Tell the user what the program is currently doing or why an action was refused.
                text="Lock correction has residual drift",
                text_color=ORANGE_COLOR
            )

    # -----------------------------------------------------------------------------
    # 7.1 TRACK NORMAL STAGE MOVEMENT
    # Position, moved distance, and comparison labels are refreshed while the stage moves.
    # -----------------------------------------------------------------------------
    def stage_ui_loop(self):

        movement_base = self.stage_movement_before_move
        # Use the pre-move total as the base for live movement tracking.

        while self.stage.is_moving:
        # Wait until the current stage step has finished.

            pos = self.stage.get_position()
            # Read the stage position for display or completion checks.

            moved = abs(pos - self.stage_start_position)
            # Calculate movement completed since this move started.

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                lambda p=pos, m=moved, b=movement_base: # Use the captured value for the scheduled UI update.
                self.update_stage_labels(p, m, b)
            )

            time.sleep(0.05)
            # Pause briefly so hardware state can settle before checking again.

        pos = self.stage.get_position()
        # Read the stage position for display or completion checks.

        moved = abs(pos - self.stage_start_position)
        # Calculate movement completed since this move started.
        self.total_stage_movement = (
        # Store the final accumulated movement after the stage stops.
            movement_base + moved
        )

        if self.reset_stage_movement_after_move:
        # Run the calibration reset path after the return movement completes.

            self.reset_stage_movement_after_move = False
            # Cancel the planned after-move reset because there will be no stage-ui loop completion event for a failed move.

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                lambda p=pos: # Use the captured value for the scheduled UI update.
                self.reset_stage_after_calibration(p)
            )

        else:
        # Continue with the normal path for this case because the special case above does not apply.

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                lambda p=pos, m=moved, b=movement_base: # Use the captured value for the scheduled UI update.
                self.update_stage_labels(p, m, b)
            )

        if self.center_stage_after_calibration_pending:
        # Start the postponed return-to-zero move after the current move finishes.

            self.center_stage_after_calibration_pending = False
            # Start without a postponed centering move.

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                self.move_to_center_after_calibration
            )

    # -----------------------------------------------------------------------------
    # 7.2 SHOW INITIAL STAGE POSITION
    # The UI is filled with the current stage position after startup.
    # -----------------------------------------------------------------------------
    def update_stage_position_once(self):

        if self.stage_connected:
        # Handle this state before continuing so the measurement and stage control stay consistent.

            pos = self.stage.get_position()
            # Read the stage position for display or completion checks.

            self.label_stage_position.configure(
            # Update the displayed stage position.
                text=f"Stage Position: {pos:.6f} mm"
            )

    # -----------------------------------------------------------------------------
    # 7.3 UPDATE STAGE MOVEMENT DISPLAY
    # Stage position and accumulated movement are written into the UI.
    # -----------------------------------------------------------------------------
    def update_stage_labels(self, pos, moved, movement_base=None):

        if movement_base is None:
        # If no movement baseline was passed in, continue from the current accumulated movement total.
            movement_base = self.total_stage_movement
            # Use the current accumulated movement as the baseline when no explicit baseline was provided.

        current_total_stage_movement = (
        # Combine previous movement and current movement for the display.
            movement_base + abs(moved)
            # Calculate a bounded or positive value needed for movement or comparison.
        )
        self.current_stage_movement_for_compare = (
        # Store the driven distance used by the comparison display.
            current_total_stage_movement
        )

        self.label_stage_position.configure(
        # Update the displayed stage position.
            text=f"Stage Position: {pos:.6f} mm"
        )

        self.label_stage_moved.configure(
        # Update the displayed accumulated stage movement.
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
    # The software movement counter is set back to zero.
    # -----------------------------------------------------------------------------
    def reset_stage_movement_tracking(self, pos=None):

        self.total_stage_movement = 0.0
        # Start accumulated stage travel at zero.
        self.stage_movement_before_move = 0.0
        # Start the movement baseline at zero.
        self.current_stage_movement_for_compare = 0.0
        # Start the driven-distance comparison value at zero.

        if pos is not None:
        # Use the provided position as the new stage reference when available.
            self.stage_reference_position = pos
            # Use the provided position as the new software reference so the display matches the known stage position.
            self.label_stage_position.configure(
            # Update the displayed stage position.
                text=f"Stage Position: {pos:.6f} mm"
            )
        elif self.stage_connected:
        # Use the actual hardware position as reference when the stage is connected.
            self.stage_reference_position = self.stage.get_position()
            # Record the current hardware position as the movement reference.
        else:
        # Continue with the normal path for this case because the special case above does not apply.
            self.stage_reference_position = 0.0
            # Prepare the reference position used for movement tracking.

        self.label_stage_moved.configure(
        # Update the displayed accumulated stage movement.
            text="Accumulated Movement: 0.000000 mm"
        )

        self.update_comparison_labels(0.0)
        # Show zero driven distance in the comparison display.

    # -----------------------------------------------------------------------------
    # 7.5 RESET FRINGE MEASUREMENT DISPLAY
    # The fringe-based distance and delay display are returned to zero.
    # -----------------------------------------------------------------------------
    def reset_measurement_after_calibration(self):

        self.accumulated_fringes = 0
        # Clear the fringe counter.
        self.was_dark = False
        # Clear the remembered dark phase so the next fringe count requires a fresh dark-to-bright transition.
        self.last_count_time = 0
        # Start with no previous fringe timestamp.
        self.dark_counter = 0
        # Reset the dark-frame streak so a new stable dark phase must be detected from scratch.
        self.bright_counter = 0
        # Reset the bright-frame streak so a new stable bright phase must be detected from scratch.
        self.intensity_history = []
        # Clear old intensity samples so smoothing starts from the current measurement state.

        self.label_um.configure(
        # Update the displayed distance in micrometers.
            text="Distance: 0.000 µm"
        )

        self.label_ps.configure(
        # Update the displayed time delay.
            text="Time Delay: 0.0000 ps"
        )

        self.label_accumulated_fringes.configure(
        # Update the displayed fringe count.
            text="Accumulated Fringes Count: 0"
        )

        self.update_comparison_labels(0.0)
        # Show zero driven distance in the comparison display.

    # -----------------------------------------------------------------------------
    # 7.6 START RETURN AFTER CALIBRATION
    # After threshold calibration, the stage is asked to return to zero.
    # -----------------------------------------------------------------------------
    def finish_calibration_stage_reset(self):

        self.returning_stage_after_calibration = True
        # Mark that the stage is returning after calibration.

        self.status.configure(
        # Tell the user what the program is currently doing or why an action was refused.
            text="Calibration done - stage returning to 0.00000000000 mm",
            text_color=ORANGE_COLOR
        )

        self.start_stage_move_to(
        # Reuse the central movement routine so all safety checks and tracking updates happen the same way.
            0.0,
            reset_after_move=True
        )

    # -----------------------------------------------------------------------------
    # 7.7 MOVE STAGE DURING CALIBRATION
    # The stage moves forward and back so the threshold calibration sees changing intensity.
    # -----------------------------------------------------------------------------
    def calibration_stage_motion(self):

        if not self.stage_connected:
        # Refuse movement commands when the stage connection failed, because the program cannot safely control hardware.
            return
            # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

        start_pos = self.stage.get_position()
        # Read the current stage position so it can be used as the movement start, reference, or drift value.
        step_mm = 0.0001
        # Use small calibration steps to sweep the signal gently.
        steps = 4
        # Use four steps in each calibration direction.

        # Move forward so calibration samples changing intensity.
        for i in range(1, steps + 1):
        # Repeat the calibration movement for the planned step positions.
            if not self.is_monitoring:
            # Stop calibration movement if monitoring was stopped.
                return
                # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

            target = start_pos + step_mm * i
            # Calculate the next calibration position.
            target = self.stage.clamp_position(target)
            # Keep this intermediate value so the following measurement or movement update uses the correct state.

            if not self.stage.move_absolute(target):
            # Handle this state before continuing so the measurement and stage control stay consistent.
                return
                # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

            while self.stage.is_moving and self.is_monitoring:
            # Wait for calibration motion while monitoring is still active.
                time.sleep(0.01)
                # Pause briefly so hardware state can settle before checking again.

            time.sleep(0.25)
            # Pause briefly so hardware state can settle before checking again.

        # Move back so the stage returns toward the start position after sampling.
        for i in range(steps - 1, -1, -1):
        # Repeat the calibration movement for the planned step positions.
            if not self.is_monitoring:
            # Stop calibration movement if monitoring was stopped.
                return
                # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

            target = start_pos + step_mm * i
            # Calculate the next calibration position.
            target = self.stage.clamp_position(target)
            # Keep this intermediate value so the following measurement or movement update uses the correct state.

            if not self.stage.move_absolute(target):
            # Handle this state before continuing so the measurement and stage control stay consistent.
                return
                # Stop this routine here because the current branch has already handled the situation and no later movement/measurement code should run.

            while self.stage.is_moving and self.is_monitoring:
            # Wait for calibration motion while monitoring is still active.
                time.sleep(0.01)
                # Pause briefly so hardware state can settle before checking again.

            time.sleep(0.25)
            # Pause briefly so hardware state can settle before checking again.

    # -----------------------------------------------------------------------------
    # 7.8 CENTER STAGE AFTER A PENDING CALIBRATION MOVE
    # If calibration ends during another move, the return to zero is postponed until it is safe.
    # -----------------------------------------------------------------------------
    def move_to_center_after_calibration(self):

        self.returning_stage_after_calibration = True
        # Mark that the stage is returning after calibration.

        self.start_stage_move_to(
        # Reuse the central movement routine so all safety checks and tracking updates happen the same way.
            0.0,
            reset_after_move=True
        )

    # -----------------------------------------------------------------------------
    # 7.9 FINISH CALIBRATION RESET
    # Stage tracking and measurement display are reset after the stage return is done.
    # -----------------------------------------------------------------------------
    def reset_stage_after_calibration(self, pos=None):

        self.reset_stage_movement_tracking(pos)

        self.reset_measurement_after_calibration()
        # Reset fringe-based distance and delay displays.

        self.returning_stage_after_calibration = False
        # Mark that the calibration return is finished.

        self.status.configure(
        # Tell the user what the program is currently doing or why an action was refused.
            text="Monitoring running",
            text_color=GREEN_COLOR
        )

    # -----------------------------------------------------------------------------
    # 7.10 UPDATE DRIVEN VS CALCULATED DISTANCE
    # The stage movement distance is compared with the distance calculated from counted fringes.
    # -----------------------------------------------------------------------------
    def update_comparison_labels(self, driven_mm=None):

        if driven_mm is None:
        # Use the stored driven distance when no value is provided.

            driven_mm = self.current_stage_movement_for_compare
            # Use the latest tracked stage movement for comparison.

        driven_distance_mm = abs(driven_mm)
        # Compare distances as positive lengths.

        calculated_fringes = self.accumulated_fringes
        # Use the current fringe count for calculated distance.

        calculated_mm = (
        # Convert fringe count into calculated distance.
            calculated_fringes
            * self.fringe_distance_mm
        )

        difference_mm = (
        # Calculate disagreement between driven and fringe-calculated distance.
            driven_distance_mm
            - calculated_mm
        )

        self.label_compare_driven.configure(
        # Update the driven-distance comparison label.
            text=(
                f"Driven: {driven_distance_mm:.6f} mm"
            )
        )

        self.label_compare_calculated.configure(
        # Update the fringe-calculated distance label.
            text=(
                f"Calculated: {calculated_mm:.6f} mm"
            )
        )

        self.label_compare_difference.configure(
        # Update the difference between driven and calculated distance.
            text=(
                f"Difference: {difference_mm:.6f} mm"
            )
        )

    # -----------------------------------------------------------------------------
    # 8.1 CAMERA AND MEASUREMENT LOOP
    # Frames are read, thresholds are calibrated, fringes are counted, and displays are updated.
    # -----------------------------------------------------------------------------
    def loop(self):

        frame_counter = 0
        # Start counting camera frames for live-image throttling.

        while self.is_monitoring:
        # Keep processing camera frames while monitoring is active.

            img = self.camera_handler.get_frame()
            # Read the next camera frame.

            if img is None:
            # Skip this loop if no camera frame arrived.
                continue
                # Skip this camera-loop pass and wait for the next frame.

            frame_counter += 1
            # Count this received camera frame.

            if frame_counter % 20 == 0:
            # Refresh the live image only occasionally to keep the UI responsive.

                self.after(
                # Queue the display update safely from background work so the visible UI reflects the newest state.
                    0,
                    lambda f=img: # Use the captured value for the scheduled UI update.
                    self.update_image(f)
                )

            intensity = (
            # Calculate the fringe intensity from the camera frame.
                self.camera_handler
                .get_fringe_intensity_from_frame(img)
            )

            if intensity is not None:
            # Handle this state before continuing so the measurement and stage control stay consistent.

                fringe_counted = False
                # Start this loop iteration assuming no new fringe was counted.

                if self.calibrating:
                # Collect threshold data instead of counting fringes during calibration.

                    if (not self.calibration_motion_started
                    # Start the calibration motion once when calibration begins and the stage is available.
                            and self.stage_connected):
                        self.calibration_motion_started = True
                        # Remember that calibration motion has been started.
                        threading.Thread(
                        # Start the long-running movement or camera work in the background so the window can still update and react.
                            target=self.calibration_stage_motion,
                            daemon=True
                        ).start()
                        # Begin the background worker that will monitor movement or process frames while the UI stays responsive.

                    self.calibration_values.append(
                    # Add the current intensity to the calibration sample list.
                        intensity
                    )

                    elapsed = (
                    # Measure how long threshold calibration has been running.
                        time.time()
                        - self.calibration_start_time
                    )

                    self.after(
                    # Queue the display update safely from background work so the visible UI reflects the newest state.
                        0,
                        lambda e=elapsed: # Use the captured value for the scheduled UI update.
                        self.label_thresholds.configure(
                        # Update the displayed calibration thresholds.
                            text=f"Calibrating {e:.1f}/5s"
                        )
                    )

                    if elapsed >= 5:
                    # Finish threshold calibration after five seconds of samples.

                        min_val = min(
                        # Use the lowest calibration intensity as the dark end of the signal.
                            self.calibration_values
                        )

                        max_val = max(
                        # Use the highest calibration intensity as the bright end of the signal.
                            self.calibration_values
                        )

                        value_range = (
                        # Measure the signal range seen during calibration.
                            max_val - min_val
                        )

                        self.dark_threshold = (
                        # Place the dark threshold near the low end of the calibrated signal.
                            min_val
                            + value_range * 0.125
                        )

                        self.bright_threshold = (
                        # Place the bright threshold below the high end of the calibrated signal.
                            max_val
                            - value_range * 0.30
                        )

                        self.calibrating = False
                        # Leave calibration mode and begin normal fringe counting.

                        self.after(
                        # Queue the display update safely from background work so the visible UI reflects the newest state.
                            0,
                            lambda: # Use the captured value for the scheduled UI update.
                            self.label_thresholds.configure(
                            # Update the displayed calibration thresholds.
                                text=(
                                    f"Dark: "
                                    f"{self.dark_threshold:.2f} | "
                                    f"Bright: "
                                    f"{self.bright_threshold:.2f}"
                                )
                            )
                        )

                        self.after(
                        # Queue the display update safely from background work so the visible UI reflects the newest state.
                            0,
                            lambda: # Use the captured value for the scheduled UI update.
                            self.status.configure(
                            # Tell the user what the program is currently doing or why an action was refused.
                                text="Monitoring running",
                                text_color=GREEN_COLOR
                            )
                        )

                        self.after(
                        # Queue the display update safely from background work so the visible UI reflects the newest state.
                            0,
                            self.finish_calibration_stage_reset
                        )

                else:
                # Continue with the normal path for this case because the special case above does not apply.

                    if (
                    # Skip correction while hardware or measurement state is busy; lock correction should only run in a stable state.
                        not self.returning_stage_after_calibration
                        # Count fringes only when the calibration return is not happening.
                        and not self.lock_correction_active
                        # Avoid counting lock-correction motion as measurement fringes.
                    ):

                        fringe_counted = (
                        # Run the fringe detector for the current intensity.
                            self.update_accumulated_fringes(
                                intensity
                            )
                        )

                        if fringe_counted:
                        # React to a newly counted fringe.

                            self.handle_lock_after_fringe()
                            # Let the lock system correct drift after a fringe event if needed.

                self.after(
                # Queue the display update safely from background work so the visible UI reflects the newest state.
                    0,
                    lambda v=intensity, c=fringe_counted: # Use the captured value for the scheduled UI update.
                    self.update_intensity_label(v, c)
                )

            dist_mm = (
            # Convert counted fringes into distance in millimeters.
                self.accumulated_fringes
                * self.fringe_distance_mm
            )

            dist_um = dist_mm * 1000
            # Convert the distance into micrometers for display.

            time_ps = (
            # Convert the optical path distance into time delay.
                2 * dist_mm
            ) / SPEED_OF_LIGHT_MM_PS

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                lambda: # Use the captured value for the scheduled UI update.
                self.update_values(
                    dist_mm,
                    dist_um,
                    time_ps
                )
            )

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                0,
                lambda: # Use the captured value for the scheduled UI update.
                self.label_accumulated_fringes.configure(
                # Update the displayed fringe count.
                    text=(
                        f"Accumulated Fringes Count: "
                        f"{self.accumulated_fringes}"
                    )
                )
            )

    # -----------------------------------------------------------------------------
    # 8.2 DETECT AND COUNT FRINGES
    # A stable dark-to-bright transition is counted as one fringe.
    # -----------------------------------------------------------------------------
    def update_accumulated_fringes(
        self,
        intensity
    ):

        self.intensity_history.append(
        # Add this intensity to the smoothing history.
            intensity
        )

        if len(self.intensity_history) > 5:
        # Keep only the most recent intensity values for smoothing.
            self.intensity_history.pop(0)
            # Remove the oldest intensity sample.

        smooth_intensity = np.mean(
        # Smooth the intensity with a short moving average.
            self.intensity_history
        )

        if smooth_intensity < self.dark_threshold:
        # Treat the smoothed signal as dark when it is below the dark threshold.

            self.dark_counter += 1
            # Extend the current dark streak.

        else:
        # Continue with the normal path for this case because the special case above does not apply.

            self.dark_counter = 0
            # Reset the dark-frame streak so a new stable dark phase must be detected from scratch.

        if self.dark_counter >= REQUIRED_DARK_FRAMES:
        # Accept the dark phase only after enough stable dark frames.

            self.was_dark = True
            # Remember that the detector has seen the dark phase of a fringe.

        if smooth_intensity > self.bright_threshold:
        # Treat the smoothed signal as bright when it is above the bright threshold.

            self.bright_counter += 1
            # Extend the current bright streak.

        else:
        # Continue with the normal path for this case because the special case above does not apply.

            self.bright_counter = 0
            # Reset the bright-frame streak so a new stable bright phase must be detected from scratch.

        cooldown_ok = (
        # Check whether enough time has passed since the last counted fringe.
            time.time() - self.last_count_time
        ) > FRINGE_COOLDOWN

        if (
        # Skip correction while hardware or measurement state is busy; lock correction should only run in a stable state.
            self.was_dark
            and self.bright_counter
            >= REQUIRED_BRIGHT_FRAMES
            and cooldown_ok
        ):

            self.accumulated_fringes += 1
            # Count one completed dark-to-bright fringe transition.

            self.was_dark = False
            # Clear the remembered dark phase so the next fringe count requires a fresh dark-to-bright transition.

            self.last_count_time = time.time()
            # Restart the fringe cooldown timer after changing lock state.

            self.dark_counter = 0
            # Reset the dark-frame streak so a new stable dark phase must be detected from scratch.

            self.bright_counter = 0
            # Reset the bright-frame streak so a new stable bright phase must be detected from scratch.

            return True
            # Return the computed result to the code that requested it.

        return False
        # Return the computed result to the code that requested it.

    # -----------------------------------------------------------------------------
    # 8.3 SHOW CURRENT INTENSITY
    # The intensity display is updated and briefly highlighted when a fringe is counted.
    # -----------------------------------------------------------------------------
    def update_intensity_label(
        self,
        intensity,
        fringe_counted
    ):

        self.label_intensity.configure(
        # Update the displayed intensity.
            text=f"Intensity: {intensity:.2f}"
        )

        if fringe_counted:
        # React to a newly counted fringe.

            self.label_intensity.configure(
            # Update the displayed intensity.
                text_color=GREEN_COLOR
            )

            self.after(
            # Queue the display update safely from background work so the visible UI reflects the newest state.
                250,
                lambda: # Use the captured value for the scheduled UI update.
                self.label_intensity.configure(
                # Update the displayed intensity.
                    text_color=TEXT_COLOR
                )
            )

    # -----------------------------------------------------------------------------
    # 8.4 SHOW DISTANCE AND TIME DELAY
    # The current fringe count is converted into distance and optical delay values.
    # -----------------------------------------------------------------------------
    def update_values(
        self,
        mm,
        um,
        ps
    ):

        self.label_um.configure(
        # Update the displayed distance in micrometers.
            text=f"Distance: {um:.3f} µm"
        )

        self.label_ps.configure(
        # Update the displayed time delay.
            text=f"Time Delay: {ps:.4f} ps"
        )

        self.update_comparison_labels()
        # Fill the comparison display with the current start values.

    # -----------------------------------------------------------------------------
    # 8.5 SHOW LIVE CAMERA IMAGE
    # The camera image is normalized, resized, marked with the ROI, and shown in the UI.
    # -----------------------------------------------------------------------------
    def update_image(self, img):

        display = img.astype(np.float32)
        # Prepare the camera frame for display scaling.

        display -= np.min(display)
        # Shift the image so the darkest pixel becomes zero.

        if np.max(display) > 0:
        # Normalize only when the image contains nonzero signal.
            display /= np.max(display)
            # Scale image brightness into a 0-to-1 range.

        display = (
        # Convert the normalized image into display brightness values.
            display * 255
        ).astype(np.uint8)

        pil = Image.fromarray(display).convert(
        # Create an RGB image for resizing and ROI drawing.
            "RGB"
        )

        original_w, original_h = pil.size
        # Remember the original image size for ROI scaling.

        scale_x = (
        # Calculate horizontal scaling from camera pixels to preview pixels.
            self.live_size[0] / original_w
        )

        scale_y = (
        # Calculate vertical scaling from camera pixels to preview pixels.
            self.live_size[1] / original_h
        )

        pil = pil.resize(self.live_size)
        # Resize the camera image to the preview area.

        draw = ImageDraw.Draw(pil)
        # Prepare to draw the ROI overlay.

        x1 = int(
        # Calculate the left edge of the ROI in preview coordinates.
            self.camera_handler.roi_x * scale_x
        )

        y1 = int(
        # Calculate the top edge of the ROI in preview coordinates.
            self.camera_handler.roi_y * scale_y
        )

        x2 = int(
        # Calculate the right edge of the ROI in preview coordinates.
            (
                self.camera_handler.roi_x
                + self.camera_handler.roi_w
            ) * scale_x
        )

        y2 = int(
        # Calculate the bottom edge of the ROI in preview coordinates.
            (
                self.camera_handler.roi_y
                + self.camera_handler.roi_h
            ) * scale_y
        )

        draw.rectangle(
        # Draw the selected ROI on the live image.
            [x1, y1, x2, y2],
            outline="yellow",
            width=3
        )

        ctk_img = ctk.CTkImage(
        # Convert the annotated image into a CustomTkinter image.
            light_image=pil,
            size=self.live_size
        )

        self.image_label.configure(
        # Replace the live-image placeholder with the current camera image.
            image=ctk_img,
            text=""
        )

        self.image_label.image = ctk_img
        # Keep a reference so the live image stays visible.

    # -----------------------------------------------------------------------------
    # 9.1 SHUT DOWN HARDWARE CLEANLY
    # Monitoring is stopped and camera/stage connections are closed before the window exits.
    # -----------------------------------------------------------------------------
    def on_close(self):

        self.is_monitoring = False
        # Start with the camera measurement loop stopped.

        try:
        # Try to close the hardware resource; shutdown should continue even if closing fails.
            self.camera_handler.close()
            # Release the camera connection.

        except:
        # Ignore shutdown errors so the app can still close.
            pass
            # Continue shutdown even if one hardware close call failed.

        try:
        # Try to close the hardware resource; shutdown should continue even if closing fails.
            self.stage.close()
            # Release the stage connection.

        except:
        # Ignore shutdown errors so the app can still close.
            pass
            # Continue shutdown even if one hardware close call failed.

        self.destroy()
        # Close the application window.


# -----------------------------------------------------------------------------
# 9. PROGRAM START
# -----------------------------------------------------------------------------
if __name__ == "__main__":
# Handle this state before continuing so the measurement and stage control stay consistent.

    app = InterferometerApp()
    # Create the monitor application.

    app.protocol(
    # Connect the window close button to the cleanup routine.
        "WM_DELETE_WINDOW",
        app.on_close
    )

    app.mainloop()
    # Start the graphical application loop.
