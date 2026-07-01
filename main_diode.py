# this code is basically identical with main_camera.py except for some minor adjustments of the logik, because camera changed to photodiode

# TABLE OF CONTENTS
# 1. Basic settings
# 2. Imports #NEW (obviously changed for the PD)
# 3. Physical constants and colors
# 4. SideApp class (UI) #NEW (here we dont have a live image, but a matplot of the signal)
# 5. Monitoring and reset
# 6. Translation stage control
# 7. Calibration #NEW (in main_camera.py we use the pixel brightnesses for calibration, in main_diode.py we use the diode voltage)
# 8. Diode loop and plotting #NEW (instead of Bright/Dark Values, we use voltage difference as counting)
# 9. Cleanup and program start


# -----------------------------------------------------------------------------
# 1. BASIC SETTINGS
# -----------------------------------------------------------------------------

RAW_HISTORY_LENGTH = 300 #how many raw voltage values are kept in the plot in the gui
STEP_PAUSE_S = 0.05 #pause between steps in stepped mode
#the number of consecutive dark or bright frames required to count a fringe, this is to filter out noise and avoid counting false fringes due to intensity fluctuations
REQUIRED_DARK_FRAMES = 3
REQUIRED_BRIGHT_FRAMES = 3
#after counting a fringe, the system will ignore any new fringes for this amount of time, this is to avoid counting multiple fringes if the intensity fluctuates around the threshold
FRINGE_COOLDOWN = 0.08
MODE = "continuous" #"continuous" or "stepped" - determines how the stage moves
VELOCITY_MM_S = 0.0006 #speed for continuous mode
TOTAL_DISTANCE_MM = 13.0 #total distance to move in continuous mode
VELOCITY_MM_S_STEPPED = 1.00 #speed for stepped mode
STEP_SIZE_MM = 0.00001 #step size for stepped mode
STEPS = 100 #number of steps for stepped mode

# -----------------------------------------------------------------------------
# 2. IMPORTS
# -----------------------------------------------------------------------------

import threading # so that camera and stage can run without freezing the UI
import time # for timestamps
import customtkinter as ctk # pythons standard UI library
try: #instead of importing the dlls like in main_camera.py here we import matplotlib and the diode handler file
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    Figure = None
    FigureCanvasTkAgg = None
from diode_handler import (
    CALIBRATION_SECONDS, 
    LASER_WAVELENGTH_NM,
    PHOTODIODE_CHANNEL,
    SAMPLE_INTERVAL_S,
    SingleDiodeHandler,
    compute_fringe_distance_mm
)
from stage_controller import StageController

# -----------------------------------------------------------------------------
# 3. PHYSICAL CONSTANTS
# -----------------------------------------------------------------------------

SPEED_OF_LIGHT_MM_PS = 0.299792458
DEFAULT_STAGE_SPEED_MM_S = 0.0006
def compute_quarter_wavelength_step_mm(wavelength_nm):
    return (wavelength_nm / 4) / 1_000_000

# -----------------------------------------------------------------------------
# 3.1 COLORS AND FILTER TIMINGS
# -----------------------------------------------------------------------------

TEXT_COLOR = "#0A4A51"
GREEN_COLOR = "#1EAD4F"
RED_COLOR = "#C0392B"
ORANGE_COLOR = "#D35400"

# -----------------------------------------------------------------------------
# 4. APP CLASS (UI)
# -----------------------------------------------------------------------------

