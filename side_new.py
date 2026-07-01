# TABLE OF CONTENTS
# 1. Basic settings
# 2. Imports
# 3. Physical constants and colors
# 4. SideApp class (UI)
# 5. Monitoring and reset
# 6. Translation stage control
# 7. Calibration
# 8. Diode loop and plotting
# 9. Cleanup and program start


# -----------------------------------------------------------------------------
# 1. BASIC SETTINGS
# -----------------------------------------------------------------------------

RAW_HISTORY_LENGTH = 300  # NEU: Max. Anzahl an Messwerten im Diagramm
STEP_PAUSE_S = 0.05  # NEU: Pause in Sekunden im Schrittbetrieb
#the number of consecutive dark or bright frames required to count a fringe, this is to filter out noise and avoid counting false fringes due to intensity fluctuations
REQUIRED_DARK_FRAMES = 3
REQUIRED_BRIGHT_FRAMES = 3
#after counting a fringe, the system will ignore any new fringes for this amount of time, this is to avoid counting multiple fringes if the intensity fluctuates around the threshold
FRINGE_COOLDOWN = 0.08
MODE = "continuous"  # NEU: Tisch-Bewegungsmodus (kontinuierlich/schrittweise)
VELOCITY_MM_S = 0.0006  # NEU: Tischgeschwindigkeit kontinuierlich (mm/s)
TOTAL_DISTANCE_MM = 13.0  # NEU: Gesamtweg kontinuierliche Fahrt (mm)
VELOCITY_MM_S_STEPPED = 1.00  # NEU: Tischgeschwindigkeit schrittweise (mm/s)
STEP_SIZE_MM = 0.00001  # NEU: Schrittweite im Schrittbetrieb (mm)
STEPS = 100  # NEU: Anzahl Schritte im Schrittbetrieb

# -----------------------------------------------------------------------------
# 2. IMPORTS
# -----------------------------------------------------------------------------

import threading # so that camera and stage can run without freezing the UI
import time # for timestamps
import customtkinter as ctk # pythons standard UI library
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # NEU: Matplotlib Tkinter-Anbindung laden
    from matplotlib.figure import Figure  # NEU: Matplotlib-Klasse für Diagramme laden
except ImportError:  # NEU: Fehler abfangen, falls Matplotlib fehlt
    Figure = None  # NEU: Diagramm-Objekt nullen bei fehlendem Matplotlib
    FigureCanvasTkAgg = None  # NEU: Canvas-Objekt nullen bei fehlendem Matplotlib
from diode_handler import (  # NEU: Kommunikations-Bibliothek der Photodiode laden
    CALIBRATION_SECONDS,  # NEU: Dauer der Kalibrierung (Sekunden) laden
    LASER_WAVELENGTH_NM,  # NEU: Laserwellenlänge (Nanometer) laden
    PHOTODIODE_CHANNEL,  # NEU: Messkanal der Photodiode laden
    SAMPLE_INTERVAL_S,  # NEU: Abtastintervall der Diode laden
    SingleDiodeHandler,  # NEU: Klasse für Photodioden-Erfassung laden
    compute_fringe_distance_mm  # NEU: Streifenabstands-Formel laden
)
from stage_controller import StageController

# -----------------------------------------------------------------------------
# 3. PHYSICAL CONSTANTS
# -----------------------------------------------------------------------------

SPEED_OF_LIGHT_MM_PS = 0.299792458
DEFAULT_STAGE_SPEED_MM_S = 0.0006  # NEU: Standard-Tischgeschwindigkeit (mm/s)
def compute_quarter_wavelength_step_mm(wavelength_nm):  # NEU: Berechnet Lambda/4-Schritte
    return (wavelength_nm / 4) / 1_000_000  # NEU: Rechnet Lambda/4 in Millimeter um

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

