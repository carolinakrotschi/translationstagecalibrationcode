# Originalkommentar oder Abschnittsüberschrift.
# this code is basically identical with side.py except for "from stage_controller_thor import StageController"
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# TABLE OF CONTENTS
# Originalkommentar oder Abschnittsüberschrift.
# 1. Basic settings
# Originalkommentar oder Abschnittsüberschrift.
# 2. Imports 
# Originalkommentar oder Abschnittsüberschrift.
# 3. Physical constants and colors
# Originalkommentar oder Abschnittsüberschrift.
# 4. SideApp class (UI) 
# Originalkommentar oder Abschnittsüberschrift.
# 5. Monitoring and reset
# Originalkommentar oder Abschnittsüberschrift.
# 6. Translation stage control
# Originalkommentar oder Abschnittsüberschrift.
# 7. Calibration 
# Originalkommentar oder Abschnittsüberschrift.
# 8. Diode loop and plotting 
# Originalkommentar oder Abschnittsüberschrift.
# 9. Cleanup and program start
# Leerzeile zur besseren Lesbarkeit.

# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 1. BASIC SETTINGS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `20.0` in der Konstante `CALIBRATION_SECONDS`. Das ist die Gesamtzeit für den Kalibrierungsablauf.
CALIBRATION_SECONDS = 20.0
# In Python speichert `=` hier den festen Wert `0.01` in der Konstante `CALIBRATION_STAGE_DISTANCE_MM`. Damit fährt die Stage pro Kalibrierungs-Hinweg eine sehr kleine Strecke.
CALIBRATION_STAGE_DISTANCE_MM = 0.01
# In Python berechnet `=` hier die Konstante `CALIBRATION_STAGE_MOTION_SECONDS` aus anderen Größen. Davon wird ein Bewegungsanteil für die Kalibrierung abgeleitet.
CALIBRATION_STAGE_MOTION_SECONDS = CALIBRATION_SECONDS * 0.85
# In Python speichert `=` hier einen Wert in der Konstante `CALIBRATION_STAGE_SPEED_MM_S`. So wird die passende Stage-Geschwindigkeit aus Weg und Zeit berechnet.
CALIBRATION_STAGE_SPEED_MM_S = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    2 * CALIBRATION_STAGE_DISTANCE_MM
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
) / CALIBRATION_STAGE_MOTION_SECONDS
# In Python speichert `=` hier einen Wert in der Konstante `CALIBRATION_FORWARD_ANALYSIS_FRACTION`. Damit wird festgelegt, wie viel vom Vorwärts-Hub für die Auswertung genutzt wird.
CALIBRATION_FORWARD_ANALYSIS_FRACTION = min(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    0.60,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    (CALIBRATION_STAGE_MOTION_SECONDS / 2) / CALIBRATION_SECONDS + 0.03
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
)
# In Python speichert `=` hier den festen Wert `0.010` in der Konstante `EXPECTED_FRINGE_AMPLITUDE_V`. Das ist die erwartete Fringe-Höhe im Signal.
EXPECTED_FRINGE_AMPLITUDE_V = 0.010
# In Python speichert `=` hier den festen Wert `5.0` in der Konstante `MIN_FRINGE_TO_NOISE_RATIO`. Damit wird geprüft, wie viel größer ein Fringe als das Rauschen sein muss.
MIN_FRINGE_TO_NOISE_RATIO = 5.0
# In Python speichert `=` hier einen Wert in der Konstante `DEFAULT_NOISE_AMPLITUDE_V`. Daraus wird eine typische Rauschamplitude geschätzt.
DEFAULT_NOISE_AMPLITUDE_V = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    EXPECTED_FRINGE_AMPLITUDE_V / MIN_FRINGE_TO_NOISE_RATIO
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
)
# In Python speichert `=` hier einen Wert in der Konstante `DEFAULT_FRINGE_AMPLITUDE_V`. Das ist der Standardwert für die Fringe-Höhe.
DEFAULT_FRINGE_AMPLITUDE_V = EXPECTED_FRINGE_AMPLITUDE_V
# In Python speichert `=` hier den festen Wert `0.005` in der Konstante `MIN_VALID_FRINGE_AMPLITUDE_V`. So klein darf ein echtes Fringe-Signal mindestens sein.
MIN_VALID_FRINGE_AMPLITUDE_V = 0.005
# In Python speichert `=` hier den festen Wert `0.020` in der Konstante `MAX_VALID_FRINGE_AMPLITUDE_V`. So groß darf ein echtes Fringe-Signal höchstens sein.
MAX_VALID_FRINGE_AMPLITUDE_V = 0.020
# In Python speichert `=` hier den festen Wert `0.50` in der Konstante `FRINGE_RISE_FRACTION`. Das ist der Anteil des Anstiegs, der für ein Fringe nötig ist.
FRINGE_RISE_FRACTION = 0.50
# In Python speichert `=` hier den festen Wert `0.25` in der Konstante `FRINGE_REARM_FRACTION`. Damit wird der Wiederscharf-Schwellwert für die Erkennung festgelegt.
FRINGE_REARM_FRACTION = 0.25
# In Python speichert `=` hier den festen Wert `0.50` in der Konstante `DARK_LEVEL_FRACTION`. Damit wird der dunkle Bereich des Signals abgeschätzt.
DARK_LEVEL_FRACTION = 0.50
# In Python speichert `=` hier den festen Wert `0.80` in der Konstante `BRIGHT_LEVEL_FRACTION`. Damit wird der helle Bereich des Signals abgeschätzt.
BRIGHT_LEVEL_FRACTION = 0.80
# In Python speichert `=` hier den festen Wert `300` in der Konstante `RAW_HISTORY_LENGTH`. So viele Rohwerte werden im Verlauf behalten.
RAW_HISTORY_LENGTH = 300
# In Python speichert `=` hier den festen Wert `3` in der Konstante `SMOOTHING_WINDOW_LENGTH`. Über so viele Werte wird geglättet.
SMOOTHING_WINDOW_LENGTH = 3
# In Python speichert `=` hier den festen Wert `0.05` in der Konstante `STEP_PAUSE_S`. So lange wartet der Code zwischen zwei Schritten.
STEP_PAUSE_S = 0.05
# In Python speichert `=` hier den festen Wert `4` in der Konstante `REQUIRED_DARK_FRAMES`. So viele dunkle Frames braucht die Erkennung.
REQUIRED_DARK_FRAMES = 4
# In Python speichert `=` hier den festen Wert `5` in der Konstante `REQUIRED_BRIGHT_FRAMES`. So viele helle Frames braucht die Erkennung.
REQUIRED_BRIGHT_FRAMES = 5
# In Python speichert `=` hier den festen Wert `15` in der Konstante `MAX_FRINGE_WIDTH_FRAMES`. So breit darf ein Fringe-Zeitfenster maximal sein.
MAX_FRINGE_WIDTH_FRAMES = 15
# In Python speichert `=` hier den festen Wert `100` in der Konstante `STAGE_STATUS_POLL_MS`. So oft wird der Stage-Status abgefragt.
STAGE_STATUS_POLL_MS = 100
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in der Konstante `MODE`. Damit wird der Bewegungsmodus gewählt.
MODE = "continuous"
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `0.0006` in der Konstante `VELOCITY_MM_S`. Das ist die Geschwindigkeit für den kontinuierlichen Modus.
VELOCITY_MM_S = 0.0006
# In Python speichert `=` hier den festen Wert `13.0` in der Konstante `TOTAL_DISTANCE_MM`. Das ist die gesamte Strecke im kontinuierlichen Modus.
TOTAL_DISTANCE_MM = 13.0
# In Python speichert `=` hier den festen Wert `1.00` in der Konstante `VELOCITY_MM_S_STEPPED`. Das ist die Geschwindigkeit für den Schrittmodus.
VELOCITY_MM_S_STEPPED = 1.00
# In Python speichert `=` hier den festen Wert `0.00001` in der Konstante `STEP_SIZE_MM`. Das ist die Größe eines einzelnen Schritts.
STEP_SIZE_MM = 0.00001
# In Python speichert `=` hier den festen Wert `100` in der Konstante `STEPS`. So viele Einzelschritte werden gemacht.
STEPS = 100
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 2. IMPORTS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import threading # so that camera and stage can run without freezing the UI
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import time # for timestamps
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import customtkinter as ctk # pythons standard UI library
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
try:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    from matplotlib.figure import Figure
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
except ImportError:
# In Python speichert `=` hier einen Startwert in `Figure`.
    Figure = None
# In Python speichert `=` hier einen Startwert in `FigureCanvasTkAgg`.
    FigureCanvasTkAgg = None
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
from handler_diode import (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    LASER_WAVELENGTH_NM,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    PHOTODIODE_CHANNEL,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    SAMPLE_INTERVAL_S,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    SingleDiodeHandler,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    compute_fringe_distance_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
from thor_handler_stage import StageController
# Leerzeile zur besseren Lesbarkeit.

# In Python berechnet `=` hier die Konstante `FRINGE_COOLDOWN` aus anderen Größen.
FRINGE_COOLDOWN = max(0.1, MAX_FRINGE_WIDTH_FRAMES * SAMPLE_INTERVAL_S)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 3. PHYSICAL CONSTANTS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `0.299792458` in der Konstante `SPEED_OF_LIGHT_MM_PS`. Das ist die Lichtgeschwindigkeit in mm pro ps.
SPEED_OF_LIGHT_MM_PS = 0.299792458
# In Python speichert `=` hier den festen Wert `0.000600` in der Konstante `DEFAULT_STAGE_SPEED_MM_S`. Das ist die Standardgeschwindigkeit für den Stage.
DEFAULT_STAGE_SPEED_MM_S = 0.000600
# `def` definiert in Python eine Funktion oder Methode. Hier: Berechnet die Viertelwellen-Schrittweite für den Stage.
def compute_quarter_wavelength_step_mm(wavelength_nm):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
    return (wavelength_nm / 4) / 1_000_000
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 3.1 COLORS AND FILTER TIMINGS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in der Konstante `TEXT_COLOR`.
TEXT_COLOR = "#0A4A51"
# In Python speichert `=` hier einen Wert in der Konstante `GREEN_COLOR`.
GREEN_COLOR = "#1EAD4F"
# In Python speichert `=` hier einen Wert in der Konstante `RED_COLOR`.
RED_COLOR = "#C0392B"
# In Python speichert `=` hier einen Wert in der Konstante `ORANGE_COLOR`.
ORANGE_COLOR = "#D35400"
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 4. APP CLASS (UI)
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `SideApp` als Bauplan für das Fenster und die Logik.
class SideApp(ctk.CTk):
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 4.1 INITIALIZATION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    #ctk.CTk is the base class for the customtkinter window, here we inherit our InterferometerApp class from it
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self):
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #init method always gets called to create a new instance of the class
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        super().__init__()
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf: Hier wird der Fenstertitel gesetzt.
        self.title("Single Photodiode Fringe Monitor")
# In Python ruft `.` eine Methode auf: Hier wird die Fenstergröße gesetzt.
        self.geometry("900x1000")
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft man eine Funktion auf: Hier wird das Farbschema eingestellt.
        ctk.set_appearance_mode("light")