class SideApp(ctk.CTk):
    # -----------------------------------------------------------------------------
    # 4.1 INITIALIZATION
    # -----------------------------------------------------------------------------

    #ctk.CTk is the base class for the customtkinter window, here we inherit our InterferometerApp class from it
    def __init__(self):
        #init method always gets called to create a new instance of the class
        super().__init__()
        self.title("Single Photodiode Fringe Monitor")
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
        self.measurement_thread = None
        #for the 5s calibration at the beginning
        self.calibrating = False #all these parameters are for initialization of the photodiode-app
        self.latest_sample = None
        self.latest_voltage = 0.0
        self.last_error_text = None
        self.raw_voltage_history = []
        self.smoothed_voltage_history = []
        self.accumulated_fringes = 0
        #a bright state only counts after darkness
        self.was_dark = False
        #number of consecutive dark/bright fringes
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0
        self.dark_threshold = 0.0
        self.bright_threshold = 0.0
        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
        self.fringe_distance_mm = compute_fringe_distance_mm(
            self.laser_wavelength_nm
        )
        self.quarter_wavelength_step_mm = compute_quarter_wavelength_step_mm(
            self.laser_wavelength_nm
        )
        self.diode = SingleDiodeHandler()
        #same for the stage
        self.stage = StageController()
        self.stage.set_velocity(VELOCITY_MM_S, 0.0)
        self.stage_connected = self.stage.connect()
        #stores values for all the start positions
        self.stage_start_position = 0.0
        self.stage_reference_position = 0.0
        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        self.last_stage_speed_time = None
        self.last_stage_speed_position = None
        self.build_ui()
        self.update_comparison_labels() # renewing the text in the UI matching the initial update of the comparison labels with 0 values using e.g self.current_stage_movement_for_compare which is 0 at the beginning
        self.update_stage_position_once() # reads the current stage position and updates the label, this is important to have the correct position at the beginning
        self.all_buttons = [
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
    # -----------------------------------------------------------------------------
    # 4.1.2 UI BUILD
    # -----------------------------------------------------------------------------

    def build_ui(self):
        ctk.CTkLabel(
            self.scroll,
            text="Single Photodiode Fringe Monitor",
            font=("Arial", 23, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=5)
        self.btn = ctk.CTkButton(
            self.scroll,
            text="START MONITORING",
            command=self.toggle,
            width=180,
            height=30,
            fg_color=TEXT_COLOR,
            font=("Arial", 11, "bold")
        )
        self.btn.pack(pady=2)
        self.restart_btn = ctk.CTkButton(
            self.scroll,
            text="RESET",
            command=self.restart,
            width=140,
            height=28,
            fg_color=ORANGE_COLOR
        )
        self.restart_btn.pack(pady=1)
        self.status = ctk.CTkLabel(
            self.scroll,
            text="Status: Stopped",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.status.pack(pady=2)
        self.stage_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )
        self.stage_frame.pack(
            fill="x",
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
        self.wavelength_entry.insert(
            0,
            f"{self.laser_wavelength_nm:.1f}"
        )
        self.wavelength_button = ctk.CTkButton(
            self.stage_frame,
            text="Set wavelength",
            width=120,
            command=self.apply_wavelength,
            fg_color=TEXT_COLOR
        )
        self.wavelength_button.pack(pady=1)
        ctk.CTkLabel(
            self.stage_frame,
            text="Step size:",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 0))
        self.step_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Step size in mm",
            width=250
        )
        self.step_entry.pack(pady=1)
        self.step_entry.insert(
            0,
            f"{self.quarter_wavelength_step_mm:.9f}"
        )
        ctk.CTkLabel(
            self.stage_frame,
            text="Velocity:",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 0))
        self.speed_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Movement speed in mm/s",
            width=250
        )
        self.speed_entry.pack(pady=1)
        stage_velocity = None
        if self.stage_connected:
            stage_velocity = self.stage.set_velocity()
        if stage_velocity is None:
            stage_velocity = DEFAULT_STAGE_SPEED_MM_S
        self.speed_entry.insert(
            0,
            f"{stage_velocity:.6f}"
        )
        self.speed_button = ctk.CTkButton(
            self.stage_frame,
            text="Set speed",
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
        ctk.CTkLabel(
            self.stage_frame,
            text="Target or Distance (mm):",
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 0))
        self.target_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Target value or distance in mm",
            width=250
        )
        self.target_entry.pack(pady=1)
        self.target_entry.insert(0, "0.0000")
        self.target_button_frame = ctk.CTkFrame(
            self.stage_frame,
            fg_color="transparent"
        )
        self.target_button_frame.pack(pady=1)
        self.btn_target_abs = ctk.CTkButton(
            self.target_button_frame,
            text="Go to target",
            width=140,
            command=self.move_to_target,
            fg_color=TEXT_COLOR
        )
        self.btn_target_abs.grid(
            row=0,
            column=0,
            padx=1
        )
        self.btn_target_rel = ctk.CTkButton(
            self.target_button_frame,
            text="Move distance",
            width=140,
            command=self.move_distance,
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
        self.label_stage_speed = ctk.CTkLabel(
            self.stage_frame,
            text="Movement Speed: 0.000000 mm/s",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_stage_speed.pack(pady=0)
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
            text="Distance from Fringes: 0.000 um",
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
        self.label_calibration_offset = ctk.CTkLabel(
            self.frame,
            text="Dark Threshold: waiting",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_calibration_offset.pack(pady=0)
        self.label_calibration_scale = ctk.CTkLabel(
            self.frame,
            text="Bright Threshold: waiting",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_calibration_scale.pack(pady=0)
        self.label_sample_count = ctk.CTkLabel(
            self.frame,
            text="Accumulated Fringes Count: 0",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_sample_count.pack(pady=0)
        self.label_min_voltage = ctk.CTkLabel(
            self.frame,
            text="Min Voltage: n/a",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_min_voltage.pack(pady=0)
        self.label_max_voltage = ctk.CTkLabel(
            self.frame,
            text="Max Voltage: n/a",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_max_voltage.pack(pady=0)
        self.label_raw = ctk.CTkLabel(
            self.frame,
            text="Raw Voltage: 0.000000 V",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_raw.pack(pady=0)
        self.label_norm = ctk.CTkLabel(
            self.frame,
            text="Normalized Voltage: 0.0000",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_norm.pack(pady=0)
        self.label_calibration = ctk.CTkLabel(
            self.frame,
            text="Calibration: waiting",
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_calibration.pack(pady=0)
        self.compare_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )
        self.compare_frame.pack(
            fill="x",
            padx=5,
            pady=4
        )
        ctk.CTkLabel(
            self.compare_frame,
            text="Stage Movement",
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
            text="Calculated from Fringes: 0.000000 mm",
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_compare_calculated.pack(pady=0)
        self.label_compare_difference = ctk.CTkLabel(
            self.compare_frame,
            text="Difference: n/a",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_compare_difference.pack(pady=0)
        channel_text = f"Channel: photodiode={PHOTODIODE_CHANNEL}"
        ctk.CTkLabel(
            self.scroll,
            text=channel_text,
            font=("Arial", 10),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 2))
        self.plot_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )
        self.plot_frame.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=(4, 10)
        )
        ctk.CTkLabel(
            self.plot_frame,
            text="Live Raw Voltage",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 2))
        self.build_plot()
    # -----------------------------------------------------------------------------
    # 4.1.3 PLOT BUILD
    # -----------------------------------------------------------------------------

    def build_plot(self): #initializes matplot diagramm for the plotting
        if Figure is None or FigureCanvasTkAgg is None:
            self.plot_axis = None
            self.plot_canvas = None #embeds the diagram in tkinter canvas
            ctk.CTkLabel(
                self.plot_frame,
                text="Matplotlib is required for live voltage plotting.",
                font=("Arial", 11),
                text_color=RED_COLOR
            ).pack(pady=8)
            return
        self.plot_figure = Figure(
            figsize=(8, 3),
            dpi=100
        )
        self.plot_axis = self.plot_figure.add_subplot(111)
        self.plot_axis.set_title("Raw diode voltage")
        self.plot_axis.set_xlabel("Samples")
        self.plot_axis.set_ylabel("Voltage")
        self.plot_axis.grid(
            True,
            linestyle=":",
            alpha=0.6
        )
        self.plot_line_voltage = self.plot_axis.plot(
            [],
            [],
            color="blue",
            label="photodiode raw"
        )[0]
        self.plot_axis.legend(loc="upper right")
        self.plot_canvas = FigureCanvasTkAgg(
            self.plot_figure,
            master=self.plot_frame
        )
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )
    # -----------------------------------------------------------------------------
    # 4.2 ENABLE OR DISABLE ALL BUTTONS
    # -----------------------------------------------------------------------------

    def set_buttons_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        for button in self.all_buttons:
            button.configure(state=state)
    # -----------------------------------------------------------------------------
    # 5.1 START OR STOP MONITORING
    # -----------------------------------------------------------------------------

    def toggle(self): # toggle method
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    # -----------------------------------------------------------------------------
    # 5.1.1 START MONITORING HELPER
    # -----------------------------------------------------------------------------

    def start_monitoring(self):
        if (
            self.measurement_thread is not None
            and self.measurement_thread.is_alive()
        ):
            return
        self.restart_values_only()
        self.diode = SingleDiodeHandler()
        self.is_monitoring = True
        self.calibrating = True
        self.last_error_text = None
        self.btn.configure(
            text="STOP MONITORING",
            fg_color=RED_COLOR
        )
        self.status.configure(
            text="Status: connecting NI...",
            text_color=ORANGE_COLOR
        )
        self.set_buttons_enabled(False)
        self.measurement_thread = threading.Thread(
            target=self.loop,
            daemon=True
        )
        self.measurement_thread.start()
    # -----------------------------------------------------------------------------
    # 5.1.2 STOP MONITORING HELPER
    # -----------------------------------------------------------------------------

    def stop_monitoring(self):
        self.is_monitoring = False
        self.calibrating = False
        if self.stage_connected and self.stage.is_moving:
            self.stage.stop()
        self.status.configure(
            text="Status: stopping...",
            text_color=ORANGE_COLOR
        )
    # -----------------------------------------------------------------------------
    # 8.1 DIODE LOOP AND MEASUREMENT
    # -----------------------------------------------------------------------------

    def loop(self):
        try:
            self.diode.connect()
            self.after(
                0,
                lambda:
                self.status.configure(
                    text=f"Status: calibrating {CALIBRATION_SECONDS:.1f}s...",
                    text_color=ORANGE_COLOR
                )
            )
            if self.stage_connected:
                threading.Thread(
                    target=self.calibration_stage_motion,
                    daemon=True
                ).start()
            calibration = self.diode.calibrate(
                seconds=CALIBRATION_SECONDS,
                sample_interval_s=SAMPLE_INTERVAL_S,
                should_continue=lambda: self.is_monitoring,
                sample_callback=self.handle_calibration_sample
            )
            if not self.is_monitoring:
                return
            self.calibrating = False
            if calibration is not None:
                self.after(
                    0,
                    lambda c=calibration:
                    self.finish_calibration_display(c)
                )
            while self.is_monitoring:
                sample = self.diode.read()
                self.after(
                    0,
                    lambda s=sample:
                    self.update_sample_display(s)
                )
                time.sleep(SAMPLE_INTERVAL_S)
        except Exception as error:
            self.last_error_text = str(error)
            self.after(
                0,
                lambda e=error:
                self.show_error(e)
            )
        finally:
            self.is_monitoring = False
            self.calibrating = False
            try:
                self.diode.close()
            except Exception:
                pass
            self.after(
                0,
                self.finish_stopped_ui
            )
    # -----------------------------------------------------------------------------
    # 7.8 HANDLE CALIBRATION SAMPLE
    # -----------------------------------------------------------------------------

    def handle_calibration_sample(self, raw_voltage, elapsed_s, total_s):
        self.after(
            0,
            lambda v=raw_voltage, e=elapsed_s, t=total_s:
            self.update_calibration_progress(v, e, t)
        )
    # -----------------------------------------------------------------------------
    # 7.8.1 UPDATE CALIBRATION PROGRESS
    # -----------------------------------------------------------------------------

    def update_calibration_progress(
        self,
        raw_voltage,
        elapsed_s,
        total_s
    ):
        self.append_raw_history(
            raw_voltage
        )
        self.update_plot()
        self.label_raw.configure(
            text=f"Raw Voltage: {raw_voltage:+.6f} V"
        )
        self.label_calibration.configure(
            text=f"Calibration: {elapsed_s:.1f}/{total_s:.1f}s"
        )
    # -----------------------------------------------------------------------------
    # 7.8.2 FINISH CALIBRATION DISPLAY
    # -----------------------------------------------------------------------------

    def finish_calibration_display(self, calibration):
        value_range = calibration.max_voltage - calibration.min_voltage
        self.dark_threshold = (
            calibration.min_voltage
            + value_range * 0.125
        )
        self.bright_threshold = (
            calibration.max_voltage
            - value_range * 0.40
        )
        self.label_calibration.configure(
            text=(
                f"Calibration min/max: "
                f"{calibration.min_voltage:+.6f}/"
                f"{calibration.max_voltage:+.6f} V"
            ),
            text_color=GREEN_COLOR
        )
        self.label_calibration_offset.configure(
            text=f"Dark Threshold: {self.dark_threshold:+.6f} V"
        )
        self.label_calibration_scale.configure(
            text=f"Bright Threshold: {self.bright_threshold:+.6f} V"
        )
        self.label_min_voltage.configure(
            text=f"Min Voltage: {calibration.min_voltage:+.6f} V"
        )
        self.label_max_voltage.configure(
            text=f"Max Voltage: {calibration.max_voltage:+.6f} V"
        )
        self.status.configure(
            text="Status: monitoring running",
            text_color=GREEN_COLOR
        )
    # -----------------------------------------------------------------------------
    # 8.3 SHOW CURRENT VOLTAGE AND DISTANCE
    # -----------------------------------------------------------------------------

    def update_sample_display(self, sample):
        self.latest_sample = sample
        self.latest_voltage = sample.raw_voltage
        fringe_counted = self.update_accumulated_fringes(
            sample.raw_voltage
        )
        self.append_raw_history(
            sample.raw_voltage
        )
        self.update_plot()
        distance_mm = self.accumulated_fringes * self.fringe_distance_mm
        distance_um = distance_mm * 1000
        time_ps = (2 * distance_mm) / SPEED_OF_LIGHT_MM_PS
        self.label_um.configure(
            text=f"Distance from Fringes: {distance_um:.6f} um"
        )
        self.label_ps.configure(
            text=f"Time Delay: {time_ps:.4f} ps"
        )
        self.label_sample_count.configure(
            text=f"Accumulated Fringes Count: {self.accumulated_fringes}"
        )
        self.label_raw.configure(
            text=f"Raw Voltage: {sample.raw_voltage:+.6f} V"
        )
        self.label_norm.configure(
            text=f"Normalized Voltage: {sample.normalized_voltage:+.4f}"
        )
        if fringe_counted:
            self.label_sample_count.configure(
                text_color=GREEN_COLOR
            )
            self.after(
                250,
                lambda:
                self.label_sample_count.configure(
                    text_color=TEXT_COLOR
                )
            )
        self.update_comparison_labels()
    # -----------------------------------------------------------------------------
    # 8.2 DETECT AND COUNT FRINGES
    # -----------------------------------------------------------------------------

    def update_accumulated_fringes(self, voltage):
        self.smoothed_voltage_history.append(
            voltage
        )
        if len(self.smoothed_voltage_history) > 5:
            self.smoothed_voltage_history.pop(0)
        smooth_voltage = (
            sum(self.smoothed_voltage_history)
            / len(self.smoothed_voltage_history)
        )
        if smooth_voltage < self.dark_threshold:
            self.dark_counter += 1
        else:
            self.dark_counter = 0
        if self.dark_counter >= REQUIRED_DARK_FRAMES:
            self.was_dark = True
        if smooth_voltage > self.bright_threshold:
            self.bright_counter += 1
        else:
            self.bright_counter = 0
        cooldown_ok = (
            time.time() - self.last_count_time
        ) > FRINGE_COOLDOWN
        if (
            self.was_dark
            and self.bright_counter >= REQUIRED_BRIGHT_FRAMES
            and cooldown_ok
        ):
            self.accumulated_fringes += 1
            self.was_dark = False
            self.last_count_time = time.time()
            self.dark_counter = 0
            self.bright_counter = 0
            return True
        return False
    # -----------------------------------------------------------------------------
    # 8.4 APPEND RAW VOLTAGE TO HISTORY
    # -----------------------------------------------------------------------------

    def append_raw_history(self, raw_voltage):
        self.raw_voltage_history.append(raw_voltage)
        if len(self.raw_voltage_history) > RAW_HISTORY_LENGTH:
            self.raw_voltage_history.pop(0)
    # -----------------------------------------------------------------------------
    # 8.5 LIVE VOLTAGE PLOT UPDATE
    # -----------------------------------------------------------------------------

    def update_plot(self, reset=False): #updates  the x and y of the plot diagramm, when reset=true, all the data is deleted
        if self.plot_axis is None:
            return
        if reset:
            self.plot_line_voltage.set_data([], [])
            self.plot_axis.relim()
            self.plot_axis.autoscale_view()
            self.plot_canvas.draw_idle()
            return
        x = list(
            range(len(self.raw_voltage_history))
        )
        self.plot_line_voltage.set_data(
            x,
            self.raw_voltage_history
        )
        self.plot_axis.relim()
        self.plot_axis.autoscale_view()
        self.plot_canvas.draw_idle()
    # -----------------------------------------------------------------------------
    # 8.6 SHOW MONITORING ERROR
    # -----------------------------------------------------------------------------

    def show_error(self, error):
        self.status.configure(
            text=f"Status: {error}",
            text_color=RED_COLOR
        )
    # -----------------------------------------------------------------------------
    # 8.7 RESET UI AFTER MONITORING STOPS
    # -----------------------------------------------------------------------------

    def finish_stopped_ui(self):
        self.btn.configure(
            text="START MONITORING",
            fg_color=TEXT_COLOR
        )
        if self.last_error_text:
            self.status.configure(
                text=f"Status: {self.last_error_text}",
                text_color=RED_COLOR
            )
        else:
            self.status.configure(
                text="Status: Stopped",
                text_color=TEXT_COLOR
            )
    # -----------------------------------------------------------------------------
    # 5.2 RESET BUTTON
    # -----------------------------------------------------------------------------

    def restart(self):
        self.restart_values_only() # button calls "restart" function, which forwards to "restart_values_only"
    # -----------------------------------------------------------------------------
    # 5.2.1 RESET VALUES ONLY
    # -----------------------------------------------------------------------------

    def restart_values_only(self):
        if self.diode is not None:
            self.diode.counter.reset()
        self.latest_sample = None
        self.latest_voltage = 0.0
        self.raw_voltage_history = []
        self.smoothed_voltage_history = []
        #defines what the values should look like after pressing reset
        self.accumulated_fringes = 0
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0
        self.reset_stage_movement_tracking() # function defined later
        self.label_um.configure(
            text="Distance from Fringes: 0.000 um"
        )
        self.label_ps.configure(
            text="Time Delay: 0.0000 ps"
        )
        self.label_calibration_offset.configure(
            text="Dark Threshold: waiting"
        )
        self.label_calibration_scale.configure(
            text="Bright Threshold: waiting"
        )
        self.label_sample_count.configure(
            text="Accumulated Fringes Count: 0",
            text_color=TEXT_COLOR
        )
        self.label_min_voltage.configure(
            text="Min Voltage: n/a"
        )
        self.label_max_voltage.configure(
            text="Max Voltage: n/a"
        )
        self.label_raw.configure(
            text="Raw Voltage: 0.000000 V"
        )
        self.label_norm.configure(
            text="Normalized Voltage: 0.0000"
        )
        self.label_calibration.configure(
            text="Calibration: waiting",
            text_color=TEXT_COLOR
        )
        self.update_plot(reset=True)
        self.update_comparison_labels(0.0)
    def parse_entry_float(self, entry):
        return float(
            entry.get().replace(",", ".")
        )
    # -----------------------------------------------------------------------------
    # 5.6 READ STEP SIZE FROM THE UI
    # -----------------------------------------------------------------------------

    def get_step_size(self):
        #convert the user input from the UI into something readable for the program
        try:
            value = self.parse_entry_float(
                self.step_entry
            )
            value = abs(value)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            self.status.configure(
                text="Status: invalid step size",
                text_color=RED_COLOR
            )
            return 0.0001 # safe default size when step size invalid
    # -----------------------------------------------------------------------------
    # 5.6.1 READ STAGE SPEED FROM THE UI
    # -----------------------------------------------------------------------------

    def get_stage_speed(self):
        try:
            value = self.parse_entry_float(
                self.speed_entry
            )
            value = abs(value)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            self.status.configure(
                text="Status: invalid movement speed",
                text_color=RED_COLOR
            )
            return None
    # -----------------------------------------------------------------------------
    # 5.8 APPLY A NEW LASER WAVELENGTH
    # -----------------------------------------------------------------------------

    def apply_wavelength(self):
        # get the new laser wavelenght from the UI
        try:
            wavelength_nm = self.parse_entry_float(
                self.wavelength_entry
            )
        except ValueError:
            self.status.configure(
                text="Invalid wavelength value",
                text_color=RED_COLOR
            )
            return
        if wavelength_nm <= 0:
            self.status.configure(
                text="Wavelength must be positive",
                text_color=RED_COLOR
            )
            return
        self.laser_wavelength_nm = wavelength_nm
        self.fringe_distance_mm = compute_fringe_distance_mm(
            self.laser_wavelength_nm
        )
        self.quarter_wavelength_step_mm = compute_quarter_wavelength_step_mm(
            self.laser_wavelength_nm
        )
        #clear old suggested stepsize
        self.step_entry.delete(0, "end")
        self.step_entry.insert(
            0,
            f"{self.quarter_wavelength_step_mm:.9f}"
        )
        self.status.configure(
            text=f"Wavelength set to {self.laser_wavelength_nm:.1f} nm",
            text_color=GREEN_COLOR
        )
    # -----------------------------------------------------------------------------
    # 5.6.2 APPLY STAGE SPEED
    # -----------------------------------------------------------------------------

    def apply_stage_speed(self, update_status=True):
        speed_mm_s = self.get_stage_speed()
        if speed_mm_s is None:
            return False
        self.speed_entry.delete(0, "end")
        self.speed_entry.insert(
            0,
            f"{speed_mm_s:.6f}"
        )
        if not self.stage_connected:
            if update_status:
                self.status.configure(
                    text="Stage not connected",
                    text_color=RED_COLOR
                )
            return False
        if not self.stage.set_velocity(speed_mm_s):
            if update_status:
                self.status.configure(
                    text="Could not set stage speed",
                    text_color=RED_COLOR
                )
            return False
        self.label_stage_speed.configure(
            text=f"Movement Speed: {speed_mm_s:.6f} mm/s"
        )
        if update_status:
            self.status.configure(
                text=f"Stage speed set to {speed_mm_s:.6f} mm/s",
                text_color=GREEN_COLOR
            )
        return True
    # -----------------------------------------------------------------------------
    # 6.6 STAGE CONTROL HELPER
    # -----------------------------------------------------------------------------

    def prepare_stage_for_move(self):
        if not self.stage_connected:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return False
        if self.stage.is_moving:
            self.status.configure(
                text="Stage is already moving",
                text_color=ORANGE_COLOR
            )
            return False
        return self.apply_stage_speed(
            update_status=False
        )
    # -----------------------------------------------------------------------------
    # 6.1 MOVE STAGE TO AN ABSOLUTE POSITION
    # -----------------------------------------------------------------------------

    def start_stage_move_to(self, target_mm, start_pos=None):
        if not self.prepare_stage_for_move():
            return
        if start_pos is None:
            start_pos = self.stage.get_position()
        target_mm = self.stage.clamp_position(
            target_mm
        )
        move_mm = target_mm - start_pos
        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.reset_stage_speed_tracking(start_pos)
        if abs(move_mm) < 1e-12:
            self.update_stage_labels(
                start_pos,
                0.0,
                self.stage_movement_before_move
            )
            self.status.configure(
                text="Stage already at target",
                text_color=TEXT_COLOR
            )
            return
        if not self.stage.move_absolute(target_mm):
            self.status.configure(
                text="Stage move failed",
                text_color=RED_COLOR
            )
            return
        self.status.configure(
            text=f"Stage moving to {target_mm:.6f} mm",
            text_color=TEXT_COLOR
        )
        threading.Thread(
            target=self.stage_ui_loop,
            daemon=True
        ).start()
    # -----------------------------------------------------------------------------
    # 6.2 MOVE STAGE BY A RELATIVE DISTANCE
    # -----------------------------------------------------------------------------

    def start_stage_move_by(self, move_mm):
        if not self.stage_connected:
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return
        start_pos = self.stage.get_position()
        self.start_stage_move_to(
            start_pos + move_mm,
            start_pos=start_pos
        )
    # -----------------------------------------------------------------------------
    # 6.3 MOVE STAGE TO TARGET IN STEPS
    # -----------------------------------------------------------------------------

    def start_stage_move_to_stepped(
        self,
        target_mm,
        step_mm=None,
        pause_s=STEP_PAUSE_S,
        label_prefix="Moving"
    ):
        if not self.prepare_stage_for_move():
            return
        start_pos = self.stage.get_position()
        target_mm = self.stage.clamp_position(
            target_mm
        )
        if abs(target_mm - start_pos) < 1e-12:
            self.status.configure(
                text="Stage already at target",
                text_color=TEXT_COLOR
            )
            return
        #safe the values for the stage_ui_loop
        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.reset_stage_speed_tracking(start_pos)
        if step_mm is None:
            step_mm = self.get_step_size()
        else:
            step_mm = abs(
                float(step_mm)
            )
        if step_mm <= 0:
            self.status.configure(
                text="Invalid step size",
                text_color=RED_COLOR
            )
            return
        #if none of the above cases stops the stage from moving, create a movement thread and start the movement
        threading.Thread(
            target=self.stage_stepped_move_worker,
            args=(start_pos, target_mm, step_mm, pause_s, label_prefix),
            daemon=True
        ).start()
    # -----------------------------------------------------------------------------
    # 6.4 MOVE STAGE RELATIVELY IN STEPS
    # -----------------------------------------------------------------------------

    def start_stage_move_by_steps(
        self,
        move_mm,
        step_mm=None,
        pause_s=STEP_PAUSE_S,
        label_prefix="Moving"
    ):
        #security checks so the code doesnt crash
        if not self.stage_connected: # translation stage connected?
            self.status.configure(
                text="Stage not connected",
                text_color=RED_COLOR
            )
            return
        start_pos = self.stage.get_position()
        self.start_stage_move_to_stepped(
            start_pos + move_mm,
            step_mm=step_mm,
            pause_s=pause_s,
            label_prefix=label_prefix
        )
    # -----------------------------------------------------------------------------
    # 6.5 WORKER FOR STEPPED MOVEMENT
    # -----------------------------------------------------------------------------

    def stage_stepped_move_worker(
        self,
        start_pos,
        target_mm,
        step_mm,
        pause_s,
        label_prefix
    ):
        step_sign = 1 if target_mm > start_pos else -1
        current_pos = start_pos
        remaining = abs(target_mm - start_pos)
        moved = 0.0
        self.after(
            0,
            lambda:
            self.status.configure(
                text=(
                    f"{label_prefix} to {target_mm:.6f} mm in "
                    f"{step_mm:.9f} mm steps"
                ),
                text_color=TEXT_COLOR
            )
        )
        while remaining > 1e-12:
            next_step = min(
                step_mm,
                remaining
            )
            next_target = current_pos + step_sign * next_step
            if not self.stage.move_absolute(next_target):
                self.after(
                    0,
                    lambda:
                    self.status.configure(
                        text="Stage move failed",
                        text_color=RED_COLOR
                    )
                )
                return
            while self.stage.is_moving:
                time.sleep(0.005 if pause_s <= 0 else 0.01)
            step_distance = abs(
                next_target - current_pos
            )
            moved += step_distance
            current_pos = next_target
            remaining = abs(
                target_mm - current_pos
            )
            self.total_stage_movement = (
                self.stage_movement_before_move + moved
            )
            self.after(
                0,
                lambda p=current_pos, m=moved, b=self.stage_movement_before_move:
                self.update_stage_labels(p, m, b)
            )
            if remaining > 1e-12 and pause_s > 0:
                time.sleep(pause_s)
        self.after(
            0,
            lambda:
            self.finish_stage_move(current_pos)
        )
    # -----------------------------------------------------------------------------
    # 7.1 TRACK NORMAL STAGE MOVEMENT
    # -----------------------------------------------------------------------------

    def stage_ui_loop(self):
        #how much did the stage move befor the current movement? use this as base
        movement_base = self.stage_movement_before_move
        while self.stage.is_moving:
            pos = self.stage.get_position()
            moved = abs(
                pos - self.stage_start_position
            )
            self.after(
                0,
                lambda p=pos, m=moved, b=movement_base:
                self.update_stage_labels(p, m, b)
            )
            time.sleep(0.05)
        pos = self.stage.get_position()
        moved = abs(
            pos - self.stage_start_position
        )
        self.total_stage_movement = movement_base + moved
        self.after(
            0,
            lambda p=pos:
            self.finish_stage_move(p)
        )
    # -----------------------------------------------------------------------------
    # 7.1.1 FINISH STAGE MOVE
    # -----------------------------------------------------------------------------

    def finish_stage_move(self, pos):
        moved = abs(
            pos - self.stage_start_position
        )
        self.update_stage_labels(
            pos,
            moved,
            self.stage_movement_before_move
        )
        self.label_stage_speed.configure(
            text="Movement Speed: 0.000000 mm/s"
        )
        self.status.configure(
            text=f"Reached {pos:.6f} mm",
            text_color=GREEN_COLOR
        )
    # -----------------------------------------------------------------------------
    # 5.9 STAGE BUTTON ACTIONS
    # -----------------------------------------------------------------------------

    def move_to_min(self):
        self.start_stage_move_to(
            self.stage.min_position
        )
    # -----------------------------------------------------------------------------
    # 5.9.1 STEP NEGATIVE
    # -----------------------------------------------------------------------------

    def step_negative(self):
        self.start_stage_move_by(
            -self.get_step_size()
        )
    # -----------------------------------------------------------------------------
    # 5.9.2 MOVE TO CENTER
    # -----------------------------------------------------------------------------

    def move_to_center(self):
        self.start_stage_move_to_stepped( # move to center button also goes in steps
            0.0
        )
    # -----------------------------------------------------------------------------
    # 5.9.3 STEP POSITIVE
    # -----------------------------------------------------------------------------

    def step_positive(self):
        self.start_stage_move_by(
            self.get_step_size()
        )
    # -----------------------------------------------------------------------------
    # 5.9.4 MOVE TO MAX
    # -----------------------------------------------------------------------------

    def move_to_max(self):
        self.start_stage_move_to(
            self.stage.max_position
        )
    # -----------------------------------------------------------------------------
    # 5.9.5 MOVE TO TARGET FROM UI
    # -----------------------------------------------------------------------------

    def move_to_target(self):
        try:
            target_mm = self.parse_entry_float(
                self.target_entry
            )
        except ValueError:
            self.status.configure(
                text="Invalid target value",
                text_color=RED_COLOR
            )
            return
        self.start_stage_move_to(
            target_mm
        )
    # -----------------------------------------------------------------------------
    # 5.9.6 MOVE DISTANCE FROM UI
    # -----------------------------------------------------------------------------

    def move_distance(self):
        try:
            distance_mm = self.parse_entry_float(
                self.target_entry
            )
        except ValueError:
            self.status.configure(
                text="Invalid distance value",
                text_color=RED_COLOR
            )
            return
        self.start_stage_move_by(
            distance_mm
        )
    # -----------------------------------------------------------------------------
    # 5.9.7 STOP STAGE ACTION
    # -----------------------------------------------------------------------------

    def stop_stage(self):
        if self.stage_connected:
            self.stage.stop()
        self.after(
            0,
            lambda:
            self.status.configure(
                text="Stage stopped manually",
                text_color=RED_COLOR
            )
        )
    # -----------------------------------------------------------------------------
    # 7.2 SHOW INITIAL STAGE POSITION
    # -----------------------------------------------------------------------------

    #after calibration UI is filled with current stage position
    def update_stage_position_once(self):
        if self.stage_connected:
            pos = self.stage.get_position()
            self.stage_reference_position = pos
            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )
        else:
            self.status.configure(
                text="Status: Stage not connected",
                text_color=ORANGE_COLOR
            )
    # -----------------------------------------------------------------------------
    # 7.3 UPDATE STAGE MOVEMENT DISPLAY
    # -----------------------------------------------------------------------------

    def update_stage_labels(self, pos, moved, movement_base=None):
        if movement_base is None:
            movement_base = self.total_stage_movement
        current_total_stage_movement = movement_base + abs(
            moved
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
        self.update_stage_speed_label(pos)
        self.update_comparison_labels(
            current_total_stage_movement
        )
    # -----------------------------------------------------------------------------
    # 7.5 RESET STAGE SPEED TRACKING
    # -----------------------------------------------------------------------------

    def reset_stage_speed_tracking(self, pos):
        self.last_stage_speed_position = pos
        self.last_stage_speed_time = time.time()
    # -----------------------------------------------------------------------------
    # 7.6 UPDATE STAGE SPEED DISPLAY
    # -----------------------------------------------------------------------------

    def update_stage_speed_label(self, pos):
        now = time.time()
        if (
            self.last_stage_speed_time is None
            or self.last_stage_speed_position is None
        ):
            self.reset_stage_speed_tracking(pos)
            return
        dt = now - self.last_stage_speed_time
        if dt <= 0:
            return
        speed_mm_s = abs(
            pos - self.last_stage_speed_position
        ) / dt
        self.last_stage_speed_time = now
        self.last_stage_speed_position = pos
        self.label_stage_speed.configure(
            text=f"Movement Speed: {speed_mm_s:.6f} mm/s"
        )
    # -----------------------------------------------------------------------------
    # 7.4 RESET STAGE MOVEMENT TRACKING
    # -----------------------------------------------------------------------------

    def reset_stage_movement_tracking(self, pos=None):
        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        if pos is not None: # use provided position as new reference
            self.stage_reference_position = pos
            self.label_stage_position.configure(
                text=f"Stage Position: {pos:.6f} mm"
            )
        elif self.stage_connected: # if the stage is connected use actual hardware position as reference
            self.stage_reference_position = self.stage.get_position()
        else:
            self.stage_reference_position = 0.0
        self.label_stage_moved.configure(
            text="Accumulated Movement: 0.000000 mm"
        )
        self.label_stage_speed.configure(
            text="Movement Speed: 0.000000 mm/s"
        )
    # -----------------------------------------------------------------------------
    # 7.11 UPDATE DRIVEN VS CALCULATED DISTANCE
    # -----------------------------------------------------------------------------

    #stage movement distance is compared with distance calculated from counted fringes
    def update_comparison_labels(self, driven_mm=None):
        if driven_mm is None:
            driven_mm = self.current_stage_movement_for_compare
        driven_distance_mm = abs(
            driven_mm
        )
        calculated_mm = (
            self.accumulated_fringes
            * self.fringe_distance_mm
        )
        difference_mm = driven_distance_mm - calculated_mm
        self.label_compare_driven.configure(
            text=f"Driven: {driven_distance_mm:.6f} mm"
        )
        self.label_compare_calculated.configure(
            text=f"Calculated from Fringes: {calculated_mm:.6f} mm"
        )
        self.label_compare_difference.configure(
            text=f"Difference: {difference_mm:.6f} mm"
        )
    # -----------------------------------------------------------------------------
    # 8.8 RUN STAGE MOTION BY PARAMETERS
    # -----------------------------------------------------------------------------

    def run_stage_motion_by_parameters(self):
        if not self.stage_connected:
            return
        current_position = self.stage.get_position()
        if MODE.lower().startswith("c"):
            self.stage.set_velocity(VELOCITY_MM_S)
            final_target = self.stage.clamp_position(current_position + TOTAL_DISTANCE_MM)
            self.stage_start_position = current_position
            self.stage_movement_before_move = self.total_stage_movement
            self.reset_stage_speed_tracking(current_position)
            self.after(
                0,
                lambda:
                self.status.configure(
                    text=(
                        f"Continuous move to {final_target:.6f} mm "
                        f"at {VELOCITY_MM_S} mm/s"
                    ),
                    text_color=TEXT_COLOR
                )
            )
            if not self.stage.move_absolute(final_target):
                self.after(
                    0,
                    lambda:
                    self.status.configure(
                        text="Stage move failed",
                        text_color=RED_COLOR
                    )
                )
                return
            while self.stage.is_moving and self.is_monitoring:
                pos = self.stage.get_position()
                moved = abs(pos - self.stage_start_position)
                self.after(
                    0,
                    lambda p=pos, m=moved, b=self.stage_movement_before_move:
                    self.update_stage_labels(p, m, b)
                )
                time.sleep(0.05)
            pos = self.stage.get_position()
            moved = abs(pos - self.stage_start_position)
            self.total_stage_movement = (
                self.stage_movement_before_move + moved
            )
            self.after(
                0,
                lambda p=pos:
                self.finish_stage_move(p)
            )
        else:
            self.stage.set_velocity(VELOCITY_MM_S_STEPPED)
            self.stage_start_position = current_position
            self.stage_movement_before_move = self.total_stage_movement
            self.reset_stage_speed_tracking(current_position)
            self.after(
                0,
                lambda:
                self.status.configure(
                    text=(
                        f"Stepped move: {STEPS} steps of "
                        f"{STEP_SIZE_MM} mm"
                    ),
                    text_color=TEXT_COLOR
                )
            )
            current_pos = current_position
            moved = 0.0
            for step in range(STEPS):
                if not self.is_monitoring:
                    break
                next_position = self.stage.clamp_position(
                    current_pos + STEP_SIZE_MM
                )
                self.after(
                    0,
                    lambda s=step, n=next_position:
                    self.status.configure(
                        text=(
                            f"Step {s + 1}/{STEPS}: "
                            f"move to {n:.7f} mm"
                        ),
                        text_color=TEXT_COLOR
                    )
                )
                if not self.stage.move_absolute(next_position):
                    self.after(
                        0,
                        lambda:
                        self.status.configure(
                            text="Move command failed",
                            text_color=RED_COLOR
                        )
                    )
                    break
                while self.stage.is_moving and self.is_monitoring:
                    time.sleep(0.01)
                step_distance = abs(next_position - current_pos)
                moved += step_distance
                current_pos = next_position
                self.total_stage_movement = (
                    self.stage_movement_before_move + moved
                )
                self.after(
                    0,
                    lambda p=current_pos, m=moved, b=self.stage_movement_before_move:
                    self.update_stage_labels(p, m, b)
                )
                if step < STEPS - 1:
                    time.sleep(STEP_PAUSE_S)
            self.after(
                0,
                lambda p=current_pos:
                self.finish_stage_move(p)
            )
    # -----------------------------------------------------------------------------
    # 7.7 MOVE STAGE DURING CALIBRATION
    # -----------------------------------------------------------------------------

    def calibration_stage_motion(self):
        try:
            if not self.stage_connected: # refuse movement commands when stage is not connected
                return
            start_pos = self.stage.get_position() # current stage position as movement start
            step_mm = 0.0001
            steps = 8
            # move forward in 4 steps
            for i in range(1, steps + 1):
                if not self.is_monitoring:
                    return
                target = start_pos + step_mm * i
                target = self.stage.clamp_position(target)
                if not self.stage.move_absolute(target):
                    return
                while self.stage.is_moving and self.is_monitoring:
                    time.sleep(0.01)
                time.sleep(0.25)
            # move back in 4 steps
            for i in range(steps - 1, -1, -1):
                if not self.is_monitoring:
                    return
                target = start_pos + step_mm * i
                target = self.stage.clamp_position(target)
                if not self.stage.move_absolute(target):
                    return
                while self.stage.is_moving and self.is_monitoring:
                    time.sleep(0.01)
                time.sleep(0.25)
        finally:
            self.after(0, self.finish_calibration_movement)
    # -----------------------------------------------------------------------------
    # 7.10 FINISH CALIBRATION RESET
    # -----------------------------------------------------------------------------

    def finish_calibration_movement(self):
        if self.stage_connected:
            current_pos = self.stage.get_position()
            self.reset_stage_movement_tracking(current_pos)
        else:
            self.reset_stage_movement_tracking(150.0)
        self.set_buttons_enabled(True)
        self.status.configure(
            text="Monitoring running",
            text_color=GREEN_COLOR
        )
    # -----------------------------------------------------------------------------
    # 9.1 SHUT DOWN HARDWARE CLEANLY
    # -----------------------------------------------------------------------------

    def on_close(self):
        self.is_monitoring = False
        try:
            self.diode.close()
        except Exception:
            pass
        try:
            self.stage.close()
        except Exception:
            pass
        self.destroy()

# -----------------------------------------------------------------------------
# 9. PROGRAM START
# -----------------------------------------------------------------------------

# 9. PROGRAM START
if __name__ == "__main__":
    app = SideApp()
    app.protocol(
        "WM_DELETE_WINDOW", # connect window close button to cleanup routine
        app.on_close
    )
    app.mainloop() # start the graphical application loop