class SideApp(ctk.CTk):  # NEU: Hauptklasse für Photodioden-Version
    # -----------------------------------------------------------------------------
    # 4.1 INITIALIZATION
    # -----------------------------------------------------------------------------

    #ctk.CTk is the base class for the customtkinter window, here we inherit our InterferometerApp class from it
    def __init__(self):
        #init method always gets called to create a new instance of the class
        super().__init__()
        self.title("Single Photodiode Fringe Monitor")  # NEU: Titel der Photodioden-App festlegen
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
        self.measurement_thread = None  # NEU: Erstellt den Hintergrund-Erfassungsthread
        #for the 5s calibration at the beginning
        self.calibrating = False
        self.latest_sample = None  # NEU: Initialisierung der Photodioden-App
        self.latest_voltage = 0.0  # NEU: Initialisierung der Photodioden-App
        self.last_error_text = None  # NEU: Initialisierung der Photodioden-App
        self.raw_voltage_history = []  # NEU: Initialisierung der Photodioden-App
        self.smoothed_voltage_history = []  # NEU: Initialisierung der Photodioden-App
        self.accumulated_fringes = 0
        #a bright state only counts after darkness
        self.was_dark = False
        #number of consecutive dark/bright fringes
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0  # NEU: Initialisierung der Photodioden-App
        self.dark_threshold = 0.0  # NEU: Initialisierung der Photodioden-App
        self.bright_threshold = 0.0  # NEU: Initialisierung der Photodioden-App
        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
        self.fringe_distance_mm = compute_fringe_distance_mm(  # NEU: Streifenabstands-Formel laden
            self.laser_wavelength_nm
        )
        self.quarter_wavelength_step_mm = compute_quarter_wavelength_step_mm(  # NEU: Initialisierung der Photodioden-App
            self.laser_wavelength_nm
        )
        self.diode = SingleDiodeHandler()  # NEU: Klasse für Photodioden-Erfassung laden
        #same for the stage
        self.stage = StageController()
        self.stage_connected = self.stage.connect()  # NEU: Initialisierung der Photodioden-App
        #stores values for all the start positions
        self.stage_start_position = 0.0
        self.stage_reference_position = 0.0
        self.total_stage_movement = 0.0
        self.stage_movement_before_move = 0.0
        self.current_stage_movement_for_compare = 0.0
        self.last_stage_speed_time = None  # NEU: Initialisierung der Photodioden-App
        self.last_stage_speed_position = None  # NEU: Initialisierung der Photodioden-App
        self.build_ui()  # NEU: Initialisierung der Photodioden-App
        self.update_comparison_labels() # renewing the text in the UI matching the initial update of the comparison labels with 0 values using e.g self.current_stage_movement_for_compare which is 0 at the beginning
        self.update_stage_position_once() # reads the current stage position and updates the label, this is important to have the correct position at the beginning
        self.all_buttons = [
            self.restart_btn,
            self.wavelength_button,
            self.speed_button,  # NEU: Initialisierung der Photodioden-App
            self.btn_target_abs,
            self.btn_target_rel,
            self.btn_stop,  # NEU: Initialisierung der Photodioden-App
            self.btn_min,
            self.btn_left,
            self.btn_center,
            self.btn_right,
            self.btn_max  # NEU: Initialisierung der Photodioden-App
        ]
    # -----------------------------------------------------------------------------
    # 4.1.2 UI BUILD
    # -----------------------------------------------------------------------------

    def build_ui(self):  # NEU: Oberfläche für Photodiode aufbauen
        ctk.CTkLabel(
            self.scroll,
            text="Single Photodiode Fringe Monitor",  # NEU: Titel der Photodioden-App festlegen
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
        self.wavelength_entry.insert(  # NEU: Oberfläche für Photodiode aufbauen
            0,
            f"{self.laser_wavelength_nm:.1f}"  # NEU: Oberfläche für Photodiode aufbauen
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
            text="Schrittweite / Step size:",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 0))  # NEU: Oberfläche für Photodiode aufbauen
        self.step_entry = ctk.CTkEntry(
            self.stage_frame,
            placeholder_text="Step size in mm",
            width=250
        )
        self.step_entry.pack(pady=1)
        self.step_entry.insert(
            0,
            f"{self.quarter_wavelength_step_mm:.9f}"  # NEU: Oberfläche für Photodiode aufbauen
        )
        ctk.CTkLabel(
            self.stage_frame,
            text="Geschwindigkeit / Velocity:",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 0))  # NEU: Oberfläche für Photodiode aufbauen
        self.speed_entry = ctk.CTkEntry(  # NEU: Eingabefeld für Tischgeschwindigkeit
            self.stage_frame,
            placeholder_text="Movement speed in mm/s",  # NEU: Oberfläche für Photodiode aufbauen
            width=250
        )
        self.speed_entry.pack(pady=1)  # NEU: Oberfläche für Photodiode aufbauen
        stage_velocity = None  # NEU: Oberfläche für Photodiode aufbauen
        if self.stage_connected:
            stage_velocity = self.stage.set_velocity()  # NEU: Oberfläche für Photodiode aufbauen
        if stage_velocity is None:  # NEU: Oberfläche für Photodiode aufbauen
            stage_velocity = DEFAULT_STAGE_SPEED_MM_S  # NEU: Oberfläche für Photodiode aufbauen
        self.speed_entry.insert(  # NEU: Oberfläche für Photodiode aufbauen
            0,
            f"{stage_velocity:.6f}"  # NEU: Oberfläche für Photodiode aufbauen
        )
        self.speed_button = ctk.CTkButton(  # NEU: Button zum Setzen der Geschwindigkeit
            self.stage_frame,
            text="Set speed",  # NEU: Oberfläche für Photodiode aufbauen
            width=120,
            command=self.apply_stage_speed,  # NEU: Oberfläche für Photodiode aufbauen
            fg_color=TEXT_COLOR
        )
        self.speed_button.pack(pady=1)  # NEU: Oberfläche für Photodiode aufbauen
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
            text="Zielposition oder Distanz / Target or Distance (mm):",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 11, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 0))  # NEU: Oberfläche für Photodiode aufbauen
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
            command=self.move_to_target,  # NEU: Oberfläche für Photodiode aufbauen
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
            command=self.move_distance,  # NEU: Oberfläche für Photodiode aufbauen
            fg_color=TEXT_COLOR
        )
        self.btn_target_rel.grid(
            row=0,
            column=1,
            padx=1
        )
        self.btn_stop = ctk.CTkButton(  # NEU: Button zum Stoppen des Tisches
            self.target_button_frame,
            text="STOP STAGE",  # NEU: Oberfläche für Photodiode aufbauen
            width=140,
            command=self.stop_stage,  # NEU: Oberfläche für Photodiode aufbauen
            fg_color=RED_COLOR,  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 11, "bold")
        )
        self.btn_stop.grid(  # NEU: Oberfläche für Photodiode aufbauen
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
        self.label_stage_speed = ctk.CTkLabel(  # NEU: Anzeige der berechneten Geschwindigkeit
            self.stage_frame,
            text="Movement Speed: 0.000000 mm/s",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_stage_speed.pack(pady=0)  # NEU: Oberfläche für Photodiode aufbauen
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
            text="Distance from Fringes: 0.000 um",  # NEU: Oberfläche für Photodiode aufbauen
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
        self.label_calibration_offset = ctk.CTkLabel(  # NEU: Anzeige der Dunkelschwelle
            self.frame,
            text="Dark Threshold: waiting",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_calibration_offset.pack(pady=0)  # NEU: Oberfläche für Photodiode aufbauen
        self.label_calibration_scale = ctk.CTkLabel(  # NEU: Anzeige der Hellschwelle
            self.frame,
            text="Bright Threshold: waiting",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_calibration_scale.pack(pady=0)  # NEU: Oberfläche für Photodiode aufbauen
        self.label_sample_count = ctk.CTkLabel(  # NEU: Oberfläche für Photodiode aufbauen
            self.frame,
            text="Accumulated Fringes Count: 0",
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_sample_count.pack(pady=0)  # NEU: Oberfläche für Photodiode aufbauen
        self.label_min_voltage = ctk.CTkLabel(  # NEU: Anzeige der minimalen Diodenspannung
            self.frame,
            text="Min Voltage: n/a",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_min_voltage.pack(pady=0)  # NEU: Oberfläche für Photodiode aufbauen
        self.label_max_voltage = ctk.CTkLabel(  # NEU: Anzeige der maximalen Diodenspannung
            self.frame,
            text="Max Voltage: n/a",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_max_voltage.pack(pady=0)  # NEU: Oberfläche für Photodiode aufbauen
        self.label_raw = ctk.CTkLabel(  # NEU: Anzeige der rohen Spannung
            self.frame,
            text="Raw Voltage: 0.000000 V",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_raw.pack(pady=0)  # NEU: Oberfläche für Photodiode aufbauen
        self.label_norm = ctk.CTkLabel(  # NEU: Anzeige der normierten Spannung
            self.frame,
            text="Normalized Voltage: 0.0000",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_norm.pack(pady=0)  # NEU: Oberfläche für Photodiode aufbauen
        self.label_calibration = ctk.CTkLabel(  # NEU: Anzeige des Kalibrierungsfortschritts
            self.frame,
            text="Calibration: waiting",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 10),
            text_color=TEXT_COLOR
        )
        self.label_calibration.pack(pady=0)  # NEU: Oberfläche für Photodiode aufbauen
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
            text="Stage Movement",  # NEU: Oberfläche für Photodiode aufbauen
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
            text="Calculated from Fringes: 0.000000 mm",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 11),
            text_color=TEXT_COLOR
        )
        self.label_compare_calculated.pack(pady=0)
        self.label_compare_difference = ctk.CTkLabel(
            self.compare_frame,
            text="Difference: n/a",  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 13, "bold"),
            text_color=TEXT_COLOR
        )
        self.label_compare_difference.pack(pady=0)
        channel_text = f"Channel: photodiode={PHOTODIODE_CHANNEL}"  # NEU: Messkanal der Photodiode laden
        ctk.CTkLabel(
            self.scroll,
            text=channel_text,  # NEU: Oberfläche für Photodiode aufbauen
            font=("Arial", 10),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 2))
        self.plot_frame = ctk.CTkFrame(  # NEU: Rahmen (Frame) für das Diagramm anlegen
            self.scroll,
            fg_color="#EEEEEE"
        )
        self.plot_frame.pack(  # NEU: Diagramm-Rahmen in GUI einbetten
            fill="both",
            expand=True,
            padx=5,
            pady=(4, 10)  # NEU: Oberfläche für Photodiode aufbauen
        )
        ctk.CTkLabel(
            self.plot_frame,  # NEU: Oberfläche für Photodiode aufbauen
            text="Live Raw Voltage",  # NEU: Überschrift des Diagramms erstellen
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(5, 2))
        self.build_plot()  # NEU: Live-Diagramm initialisieren
    # -----------------------------------------------------------------------------
    # 4.1.3 PLOT BUILD
    # -----------------------------------------------------------------------------

    def build_plot(self):  # NEU: Erstellt Matplotlib-Diagramm und bindet es in GUI ein
        if Figure is None or FigureCanvasTkAgg is None:  # NEU: Diagramm-Setup
            self.plot_axis = None  # NEU: Koordinatensystem für Messdaten anlegen
            self.plot_canvas = None  # NEU: Diagramm in Tkinter-Canvas einbetten
            ctk.CTkLabel(
                self.plot_frame,  # NEU: Diagramm-Setup
                text="Matplotlib is required for live voltage plotting.",  # NEU: Diagramm-Setup
                font=("Arial", 11),
                text_color=RED_COLOR
            ).pack(pady=8)  # NEU: Diagramm-Setup
            return
        self.plot_figure = Figure(  # NEU: Matplotlib Figure-Objekt erstellen
            figsize=(8, 3),  # NEU: Diagramm-Setup
            dpi=100  # NEU: Diagramm-Setup
        )
        self.plot_axis = self.plot_figure.add_subplot(111)  # NEU: Koordinatensystem für Messdaten anlegen
        self.plot_axis.set_title("Raw diode voltage")  # NEU: Titel des Diagramms setzen
        self.plot_axis.set_xlabel("Samples")  # NEU: Beschriftung der X-Achse setzen
        self.plot_axis.set_ylabel("Voltage")  # NEU: Beschriftung der Y-Achse setzen
        self.plot_axis.grid(  # NEU: Hintergrundgitter im Diagramm aktivieren
            True,  # NEU: Diagramm-Setup
            linestyle=":",  # NEU: Diagramm-Setup
            alpha=0.6  # NEU: Diagramm-Setup
        )
        self.plot_line_voltage = self.plot_axis.plot(  # NEU: Datenlinie für Diodenspannung anlegen
            [],  # NEU: Diagramm-Setup
            [],  # NEU: Diagramm-Setup
            color="blue",  # NEU: Diagramm-Setup
            label="photodiode raw"  # NEU: Diagramm-Setup
        )[0]  # NEU: Diagramm-Setup
        self.plot_axis.legend(loc="upper right")  # NEU: Diagramm-Setup
        self.plot_canvas = FigureCanvasTkAgg(  # NEU: Diagramm in Tkinter-Canvas einbetten
            self.plot_figure,  # NEU: Diagramm-Setup
            master=self.plot_frame  # NEU: Diagramm-Setup
        )
        self.plot_canvas.draw()  # NEU: Diagramm zum ersten Mal zeichnen
        self.plot_canvas.get_tk_widget().pack(  # NEU: Diagramm-Setup
            fill="both",
            expand=True,
            padx=8,  # NEU: Diagramm-Setup
            pady=8  # NEU: Diagramm-Setup
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
            self.stop_monitoring()  # NEU: Komponente der Photodioden-Klasse
        else:
            self.start_monitoring()  # NEU: Komponente der Photodioden-Klasse
    # -----------------------------------------------------------------------------
    # 5.1.1 START MONITORING HELPER
    # -----------------------------------------------------------------------------

    def start_monitoring(self):  # NEU: Initialisiert Hardware & startet Messungen
        if (
            self.measurement_thread is not None  # NEU: Photodioden-Erfassung starten
            and self.measurement_thread.is_alive()  # NEU: Photodioden-Erfassung starten
        ):
            return
        self.restart_values_only()
        self.diode = SingleDiodeHandler()  # NEU: Klasse für Photodioden-Erfassung laden
        self.is_monitoring = True
        self.calibrating = True
        self.last_error_text = None  # NEU: Photodioden-Erfassung starten
        self.btn.configure(
            text="STOP MONITORING",
            fg_color=RED_COLOR
        )
        self.status.configure(
            text="Status: connecting NI...",  # NEU: Photodioden-Erfassung starten
            text_color=ORANGE_COLOR
        )
        self.set_buttons_enabled(False)
        self.measurement_thread = threading.Thread(  # NEU: Erstellt den Hintergrund-Erfassungsthread
            target=self.loop,
            daemon=True
        )
        self.measurement_thread.start()  # NEU: Erfassungsthread starten
    # -----------------------------------------------------------------------------
    # 5.1.2 STOP MONITORING HELPER
    # -----------------------------------------------------------------------------

    def stop_monitoring(self):  # NEU: Erfassung stoppen & Tisch anhalten
        self.is_monitoring = False
        self.calibrating = False
        if self.stage_connected and self.stage.is_moving:
            self.stage.stop()
        self.status.configure(
            text="Status: stopping...",  # NEU: Photodioden-Erfassung stoppen
            text_color=ORANGE_COLOR
        )
    # -----------------------------------------------------------------------------
    # 8.1 DIODE LOOP AND MEASUREMENT
    # -----------------------------------------------------------------------------

    def loop(self):
        try:
            self.diode.connect()  # NEU: Messdaten-Erfassungsschleife
            self.after(
                0,
                lambda:
                self.status.configure(
                    text=f"Status: calibrating {CALIBRATION_SECONDS:.1f}s...",  # NEU: Dauer der Kalibrierung (Sekunden) laden
                    text_color=ORANGE_COLOR
                )
            )
            if self.stage_connected:
                threading.Thread(
                    target=self.calibration_stage_motion,
                    daemon=True
                ).start()
            calibration = self.diode.calibrate(  # NEU: Messdaten-Erfassungsschleife
                seconds=CALIBRATION_SECONDS,  # NEU: Dauer der Kalibrierung (Sekunden) laden
                sample_interval_s=SAMPLE_INTERVAL_S,  # NEU: Abtastintervall der Diode laden
                should_continue=lambda: self.is_monitoring,  # NEU: Messdaten-Erfassungsschleife
                sample_callback=self.handle_calibration_sample  # NEU: Messdaten-Erfassungsschleife
            )
            if not self.is_monitoring:
                return
            self.calibrating = False
            if calibration is not None:  # NEU: Messdaten-Erfassungsschleife
                self.after(
                    0,
                    lambda c=calibration:  # NEU: Messdaten-Erfassungsschleife
                    self.finish_calibration_display(c)  # NEU: Messdaten-Erfassungsschleife
                )
            while self.is_monitoring:
                sample = self.diode.read()  # NEU: Messdaten-Erfassungsschleife
                self.after(
                    0,
                    lambda s=sample:  # NEU: Messdaten-Erfassungsschleife
                    self.update_sample_display(s)  # NEU: Messdaten-Erfassungsschleife
                )
                time.sleep(SAMPLE_INTERVAL_S)  # NEU: Abtastintervall der Diode laden
        except Exception as error:  # NEU: Messdaten-Erfassungsschleife
            self.last_error_text = str(error)  # NEU: Messdaten-Erfassungsschleife
            self.after(
                0,
                lambda e=error:  # NEU: Messdaten-Erfassungsschleife
                self.show_error(e)  # NEU: Messdaten-Erfassungsschleife
            )
        finally:
            self.is_monitoring = False
            self.calibrating = False
            try:
                self.diode.close()  # NEU: Messdaten-Erfassungsschleife
            except Exception:  # NEU: Messdaten-Erfassungsschleife
                pass
            self.after(
                0,
                self.finish_stopped_ui  # NEU: Messdaten-Erfassungsschleife
            )
    # -----------------------------------------------------------------------------
    # 7.8 HANDLE CALIBRATION SAMPLE
    # -----------------------------------------------------------------------------

    def handle_calibration_sample(self, raw_voltage, elapsed_s, total_s):  # NEU: Kalibrierungs-Messdaten an UI senden
        self.after(
            0,
            lambda v=raw_voltage, e=elapsed_s, t=total_s:  # NEU: Kalibrierungswert an UI leiten
            self.update_calibration_progress(v, e, t)  # NEU: Kalibrierungswert an UI leiten
        )
    # -----------------------------------------------------------------------------
    # 7.8.1 UPDATE CALIBRATION PROGRESS
    # -----------------------------------------------------------------------------

    def update_calibration_progress(  # NEU: Kalibrierungsfortschritt im UI anzeigen
        self,
        raw_voltage,  # NEU: Kalibrierungsfortschritt anzeigen
        elapsed_s,  # NEU: Kalibrierungsfortschritt anzeigen
        total_s  # NEU: Kalibrierungsfortschritt anzeigen
    ):
        self.append_raw_history(  # NEU: Kalibrierungsfortschritt anzeigen
            raw_voltage  # NEU: Kalibrierungsfortschritt anzeigen
        )
        self.update_plot()  # NEU: Kalibrierungsfortschritt anzeigen
        self.label_raw.configure(  # NEU: Kalibrierungsfortschritt anzeigen
            text=f"Raw Voltage: {raw_voltage:+.6f} V"  # NEU: Kalibrierungsfortschritt anzeigen
        )
        self.label_calibration.configure(  # NEU: Kalibrierungsfortschritt anzeigen
            text=f"Calibration: {elapsed_s:.1f}/{total_s:.1f}s"  # NEU: Kalibrierungsfortschritt anzeigen
        )
    # -----------------------------------------------------------------------------
    # 7.8.2 FINISH CALIBRATION DISPLAY
    # -----------------------------------------------------------------------------

    def finish_calibration_display(self, calibration):  # NEU: Hell/Dunkel-Schwellenwerte berechnen & setzen
        value_range = calibration.max_voltage - calibration.min_voltage  # NEU: Kalibrierungswerte anzeigen
        self.dark_threshold = (
            calibration.min_voltage  # NEU: Kalibrierungswerte anzeigen
            + value_range * 0.125
        )
        self.bright_threshold = (
            calibration.max_voltage  # NEU: Kalibrierungswerte anzeigen
            - value_range * 0.40
        )
        self.label_calibration.configure(  # NEU: Kalibrierungswerte anzeigen
            text=(
                f"Calibration min/max: "  # NEU: Kalibrierungswerte anzeigen
                f"{calibration.min_voltage:+.6f}/"  # NEU: Kalibrierungswerte anzeigen
                f"{calibration.max_voltage:+.6f} V"  # NEU: Kalibrierungswerte anzeigen
            ),
            text_color=GREEN_COLOR
        )
        self.label_calibration_offset.configure(  # NEU: Kalibrierungswerte anzeigen
            text=f"Dark Threshold: {self.dark_threshold:+.6f} V"  # NEU: Kalibrierungswerte anzeigen
        )
        self.label_calibration_scale.configure(  # NEU: Kalibrierungswerte anzeigen
            text=f"Bright Threshold: {self.bright_threshold:+.6f} V"  # NEU: Kalibrierungswerte anzeigen
        )
        self.label_min_voltage.configure(  # NEU: Kalibrierungswerte anzeigen
            text=f"Min Voltage: {calibration.min_voltage:+.6f} V"  # NEU: Kalibrierungswerte anzeigen
        )
        self.label_max_voltage.configure(  # NEU: Kalibrierungswerte anzeigen
            text=f"Max Voltage: {calibration.max_voltage:+.6f} V"  # NEU: Kalibrierungswerte anzeigen
        )
        self.status.configure(
            text="Status: monitoring running",  # NEU: Kalibrierungswerte anzeigen
            text_color=GREEN_COLOR
        )
    # -----------------------------------------------------------------------------
    # 8.3 SHOW CURRENT VOLTAGE AND DISTANCE
    # -----------------------------------------------------------------------------

    def update_sample_display(self, sample):  # NEU: Messwert verarbeiten, Fringes zählen & Plot updaten
        self.latest_sample = sample  # NEU: Messwert verarbeiten und anzeigen
        self.latest_voltage = sample.raw_voltage  # NEU: Messwert verarbeiten und anzeigen
        fringe_counted = self.update_accumulated_fringes(  # NEU: Messwert verarbeiten und anzeigen
            sample.raw_voltage  # NEU: Messwert verarbeiten und anzeigen
        )
        self.append_raw_history(  # NEU: Messwert verarbeiten und anzeigen
            sample.raw_voltage  # NEU: Messwert verarbeiten und anzeigen
        )
        self.update_plot()  # NEU: Messwert verarbeiten und anzeigen
        distance_mm = self.accumulated_fringes * self.fringe_distance_mm  # NEU: Messwert verarbeiten und anzeigen
        distance_um = distance_mm * 1000  # NEU: Messwert verarbeiten und anzeigen
        time_ps = (2 * distance_mm) / SPEED_OF_LIGHT_MM_PS  # NEU: Messwert verarbeiten und anzeigen
        self.label_um.configure(
            text=f"Distance from Fringes: {distance_um:.6f} um"  # NEU: Messwert verarbeiten und anzeigen
        )
        self.label_ps.configure(
            text=f"Time Delay: {time_ps:.4f} ps"  # NEU: Messwert verarbeiten und anzeigen
        )
        self.label_sample_count.configure(  # NEU: Messwert verarbeiten und anzeigen
            text=f"Accumulated Fringes Count: {self.accumulated_fringes}"  # NEU: Messwert verarbeiten und anzeigen
        )
        self.label_raw.configure(  # NEU: Messwert verarbeiten und anzeigen
            text=f"Raw Voltage: {sample.raw_voltage:+.6f} V"  # NEU: Messwert verarbeiten und anzeigen
        )
        self.label_norm.configure(  # NEU: Messwert verarbeiten und anzeigen
            text=f"Normalized Voltage: {sample.normalized_voltage:+.4f}"  # NEU: Messwert verarbeiten und anzeigen
        )
        if fringe_counted:
            self.label_sample_count.configure(  # NEU: Messwert verarbeiten und anzeigen
                text_color=GREEN_COLOR
            )
            self.after(
                250,
                lambda:
                self.label_sample_count.configure(  # NEU: Messwert verarbeiten und anzeigen
                    text_color=TEXT_COLOR
                )
            )
        self.update_comparison_labels()
    # -----------------------------------------------------------------------------
    # 8.2 DETECT AND COUNT FRINGES
    # -----------------------------------------------------------------------------

    def update_accumulated_fringes(self, voltage):  # NEU: Streifen (Fringes) zählen
        self.smoothed_voltage_history.append(  # NEU: Streifen (Fringes) zählen
            voltage  # NEU: Streifen (Fringes) zählen
        )
        if len(self.smoothed_voltage_history) > 5:  # NEU: Streifen (Fringes) zählen
            self.smoothed_voltage_history.pop(0)  # NEU: Streifen (Fringes) zählen
        smooth_voltage = (  # NEU: Streifen (Fringes) zählen
            sum(self.smoothed_voltage_history)  # NEU: Streifen (Fringes) zählen
            / len(self.smoothed_voltage_history)  # NEU: Streifen (Fringes) zählen
        )
        if smooth_voltage < self.dark_threshold:  # NEU: Streifen (Fringes) zählen
            self.dark_counter += 1
        else:
            self.dark_counter = 0
        if self.dark_counter >= REQUIRED_DARK_FRAMES:
            self.was_dark = True
        if smooth_voltage > self.bright_threshold:  # NEU: Streifen (Fringes) zählen
            self.bright_counter += 1
        else:
            self.bright_counter = 0
        cooldown_ok = (
            time.time() - self.last_count_time
        ) > FRINGE_COOLDOWN
        if (
            self.was_dark
            and self.bright_counter >= REQUIRED_BRIGHT_FRAMES  # NEU: Streifen (Fringes) zählen
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

    def append_raw_history(self, raw_voltage):  # NEU: Fügt Messwert zur Diagrammhistorie hinzu
        self.raw_voltage_history.append(raw_voltage)  # NEU: Spannungsverlauf protokollieren
        if len(self.raw_voltage_history) > RAW_HISTORY_LENGTH:  # NEU: Spannungsverlauf protokollieren
            self.raw_voltage_history.pop(0)  # NEU: Spannungsverlauf protokollieren
    # -----------------------------------------------------------------------------
    # 8.5 LIVE VOLTAGE PLOT UPDATE
    # -----------------------------------------------------------------------------

    def update_plot(self, reset=False):  # NEU: Aktualisiert Diagrammdaten aus Historie
        if self.plot_axis is None:  # NEU: Diagramm aktualisieren
            return
        if reset:  # NEU: Diagramm aktualisieren
            self.plot_line_voltage.set_data([], [])  # NEU: Neue Plot-Daten übergeben
            self.plot_axis.relim()  # NEU: Grenzen des Diagramms neu berechnen
            self.plot_axis.autoscale_view()  # NEU: Achsen an neue Daten anpassen
            self.plot_canvas.draw_idle()  # NEU: Diagramm zum ersten Mal zeichnen
            return
        x = list(  # NEU: Diagramm aktualisieren
            range(len(self.raw_voltage_history))  # NEU: Diagramm aktualisieren
        )
        self.plot_line_voltage.set_data(  # NEU: Neue Plot-Daten übergeben
            x,  # NEU: Diagramm aktualisieren
            self.raw_voltage_history  # NEU: Diagramm aktualisieren
        )
        self.plot_axis.relim()  # NEU: Grenzen des Diagramms neu berechnen
        self.plot_axis.autoscale_view()  # NEU: Achsen an neue Daten anpassen
        self.plot_canvas.draw_idle()  # NEU: Diagramm zum ersten Mal zeichnen
    # -----------------------------------------------------------------------------
    # 8.6 SHOW MONITORING ERROR
    # -----------------------------------------------------------------------------

    def show_error(self, error):  # NEU: Fehlermeldung anzeigen
        self.status.configure(
            text=f"Status: {error}",  # NEU: Fehlermeldung anzeigen
            text_color=RED_COLOR
        )
    # -----------------------------------------------------------------------------
    # 8.7 RESET UI AFTER MONITORING STOPS
    # -----------------------------------------------------------------------------

    def finish_stopped_ui(self):  # NEU: Steuerknöpfe und Status bei Stopp zurücksetzen
        self.btn.configure(
            text="START MONITORING",
            fg_color=TEXT_COLOR
        )
        if self.last_error_text:  # NEU: UI nach Stopp zurücksetzen
            self.status.configure(
                text=f"Status: {self.last_error_text}",  # NEU: UI nach Stopp zurücksetzen
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
        if self.diode is not None:  # NEU: Komponente der Photodioden-Klasse
            self.diode.counter.reset()  # NEU: Komponente der Photodioden-Klasse
        self.latest_sample = None  # NEU: Komponente der Photodioden-Klasse
        self.latest_voltage = 0.0  # NEU: Komponente der Photodioden-Klasse
        self.raw_voltage_history = []  # NEU: Komponente der Photodioden-Klasse
        self.smoothed_voltage_history = []  # NEU: Komponente der Photodioden-Klasse
        #defines what the values should look like after pressing reset
        self.accumulated_fringes = 0
        self.was_dark = False
        self.dark_counter = 0
        self.bright_counter = 0
        self.last_count_time = 0.0  # NEU: Komponente der Photodioden-Klasse
        self.reset_stage_movement_tracking() # function defined later
        self.label_um.configure(
            text="Distance from Fringes: 0.000 um"  # NEU: Komponente der Photodioden-Klasse
        )
        self.label_ps.configure(
            text="Time Delay: 0.0000 ps"
        )
        self.label_calibration_offset.configure(  # NEU: Komponente der Photodioden-Klasse
            text="Dark Threshold: waiting"  # NEU: Komponente der Photodioden-Klasse
        )
        self.label_calibration_scale.configure(  # NEU: Komponente der Photodioden-Klasse
            text="Bright Threshold: waiting"  # NEU: Komponente der Photodioden-Klasse
        )
        self.label_sample_count.configure(  # NEU: Komponente der Photodioden-Klasse
            text="Accumulated Fringes Count: 0",
            text_color=TEXT_COLOR
        )
        self.label_min_voltage.configure(  # NEU: Komponente der Photodioden-Klasse
            text="Min Voltage: n/a"  # NEU: Komponente der Photodioden-Klasse
        )
        self.label_max_voltage.configure(  # NEU: Komponente der Photodioden-Klasse
            text="Max Voltage: n/a"  # NEU: Komponente der Photodioden-Klasse
        )
        self.label_raw.configure(  # NEU: Komponente der Photodioden-Klasse
            text="Raw Voltage: 0.000000 V"  # NEU: Komponente der Photodioden-Klasse
        )
        self.label_norm.configure(  # NEU: Komponente der Photodioden-Klasse
            text="Normalized Voltage: 0.0000"  # NEU: Komponente der Photodioden-Klasse
        )
        self.label_calibration.configure(  # NEU: Komponente der Photodioden-Klasse
            text="Calibration: waiting",  # NEU: Komponente der Photodioden-Klasse
            text_color=TEXT_COLOR
        )
        self.update_plot(reset=True)  # NEU: Komponente der Photodioden-Klasse
        self.update_comparison_labels(0.0)
    def parse_entry_float(self, entry):  # NEU: Parst Eingabewerte sicher als float
        return float(  # NEU: Text in Float-Zahl umwandeln
            entry.get().replace(",", ".")  # NEU: Text in Float-Zahl umwandeln
        )
    # -----------------------------------------------------------------------------
    # 5.6 READ STEP SIZE FROM THE UI
    # -----------------------------------------------------------------------------

    def get_step_size(self):
        #convert the user input from the UI into something readable for the program
        try:
            value = self.parse_entry_float(  # NEU: Komponente der Photodioden-Klasse
                self.step_entry  # NEU: Komponente der Photodioden-Klasse
            )
            value = abs(value)  # NEU: Komponente der Photodioden-Klasse
            if value <= 0:  # NEU: Komponente der Photodioden-Klasse
                raise ValueError  # NEU: Komponente der Photodioden-Klasse
            return value  # NEU: Komponente der Photodioden-Klasse
        except ValueError:
            self.status.configure(
                text="Status: invalid step size",  # NEU: Komponente der Photodioden-Klasse
                text_color=RED_COLOR
            )
            return 0.0001 # safe default size when step size invalid
    # -----------------------------------------------------------------------------
    # 5.6.1 READ STAGE SPEED FROM THE UI
    # -----------------------------------------------------------------------------

    def get_stage_speed(self):  # NEU: Liest und prüft Geschwindigkeitseingabe
        try:
            value = self.parse_entry_float(  # NEU: Geschwindigkeit auslesen
                self.speed_entry  # NEU: Geschwindigkeit auslesen
            )
            value = abs(value)  # NEU: Geschwindigkeit auslesen
            if value <= 0:  # NEU: Geschwindigkeit auslesen
                raise ValueError  # NEU: Geschwindigkeit auslesen
            return value  # NEU: Geschwindigkeit auslesen
        except ValueError:
            self.status.configure(
                text="Status: invalid movement speed",  # NEU: Geschwindigkeit auslesen
                text_color=RED_COLOR
            )
            return None  # NEU: Geschwindigkeit auslesen
    # -----------------------------------------------------------------------------
    # 5.8 APPLY A NEW LASER WAVELENGTH
    # -----------------------------------------------------------------------------

    def apply_wavelength(self):
        # get the new laser wavelenght from the UI
        try:
            wavelength_nm = self.parse_entry_float(  # NEU: Komponente der Photodioden-Klasse
                self.wavelength_entry  # NEU: Komponente der Photodioden-Klasse
            )
        except ValueError:
            self.status.configure(
                text="Invalid wavelength value",
                text_color=RED_COLOR
            )
            return
        if wavelength_nm <= 0:  # NEU: Komponente der Photodioden-Klasse
            self.status.configure(
                text="Wavelength must be positive",  # NEU: Komponente der Photodioden-Klasse
                text_color=RED_COLOR
            )
            return
        self.laser_wavelength_nm = wavelength_nm
        self.fringe_distance_mm = compute_fringe_distance_mm(  # NEU: Streifenabstands-Formel laden
            self.laser_wavelength_nm
        )
        self.quarter_wavelength_step_mm = compute_quarter_wavelength_step_mm(  # NEU: Komponente der Photodioden-Klasse
            self.laser_wavelength_nm
        )
        #clear old suggested stepsize
        self.step_entry.delete(0, "end")
        self.step_entry.insert(
            0,
            f"{self.quarter_wavelength_step_mm:.9f}"  # NEU: Komponente der Photodioden-Klasse
        )
        self.status.configure(
            text=f"Wavelength set to {self.laser_wavelength_nm:.1f} nm",
            text_color=GREEN_COLOR
        )
    # -----------------------------------------------------------------------------
    # 5.6.2 APPLY STAGE SPEED
    # -----------------------------------------------------------------------------

    def apply_stage_speed(self, update_status=True):  # NEU: Setzt Tischgeschwindigkeit auf Eingabewert
        speed_mm_s = self.get_stage_speed()  # NEU: Geschwindigkeit anwenden
        if speed_mm_s is None:  # NEU: Geschwindigkeit anwenden
            return False
        self.speed_entry.delete(0, "end")  # NEU: Geschwindigkeit anwenden
        self.speed_entry.insert(  # NEU: Geschwindigkeit anwenden
            0,
            f"{speed_mm_s:.6f}"  # NEU: Geschwindigkeit anwenden
        )
        if not self.stage_connected:
            if update_status:
                self.status.configure(
                    text="Stage not connected",
                    text_color=RED_COLOR
                )
            return False
        if not self.stage.set_velocity(speed_mm_s):  # NEU: Geschwindigkeit anwenden
            if update_status:
                self.status.configure(
                    text="Could not set stage speed",  # NEU: Geschwindigkeit anwenden
                    text_color=RED_COLOR
                )
            return False
        self.label_stage_speed.configure(  # NEU: Geschwindigkeit anwenden
            text=f"Movement Speed: {speed_mm_s:.6f} mm/s"  # NEU: Geschwindigkeit anwenden
        )
        if update_status:
            self.status.configure(
                text=f"Stage speed set to {speed_mm_s:.6f} mm/s",  # NEU: Geschwindigkeit anwenden
                text_color=GREEN_COLOR
            )
        return True
    # -----------------------------------------------------------------------------
    # 6.6 STAGE CONTROL HELPER
    # -----------------------------------------------------------------------------

    def prepare_stage_for_move(self):  # NEU: Prüft Status und Geschwindigkeit vor Fahrt
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
        return self.apply_stage_speed(  # NEU: Verbindung & Geschwindigkeit prüfen
            update_status=False  # NEU: Verbindung & Geschwindigkeit prüfen
        )
    # -----------------------------------------------------------------------------
    # 6.1 MOVE STAGE TO AN ABSOLUTE POSITION
    # -----------------------------------------------------------------------------

    def start_stage_move_to(self, target_mm, start_pos=None):  # NEU: Komponente der Photodioden-Klasse
        if not self.prepare_stage_for_move():  # NEU: Komponente der Photodioden-Klasse
            return
        if start_pos is None:
            start_pos = self.stage.get_position()
        target_mm = self.stage.clamp_position(  # NEU: Komponente der Photodioden-Klasse
            target_mm  # NEU: Komponente der Photodioden-Klasse
        )
        move_mm = target_mm - start_pos
        self.stage_start_position = start_pos
        self.stage_movement_before_move = self.total_stage_movement
        self.reset_stage_speed_tracking(start_pos)  # NEU: Komponente der Photodioden-Klasse
        if abs(move_mm) < 1e-12:
            self.update_stage_labels(  # NEU: Komponente der Photodioden-Klasse
                start_pos,  # NEU: Komponente der Photodioden-Klasse
                0.0,
                self.stage_movement_before_move  # NEU: Komponente der Photodioden-Klasse
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

    def start_stage_move_to_stepped(  # NEU: Komponente der Photodioden-Klasse
        self,
        target_mm,
        step_mm=None,  # NEU: Komponente der Photodioden-Klasse
        pause_s=STEP_PAUSE_S,  # NEU: Komponente der Photodioden-Klasse
        label_prefix="Moving"  # NEU: Komponente der Photodioden-Klasse
    ):
        if not self.prepare_stage_for_move():  # NEU: Komponente der Photodioden-Klasse
            return
        start_pos = self.stage.get_position()
        target_mm = self.stage.clamp_position(  # NEU: Komponente der Photodioden-Klasse
            target_mm  # NEU: Komponente der Photodioden-Klasse
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
        self.reset_stage_speed_tracking(start_pos)  # NEU: Komponente der Photodioden-Klasse
        if step_mm is None:  # NEU: Komponente der Photodioden-Klasse
            step_mm = self.get_step_size()
        else:
            step_mm = abs(  # NEU: Komponente der Photodioden-Klasse
                float(step_mm)  # NEU: Komponente der Photodioden-Klasse
            )
        if step_mm <= 0:  # NEU: Komponente der Photodioden-Klasse
            self.status.configure(
                text="Invalid step size",  # NEU: Komponente der Photodioden-Klasse
                text_color=RED_COLOR
            )
            return
        #if none of the above cases stops the stage from moving, create a movement thread and start the movement
        threading.Thread(
            target=self.stage_stepped_move_worker,
            args=(start_pos, target_mm, step_mm, pause_s, label_prefix),  # NEU: Komponente der Photodioden-Klasse
            daemon=True
        ).start()
    # -----------------------------------------------------------------------------
    # 6.4 MOVE STAGE RELATIVELY IN STEPS
    # -----------------------------------------------------------------------------

    def start_stage_move_by_steps(  # NEU: Komponente der Photodioden-Klasse
        self,
        move_mm,  # NEU: Komponente der Photodioden-Klasse
        step_mm=None,  # NEU: Komponente der Photodioden-Klasse
        pause_s=STEP_PAUSE_S,  # NEU: Komponente der Photodioden-Klasse
        label_prefix="Moving"  # NEU: Komponente der Photodioden-Klasse
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
            step_mm=step_mm,  # NEU: Komponente der Photodioden-Klasse
            pause_s=pause_s,  # NEU: Komponente der Photodioden-Klasse
            label_prefix=label_prefix  # NEU: Komponente der Photodioden-Klasse
        )
    # -----------------------------------------------------------------------------
    # 6.5 WORKER FOR STEPPED MOVEMENT
    # -----------------------------------------------------------------------------

    def stage_stepped_move_worker(  # NEU: Schrittweises Fahren im Hintergrundthread
        self,
        start_pos,  # NEU: Schrittweises Fahren im Hintergrundthread
        target_mm,
        step_mm,  # NEU: Schrittweises Fahren im Hintergrundthread
        pause_s,  # NEU: Schrittweises Fahren im Hintergrundthread
        label_prefix  # NEU: Schrittweises Fahren im Hintergrundthread
    ):
        step_sign = 1 if target_mm > start_pos else -1  # NEU: Schrittweises Fahren im Hintergrundthread
        current_pos = start_pos
        remaining = abs(target_mm - start_pos)
        moved = 0.0
        self.after(
            0,
            lambda:
            self.status.configure(
                text=(
                    f"{label_prefix} to {target_mm:.6f} mm in "  # NEU: Schrittweises Fahren im Hintergrundthread
                    f"{step_mm:.9f} mm steps"  # NEU: Schrittweises Fahren im Hintergrundthread
                ),
                text_color=TEXT_COLOR
            )
        )
        while remaining > 1e-12:
            next_step = min(  # NEU: Schrittweises Fahren im Hintergrundthread
                step_mm,  # NEU: Schrittweises Fahren im Hintergrundthread
                remaining  # NEU: Schrittweises Fahren im Hintergrundthread
            )
            next_target = current_pos + step_sign * next_step  # NEU: Schrittweises Fahren im Hintergrundthread
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
                time.sleep(0.005 if pause_s <= 0 else 0.01)  # NEU: Schrittweises Fahren im Hintergrundthread
            step_distance = abs(  # NEU: Schrittweises Fahren im Hintergrundthread
                next_target - current_pos  # NEU: Schrittweises Fahren im Hintergrundthread
            )
            moved += step_distance
            current_pos = next_target
            remaining = abs(  # NEU: Schrittweises Fahren im Hintergrundthread
                target_mm - current_pos  # NEU: Schrittweises Fahren im Hintergrundthread
            )
            self.total_stage_movement = (
                self.stage_movement_before_move + moved
            )
            self.after(
                0,
                lambda p=current_pos, m=moved, b=self.stage_movement_before_move:  # NEU: Schrittweises Fahren im Hintergrundthread
                self.update_stage_labels(p, m, b)
            )
            if remaining > 1e-12 and pause_s > 0:  # NEU: Schrittweises Fahren im Hintergrundthread
                time.sleep(pause_s)  # NEU: Schrittweises Fahren im Hintergrundthread
        self.after(
            0,
            lambda:
            self.finish_stage_move(current_pos)  # NEU: Schrittweises Fahren im Hintergrundthread
        )
    # -----------------------------------------------------------------------------
    # 7.1 TRACK NORMAL STAGE MOVEMENT
    # -----------------------------------------------------------------------------

    def stage_ui_loop(self):
        #how much did the stage move befor the current movement? use this as base
        movement_base = self.stage_movement_before_move
        while self.stage.is_moving:
            pos = self.stage.get_position()
            moved = abs(  # NEU: Tischposition auf UI aktualisieren
                pos - self.stage_start_position  # NEU: Tischposition auf UI aktualisieren
            )
            self.after(
                0,
                lambda p=pos, m=moved, b=movement_base:
                self.update_stage_labels(p, m, b)
            )
            time.sleep(0.05)
        pos = self.stage.get_position()
        moved = abs(  # NEU: Tischposition auf UI aktualisieren
            pos - self.stage_start_position  # NEU: Tischposition auf UI aktualisieren
        )
        self.total_stage_movement = movement_base + moved  # NEU: Tischposition auf UI aktualisieren
        self.after(
            0,
            lambda p=pos:
            self.finish_stage_move(p)  # NEU: Tischposition auf UI aktualisieren
        )
    # -----------------------------------------------------------------------------
    # 7.1.1 FINISH STAGE MOVE
    # -----------------------------------------------------------------------------

    def finish_stage_move(self, pos):  # NEU: Status nach Tischbewegung aktualisieren
        moved = abs(  # NEU: Status nach Tischbewegung aktualisieren
            pos - self.stage_start_position  # NEU: Status nach Tischbewegung aktualisieren
        )
        self.update_stage_labels(  # NEU: Status nach Tischbewegung aktualisieren
            pos,  # NEU: Status nach Tischbewegung aktualisieren
            moved,  # NEU: Status nach Tischbewegung aktualisieren
            self.stage_movement_before_move  # NEU: Status nach Tischbewegung aktualisieren
        )
        self.label_stage_speed.configure(  # NEU: Status nach Tischbewegung aktualisieren
            text="Movement Speed: 0.000000 mm/s"  # NEU: Status nach Tischbewegung aktualisieren
        )
        self.status.configure(
            text=f"Reached {pos:.6f} mm",  # NEU: Status nach Tischbewegung aktualisieren
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

    def move_to_target(self):  # NEU: Absolute Tischbewegung starten
        try:
            target_mm = self.parse_entry_float(  # NEU: Absolute Tischbewegung starten
                self.target_entry  # NEU: Absolute Tischbewegung starten
            )
        except ValueError:
            self.status.configure(
                text="Invalid target value",
                text_color=RED_COLOR
            )
            return
        self.start_stage_move_to(
            target_mm  # NEU: Absolute Tischbewegung starten
        )
    # -----------------------------------------------------------------------------
    # 5.9.6 MOVE DISTANCE FROM UI
    # -----------------------------------------------------------------------------

    def move_distance(self):  # NEU: Relative Tischbewegung starten
        try:
            distance_mm = self.parse_entry_float(  # NEU: Relative Tischbewegung starten
                self.target_entry  # NEU: Relative Tischbewegung starten
            )
        except ValueError:
            self.status.configure(
                text="Invalid distance value",
                text_color=RED_COLOR
            )
            return
        self.start_stage_move_by(
            distance_mm  # NEU: Relative Tischbewegung starten
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
                text="Stage stopped manually",  # NEU: Komponente der Photodioden-Klasse
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
                text="Status: Stage not connected",  # NEU: Tischposition abfragen
                text_color=ORANGE_COLOR
            )
    # -----------------------------------------------------------------------------
    # 7.3 UPDATE STAGE MOVEMENT DISPLAY
    # -----------------------------------------------------------------------------

    def update_stage_labels(self, pos, moved, movement_base=None):
        if movement_base is None:
            movement_base = self.total_stage_movement
        current_total_stage_movement = movement_base + abs(  # NEU: Tischposition und Weg anzeigen
            moved  # NEU: Tischposition und Weg anzeigen
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
        self.update_stage_speed_label(pos)  # NEU: Tischposition und Weg anzeigen
        self.update_comparison_labels(
            current_total_stage_movement
        )
    # -----------------------------------------------------------------------------
    # 7.5 RESET STAGE SPEED TRACKING
    # -----------------------------------------------------------------------------

    def reset_stage_speed_tracking(self, pos):  # NEU: Geschwindigkeitstracking zurücksetzen
        self.last_stage_speed_position = pos  # NEU: Geschwindigkeitstracking zurücksetzen
        self.last_stage_speed_time = time.time()  # NEU: Geschwindigkeitstracking zurücksetzen
    # -----------------------------------------------------------------------------
    # 7.6 UPDATE STAGE SPEED DISPLAY
    # -----------------------------------------------------------------------------

    def update_stage_speed_label(self, pos):  # NEU: Berechnet und zeigt Fahrtgeschwindigkeit an
        now = time.time()
        if (
            self.last_stage_speed_time is None  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
            or self.last_stage_speed_position is None  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
        ):
            self.reset_stage_speed_tracking(pos)  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
            return
        dt = now - self.last_stage_speed_time  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
        if dt <= 0:  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
            return
        speed_mm_s = abs(  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
            pos - self.last_stage_speed_position  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
        ) / dt  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
        self.last_stage_speed_time = now  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
        self.last_stage_speed_position = pos  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
        self.label_stage_speed.configure(  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
            text=f"Movement Speed: {speed_mm_s:.6f} mm/s"  # NEU: Fahrtgeschwindigkeit berechnen und anzeigen
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
        self.label_stage_speed.configure(  # NEU: Komponente der Photodioden-Klasse
            text="Movement Speed: 0.000000 mm/s"  # NEU: Komponente der Photodioden-Klasse
        )
    # -----------------------------------------------------------------------------
    # 7.11 UPDATE DRIVEN VS CALCULATED DISTANCE
    # -----------------------------------------------------------------------------

    #stage movement distance is compared with distance calculated from counted fringes
    def update_comparison_labels(self, driven_mm=None):
        if driven_mm is None:
            driven_mm = self.current_stage_movement_for_compare
        driven_distance_mm = abs(  # NEU: Vergleich Soll- vs. Ist-Position anzeigen
            driven_mm  # NEU: Vergleich Soll- vs. Ist-Position anzeigen
        )
        calculated_mm = (
            self.accumulated_fringes
            * self.fringe_distance_mm
        )
        difference_mm = driven_distance_mm - calculated_mm  # NEU: Vergleich Soll- vs. Ist-Position anzeigen
        self.label_compare_driven.configure(
            text=f"Driven: {driven_distance_mm:.6f} mm"  # NEU: Vergleich Soll- vs. Ist-Position anzeigen
        )
        self.label_compare_calculated.configure(
            text=f"Calculated from Fringes: {calculated_mm:.6f} mm"  # NEU: Vergleich Soll- vs. Ist-Position anzeigen
        )
        self.label_compare_difference.configure(
            text=f"Difference: {difference_mm:.6f} mm"  # NEU: Vergleich Soll- vs. Ist-Position anzeigen
        )
    # -----------------------------------------------------------------------------
    # 8.8 RUN STAGE MOTION BY PARAMETERS
    # -----------------------------------------------------------------------------

    def run_stage_motion_by_parameters(self):  # NEU: Startet automatisierte Messfahrt (kontinuierlich/schrittweise)
        if not self.stage_connected:
            return
        current_position = self.stage.get_position()  # NEU: Automatisierte Messfahrt steuern
        if MODE.lower().startswith("c"):  # NEU: Automatisierte Messfahrt steuern
            self.stage.set_velocity(VELOCITY_MM_S)  # NEU: Setzt Geschwindigkeit für kontinuierliche Fahrt
            final_target = self.stage.clamp_position(current_position + TOTAL_DISTANCE_MM)  # NEU: Automatisierte Messfahrt steuern
            self.stage_start_position = current_position  # NEU: Automatisierte Messfahrt steuern
            self.stage_movement_before_move = self.total_stage_movement
            self.reset_stage_speed_tracking(current_position)  # NEU: Automatisierte Messfahrt steuern
            self.after(
                0,
                lambda:
                self.status.configure(
                    text=(
                        f"Continuous move to {final_target:.6f} mm "  # NEU: Automatisierte Messfahrt steuern
                        f"at {VELOCITY_MM_S} mm/s"  # NEU: Automatisierte Messfahrt steuern
                    ),
                    text_color=TEXT_COLOR
                )
            )
            if not self.stage.move_absolute(final_target):  # NEU: Tisch zur Endposition fahren
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
                    lambda p=pos, m=moved, b=self.stage_movement_before_move:  # NEU: Automatisierte Messfahrt steuern
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
                self.finish_stage_move(p)  # NEU: Automatisierte Messfahrt steuern
            )
        else:
            self.stage.set_velocity(VELOCITY_MM_S_STEPPED)  # NEU: Setzt Geschwindigkeit für schrittweise Fahrt
            self.stage_start_position = current_position  # NEU: Automatisierte Messfahrt steuern
            self.stage_movement_before_move = self.total_stage_movement
            self.reset_stage_speed_tracking(current_position)  # NEU: Automatisierte Messfahrt steuern
            self.after(
                0,
                lambda:
                self.status.configure(
                    text=(
                        f"Stepped move: {STEPS} steps of "  # NEU: Automatisierte Messfahrt steuern
                        f"{STEP_SIZE_MM} mm"  # NEU: Automatisierte Messfahrt steuern
                    ),
                    text_color=TEXT_COLOR
                )
            )
            current_pos = current_position  # NEU: Automatisierte Messfahrt steuern
            moved = 0.0
            for step in range(STEPS):  # NEU: Automatisierte Messfahrt steuern
                if not self.is_monitoring:
                    break  # NEU: Automatisierte Messfahrt steuern
                next_position = self.stage.clamp_position(  # NEU: Automatisierte Messfahrt steuern
                    current_pos + STEP_SIZE_MM  # NEU: Automatisierte Messfahrt steuern
                )
                self.after(
                    0,
                    lambda s=step, n=next_position:  # NEU: Automatisierte Messfahrt steuern
                    self.status.configure(
                        text=(
                            f"Step {s + 1}/{STEPS}: "  # NEU: Automatisierte Messfahrt steuern
                            f"move to {n:.7f} mm"  # NEU: Automatisierte Messfahrt steuern
                        ),
                        text_color=TEXT_COLOR
                    )
                )
                if not self.stage.move_absolute(next_position):  # NEU: Tisch zum nächsten Einzelschritt fahren
                    self.after(
                        0,
                        lambda:
                        self.status.configure(
                            text="Move command failed",  # NEU: Automatisierte Messfahrt steuern
                            text_color=RED_COLOR
                        )
                    )
                    break  # NEU: Automatisierte Messfahrt steuern
                while self.stage.is_moving and self.is_monitoring:
                    time.sleep(0.01)
                step_distance = abs(next_position - current_pos)  # NEU: Automatisierte Messfahrt steuern
                moved += step_distance
                current_pos = next_position  # NEU: Automatisierte Messfahrt steuern
                self.total_stage_movement = (
                    self.stage_movement_before_move + moved
                )
                self.after(
                    0,
                    lambda p=current_pos, m=moved, b=self.stage_movement_before_move:  # NEU: Automatisierte Messfahrt steuern
                    self.update_stage_labels(p, m, b)
                )
                if step < STEPS - 1:  # NEU: Automatisierte Messfahrt steuern
                    time.sleep(STEP_PAUSE_S)  # NEU: Wartet Pause nach Einzelschritt ab
            self.after(
                0,
                lambda p=current_pos:  # NEU: Automatisierte Messfahrt steuern
                self.finish_stage_move(p)  # NEU: Automatisierte Messfahrt steuern
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
            steps = 8  # NEU: Tischfahrt während Kalibrierung
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
            self.after(0, self.finish_calibration_movement)  # NEU: Tischfahrt während Kalibrierung
    # -----------------------------------------------------------------------------
    # 7.10 FINISH CALIBRATION RESET
    # -----------------------------------------------------------------------------

    def finish_calibration_movement(self):  # NEU: Position nach Kalibrierungsfahrt nullen
        if self.stage_connected:
            current_pos = self.stage.get_position()
            self.reset_stage_movement_tracking(current_pos)  # NEU: Tisch-Tracking nach Kalibrierung zurücksetzen
        else:
            self.reset_stage_movement_tracking(150.0)  # NEU: Tisch-Tracking nach Kalibrierung zurücksetzen
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
            self.diode.close()  # NEU: Hardware schließen & App beenden
        except Exception:  # NEU: Hardware schließen & App beenden
            pass
        try:
            self.stage.close()
        except Exception:  # NEU: Hardware schließen & App beenden
            pass
        self.destroy()

# -----------------------------------------------------------------------------
# 9. PROGRAM START
# -----------------------------------------------------------------------------

# 9. PROGRAM START
if __name__ == "__main__":
    app = SideApp()  # NEU: Instanziierung der Photodioden-App
    app.protocol(
        "WM_DELETE_WINDOW", # connect window close button to cleanup routine
        app.on_close
    )
    app.mainloop() # start the graphical application loop