# In Python ruft `.` eine Methode auf: Hier wird das Fenster konfiguriert.
        self.configure(fg_color="white")
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #creates a scrollable frame inside the window
# In Python erzeugt `()` ein neues Objekt: Hier ein scrollbarer Bereich.
        self.scroll = ctk.CTkScrollableFrame(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="white"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Originalkommentar oder Abschnittsüberschrift.
        #the scrollable frame is put into the window
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.scroll.pack(
# In Python speichert `=` hier einen Wert in `fill`.
            fill="both",
# In Python speichert `=` hier einen Wert in `expand`.
            expand=True,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=2,
# In Python speichert `=` hier einen Wert in `pady`.
            pady=2
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #some initialization of values
# Originalkommentar oder Abschnittsüberschrift.
        #measurement loop is not running at the beginning
# In Python speichert `=` hier den booleschen Startwert aus in `is_monitoring`. Merker, ob die Messschleife läuft.
        self.is_monitoring = False
# In Python speichert `=` hier erstmal keinen Wert in `measurement_thread`.
        self.measurement_thread = None
# Originalkommentar oder Abschnittsüberschrift.
        #for the 5s calibration at the beginning
# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
        self.calibrating = False
# In Python speichert `=` hier erstmal keinen Wert in `latest_sample`. letzte Messprobe.
        self.latest_sample = None
# In Python speichert `=` einen Wert in `latest_voltage`. letzter Spannungswert.
        self.latest_voltage = 0.0
# In Python speichert `=` hier erstmal keinen Wert in `last_error_text`. letzte Fehlermeldung.
        self.last_error_text = None
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier eine leere Liste in `raw_voltage_history`. Verlauf der Rohspannungen.
        self.raw_voltage_history = []
# In Python speichert `=` hier eine leere Liste in `clean_voltage_history`. Verlauf der geglätteten Spannungen.
        self.clean_voltage_history = []
# In Python speichert `=` hier eine leere Liste in `calibration_raw_samples`. gesammelte Rohdaten der Kalibrierung.
        self.calibration_raw_samples = []
# In Python speichert `=` einen Wert in `baseline_voltage`. Baseline für das spätere Abziehen vom Rohsignal.
        self.baseline_voltage = 0.0
# In Python speichert `=` hier den booleschen Startwert aus in `baseline_recorded`. Merker, ob die Baseline schon gemessen wurde.
        self.baseline_recorded = False
# In Python speichert `=` hier eine leere Liste in `smoothed_voltage_history`. kleines Fenster geglätteter Spannungen.
        self.smoothed_voltage_history = []
# In Python speichert `=` hier den booleschen Startwert aus in `recording`. Merker, ob gerade aufgenommen wird.
        self.recording = False
# In Python speichert `=` hier eine leere Liste in `recorded_data`. gesammelte Daten für den Export.
        self.recorded_data = []
# In Python speichert `=` hier erstmal keinen Wert in `recording_start_time`. Startzeit der Aufnahme.
        self.recording_start_time = None
# In Python speichert `=` einen Wert in `accumulated_fringes`. bisher gezählte Fringe-Anzahl.
        self.accumulated_fringes = 0
# Originalkommentar oder Abschnittsüberschrift.
        #a bright state only counts after darkness
# In Python speichert `=` hier den booleschen Startwert aus in `was_dark`. Merker für den Dunkelzustand.
        self.was_dark = False
# Originalkommentar oder Abschnittsüberschrift.
        #number of consecutive dark/bright fringes
# In Python speichert `=` einen Wert in `dark_counter`. Zähler für dunkle Frames.
        self.dark_counter = 0
# In Python speichert `=` einen Wert in `bright_counter`. Zähler für helle Frames.
        self.bright_counter = 0
# In Python speichert `=` einen Wert in `last_count_time`. Zeitpunkt des letzten Zählereignisses.
        self.last_count_time = 0.0
# In Python speichert `=` einen Wert in `dark_threshold`. Schwelle für dunkel.
        self.dark_threshold = 0.0
# In Python speichert `=` einen Wert in `bright_threshold`. Schwelle für hell.
        self.bright_threshold = 0.0
# In Python speichert `=` einen Wert in `fringe_amplitude_voltage`. geschätzte Fringe-Höhe.
        self.fringe_amplitude_voltage = DEFAULT_FRINGE_AMPLITUDE_V
# In Python speichert `=` einen Wert in `noise_amplitude_voltage`. geschätzte Rauschhöhe.
        self.noise_amplitude_voltage = DEFAULT_NOISE_AMPLITUDE_V
# In Python speichert `=` einen Wert in `min_count_amplitude_voltage`. kleinste zulässige Fringe-Höhe.
        self.min_count_amplitude_voltage = MIN_VALID_FRINGE_AMPLITUDE_V
# In Python speichert `=` einen Wert in `fringe_rise_threshold_voltage`. Anstiegsschwelle für ein Fringe.
        self.fringe_rise_threshold_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            DEFAULT_FRINGE_AMPLITUDE_V * FRINGE_RISE_FRACTION
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `fringe_rearm_threshold_voltage`. Schwelle, ab der die Erkennung wieder bereit ist.
        self.fringe_rearm_threshold_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            DEFAULT_FRINGE_AMPLITUDE_V * FRINGE_REARM_FRACTION
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier erstmal keinen Wert in `fringe_trough_voltage`. gemerkter Tiefpunkt des Signals.
        self.fringe_trough_voltage = None
# In Python speichert `=` hier erstmal keinen Wert in `fringe_peak_voltage`. gemerkter Hochpunkt des Signals.
        self.fringe_peak_voltage = None
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `laser_wavelength_nm`. gespeicherte Laserwellenlänge.
        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
# In Python speichert `=` das Berechnungsergebnis in `fringe_distance_mm`. Abstand zwischen zwei Fringes.
        self.fringe_distance_mm = compute_fringe_distance_mm(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.laser_wavelength_nm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` das Berechnungsergebnis in `quarter_wavelength_step_mm`. empfohlene Viertelwellen-Schrittweite.
        self.quarter_wavelength_step_mm = compute_quarter_wavelength_step_mm(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.laser_wavelength_nm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das neu erzeugte Dioden-Objekt in einer Variable.
        self.diode = SingleDiodeHandler()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #same for the stage
# In Python speichert `=` das neu erzeugte Stage-Objekt in einer Variable.
        self.stage = StageController()
# In Python ruft `.` eine Methode auf, die die Geschwindigkeit setzt.
        self.stage.set_velocity(VELOCITY_MM_S, 0.0)
# In Python ruft `.` eine Methode auf, die die Verbindung herstellt.
        self.stage_connected = self.stage.connect()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #stores values for all the start positions
# In Python speichert `=` einen Wert in `stage_start_position`. Startposition der Bewegung.
        self.stage_start_position = 0.0
# In Python speichert `=` einen Wert in `stage_reference_position`. Referenzposition für Berechnungen.
        self.stage_reference_position = 0.0
# In Python speichert `=` einen Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
        self.total_stage_movement = 0.0
# In Python speichert `=` einen Wert in `stage_movement_before_move`. Strecke vor der aktuellen Bewegung.
        self.stage_movement_before_move = 0.0
# In Python speichert `=` einen Wert in `current_stage_movement_for_compare`. aktuelle Vergleichsstrecke.
        self.current_stage_movement_for_compare = 0.0
# In Python speichert `=` hier erstmal keinen Wert in `stage_target_position`. aktuelle Zielposition.
        self.stage_target_position = None
# In Python speichert `=` einen Wert in `stage_remaining_to_drive`. Reststrecke bis zum Ziel.
        self.stage_remaining_to_drive = 0.0
# In Python speichert `=` hier den booleschen Startwert ein in `stage_remaining_known`. Merker, ob die Reststrecke bekannt ist.
        self.stage_remaining_known = True
# In Python speichert `=` hier erstmal keinen Wert in `last_stage_speed_time`. Zeitbasis für die Geschwindigkeitsmessung.
        self.last_stage_speed_time = None
# In Python speichert `=` hier erstmal keinen Wert in `last_stage_speed_position`. Positionsbasis für die Geschwindigkeitsmessung.
        self.last_stage_speed_position = None
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.build_ui()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_comparison_labels() # renewing the text in the UI matching the initial update of the comparison labels with 0 values using e.g self.current_stage_movement_for_compare which is 0 at the beginning
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_stage_position_once() # reads the current stage position and updates the label, this is important to have the correct position at the beginning
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `all_buttons`.
        self.all_buttons = [
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.restart_btn,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.wavelength_button,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.speed_button,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.btn_target_abs,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.btn_target_rel,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.btn_stop,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.btn_min,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.btn_left,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.btn_center,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.btn_right,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.btn_max
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ]
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
        self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            STAGE_STATUS_POLL_MS,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.poll_stage_status
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 4.1.2 UI BUILD
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Erzeugt die Benutzeroberfläche.
    def build_ui(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# Fenstertitel und Hauptüberschrift.
            text="Single Photodiode Fringe Monitor",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 23, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=5)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# Button zum Starten und Stoppen der Messung.
            text="START MONITORING",
# Hier wird der Button in Python mit der Methode für Start/Stopp verbunden.
            command=self.toggle,
# In Python speichert `=` hier einen Wert in `width`.
            width=180,
# In Python speichert `=` hier einen Wert in `height`.
            height=30,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11, "bold")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.restart_btn = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# Button zum Zurücksetzen der Werte.
            text="RESET",
# Hier wird der Button in Python mit der Reset-Methode verbunden.
            command=self.restart,
# In Python speichert `=` hier einen Wert in `width`.
            width=140,
# In Python speichert `=` hier einen Wert in `height`.
            height=28,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.restart_btn.pack(pady=1)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_record = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# Button zum Starten der Aufnahme.
            text="START RECORDING",
# Hier wird der Button in Python mit der Methode für Start/Stopp verbunden.
            command=self.toggle_recording,
# In Python speichert `=` hier einen Wert in `width`.
            width=140,
# In Python speichert `=` hier einen Wert in `height`.
            height=28,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="#555555"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_record.pack(pady=1)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.status = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# Anzeige für den Zustand ohne Messung.
            text="Status: Stopped",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.status.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.stage_frame = ctk.CTkFrame(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="#EEEEEE"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.stage_frame.pack(
# In Python speichert `=` hier einen Wert in `fill`.
            fill="x",
# In Python speichert `=` hier einen Wert in `padx`.
            padx=5,
# In Python speichert `=` hier einen Wert in `pady`.
            pady=4
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Überschrift für die Stage-Steuerung.
            text="Electronic Translation Stage",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 15, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Eingabefeld.
        self.wavelength_entry = ctk.CTkEntry(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Eingabefeld für die Laserwellenlänge.
            placeholder_text="Laser wavelength in nm",
# In Python speichert `=` hier einen Wert in `width`.
            width=250
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.wavelength_entry.pack(pady=1)
# In Python wird mit `.` Text in ein Eingabefeld geschrieben.
        self.wavelength_entry.insert(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            f"{self.laser_wavelength_nm:.1f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.wavelength_button = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Button zum Übernehmen der Wellenlänge.
            text="Set wavelength",
# In Python speichert `=` hier einen Wert in `width`.
            width=120,
# Hier wird der Button in Python mit der Wellenlängen-Methode verbunden.
            command=self.apply_wavelength,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.wavelength_button.pack(pady=1)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Beschriftung der Schrittweite.
            text="Schrittweite / Step size:",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=(5, 0))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Eingabefeld.
        self.step_entry = ctk.CTkEntry(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Eingabefeld für die Schrittweite.
            placeholder_text="Step size in mm",
# In Python speichert `=` hier einen Wert in `width`.
            width=250
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.step_entry.pack(pady=1)
# In Python wird mit `.` Text in ein Eingabefeld geschrieben.
        self.step_entry.insert(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            f"{self.quarter_wavelength_step_mm:.9f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Beschriftung der Geschwindigkeit.
            text="Geschwindigkeit / Velocity:",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=(5, 0))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Eingabefeld.
        self.speed_entry = ctk.CTkEntry(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Eingabefeld für die Geschwindigkeit.
            placeholder_text="Movement speed in mm/s",
# In Python speichert `=` hier einen Wert in `width`.
            width=250
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.speed_entry.pack(pady=1)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `stage_velocity`.
        stage_velocity = DEFAULT_STAGE_SPEED_MM_S
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.stage.set_velocity(stage_velocity):
# In Python ruft `.` eine Methode auf, die die Geschwindigkeit setzt.
                stage_velocity = self.stage.set_velocity()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if stage_velocity is None:
# In Python speichert `=` hier einen Wert in `stage_velocity`.
            stage_velocity = DEFAULT_STAGE_SPEED_MM_S
# Leerzeile zur besseren Lesbarkeit.

# In Python wird mit `.` Text in ein Eingabefeld geschrieben.
        self.speed_entry.insert(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            f"{stage_velocity:.6f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.speed_button = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Button zum Übernehmen der Geschwindigkeit.
            text="Set speed",
# In Python speichert `=` hier einen Wert in `width`.
            width=120,
# Hier wird der Button in Python mit der Geschwindigkeits-Methode verbunden.
            command=self.apply_stage_speed,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.speed_button.pack(pady=1)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.button_frame = ctk.CTkFrame(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="transparent"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.button_frame.pack(pady=1)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="or",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 14, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=3)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="Zielposition oder Distanz / Target or Distance (mm):",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=(5, 0))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Eingabefeld.
        self.target_entry = ctk.CTkEntry(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Eingabefeld für Ziel oder Distanz.
            placeholder_text="Target value or distance in mm",
# In Python speichert `=` hier einen Wert in `width`.
            width=250
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.target_entry.pack(pady=1)
# In Python wird mit `.` Text in ein Eingabefeld geschrieben.
        self.target_entry.insert(0, "0.01")
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.target_button_frame = ctk.CTkFrame(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="transparent"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.target_button_frame.pack(pady=1)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_target_abs = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.target_button_frame,
# Button zum Fahren auf eine Zielposition.
            text="Go to target",
# In Python speichert `=` hier einen Wert in `width`.
            width=140,
# Hier wird der Button in Python mit der Zielpositions-Methode verbunden.
            command=self.move_to_target,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_target_abs.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=0,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=1
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_target_rel = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.target_button_frame,
# Button zum Fahren um eine Distanz.
            text="Move distance",
# In Python speichert `=` hier einen Wert in `width`.
            width=140,
# Hier wird der Button in Python mit der Distanz-Methode verbunden.
            command=self.move_distance,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_target_rel.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=1,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=1
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_stop = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.target_button_frame,
# Button für den Sofortstopp der Stage.
            text="STOP STAGE",
# In Python speichert `=` hier einen Wert in `width`.
            width=140,
# Hier wird der Button in Python mit der Stopp-Methode verbunden.
            command=self.stop_stage,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=RED_COLOR,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11, "bold")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_stop.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=3,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=1
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_min = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.button_frame,
# Button für Minimalposition.
            text="|<",
# In Python speichert `=` hier einen Wert in `width`.
            width=60,
# Hier wird der Button in Python mit der Minimalpositions-Methode verbunden.
            command=self.move_to_min,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_min.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=0,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=1
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_left = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.button_frame,
# Button für einen kleinen Schritt nach links.
            text="<",
# In Python speichert `=` hier einen Wert in `width`.
            width=60,
# Hier wird der Button in Python mit der Rückwärts-Schritt-Methode verbunden.
            command=self.step_negative,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_left.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=1,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=1
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_center = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.button_frame,
# Button für die Nullposition.
            text="0",
# In Python speichert `=` hier einen Wert in `width`.
            width=60,
# Hier wird der Button in Python mit der Nullpositions-Methode verbunden.
            command=self.move_to_center,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_center.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=2,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=1
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_right = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.button_frame,
# Button für einen kleinen Schritt nach rechts.
            text=">",
# In Python speichert `=` hier einen Wert in `width`.
            width=60,
# Hier wird der Button in Python mit der Vorwärts-Schritt-Methode verbunden.
            command=self.step_positive,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_right.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=3,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=1
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_max = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.button_frame,
# Button für Maximalposition.
            text=">|",
# In Python speichert `=` hier einen Wert in `width`.
            width=60,
# Hier wird der Button in Python mit der Maximalpositions-Methode verbunden.
            command=self.move_to_max,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_max.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=4,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=1
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_stage_position = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Anzeige der aktuellen Position.
            text="Stage Position: 0.000000 mm",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 10),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_position.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_stage_moved = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Anzeige der gefahrenen Gesamtstrecke.
            text="Accumulated Movement: 0.000000 mm",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_moved.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_stage_speed = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# Anzeige der momentanen Geschwindigkeit.
            text="Movement Speed: 0.000000 mm/s",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 10),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_speed.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.frame = ctk.CTkFrame(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="#EEEEEE"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.frame.pack(
# In Python speichert `=` hier einen Wert in `fill`.
            fill="x",
# In Python speichert `=` hier einen Wert in `padx`.
            padx=5,
# In Python speichert `=` hier einen Wert in `pady`.
            pady=4
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_um = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige der aus Fringes berechneten Strecke.
            text="Distance from Fringes: 0.000 um",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 13, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_um.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_ps = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige der Zeitverzögerung.
            text="Time Delay: 0.0000 ps",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_ps.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_calibration_offset = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige für den späteren Schwellenwert.
            text="Fringe Rise Threshold: waiting",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_calibration_offset.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_calibration_scale = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige für die Fringe-Höhe.
            text="Fringe Amplitude: waiting",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_calibration_scale.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_sample_count = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige des Fringe-Zählers.
            text="Accumulated Fringes Count: 0",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 13, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_sample_count.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_min_voltage = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige der kleinsten Spannung.
            text="Min Voltage: n/a",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 10),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_min_voltage.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_max_voltage = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige der größten Spannung.
            text="Max Voltage: n/a",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 10),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_max_voltage.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_raw = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige der Rohspannung.
            text="Raw Voltage: 0.000000 V",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 10),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_raw.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_norm = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige der normierten Spannung.
            text="Normalized Voltage: 0.0000",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 10),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_norm.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_calibration = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.frame,
# Anzeige des Kalibrierungsstatus.
            text="Calibration: waiting",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 10),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_calibration.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.compare_frame = ctk.CTkFrame(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="#EEEEEE"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.compare_frame.pack(
# In Python speichert `=` hier einen Wert in `fill`.
            fill="x",
# In Python speichert `=` hier einen Wert in `padx`.
            padx=5,
# In Python speichert `=` hier einen Wert in `pady`.
            pady=4
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.compare_frame,
# Bereich für den Wegvergleich.
            text="Stage Movement",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 15, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.compare_driven_frame = ctk.CTkFrame(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.compare_frame,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="transparent"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.compare_driven_frame.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_compare_driven = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.compare_driven_frame,
# Anzeige des gefahrenen Wegs.
            text="Driven: 0.000000 mm",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_compare_driven.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=0,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=(0, 14)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_still_to_drive = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.compare_driven_frame,
# Anzeige der Reststrecke.
            text="Still to drive: 0.000000 mm",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_still_to_drive.grid(
# In Python speichert `=` hier einen Wert in `row`.
            row=0,
# In Python speichert `=` hier einen Wert in `column`.
            column=1,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=(14, 0)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_compare_calculated = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.compare_frame,
# Anzeige des aus Fringes berechneten Wegs.
            text="Calculated from Fringes: 0.000000 mm",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_compare_calculated.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_compare_difference = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.compare_frame,
# Anzeige der Abweichung.
            text="Difference: n/a",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 13, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_compare_difference.pack(pady=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `channel_text`.
        channel_text = f"Channel: photodiode={PHOTODIODE_CHANNEL}"
# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# In Python speichert `=` hier einen Wert in `text`.
            text=channel_text,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 10),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=(5, 2))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.plot_frame = ctk.CTkFrame(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="#EEEEEE"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.plot_frame.pack(
# In Python speichert `=` hier einen Wert in `fill`.
            fill="x",
# In Python speichert `=` hier einen Wert in `expand`.
            expand=False,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=5,
# In Python speichert `=` hier einen Wert in `pady`.
            pady=(4, 10)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.plot_header_frame = ctk.CTkFrame(self.plot_frame, fg_color="transparent")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.plot_header_frame.pack(fill="x", padx=10, pady=(5, 2))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_header_frame,
# Plot für die Rohspannung.
            text="Live Raw Voltage",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 15, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(side="left")
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den booleschen Startwert aus in `show_cleaned`.
        self.show_cleaned = False
# In Python erzeugt `()` einen Button.
        self.btn_toggle_clean = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_header_frame,
# Umschalter für geglättete Daten.
            text="Cleaned Signal: OFF",
# In Python speichert `=` hier einen Wert in `width`.
            width=150,
# In Python speichert `=` hier einen Wert in `height`.
            height=24,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="#555555",
# Hier wird der Button in Python mit der Methode für Start/Stopp verbunden.
            command=self.toggle_cleaned_signal
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_toggle_clean.pack(side="right")
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.build_plot()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 4.1.3 PLOT BUILD
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Erzeugt den Live-Plot.
    def build_plot(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if Figure is None or FigureCanvasTkAgg is None:
# In Python speichert `=` hier erstmal keinen Wert in `plot_axis`.
            self.plot_axis = None
# In Python speichert `=` hier erstmal keinen Wert in `plot_canvas`.
            self.plot_canvas = None
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
            ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.plot_frame,
# In Python speichert `=` hier einen Wert in `text`.
                text="Matplotlib is required for live voltage plotting.",
# In Python speichert `=` hier einen Wert in `font`.
                font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
            ).pack(pady=8)
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` eine Matplotlib-Figur.
        self.plot_figure = Figure(
# In Python speichert `=` hier einen Wert in `figsize`.
            figsize=(8, 2),
# In Python speichert `=` hier einen Wert in `dpi`.
            dpi=100
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `plot_axis`.
        self.plot_axis = self.plot_figure.add_subplot(111)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axis.set_title("Raw diode voltage", fontsize=9)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axis.set_xlabel("Samples", fontsize=8)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axis.set_ylabel("Voltage", fontsize=8)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axis.tick_params(labelsize=8)
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.plot_axis.grid(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            True,
# In Python speichert `=` hier einen Wert in `linestyle`.
            linestyle=":",
# In Python speichert `=` hier einen Wert in `alpha`.
            alpha=0.6
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `plot_line_voltage`.
        self.plot_line_voltage = self.plot_axis.plot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            [],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            [],
# In Python speichert `=` hier einen Wert in `color`.
            color="blue",
# In Python speichert `=` hier einen Wert in `alpha`.
            alpha=1.0,
# In Python speichert `=` hier einen Wert in `label`.
            label="photodiode raw"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )[0]
# In Python speichert `=` einen Wert in `plot_line_clean`.
        self.plot_line_clean = self.plot_axis.plot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            [],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            [],
# In Python speichert `=` hier einen Wert in `color`.
            color="blue",
# In Python speichert `=` hier einen Wert in `linewidth`.
            linewidth=1.5,
# In Python speichert `=` hier einen Wert in `label`.
            label="photodiode clean"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )[0]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_line_clean.set_visible(False)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axis.legend(loc="upper right", prop={"size": 8})
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_figure.subplots_adjust(
# In Python speichert `=` hier einen Wert in `left`.
            left=0.08,
# In Python speichert `=` hier einen Wert in `right`.
            right=0.98,
# In Python speichert `=` hier einen Wert in `top`.
            top=0.85,
# In Python speichert `=` hier einen Wert in `bottom`.
            bottom=0.22
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` die Einbettung des Plots ins Tk-Fenster.
        self.plot_canvas = FigureCanvasTkAgg(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_figure,
# In Python speichert `=` hier einen Wert in `master`.
            master=self.plot_frame
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_canvas.draw()
# In Python speichert `=` hier einen Wert in `plot_widget`.
        plot_widget = self.plot_canvas.get_tk_widget()
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
        plot_widget.configure(height=220)
# In Python wird mit `.` ein UI-Element im Layout platziert.
        plot_widget.pack(
# In Python speichert `=` hier einen Wert in `fill`.
            fill="x",
# In Python speichert `=` hier einen Wert in `expand`.
            expand=False,
# In Python speichert `=` hier einen Wert in `padx`.
            padx=8,
# In Python speichert `=` hier einen Wert in `pady`.
            pady=8
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 4.2 ENABLE OR DISABLE ALL BUTTONS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Schaltet Buttons gemeinsam an oder aus.
    def set_buttons_enabled(self, enabled):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `state`.
        state = "normal" if enabled else "disabled"
# Leerzeile zur besseren Lesbarkeit.

# `for` startet in Python eine Schleife über mehrere Werte.
        for button in self.all_buttons:
# In Python ruft `.` die Methode `configure` auf, um einen Button zu aktivieren oder zu sperren.
            button.configure(state=state)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.1 START OR STOP MONITORING
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Schaltet Messung ein oder aus.
    def toggle(self): # toggle method
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.is_monitoring:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stop_monitoring()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.start_monitoring()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.1.1 START MONITORING HELPER
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Startet die Messung.
    def start_monitoring(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.measurement_thread is not None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            and self.measurement_thread.is_alive()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.restart_values_only()
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das neu erzeugte Dioden-Objekt in einer Variable.
        self.diode = SingleDiodeHandler()
# In Python speichert `=` hier den booleschen Startwert ein in `is_monitoring`. Merker, ob die Messschleife läuft.
        self.is_monitoring = True
# In Python speichert `=` hier den booleschen Startwert ein in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
        self.calibrating = True
# In Python speichert `=` hier erstmal keinen Wert in `last_error_text`. letzte Fehlermeldung.
        self.last_error_text = None
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
        self.btn.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="STOP MONITORING",
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Status: connecting NI...",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.set_buttons_enabled(False)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `Thread(...)` einen Hintergrundthread.
        self.measurement_thread = threading.Thread(
# In Python speichert `=` hier einen Wert in `target`.
            target=self.loop,
# In Python speichert `=` hier einen Startwert in `daemon`.
            daemon=True
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python startet `start()` einen bereits erzeugten Thread.
        self.measurement_thread.start()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.1.2 STOP MONITORING HELPER
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Stoppt die Messung.
    def stop_monitoring(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den booleschen Startwert aus in `is_monitoring`. Merker, ob die Messschleife läuft.
        self.is_monitoring = False
# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
        self.calibrating = False
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.recording:
# In Python speichert `=` hier den booleschen Startwert aus in `recording`. Merker, ob gerade aufgenommen wird.
            self.recording = False
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
            self.btn_record.configure(
# Button zum Starten der Aufnahme.
                text="START RECORDING",
# In Python speichert `=` hier einen Wert in `fg_color`.
                fg_color="#555555"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.save_recorded_data()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected and self.stage.is_moving:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
            self.stage.stop()
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Status: stopping...",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 8.1 DIODE LOOP AND MEASUREMENT
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Hauptschleife für Messung und Kalibrierung.
    def loop(self):
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python ruft `.` eine Methode auf, die die Messhardware öffnet.
            self.diode.connect()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
            # Record baseline for 1.0s (200 samples) before starting stage motion/calibration
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text="Status: recording baseline noise...",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier einen Startwert in `baseline_samples`.
            baseline_samples = []
# `for` startet in Python eine Schleife über mehrere Werte.
            for _ in range(200):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if not self.is_monitoring:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                    return
# In Python ruft `.` eine Methode auf, die einen Messwert liest.
                sample = self.diode.read()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                baseline_samples.append(sample.raw_voltage)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                time.sleep(SAMPLE_INTERVAL_S)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if baseline_samples:
# In Python speichert `=` einen berechneten Wert in `baseline_voltage`. Baseline für das spätere Abziehen vom Rohsignal.
                self.baseline_voltage = sum(baseline_samples) / len(baseline_samples)
# In Python speichert `=` hier den booleschen Startwert ein in `baseline_recorded`. Merker, ob die Baseline schon gemessen wurde.
                self.baseline_recorded = True
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` einen Wert in `baseline_voltage`. Baseline für das spätere Abziehen vom Rohsignal.
                self.baseline_voltage = 0.0
# In Python speichert `=` hier den booleschen Startwert ein in `baseline_recorded`. Merker, ob die Baseline schon gemessen wurde.
                self.baseline_recorded = True
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=f"Status: calibrating {CALIBRATION_SECONDS:.1f}s...",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_connected:
# In Python erzeugt `Thread(...)` einen Hintergrundthread.
                threading.Thread(
# In Python speichert `=` hier einen Wert in `target`.
                    target=self.calibration_stage_motion,
# In Python speichert `=` hier einen Startwert in `daemon`.
                    daemon=True
# In Python startet `start()` einen bereits erzeugten Thread.
                ).start()
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `calibration`.
            calibration = self.diode.calibrate(
# In Python speichert `=` hier einen Wert in `seconds`.
                seconds=CALIBRATION_SECONDS,
# In Python speichert `=` hier einen Wert in `sample_interval_s`.
                sample_interval_s=SAMPLE_INTERVAL_S,
# In Python speichert `=` hier einen Wert in `should_continue`.
                should_continue=lambda: self.is_monitoring,
# In Python speichert `=` hier einen Wert in `sample_callback`.
                sample_callback=self.handle_calibration_sample
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.is_monitoring:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
            self.calibrating = False
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stop_calibration_stage_motion()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if calibration is not None:
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python speichert `=` hier einen Wert in `lambda c`.
                    lambda c=calibration:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.finish_calibration_display(c)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
            while self.is_monitoring:
# In Python ruft `.` eine Methode auf, die einen Messwert liest.
                sample = self.diode.read()
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python speichert `=` hier einen Wert in `lambda s`.
                    lambda s=sample:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.update_sample_display(s)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                time.sleep(SAMPLE_INTERVAL_S)
# Leerzeile zur besseren Lesbarkeit.

# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except Exception as error:
# In Python speichert `=` einen Wert in `last_error_text`. letzte Fehlermeldung.
            self.last_error_text = str(error)
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda e`.
                lambda e=error:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.show_error(e)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `finally` läuft in Python immer, auch wenn vorher ein Fehler aufgetreten ist.
        finally:
# In Python speichert `=` hier den booleschen Startwert aus in `is_monitoring`. Merker, ob die Messschleife läuft.
            self.is_monitoring = False
# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
            self.calibrating = False
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
            try:
# In Python ruft `.` eine Methode auf, die die Verbindung schließt.
                self.diode.close()
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
            except Exception:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                pass
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.finish_stopped_ui
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.8 HANDLE CALIBRATION SAMPLE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Gibt einen Kalibrierungswert an die Anzeige weiter.
    def handle_calibration_sample(self, raw_voltage, elapsed_s, total_s):
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
        self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python speichert `=` hier einen Wert in `lambda v`.
            lambda v=raw_voltage, e=elapsed_s, t=total_s:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.update_calibration_progress(v, e, t)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.8.1 UPDATE CALIBRATION PROGRESS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Aktualisiert die Kalibrierungsanzeige.
    def update_calibration_progress(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        raw_voltage,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        elapsed_s,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        total_s
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.calibration_raw_samples.append(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raw_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.append_raw_history(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raw_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `now`.
        now = time.time()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if now - getattr(self, '_last_cal_draw_time', 0.0) >= 0.05:
# In Python speichert `=` einen Wert in `_last_cal_draw_time`.
            self._last_cal_draw_time = now
# In Python ruft `.` eine eigene Methode auf.
            self.update_plot()
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_raw.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"Raw Voltage: {raw_voltage:+.6f} V"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_calibration.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"Calibration: {elapsed_s:.1f}/{total_s:.1f}s"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.8.2 FINISH CALIBRATION DISPLAY
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Wertet die Kalibrierung aus.
    def finish_calibration_display(self, calibration):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `extrema_samples`.
        extrema_samples = self.select_calibration_extrema_samples(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.calibration_raw_samples
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            fringe_min_voltage,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            fringe_max_voltage,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            extrema_count,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            fringe_amplitude_voltage
# In Python speichert `=` hier einen Wert in `)`.
        ) = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.find_calibration_fringe_extrema(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                extrema_samples
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if fringe_min_voltage is None or fringe_max_voltage is None:
# In Python speichert `=` hier einen Wert in `fringe_min_voltage`.
            fringe_min_voltage = calibration.min_voltage
# In Python speichert `=` hier einen Wert in `fringe_max_voltage`.
            fringe_max_voltage = calibration.max_voltage
# In Python speichert `=` hier einen Wert in `fringe_amplitude_voltage`.
            fringe_amplitude_voltage = DEFAULT_FRINGE_AMPLITUDE_V
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.apply_calibration_extrema(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            calibration,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            fringe_min_voltage,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            fringe_max_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.configure_fringe_detection(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            fringe_amplitude_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `value_range`.
        value_range = fringe_max_voltage - fringe_min_voltage
# In Python speichert `=` einen Wert in `dark_threshold`. Schwelle für dunkel.
        self.dark_threshold = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            fringe_min_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            + value_range * DARK_LEVEL_FRACTION
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `bright_threshold`. Schwelle für hell.
        self.bright_threshold = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            fringe_min_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            + value_range * BRIGHT_LEVEL_FRACTION
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_calibration.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"Fringe calibration min/max: "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{fringe_min_voltage:+.6f}/"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{fringe_max_voltage:+.6f} V "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"({extrema_count} extrema, "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"amp {self.fringe_amplitude_voltage:.6f} V, "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"noise {self.noise_amplitude_voltage:.6f} V)"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_calibration_offset.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"Fringe Rise Threshold: "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{self.fringe_rise_threshold_voltage:.6f} V, "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"min amp {self.min_count_amplitude_voltage:.6f} V, "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"max {MAX_FRINGE_WIDTH_FRAMES} frames"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_calibration_scale.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"Fringe Amplitude: "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{self.fringe_amplitude_voltage:.6f} V"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_min_voltage.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text=f"Min Voltage: {fringe_min_voltage:+.6f} V"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_max_voltage.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text=f"Max Voltage: {fringe_max_voltage:+.6f} V"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected or not self.stage.is_moving:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.set_buttons_enabled(True)
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Status: monitoring running",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Sucht Minima und Maxima.
    def find_calibration_fringe_extrema(self, samples):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not samples:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return None, None, 0, DEFAULT_FRINGE_AMPLITUDE_V
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if len(samples) < 5:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                min(samples),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                max(samples),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                DEFAULT_FRINGE_AMPLITUDE_V
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `smoothed_samples`.
        smoothed_samples = []
# Leerzeile zur besseren Lesbarkeit.

# `for` startet in Python eine Schleife über mehrere Werte.
        for index in range(len(samples)):
# In Python speichert `=` hier einen Wert in `start_index`.
            start_index = max(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                index - 2
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier einen Wert in `end_index`.
            end_index = min(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                len(samples),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                index + 3
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier einen Wert in `window`.
            window = samples[start_index:end_index]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            smoothed_samples.append(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                sum(window) / len(window)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `minima`.
        minima = []
# In Python speichert `=` hier einen Startwert in `maxima`.
        maxima = []
# In Python speichert `=` hier einen Startwert in `extrema`.
        extrema = []
# Leerzeile zur besseren Lesbarkeit.

# `for` startet in Python eine Schleife über mehrere Werte.
        for index in range(1, len(smoothed_samples) - 1):
# In Python speichert `=` hier einen berechneten Wert in `previous_value`.
            previous_value = smoothed_samples[index - 1]
# In Python speichert `=` hier einen Wert in `current_value`.
            current_value = smoothed_samples[index]
# In Python speichert `=` hier einen berechneten Wert in `next_value`.
            next_value = smoothed_samples[index + 1]
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    current_value <= previous_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    and current_value < next_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                or (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    current_value < previous_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    and current_value <= next_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                minima.append(current_value)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                extrema.append(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    ("min", current_value)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    current_value >= previous_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    and current_value > next_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                or (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    current_value > previous_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    and current_value >= next_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                maxima.append(current_value)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                extrema.append(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    ("max", current_value)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if minima and maxima:
# In Python speichert `=` hier einen Wert in `fringe_amplitude`.
            fringe_amplitude = self.estimate_fringe_amplitude(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                extrema,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                max(maxima) - min(minima)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                min(minima),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                max(maxima),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                len(minima) + len(maxima),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                fringe_amplitude
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            min(smoothed_samples),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            max(smoothed_samples),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            DEFAULT_FRINGE_AMPLITUDE_V
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Wählt die auswertbaren Kalibrierungsdaten aus.
    def select_calibration_extrema_samples(self, samples):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            not self.stage_connected
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            or len(samples) < 10
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return samples
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `forward_sample_count`.
        forward_sample_count = int(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            len(samples) * CALIBRATION_FORWARD_ANALYSIS_FRACTION
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier einen Wert in `forward_sample_count`.
        forward_sample_count = max(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            10,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            min(len(samples), forward_sample_count)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return samples[:forward_sample_count]
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Schätzt die Fringe-Höhe.
    def estimate_fringe_amplitude(self, extrema, fallback_amplitude):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `compressed_extrema`.
        compressed_extrema = []
# Leerzeile zur besseren Lesbarkeit.

# `for` startet in Python eine Schleife über mehrere Werte.
        for kind, value in extrema:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                compressed_extrema
# In Python speichert `=` hier einen Wert in `and compressed_extrema[-1][0] =`.
                and compressed_extrema[-1][0] == kind
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ):
# In Python speichert `=` hier einen berechneten Wert in `previous_kind, previous_value`.
                previous_kind, previous_value = compressed_extrema[-1]
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if (
# In Python speichert `=` hier einen Wert in `kind =`.
                    kind == "min"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    and value < previous_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                ):
# In Python speichert `=` hier einen Wert in `compressed_extrema[-1]`.
                    compressed_extrema[-1] = (previous_kind, value)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if (
# In Python speichert `=` hier einen Wert in `kind =`.
                    kind == "max"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    and value > previous_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                ):
# In Python speichert `=` hier einen Wert in `compressed_extrema[-1]`.
                    compressed_extrema[-1] = (previous_kind, value)
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                continue
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            compressed_extrema.append(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                (kind, value)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `measured_amplitudes`.
        measured_amplitudes = []
# Leerzeile zur besseren Lesbarkeit.

# `for` startet in Python eine Schleife über mehrere Werte.
        for index in range(1, len(compressed_extrema)):
# In Python speichert `=` hier einen berechneten Wert in `previous_kind, previous_value`.
            previous_kind, previous_value = compressed_extrema[index - 1]
# In Python speichert `=` hier einen Wert in `current_kind, current_value`.
            current_kind, current_value = compressed_extrema[index]
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if previous_kind == current_kind:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                continue
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `amplitude`.
            amplitude = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                current_value - previous_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if amplitude <= MAX_VALID_FRINGE_AMPLITUDE_V:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                measured_amplitudes.append(amplitude)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `noise_amplitude`.
        noise_amplitude = self.estimate_noise_amplitude(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            measured_amplitudes
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier einen Wert in `min_count_amplitude`.
        min_count_amplitude = max(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            MIN_VALID_FRINGE_AMPLITUDE_V,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            noise_amplitude * MIN_FRINGE_TO_NOISE_RATIO
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier einen Wert in `amplitudes`.
        amplitudes = [
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            amplitude
# `for` startet in Python eine Schleife über mehrere Werte.
            for amplitude in measured_amplitudes
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if amplitude >= min_count_amplitude
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ]
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `noise_amplitude_voltage`. geschätzte Rauschhöhe.
        self.noise_amplitude_voltage = noise_amplitude
# In Python speichert `=` einen Wert in `min_count_amplitude_voltage`. kleinste zulässige Fringe-Höhe.
        self.min_count_amplitude_voltage = min_count_amplitude
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if amplitudes:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            amplitudes.sort()
# In Python speichert `=` hier einen berechneten Wert in `upper_half`.
            upper_half = amplitudes[len(amplitudes) // 2:]
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return self.median_value(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                upper_half
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            min_count_amplitude
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            <= fallback_amplitude
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            <= MAX_VALID_FRINGE_AMPLITUDE_V
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return fallback_amplitude
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return DEFAULT_FRINGE_AMPLITUDE_V
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Schätzt das Rauschen.
    def estimate_noise_amplitude(self, amplitudes):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not amplitudes:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return DEFAULT_NOISE_AMPLITUDE_V
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `sorted_amplitudes`.
        sorted_amplitudes = sorted(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            amplitude
# `for` startet in Python eine Schleife über mehrere Werte.
            for amplitude in amplitudes
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if amplitude > 0.0
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not sorted_amplitudes:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return DEFAULT_NOISE_AMPLITUDE_V
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `lower_count`.
        lower_count = max(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            1,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            len(sorted_amplitudes) // 3
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier einen Wert in `estimated_noise`.
        estimated_noise = self.median_value(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sorted_amplitudes[:lower_count]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return min(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            estimated_noise,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            DEFAULT_NOISE_AMPLITUDE_V
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Berechnet den Median.
    def median_value(self, values):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not values:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return DEFAULT_FRINGE_AMPLITUDE_V
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `sorted_values`.
        sorted_values = sorted(values)
# In Python speichert `=` hier einen berechneten Wert in `middle_index`.
        middle_index = len(sorted_values) // 2
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if len(sorted_values) % 2:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return sorted_values[middle_index]
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sorted_values[middle_index - 1]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            + sorted_values[middle_index]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / 2
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt Erkennungsschwellen neu.
    def configure_fringe_detection(self, amplitude_voltage):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            amplitude_voltage is None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            or amplitude_voltage < MIN_VALID_FRINGE_AMPLITUDE_V
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            or amplitude_voltage > MAX_VALID_FRINGE_AMPLITUDE_V
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ):
# In Python speichert `=` hier einen Wert in `amplitude_voltage`.
            amplitude_voltage = DEFAULT_FRINGE_AMPLITUDE_V
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `fringe_amplitude_voltage`. geschätzte Fringe-Höhe.
        self.fringe_amplitude_voltage = amplitude_voltage
# In Python speichert `=` hier einen Wert in `detection_amplitude_voltage`.
        detection_amplitude_voltage = min(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.fringe_amplitude_voltage,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            EXPECTED_FRINGE_AMPLITUDE_V
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `fringe_rise_threshold_voltage`. Anstiegsschwelle für ein Fringe.
        self.fringe_rise_threshold_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            detection_amplitude_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            * FRINGE_RISE_FRACTION
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `fringe_rearm_threshold_voltage`. Schwelle, ab der die Erkennung wieder bereit ist.
        self.fringe_rearm_threshold_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            detection_amplitude_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            * FRINGE_REARM_FRACTION
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier erstmal keinen Wert in `fringe_trough_voltage`. gemerkter Tiefpunkt des Signals.
        self.fringe_trough_voltage = None
# In Python speichert `=` hier erstmal keinen Wert in `fringe_peak_voltage`. gemerkter Hochpunkt des Signals.
        self.fringe_peak_voltage = None
# In Python speichert `=` hier den booleschen Startwert aus in `was_dark`. Merker für den Dunkelzustand.
        self.was_dark = False
# In Python speichert `=` einen Wert in `dark_counter`. Zähler für dunkle Frames.
        self.dark_counter = 0
# In Python speichert `=` einen Wert in `bright_counter`. Zähler für helle Frames.
        self.bright_counter = 0
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Überträgt die Kalibrierung.
    def apply_calibration_extrema(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        calibration,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        min_voltage,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        max_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `offset_voltage`.
        offset_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            min_voltage + max_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / 2
# In Python speichert `=` hier einen Wert in `scale_voltage`.
        scale_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            max_voltage - min_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / 2
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if scale_voltage <= 1e-12:
# In Python speichert `=` hier einen Wert in `scale_voltage`.
            scale_voltage = 1.0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `calibration.min_voltage`.
        calibration.min_voltage = min_voltage
# In Python speichert `=` hier einen Wert in `calibration.max_voltage`.
        calibration.max_voltage = max_voltage
# In Python speichert `=` hier einen Wert in `calibration.offset_voltage`.
        calibration.offset_voltage = offset_voltage
# In Python speichert `=` hier einen Wert in `calibration.scale_voltage`.
        calibration.scale_voltage = scale_voltage
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `diode.counter.min_voltage`.
        self.diode.counter.min_voltage = min_voltage
# In Python speichert `=` einen Wert in `diode.counter.max_voltage`.
        self.diode.counter.max_voltage = max_voltage
# In Python speichert `=` einen Wert in `diode.counter.offset_voltage`.
        self.diode.counter.offset_voltage = offset_voltage
# In Python speichert `=` einen Wert in `diode.counter.scale_voltage`.
        self.diode.counter.scale_voltage = scale_voltage
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 8.3 SHOW CURRENT VOLTAGE AND DISTANCE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Aktualisiert die Live-Anzeige.
    def update_sample_display(self, sample):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `latest_sample`. letzte Messprobe.
        self.latest_sample = sample
# In Python speichert `=` einen Wert in `latest_voltage`. letzter Spannungswert.
        self.latest_voltage = sample.raw_voltage
# In Python speichert `=` hier einen Wert in `fringe_counted`.
        fringe_counted = self.update_accumulated_fringes(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sample.raw_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.append_raw_history(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sample.raw_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `distance_mm`.
        distance_mm = self.accumulated_fringes * self.fringe_distance_mm
# In Python speichert `=` hier einen berechneten Wert in `distance_um`.
        distance_um = distance_mm * 1000
# In Python speichert `=` hier einen berechneten Wert in `time_ps`.
        time_ps = (2 * distance_mm) / SPEED_OF_LIGHT_MM_PS
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.recording:
# In Python speichert `=` hier einen berechneten Wert in `elapsed`.
            elapsed = time.time() - self.recording_start_time
# In Python speichert `=` hier einen berechneten Wert in `clean_val`.
            clean_val = sample.raw_voltage - self.baseline_voltage
# In Python ruft `.` eine Methode auf, die die Position liest.
            stage_pos = self.stage.get_position() if (self.stage_connected and self.stage is not None) else 0.0
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.recorded_data.append((
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                elapsed,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                sample.raw_voltage,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                clean_val,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.accumulated_fringes,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                distance_mm,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                stage_pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ))
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `now`.
        now = time.time()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if now - getattr(self, '_last_sample_draw_time', 0.0) >= 0.05:
# In Python speichert `=` einen Wert in `_last_sample_draw_time`.
            self._last_sample_draw_time = now
# In Python ruft `.` eine eigene Methode auf.
            self.update_plot()
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_um.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Distance from Fringes: {distance_um:.6f} um"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_ps.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Time Delay: {time_ps:.4f} ps"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_sample_count.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Accumulated Fringes Count: {self.accumulated_fringes}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_raw.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"Raw Voltage: {sample.raw_voltage:+.6f} V"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_norm.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"Normalized Voltage: {sample.normalized_voltage:+.4f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if fringe_counted:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_sample_count.configure(
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                250,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_sample_count.configure(
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_comparison_labels()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 8.2 DETECT AND COUNT FRINGES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Zählt Fringes mit Hysterese.
    def update_accumulated_fringes(self, voltage):
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.smoothed_voltage_history.append(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if len(self.smoothed_voltage_history) > SMOOTHING_WINDOW_LENGTH:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.smoothed_voltage_history.pop(0)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `smooth_voltage`.
        smooth_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sum(self.smoothed_voltage_history)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            / len(self.smoothed_voltage_history)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.fringe_trough_voltage is None:
# In Python speichert `=` einen Wert in `fringe_trough_voltage`. gemerkter Tiefpunkt des Signals.
            self.fringe_trough_voltage = smooth_voltage
# In Python speichert `=` einen Wert in `fringe_peak_voltage`. gemerkter Hochpunkt des Signals.
            self.fringe_peak_voltage = smooth_voltage
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.fringe_peak_voltage is None:
# In Python speichert `=` einen Wert in `fringe_peak_voltage`. gemerkter Hochpunkt des Signals.
            self.fringe_peak_voltage = smooth_voltage
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `cooldown_ok`.
        cooldown_ok = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            time.time() - self.last_count_time
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) > FRINGE_COOLDOWN
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.was_dark:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if smooth_voltage > self.fringe_peak_voltage:
# In Python speichert `=` einen Wert in `fringe_peak_voltage`. gemerkter Hochpunkt des Signals.
                self.fringe_peak_voltage = smooth_voltage
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `enough_drop_from_peak`.
            enough_drop_from_peak = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.fringe_peak_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                - smooth_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ) >= self.fringe_rearm_threshold_voltage
# In Python speichert `=` hier einen Wert in `below_dark_level`.
            below_dark_level = smooth_voltage <= self.dark_threshold
# In Python speichert `=` hier einen Wert in `started_near_trough`.
            started_near_trough = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.fringe_peak_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                - self.fringe_trough_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ) < self.fringe_rearm_threshold_voltage
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                enough_drop_from_peak
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                or below_dark_level
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                or started_near_trough
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ):
# In Python speichert `=` einen Wert in `dark_counter +`.
                self.dark_counter += 1
# In Python speichert `=` einen Wert in `fringe_trough_voltage`. gemerkter Tiefpunkt des Signals.
                self.fringe_trough_voltage = min(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.fringe_trough_voltage,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    smooth_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` einen Wert in `dark_counter`. Zähler für dunkle Frames.
                self.dark_counter = 0
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.dark_counter >= REQUIRED_DARK_FRAMES:
# In Python speichert `=` hier den booleschen Startwert ein in `was_dark`. Merker für den Dunkelzustand.
                self.was_dark = True
# In Python speichert `=` einen Wert in `fringe_trough_voltage`. gemerkter Tiefpunkt des Signals.
                self.fringe_trough_voltage = smooth_voltage
# In Python speichert `=` einen Wert in `bright_counter`. Zähler für helle Frames.
                self.bright_counter = 0
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if smooth_voltage < self.fringe_trough_voltage:
# In Python speichert `=` einen Wert in `fringe_trough_voltage`. gemerkter Tiefpunkt des Signals.
            self.fringe_trough_voltage = smooth_voltage
# In Python speichert `=` einen Wert in `bright_counter`. Zähler für helle Frames.
            self.bright_counter = 0
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `rise_from_trough`.
        rise_from_trough = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            smooth_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            - self.fringe_trough_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier einen Wert in `peak_is_large_enough`.
        peak_is_large_enough = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            rise_from_trough >= self.fringe_rise_threshold_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if peak_is_large_enough:
# In Python speichert `=` einen Wert in `bright_counter +`.
            self.bright_counter += 1
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` einen Wert in `bright_counter`. Zähler für helle Frames.
            self.bright_counter = 0
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.was_dark
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            and self.bright_counter >= REQUIRED_BRIGHT_FRAMES
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            and cooldown_ok
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ):
# In Python speichert `=` einen Wert in `accumulated_fringes +`.
            self.accumulated_fringes += 1
# In Python speichert `=` hier den booleschen Startwert aus in `was_dark`. Merker für den Dunkelzustand.
            self.was_dark = False
# In Python speichert `=` den aktuellen Zeitstempel in `last_count_time`. Zeitpunkt des letzten Zählereignisses.
            self.last_count_time = time.time()
# In Python speichert `=` einen Wert in `dark_counter`. Zähler für dunkle Frames.
            self.dark_counter = 0
# In Python speichert `=` einen Wert in `bright_counter`. Zähler für helle Frames.
            self.bright_counter = 0
# In Python speichert `=` einen Wert in `fringe_peak_voltage`. gemerkter Hochpunkt des Signals.
            self.fringe_peak_voltage = smooth_voltage
# In Python speichert `=` einen Wert in `fringe_trough_voltage`. gemerkter Tiefpunkt des Signals.
            self.fringe_trough_voltage = smooth_voltage
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return True
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return False
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 8.4 APPEND RAW VOLTAGE TO HISTORY
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Speichert Rohwerte für den Plot.
    def append_raw_history(self, raw_voltage):
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.raw_voltage_history.append(raw_voltage)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if len(self.raw_voltage_history) > RAW_HISTORY_LENGTH:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.raw_voltage_history.pop(0)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Cleaned version: subtract baseline and apply low-pass filter
# In Python speichert `=` hier einen Wert in `baseline`.
        baseline = getattr(self, 'baseline_voltage', 0.0)
# In Python speichert `=` hier einen berechneten Wert in `clean_voltage`.
        clean_voltage = raw_voltage - baseline
# Leerzeile zur besseren Lesbarkeit.
        
# In Python speichert `=` hier einen Wert in `alpha`.
        alpha = 0.3
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not hasattr(self, 'clean_lp_voltage'):
# In Python speichert `=` einen Wert in `clean_lp_voltage`.
            self.clean_lp_voltage = clean_voltage
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` einen berechneten Wert in `clean_lp_voltage`.
            self.clean_lp_voltage = alpha * clean_voltage + (1.0 - alpha) * self.clean_lp_voltage
# Leerzeile zur besseren Lesbarkeit.
            
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.clean_voltage_history.append(self.clean_lp_voltage)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if len(self.clean_voltage_history) > RAW_HISTORY_LENGTH:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.clean_voltage_history.pop(0)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 8.5 LIVE VOLTAGE PLOT UPDATE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Aktualisiert die Grafik.
    def update_plot(self, reset=False):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.plot_axis is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if reset:
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_line_voltage.set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_line_clean.set_data([], [])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_axis.relim()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_axis.autoscale_view()
# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
            self.plot_canvas.draw_idle()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `x`.
        x = list(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            range(len(self.raw_voltage_history))
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
        self.plot_line_voltage.set_data(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            x,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.raw_voltage_history
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.show_cleaned and len(self.clean_voltage_history) == len(x):
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_line_clean.set_data(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                x,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.clean_voltage_history
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_line_clean.set_data([], [])
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axis.relim()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axis.autoscale_view()
# Leerzeile zur besseren Lesbarkeit.

# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
        self.plot_canvas.draw_idle()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Schaltet die geglättete Anzeige um.
    def toggle_cleaned_signal(self):
# In Python speichert `=` einen Wert in `show_cleaned`.
        self.show_cleaned = not self.show_cleaned
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.show_cleaned:
# In Python ruft `.` die Methode `configure` auf, um den Text eines UI-Elements zu ändern.
            self.btn_toggle_clean.configure(text="Cleaned Signal: ON", fg_color=TEXT_COLOR)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_line_voltage.set_alpha(0.3)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_line_clean.set_visible(True)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# Umschalter für geglättete Daten.
            self.btn_toggle_clean.configure(text="Cleaned Signal: OFF", fg_color="#555555")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_line_voltage.set_alpha(1.0)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_line_clean.set_visible(False)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axis.legend(loc="upper right", prop={"size": 8})
# In Python ruft `.` eine eigene Methode auf.
        self.update_plot()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 8.6 SHOW MONITORING ERROR
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Zeigt eine Fehlermeldung.
    def show_error(self, error):
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Status: {error}",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 8.7 RESET UI AFTER MONITORING STOPS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt die Oberfläche nach dem Stopp zurück.
    def finish_stopped_ui(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
        self.btn.configure(
# Button zum Starten und Stoppen der Messung.
            text="START MONITORING",
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.last_error_text:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Status: {self.last_error_text}",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# Anzeige für den Zustand ohne Messung.
                text="Status: Stopped",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.2 RESET BUTTON
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Löst einen Reset aus.
    def restart(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.restart_values_only() # button calls "restart" function, which forwards to "restart_values_only"
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.2.1 RESET VALUES ONLY
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt Messwerte zurück.
    def restart_values_only(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.diode is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.diode.counter.reset()
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier erstmal keinen Wert in `latest_sample`. letzte Messprobe.
        self.latest_sample = None
# In Python speichert `=` einen Wert in `latest_voltage`. letzter Spannungswert.
        self.latest_voltage = 0.0
# In Python speichert `=` hier eine leere Liste in `raw_voltage_history`. Verlauf der Rohspannungen.
        self.raw_voltage_history = []
# In Python speichert `=` hier eine leere Liste in `clean_voltage_history`. Verlauf der geglätteten Spannungen.
        self.clean_voltage_history = []
# In Python speichert `=` hier eine leere Liste in `calibration_raw_samples`. gesammelte Rohdaten der Kalibrierung.
        self.calibration_raw_samples = []
# In Python speichert `=` hier eine leere Liste in `smoothed_voltage_history`. kleines Fenster geglätteter Spannungen.
        self.smoothed_voltage_history = []
# In Python speichert `=` hier eine leere Liste in `recorded_data`. gesammelte Daten für den Export.
        self.recorded_data = []
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'clean_lp_voltage'):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            del self.clean_lp_voltage
# Originalkommentar oder Abschnittsüberschrift.
        #defines what the values should look like after pressing reset
# In Python speichert `=` einen Wert in `accumulated_fringes`. bisher gezählte Fringe-Anzahl.
        self.accumulated_fringes = 0
# In Python speichert `=` hier den booleschen Startwert aus in `was_dark`. Merker für den Dunkelzustand.
        self.was_dark = False
# In Python speichert `=` einen Wert in `dark_counter`. Zähler für dunkle Frames.
        self.dark_counter = 0
# In Python speichert `=` einen Wert in `bright_counter`. Zähler für helle Frames.
        self.bright_counter = 0
# In Python speichert `=` einen Wert in `last_count_time`. Zeitpunkt des letzten Zählereignisses.
        self.last_count_time = 0.0
# In Python speichert `=` einen Wert in `dark_threshold`. Schwelle für dunkel.
        self.dark_threshold = 0.0
# In Python speichert `=` einen Wert in `bright_threshold`. Schwelle für hell.
        self.bright_threshold = 0.0
# In Python speichert `=` einen Wert in `noise_amplitude_voltage`. geschätzte Rauschhöhe.
        self.noise_amplitude_voltage = DEFAULT_NOISE_AMPLITUDE_V
# In Python speichert `=` einen Wert in `min_count_amplitude_voltage`. kleinste zulässige Fringe-Höhe.
        self.min_count_amplitude_voltage = MIN_VALID_FRINGE_AMPLITUDE_V
# In Python speichert `=` hier erstmal keinen Wert in `fringe_trough_voltage`. gemerkter Tiefpunkt des Signals.
        self.fringe_trough_voltage = None
# In Python speichert `=` hier erstmal keinen Wert in `fringe_peak_voltage`. gemerkter Hochpunkt des Signals.
        self.fringe_peak_voltage = None
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.reset_stage_movement_tracking() # function defined later
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_um.configure(
# Anzeige der aus Fringes berechneten Strecke.
            text="Distance from Fringes: 0.000 um"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_ps.configure(
# Anzeige der Zeitverzögerung.
            text="Time Delay: 0.0000 ps"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Startet oder stoppt die Aufzeichnung.
    def toggle_recording(self):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        import time
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        from tkinter import messagebox
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.is_monitoring:
# In Python öffnet das `messagebox`-Modul ein Dialogfenster für den Benutzer.
            messagebox.showwarning("Aufnahme", "Bitte starte zuerst das Monitoring.")
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.recording:
# In Python speichert `=` hier eine leere Liste in `recorded_data`. gesammelte Daten für den Export.
            self.recorded_data = []
# In Python speichert `=` den aktuellen Zeitstempel in `recording_start_time`. Startzeit der Aufnahme.
            self.recording_start_time = time.time()
# In Python speichert `=` hier den booleschen Startwert ein in `recording`. Merker, ob gerade aufgenommen wird.
            self.recording = True
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
            self.btn_record.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="REC ● STOP",
# In Python speichert `=` hier einen Wert in `fg_color`.
                fg_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` hier den booleschen Startwert aus in `recording`. Merker, ob gerade aufgenommen wird.
            self.recording = False
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
            self.btn_record.configure(
# Button zum Starten der Aufnahme.
                text="START RECORDING",
# In Python speichert `=` hier einen Wert in `fg_color`.
                fg_color="#555555"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.save_recorded_data()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Speichert die aufgezeichneten Daten.
    def save_recorded_data(self):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        import datetime
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        import csv
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        from tkinter import filedialog, messagebox
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.recorded_data:
# In Python öffnet das `messagebox`-Modul ein Dialogfenster für den Benutzer.
            messagebox.showinfo("Aufnahme", "Keine Messdaten zum Speichern vorhanden.")
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `file_path`.
        file_path = filedialog.asksaveasfilename(
# In Python speichert `=` hier einen Wert in `defaultextension`.
            defaultextension=".csv",
# In Python speichert `=` hier einen berechneten Wert in `filetypes`.
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
# In Python speichert `=` hier einen Wert in `title`.
            title="Messdaten speichern",
# In Python speichert `=` hier einen Wert in `initialfile`.
            initialfile=f"diode_messung_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.
        
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if file_path:
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
            try:
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
                with open(file_path, "w", newline="") as f:
# In Python speichert `=` hier einen Wert in `writer`.
                    writer = csv.writer(f)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    writer.writerow([
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Relative_Time_s",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Raw_Voltage_V",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Clean_Voltage_V",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Fringe_Count",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Calculated_Distance_mm",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Stage_Position_mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    ])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    writer.writerows(self.recorded_data)
# In Python öffnet das `messagebox`-Modul ein Dialogfenster für den Benutzer.
                messagebox.showinfo("Erfolg", f"Daten erfolgreich in '{file_path}' gespeichert!")
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
            except Exception as e:
# In Python öffnet das `messagebox`-Modul ein Dialogfenster für den Benutzer.
                messagebox.showerror("Fehler", f"Fehler beim Speichern der Datei:\n{str(e)}")
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_calibration_offset.configure(
# Anzeige für den späteren Schwellenwert.
            text="Fringe Rise Threshold: waiting"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_calibration_scale.configure(
# Anzeige für die Fringe-Höhe.
            text="Fringe Amplitude: waiting"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_sample_count.configure(
# Anzeige des Fringe-Zählers.
            text="Accumulated Fringes Count: 0",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_min_voltage.configure(
# Anzeige der kleinsten Spannung.
            text="Min Voltage: n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_max_voltage.configure(
# Anzeige der größten Spannung.
            text="Max Voltage: n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_raw.configure(
# Anzeige der Rohspannung.
            text="Raw Voltage: 0.000000 V"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_norm.configure(
# Anzeige der normierten Spannung.
            text="Normalized Voltage: 0.0000"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_calibration.configure(
# Anzeige des Kalibrierungsstatus.
            text="Calibration: waiting",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine eigene Methode auf.
        self.update_plot(reset=True)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_comparison_labels(0.0)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Liest eine Zahl aus einem Eingabefeld.
    def parse_entry_float(self, entry):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return float(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            entry.get().replace(",", ".")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.6 READ STEP SIZE FROM THE UI
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Liest die Schrittweite.
    def get_step_size(self):
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #convert the user input from the UI into something readable for the program
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `value`.
            value = self.parse_entry_float(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.step_entry
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier einen Wert in `value`.
            value = abs(value)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if value <= 0:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                raise ValueError
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return value
# Leerzeile zur besseren Lesbarkeit.

# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except ValueError:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: invalid step size",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return 0.0001 # safe default size when step size invalid
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.6.1 READ STAGE SPEED FROM THE UI
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Liest die Geschwindigkeit.
    def get_stage_speed(self):
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `value`.
            value = self.parse_entry_float(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.speed_entry
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier einen Wert in `value`.
            value = abs(value)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if value <= 0:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                raise ValueError
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return value
# Leerzeile zur besseren Lesbarkeit.

# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except ValueError:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: invalid movement speed",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return None
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.8 APPLY A NEW LASER WAVELENGTH
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Übernimmt die Laserwellenlänge.
    def apply_wavelength(self):
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # get the new laser wavelenght from the UI
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `wavelength_nm`.
            wavelength_nm = self.parse_entry_float(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.wavelength_entry
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except ValueError:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Invalid wavelength value",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if wavelength_nm <= 0:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Wavelength must be positive",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `laser_wavelength_nm`. gespeicherte Laserwellenlänge.
        self.laser_wavelength_nm = wavelength_nm
# In Python speichert `=` das Berechnungsergebnis in `fringe_distance_mm`. Abstand zwischen zwei Fringes.
        self.fringe_distance_mm = compute_fringe_distance_mm(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.laser_wavelength_nm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` das Berechnungsergebnis in `quarter_wavelength_step_mm`. empfohlene Viertelwellen-Schrittweite.
        self.quarter_wavelength_step_mm = compute_quarter_wavelength_step_mm(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.laser_wavelength_nm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #clear old suggested stepsize
# In Python wird mit `.` ein Eingabefeld geleert.
        self.step_entry.delete(0, "end")
# In Python wird mit `.` Text in ein Eingabefeld geschrieben.
        self.step_entry.insert(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            f"{self.quarter_wavelength_step_mm:.9f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Wavelength set to {self.laser_wavelength_nm:.1f} nm",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.6.2 APPLY STAGE SPEED
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Übernimmt die Stage-Geschwindigkeit.
    def apply_stage_speed(self, update_status=True):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `speed_mm_s`.
        speed_mm_s = self.get_stage_speed()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if speed_mm_s is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# In Python wird mit `.` ein Eingabefeld geleert.
        self.speed_entry.delete(0, "end")
# In Python wird mit `.` Text in ein Eingabefeld geschrieben.
        self.speed_entry.insert(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            f"{speed_mm_s:.6f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if update_status:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text="Stage not connected",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage.set_velocity(speed_mm_s):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if update_status:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text="Could not set stage speed",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_speed.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text=f"Movement Speed: {speed_mm_s:.6f} mm/s"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if update_status:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"Stage speed set to {speed_mm_s:.6f} mm/s",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return True
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 6.6 STAGE CONTROL HELPER
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Prüft, ob der Stage fahren darf.
    def prepare_stage_for_move(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Stage not connected",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage.is_moving:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.update_still_to_drive_label()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_remaining_known:
# In Python speichert `=` hier einen Wert in `remaining_text`.
                remaining_text = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"{self.stage_remaining_to_drive:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `remaining_text`.
                remaining_text = "target unknown"
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"Stage is already moving, still to drive "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"{remaining_text}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                ),
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.apply_stage_speed(
# In Python speichert `=` hier einen Startwert in `update_status`.
            update_status=False
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 6.1 MOVE STAGE TO AN ABSOLUTE POSITION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt zu einer Zielposition.
    def start_stage_move_to(self, target_mm, start_pos=None):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.prepare_stage_for_move():
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if start_pos is None:
# In Python ruft `.` eine Methode auf, die die Position liest.
            start_pos = self.stage.get_position()
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `target_mm`.
        target_mm = self.stage.clamp_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            target_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `move_mm`.
        move_mm = target_mm - start_pos
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `stage_start_position`. Startposition der Bewegung.
        self.stage_start_position = start_pos
# In Python speichert `=` einen Wert in `stage_movement_before_move`. Strecke vor der aktuellen Bewegung.
        self.stage_movement_before_move = self.total_stage_movement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.set_stage_target_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            target_mm,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            start_pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.reset_stage_speed_tracking(start_pos)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if abs(move_mm) < 1e-12:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.update_stage_labels(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                start_pos,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0.0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.stage_movement_before_move
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Stage already at target",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.clear_stage_target_position()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage.move_absolute(target_mm):
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Stage move failed",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.clear_stage_target_position()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Stage moving to {target_mm:.6f} mm",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `Thread(...)` einen Hintergrundthread.
        threading.Thread(
# In Python speichert `=` hier einen Wert in `target`.
            target=self.stage_ui_loop,
# In Python speichert `=` hier einen Startwert in `daemon`.
            daemon=True
# In Python startet `start()` einen bereits erzeugten Thread.
        ).start()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 6.2 MOVE STAGE BY A RELATIVE DISTANCE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt um eine Strecke.
    def start_stage_move_by(self, move_mm):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Stage not connected",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
        start_pos = self.stage.get_position()
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_to(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            start_pos + move_mm,
# In Python speichert `=` hier einen Wert in `start_pos`.
            start_pos=start_pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 6.3 MOVE STAGE TO TARGET IN STEPS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt in kleinen Schritten zu einem Ziel.
    def start_stage_move_to_stepped(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        target_mm,
# In Python speichert `=` hier einen Wert in `step_mm`.
        step_mm=None,
# In Python speichert `=` hier einen Wert in `pause_s`.
        pause_s=STEP_PAUSE_S,
# In Python speichert `=` hier einen Wert in `label_prefix`.
        label_prefix="Moving"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.prepare_stage_for_move():
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
        start_pos = self.stage.get_position()
# In Python speichert `=` hier einen Wert in `target_mm`.
        target_mm = self.stage.clamp_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            target_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if abs(target_mm - start_pos) < 1e-12:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Stage already at target",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #safe the values for the stage_ui_loop
# In Python speichert `=` einen Wert in `stage_start_position`. Startposition der Bewegung.
        self.stage_start_position = start_pos
# In Python speichert `=` einen Wert in `stage_movement_before_move`. Strecke vor der aktuellen Bewegung.
        self.stage_movement_before_move = self.total_stage_movement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.set_stage_target_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            target_mm,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            start_pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.reset_stage_speed_tracking(start_pos)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if step_mm is None:
# In Python speichert `=` hier einen Wert in `step_mm`.
            step_mm = self.get_step_size()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` hier einen Wert in `step_mm`.
            step_mm = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                float(step_mm)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if step_mm <= 0:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Invalid step size",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.clear_stage_target_position()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #if none of the above cases stops the stage from moving, create a movement thread and start the movement
# In Python erzeugt `Thread(...)` einen Hintergrundthread.
        threading.Thread(
# In Python speichert `=` hier einen Wert in `target`.
            target=self.stage_stepped_move_worker,
# In Python speichert `=` hier einen Wert in `args`.
            args=(start_pos, target_mm, step_mm, pause_s, label_prefix),
# In Python speichert `=` hier einen Startwert in `daemon`.
            daemon=True
# In Python startet `start()` einen bereits erzeugten Thread.
        ).start()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 6.4 MOVE STAGE RELATIVELY IN STEPS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt in kleinen Schritten um eine Strecke.
    def start_stage_move_by_steps(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        move_mm,
# In Python speichert `=` hier einen Wert in `step_mm`.
        step_mm=None,
# In Python speichert `=` hier einen Wert in `pause_s`.
        pause_s=STEP_PAUSE_S,
# In Python speichert `=` hier einen Wert in `label_prefix`.
        label_prefix="Moving"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #security checks so the code doesnt crash
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected: # translation stage connected?
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Stage not connected",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
        start_pos = self.stage.get_position()
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_to_stepped(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            start_pos + move_mm,
# In Python speichert `=` hier einen Wert in `step_mm`.
            step_mm=step_mm,
# In Python speichert `=` hier einen Wert in `pause_s`.
            pause_s=pause_s,
# In Python speichert `=` hier einen Wert in `label_prefix`.
            label_prefix=label_prefix
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 6.5 WORKER FOR STEPPED MOVEMENT
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Führt die Schrittfahrt im Hintergrund aus.
    def stage_stepped_move_worker(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        start_pos,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        target_mm,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        step_mm,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        pause_s,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        label_prefix
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `step_sign`.
        step_sign = 1 if target_mm > start_pos else -1
# In Python speichert `=` hier einen Wert in `current_pos`.
        current_pos = start_pos
# In Python speichert `=` hier einen berechneten Wert in `remaining`.
        remaining = abs(target_mm - start_pos)
# In Python speichert `=` hier einen Wert in `moved`.
        moved = 0.0
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
        self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"{label_prefix} to {target_mm:.6f} mm in "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"{step_mm:.9f} mm steps"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                ),
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
        while remaining > 1e-12:
# In Python speichert `=` hier einen Wert in `next_step`.
            next_step = min(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                step_mm,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                remaining
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier einen berechneten Wert in `next_target`.
            next_target = current_pos + step_sign * next_step
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.stage.move_absolute(next_target):
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                    self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                        text="Stage move failed",
# In Python speichert `=` hier einen Wert in `text_color`.
                        text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.clear_stage_target_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
            while self.stage.is_moving:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                time.sleep(0.005 if pause_s <= 0 else 0.01)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `step_distance`.
            step_distance = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                next_target - current_pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier einen Wert in `moved +`.
            moved += step_distance
# In Python speichert `=` hier einen Wert in `current_pos`.
            current_pos = next_target
# In Python speichert `=` hier einen Wert in `remaining`.
            remaining = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                target_mm - current_pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
            self.total_stage_movement = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.stage_movement_before_move + moved
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=current_pos, m=moved, b=self.stage_movement_before_move:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.update_stage_labels(p, m, b)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if remaining > 1e-12 and pause_s > 0:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                time.sleep(pause_s)
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
        self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            lambda:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.finish_stage_move(current_pos)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.1 TRACK NORMAL STAGE MOVEMENT
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Aktualisiert die Stage-Anzeige während der Fahrt.
    def stage_ui_loop(self):
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #how much did the stage move befor the current movement? use this as base
# In Python speichert `=` hier einen Wert in `movement_base`.
        movement_base = self.stage_movement_before_move
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
        while self.stage.is_moving:
# In Python ruft `.` eine Methode auf, die die Position liest.
            pos = self.stage.get_position()
# In Python speichert `=` hier einen Wert in `moved`.
            moved = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                pos - self.stage_start_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=pos, m=moved, b=movement_base:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.update_stage_labels(p, m, b)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            time.sleep(0.05)
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
        pos = self.stage.get_position()
# In Python speichert `=` hier einen Wert in `moved`.
        moved = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            pos - self.stage_start_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen berechneten Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
        self.total_stage_movement = movement_base + moved
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
        self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python speichert `=` hier einen Wert in `lambda p`.
            lambda p=pos:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.finish_stage_move(p)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.1.1 FINISH STAGE MOVE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt eine Stage-Fahrt ab.
    def finish_stage_move(self, pos):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `moved`.
        moved = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            pos - self.stage_start_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_stage_labels(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            pos,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            moved,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_movement_before_move
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.clear_stage_target_position()
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_speed.configure(
# Anzeige der momentanen Geschwindigkeit.
            text="Movement Speed: 0.000000 mm/s"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Reached {pos:.6f} mm",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.9 STAGE BUTTON ACTIONS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt zur Minimalposition.
    def move_to_min(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_to(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage.min_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.9.1 STEP NEGATIVE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt einen kleinen Schritt rückwärts.
    def step_negative(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_by(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            -self.get_step_size()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.9.2 MOVE TO CENTER
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt zur Nullposition.
    def move_to_center(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_to_stepped( # move to center button also goes in steps
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0.0
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.9.3 STEP POSITIVE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt einen kleinen Schritt vorwärts.
    def step_positive(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_by(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.get_step_size()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.9.4 MOVE TO MAX
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt zur Maximalposition.
    def move_to_max(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_to(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage.max_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.9.5 MOVE TO TARGET FROM UI
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt zu einer Zielposition.
    def move_to_target(self):
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `target_mm`.
            target_mm = self.parse_entry_float(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.target_entry
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except ValueError:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Invalid target value",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_to(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            target_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.9.6 MOVE DISTANCE FROM UI
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt um eine Distanz.
    def move_distance(self):
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `distance_mm`.
            distance_mm = self.parse_entry_float(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.target_entry
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except ValueError:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Invalid distance value",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_by(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            distance_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 5.9.7 STOP STAGE ACTION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Stoppt den Stage.
    def stop_stage(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
            self.stage.stop()
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
        self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Stage stopped manually",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.2 SHOW INITIAL STAGE POSITION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    #after calibration UI is filled with current stage position
# `def` definiert in Python eine Funktion oder Methode. Hier: Liest die Anfangsposition ein.
    def update_stage_position_once(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected:
# In Python ruft `.` eine Methode auf, die die Position liest.
            pos = self.stage.get_position()
# In Python speichert `=` einen Wert in `stage_reference_position`. Referenzposition für Berechnungen.
            self.stage_reference_position = pos
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_stage_position.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Stage Position: {pos:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: Stage not connected",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fragt den Stage regelmäßig ab.
    def poll_stage_status(self):
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_connected:
# In Python ruft `.` eine Methode auf, die die Position liest.
                pos = self.stage.get_position()
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_stage_position.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=f"Stage Position: {pos:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.update_still_to_drive_label(pos)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if self.stage.is_moving:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.update_stage_speed_label(pos)
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
                elif (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.stage_remaining_known
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    and self.stage_remaining_to_drive <= 0
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                ):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                    self.label_stage_speed.configure(
# Anzeige der momentanen Geschwindigkeit.
                        text="Movement Speed: 0.000000 mm/s"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# Leerzeile zur besseren Lesbarkeit.

# `finally` läuft in Python immer, auch wenn vorher ein Fehler aufgetreten ist.
        finally:
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                STAGE_STATUS_POLL_MS,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.poll_stage_status
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.3 UPDATE STAGE MOVEMENT DISPLAY
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Aktualisiert die Stage-Anzeigen.
    def update_stage_labels(self, pos, moved, movement_base=None):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if movement_base is None:
# In Python speichert `=` hier einen Wert in `movement_base`.
            movement_base = self.total_stage_movement
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `current_total_stage_movement`.
        current_total_stage_movement = movement_base + abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            moved
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `current_stage_movement_for_compare`. aktuelle Vergleichsstrecke.
        self.current_stage_movement_for_compare = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            current_total_stage_movement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_position.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Stage Position: {pos:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_moved.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"Accumulated Movement: "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{current_total_stage_movement:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_still_to_drive_label(pos)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_stage_speed_label(pos)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_comparison_labels(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            current_total_stage_movement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Speichert ein Ziel.
    def set_stage_target_position(self, target_mm, current_pos=None):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `stage_target_position`. aktuelle Zielposition.
        self.stage_target_position = target_mm
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if current_pos is None:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_connected:
# In Python ruft `.` eine Methode auf, die die Position liest.
                current_pos = self.stage.get_position()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `current_pos`.
                current_pos = target_mm
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_still_to_drive_label(current_pos)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Löscht das Ziel.
    def clear_stage_target_position(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier erstmal keinen Wert in `stage_target_position`. aktuelle Zielposition.
        self.stage_target_position = None
# In Python speichert `=` einen Wert in `stage_remaining_to_drive`. Reststrecke bis zum Ziel.
        self.stage_remaining_to_drive = 0.0
# In Python speichert `=` hier den booleschen Startwert ein in `stage_remaining_known`. Merker, ob die Reststrecke bekannt ist.
        self.stage_remaining_known = True
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, "label_still_to_drive"):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_still_to_drive.configure(
# Anzeige der Reststrecke.
                text="Still to drive: 0.000000 mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Zeigt die Reststrecke.
    def update_still_to_drive_label(self, pos=None):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `target_position`.
        target_position = self.get_active_stage_target_position()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if target_position is None:
# In Python speichert `=` einen Wert in `stage_remaining_to_drive`. Reststrecke bis zum Ziel.
            self.stage_remaining_to_drive = 0.0
# In Python speichert `=` einen Wert in `stage_remaining_known`. Merker, ob die Reststrecke bekannt ist.
            self.stage_remaining_known = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                not self.stage_connected
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                or not self.stage.is_moving
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` hier den booleschen Startwert ein in `stage_remaining_known`. Merker, ob die Reststrecke bekannt ist.
            self.stage_remaining_known = True
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if pos is None:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if self.stage_connected:
# In Python ruft `.` eine Methode auf, die die Position liest.
                    pos = self.stage.get_position()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
                else:
# In Python speichert `=` hier einen Wert in `pos`.
                    pos = target_position
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `stage_remaining_to_drive`. Reststrecke bis zum Ziel.
            self.stage_remaining_to_drive = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                target_position - pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_remaining_to_drive < 1e-6:
# In Python speichert `=` einen Wert in `stage_remaining_to_drive`. Reststrecke bis zum Ziel.
                self.stage_remaining_to_drive = 0.0
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, "label_still_to_drive"):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_remaining_known:
# In Python speichert `=` hier einen Wert in `label_text`.
                label_text = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"Still to drive: "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"{self.stage_remaining_to_drive:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `label_text`.
                label_text = "Still to drive: target unknown"
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_still_to_drive.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=label_text
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Gibt das gespeicherte Ziel zurück.
    def get_active_stage_target_position(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_target_position is not None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return self.stage_target_position
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return None
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.5 RESET STAGE SPEED TRACKING
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt die Geschwindigkeitsmessung zurück.
    def reset_stage_speed_tracking(self, pos):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `last_stage_speed_position`. Positionsbasis für die Geschwindigkeitsmessung.
        self.last_stage_speed_position = pos
# In Python speichert `=` den aktuellen Zeitstempel in `last_stage_speed_time`. Zeitbasis für die Geschwindigkeitsmessung.
        self.last_stage_speed_time = time.time()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.6 UPDATE STAGE SPEED DISPLAY
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Berechnet die Geschwindigkeit.
    def update_stage_speed_label(self, pos):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `now`.
        now = time.time()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.last_stage_speed_time is None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            or self.last_stage_speed_position is None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.reset_stage_speed_tracking(pos)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `dt`.
        dt = now - self.last_stage_speed_time
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if dt <= 0:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `speed_mm_s`.
        speed_mm_s = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            pos - self.last_stage_speed_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / dt
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `last_stage_speed_time`. Zeitbasis für die Geschwindigkeitsmessung.
        self.last_stage_speed_time = now
# In Python speichert `=` einen Wert in `last_stage_speed_position`. Positionsbasis für die Geschwindigkeitsmessung.
        self.last_stage_speed_position = pos
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_speed.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text=f"Movement Speed: {speed_mm_s:.6f} mm/s"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.4 RESET STAGE MOVEMENT TRACKING
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt die Wegmessung zurück.
    def reset_stage_movement_tracking(self, pos=None):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
        self.total_stage_movement = 0.0
# In Python speichert `=` einen Wert in `stage_movement_before_move`. Strecke vor der aktuellen Bewegung.
        self.stage_movement_before_move = 0.0
# In Python speichert `=` einen Wert in `current_stage_movement_for_compare`. aktuelle Vergleichsstrecke.
        self.current_stage_movement_for_compare = 0.0
# In Python speichert `=` hier erstmal keinen Wert in `stage_target_position`. aktuelle Zielposition.
        self.stage_target_position = None
# In Python speichert `=` einen Wert in `stage_remaining_to_drive`. Reststrecke bis zum Ziel.
        self.stage_remaining_to_drive = 0.0
# In Python speichert `=` hier den booleschen Startwert ein in `stage_remaining_known`. Merker, ob die Reststrecke bekannt ist.
        self.stage_remaining_known = True
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if pos is not None: # use provided position as new reference
# In Python speichert `=` einen Wert in `stage_reference_position`. Referenzposition für Berechnungen.
            self.stage_reference_position = pos
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_stage_position.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Stage Position: {pos:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
        elif self.stage_connected: # if the stage is connected use actual hardware position as reference
# In Python ruft `.` eine Methode auf, die die Position liest.
            self.stage_reference_position = self.stage.get_position()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` einen Wert in `stage_reference_position`. Referenzposition für Berechnungen.
            self.stage_reference_position = 0.0
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_moved.configure(
# Anzeige der gefahrenen Gesamtstrecke.
            text="Accumulated Movement: 0.000000 mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_speed.configure(
# Anzeige der momentanen Geschwindigkeit.
            text="Movement Speed: 0.000000 mm/s"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.clear_stage_target_position()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.11 UPDATE DRIVEN VS CALCULATED DISTANCE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    #stage movement distance is compared with distance calculated from counted fringes
# `def` definiert in Python eine Funktion oder Methode. Hier: Vergleicht Weg und Fringe-Berechnung.
    def update_comparison_labels(self, driven_mm=None):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if driven_mm is None:
# In Python speichert `=` hier einen Wert in `driven_mm`.
            driven_mm = self.current_stage_movement_for_compare
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `driven_distance_mm`.
        driven_distance_mm = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            driven_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier einen Wert in `calculated_mm`.
        calculated_mm = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.accumulated_fringes
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            * self.fringe_distance_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier einen berechneten Wert in `difference_mm`.
        difference_mm = driven_distance_mm - calculated_mm
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_compare_driven.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Driven: {driven_distance_mm:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_compare_calculated.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Calculated from Fringes: {calculated_mm:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_compare_difference.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Difference: {difference_mm:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 8.8 RUN STAGE MOTION BY PARAMETERS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Startet die Stage-Bewegung nach Modus.
    def run_stage_motion_by_parameters(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
        current_position = self.stage.get_position()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if MODE.lower().startswith("c"):
# In Python ruft `.` eine Methode auf, die die Geschwindigkeit setzt.
            self.stage.set_velocity(VELOCITY_MM_S)
# In Python speichert `=` hier einen berechneten Wert in `final_target`.
            final_target = self.stage.clamp_position(current_position + TOTAL_DISTANCE_MM)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `stage_start_position`. Startposition der Bewegung.
            self.stage_start_position = current_position
# In Python speichert `=` einen Wert in `stage_movement_before_move`. Strecke vor der aktuellen Bewegung.
            self.stage_movement_before_move = self.total_stage_movement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.set_stage_target_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                final_target,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                current_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.reset_stage_speed_tracking(current_position)
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        f"Continuous move to {final_target:.6f} mm "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        f"at {VELOCITY_MM_S} mm/s"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    ),
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.stage.move_absolute(final_target):
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                    self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                        text="Stage move failed",
# In Python speichert `=` hier einen Wert in `text_color`.
                        text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.clear_stage_target_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
            while self.stage.is_moving and self.is_monitoring:
# In Python ruft `.` eine Methode auf, die die Position liest.
                pos = self.stage.get_position()
# In Python speichert `=` hier einen berechneten Wert in `moved`.
                moved = abs(pos - self.stage_start_position)
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                    lambda p=pos, m=moved, b=self.stage_movement_before_move:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.update_stage_labels(p, m, b)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                time.sleep(0.05)
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
            pos = self.stage.get_position()
# In Python speichert `=` hier einen berechneten Wert in `moved`.
            moved = abs(pos - self.stage_start_position)
# In Python speichert `=` einen Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
            self.total_stage_movement = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.stage_movement_before_move + moved
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=pos:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.finish_stage_move(p)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python ruft `.` eine Methode auf, die die Geschwindigkeit setzt.
            self.stage.set_velocity(VELOCITY_MM_S_STEPPED)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `stage_start_position`. Startposition der Bewegung.
            self.stage_start_position = current_position
# In Python speichert `=` einen Wert in `stage_movement_before_move`. Strecke vor der aktuellen Bewegung.
            self.stage_movement_before_move = self.total_stage_movement
# In Python speichert `=` hier einen Wert in `stepped_target`.
            stepped_target = self.stage.clamp_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                current_position + STEP_SIZE_MM * STEPS
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.set_stage_target_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                stepped_target,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                current_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.reset_stage_speed_tracking(current_position)
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        f"Stepped move: {STEPS} steps of "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        f"{STEP_SIZE_MM} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    ),
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `current_pos`.
            current_pos = current_position
# In Python speichert `=` hier einen Wert in `moved`.
            moved = 0.0
# Leerzeile zur besseren Lesbarkeit.

# `for` startet in Python eine Schleife über mehrere Werte.
            for step in range(STEPS):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if not self.is_monitoring:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    break
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `next_position`.
                next_position = self.stage.clamp_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    current_pos + STEP_SIZE_MM
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python speichert `=` hier einen Wert in `lambda s`.
                    lambda s=step, n=next_position:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                    self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                        text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            f"Step {s + 1}/{STEPS}: "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            f"move to {n:.7f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        ),
# In Python speichert `=` hier einen Wert in `text_color`.
                        text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if not self.stage.move_absolute(next_position):
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                    self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                            text="Move command failed",
# In Python speichert `=` hier einen Wert in `text_color`.
                            text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    break
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
                while self.stage.is_moving and self.is_monitoring:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    time.sleep(0.01)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `step_distance`.
                step_distance = abs(next_position - current_pos)
# In Python speichert `=` hier einen Wert in `moved +`.
                moved += step_distance
# In Python speichert `=` hier einen Wert in `current_pos`.
                current_pos = next_position
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
                self.total_stage_movement = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.stage_movement_before_move + moved
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                    lambda p=current_pos, m=moved, b=self.stage_movement_before_move:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.update_stage_labels(p, m, b)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if step < STEPS - 1:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    time.sleep(STEP_PAUSE_S)
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=current_pos:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.finish_stage_move(p)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.7 MOVE STAGE DURING CALIBRATION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt den Stage für die Kalibrierung.
    def calibration_stage_motion(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `previous_velocity`.
        previous_velocity = None
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.stage_connected: # refuse movement commands when stage is not connected
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
            start_pos = self.stage.get_position() # current stage position as movement start
# In Python speichert `=` hier einen Wert in `forward_target`.
            forward_target = self.stage.clamp_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                start_pos + CALIBRATION_STAGE_DISTANCE_MM
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier einen Wert in `back_target`.
            back_target = self.stage.clamp_position(start_pos)
# In Python speichert `=` hier einen Wert in `sweep_distance_mm`.
            sweep_distance_mm = abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                forward_target - start_pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if sweep_distance_mm <= 1e-12:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Geschwindigkeit setzt.
            previous_velocity = self.stage.set_velocity()
# In Python speichert `=` hier einen Wert in `calibration_speed_mm_s`.
            calibration_speed_mm_s = CALIBRATION_STAGE_SPEED_MM_S
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.stage.set_velocity(calibration_speed_mm_s):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `stage_start_position`. Startposition der Bewegung.
            self.stage_start_position = start_pos
# In Python speichert `=` einen Wert in `stage_movement_before_move`. Strecke vor der aktuellen Bewegung.
            self.stage_movement_before_move = 0.0
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.reset_stage_speed_tracking(start_pos)
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        f"Calibration sweep: "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        f"{sweep_distance_mm:.5f} mm "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        f"at {calibration_speed_mm_s:.6f} mm/s"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    ),
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `accumulated_movement_mm`.
            accumulated_movement_mm = 0.0
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
            while self.is_monitoring and self.calibrating:
# `for` startet in Python eine Schleife über mehrere Werte.
                for target in (forward_target, back_target):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if not self.is_monitoring or not self.calibrating:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                        return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
                    leg_start_pos = self.stage.get_position()
# In Python speichert `=` einen Wert in `stage_target_position`. aktuelle Zielposition.
                    self.stage_target_position = target
# In Python speichert `=` hier den booleschen Startwert ein in `stage_remaining_known`. Merker, ob die Reststrecke bekannt ist.
                    self.stage_remaining_known = True
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if not self.stage.move_absolute(target):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                        return
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
                    while (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        self.stage.is_moving
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        and self.is_monitoring
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        and self.calibrating
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    ):
# In Python ruft `.` eine Methode auf, die die Position liest.
                        current_pos = self.stage.get_position()
# In Python speichert `=` hier einen berechneten Wert in `moved`.
                        moved = accumulated_movement_mm + abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            current_pos - leg_start_pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        )
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                        self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                            lambda p=current_pos, m=moved:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            self.update_stage_labels(p, m, 0.0)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        time.sleep(0.01)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if not self.is_monitoring or not self.calibrating:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                        return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
                    current_pos = self.stage.get_position()
# In Python speichert `=` hier einen berechneten Wert in `accumulated_movement_mm +`.
                    accumulated_movement_mm += abs(current_pos - leg_start_pos)
# In Python speichert `=` einen Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
                    self.total_stage_movement = accumulated_movement_mm
# In Python speichert `=` einen Wert in `current_stage_movement_for_compare`. aktuelle Vergleichsstrecke.
                    self.current_stage_movement_for_compare = accumulated_movement_mm
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
                    self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                        lambda p=current_pos, m=accumulated_movement_mm:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        self.update_stage_labels(p, m, 0.0)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# Leerzeile zur besseren Lesbarkeit.

# `finally` läuft in Python immer, auch wenn vorher ein Fehler aufgetreten ist.
        finally:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.stage_connected
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                and self.stage.is_moving
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ):
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
                self.stage.stop()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if previous_velocity is not None and self.stage_connected:
# In Python ruft `.` eine Methode auf, die die Geschwindigkeit setzt.
                self.stage.set_velocity(previous_velocity)
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
            pos = self.stage.get_position()
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=pos, m=accumulated_movement_mm:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.finish_calibration_movement(p, m)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Stoppt die Kalibrierungsfahrt.
    def stop_calibration_stage_motion(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.clear_stage_target_position()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage.is_moving:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
            self.stage.stop()
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
        self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Calibration ended, stage stopped",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.10 FINISH CALIBRATION RESET
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Beendet die Kalibrierungsfahrt.
    def finish_calibration_movement(self, pos=None, accumulated_movement_mm=None):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected and self.stage.is_moving:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
            self.stage.stop()
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Calibration ended, waiting for stage stop",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop.
            self.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                STAGE_STATUS_POLL_MS,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=pos, m=accumulated_movement_mm: self.finish_calibration_movement(p, m)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if pos is None:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_connected:
# In Python ruft `.` eine Methode auf, die die Position liest.
                pos = self.stage.get_position()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `pos`.
                pos = 0.0
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if accumulated_movement_mm is None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.reset_stage_movement_tracking(pos)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` einen Wert in `stage_reference_position`. Referenzposition für Berechnungen.
            self.stage_reference_position = pos
# In Python speichert `=` einen Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
            self.total_stage_movement = accumulated_movement_mm
# In Python speichert `=` einen Wert in `current_stage_movement_for_compare`. aktuelle Vergleichsstrecke.
            self.current_stage_movement_for_compare = accumulated_movement_mm
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_stage_position.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Stage Position: {pos:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_stage_moved.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Accumulated Movement: {accumulated_movement_mm:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.clear_stage_target_position()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.update_comparison_labels(accumulated_movement_mm)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.calibrating:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Calibration sweep finished",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.set_buttons_enabled(True)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.is_monitoring:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Monitoring running",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 9.1 SHUT DOWN HARDWARE CLEANLY
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt Hardware und Fenster sauber.
    def on_close(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den booleschen Startwert aus in `is_monitoring`. Merker, ob die Messschleife läuft.
        self.is_monitoring = False
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python ruft `.` eine Methode auf, die die Verbindung schließt.
            self.diode.close()
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except Exception:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            pass
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python schließt `close()` eine geöffnete Verbindung wieder.
            self.stage.close()
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except Exception:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            pass
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.destroy()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 9. PROGRAM START
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# 9. PROGRAM START
# In Python bedeutet das: Dieser Block läuft nur beim direkten Start der Datei.
if __name__ == "__main__":
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `app`.
    app = SideApp()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    app.protocol(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        "WM_DELETE_WINDOW", # connect window close button to cleanup routine
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        app.on_close
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    app.mainloop() # start the graphical application loop
