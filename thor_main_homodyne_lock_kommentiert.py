# Originalkommentar oder Abschnittsüberschrift.
# basically identical to homodyne.py, but we use the Thorlabs stage controller
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
# 4. HomodyneGui class (UI)
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

# In Python berechnet `=` hier die Konstante `PHOTODIODE_CHANNEL_S1` aus anderen Größen. Das ist der NI-Eingang für das erste Diodensignal.
PHOTODIODE_CHANNEL_S1 = "Dev1/ai0"
# In Python berechnet `=` hier die Konstante `PHOTODIODE_CHANNEL_S2` aus anderen Größen. Das ist der NI-Eingang für das zweite Diodensignal.
PHOTODIODE_CHANNEL_S2 = "Dev1/ai1"
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `5.0` in der Konstante `CALIBRATION_SECONDS`. Das ist die Gesamtzeit für den Kalibrierungsablauf.
CALIBRATION_SECONDS = 5.0
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
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `300` in der Konstante `RAW_HISTORY_LENGTH`. So viele Rohwerte werden im Verlauf behalten.
RAW_HISTORY_LENGTH = 300
# In Python speichert `=` hier den festen Wert `0.05` in der Konstante `STEP_PAUSE_S`. So lange wartet der Code zwischen zwei Schritten.
STEP_PAUSE_S = 0.05
# In Python speichert `=` hier den festen Wert `100` in der Konstante `STAGE_STATUS_POLL_MS`. So oft wird der Stage-Status abgefragt.
STAGE_STATUS_POLL_MS = 100
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `0.005` in der Konstante `SAMPLE_INTERVAL_S`. So oft wird gemessen.
SAMPLE_INTERVAL_S = 0.005
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# Threshold for classifying movement direction (reduces tiny jitter being labeled)
# In Python speichert `=` hier den festen Wert `0.004` in der Konstante `DIRECTION_THRESHOLD`. Kleine Richtungswechsel durch Jitter werden damit ignoriert.
DIRECTION_THRESHOLD = 0.004
# Leerzeile zur besseren Lesbarkeit.

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
# In Python speichert `=` hier den festen Wert `0.30` in der Konstante `DARK_LEVEL_FRACTION`. Damit wird der dunkle Bereich des Signals abgeschätzt.
DARK_LEVEL_FRACTION = 0.30
# In Python speichert `=` hier den festen Wert `0.55` in der Konstante `BRIGHT_LEVEL_FRACTION`. Damit wird der helle Bereich des Signals abgeschätzt.
BRIGHT_LEVEL_FRACTION = 0.55
# In Python speichert `=` hier den festen Wert `3` in der Konstante `SMOOTHING_WINDOW_LENGTH`. Über so viele Werte wird geglättet.
SMOOTHING_WINDOW_LENGTH = 3
# In Python speichert `=` hier den festen Wert `2` in der Konstante `REQUIRED_DARK_FRAMES`. So viele dunkle Frames braucht die Erkennung.
REQUIRED_DARK_FRAMES = 2
# In Python speichert `=` hier den festen Wert `2` in der Konstante `REQUIRED_BRIGHT_FRAMES`. So viele helle Frames braucht die Erkennung.
REQUIRED_BRIGHT_FRAMES = 2
# In Python speichert `=` hier den festen Wert `15` in der Konstante `MAX_FRINGE_WIDTH_FRAMES`. So breit darf ein Fringe-Zeitfenster maximal sein.
MAX_FRINGE_WIDTH_FRAMES = 15
# In Python berechnet `=` hier die Konstante `FRINGE_COOLDOWN` aus anderen Größen.
FRINGE_COOLDOWN = max(0.04, MAX_FRINGE_WIDTH_FRAMES * SAMPLE_INTERVAL_S)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in der Konstante `MODE`. Damit wird der Bewegungsmodus gewählt.
MODE = "continuous"
# In Python speichert `=` hier den festen Wert `0.0006` in der Konstante `VELOCITY_MM_S`. Das ist die Geschwindigkeit für den kontinuierlichen Modus.
VELOCITY_MM_S = 0.0006
# In Python speichert `=` hier den festen Wert `13.0` in der Konstante `TOTAL_DISTANCE_MM`. Das ist die gesamte Strecke im kontinuierlichen Modus.
TOTAL_DISTANCE_MM = 13.0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `1.00` in der Konstante `VELOCITY_MM_S_STEPPED`. Das ist die Geschwindigkeit für den Schrittmodus.
VELOCITY_MM_S_STEPPED = 1.00
# In Python speichert `=` hier den festen Wert `0.00001` in der Konstante `STEP_SIZE_MM`. Das ist die Größe eines einzelnen Schritts.
STEP_SIZE_MM = 0.00001
# In Python speichert `=` hier den festen Wert `100` in der Konstante `STEPS`. So viele Einzelschritte werden gemacht.
STEPS = 100
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `0.1` in der Konstante `UI_UPDATE_INTERVAL_S`. So oft wird die Oberfläche aktualisiert.
UI_UPDATE_INTERVAL_S = 0.1
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `1.0` in der Konstante `LOCK_TRIGGER_FRINGES`. Ab so vielen Fringes wird eine Korrektur ausgelöst.
LOCK_TRIGGER_FRINGES = 1.0
# In Python speichert `=` hier den festen Wert `0.30` in der Konstante `LOCK_CORRECTION_COOLDOWN_S`. So lange wartet der Lock zwischen zwei Korrekturen.
LOCK_CORRECTION_COOLDOWN_S = 0.30
# Leerzeile zur besseren Lesbarkeit.

# In Python berechnet `=` hier die Konstante `STAGE_CORRECTION_SIGN` aus anderen Größen. Damit wird die Richtung der Korrektur festgelegt.
STAGE_CORRECTION_SIGN = -1
# In Python speichert `=` hier den festen Wert `60.0` in der Konstante `STAGE_MOVE_TIMEOUT_S`. So lange darf eine Stage-Bewegung maximal dauern.
STAGE_MOVE_TIMEOUT_S = 60.0
# In Python speichert `=` hier den festen Wert `180.0` in der Konstante `STAGE_CHECK_TIMEOUT_S`. So lange wird maximal auf eine Prüfung gewartet.
STAGE_CHECK_TIMEOUT_S = 180.0
# In Python speichert `=` hier den festen Wert `0.05` in der Konstante `STAGE_POLL_INTERVAL_S`. So oft wird der Stage abgefragt.
STAGE_POLL_INTERVAL_S = 0.05
# In Python speichert `=` hier den festen Wert `200` in der Konstante `PLOT_SAMPLE_WINDOW`. So viele Messpunkte sind im Plot sichtbar.
PLOT_SAMPLE_WINDOW = 200
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 2. IMPORTS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import math
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import threading # so that camera and stage can run without freezing the UI
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import time # for timestamps
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
from dataclasses import dataclass
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import tkinter.simpledialog as sd
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
try:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    import customtkinter as ctk # pythons standard UI library
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
except ImportError:
# In Python speichert `=` hier einen Startwert in `ctk`.
    ctk = None
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
try:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    import matplotlib.pyplot as plt
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
except ImportError:
# In Python speichert `=` hier einen Startwert in `plt`.
    plt = None
# In Python speichert `=` hier einen Startwert in `FigureCanvasTkAgg`.
    FigureCanvasTkAgg = None
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
try:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    from thor_handler_stage import StageController
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
except Exception as stage_import_error:
# In Python speichert `=` hier einen Startwert in `StageController`.
    StageController = None
# In Python speichert `=` hier einen Wert in der Konstante `STAGE_IMPORT_ERROR`.
    STAGE_IMPORT_ERROR = str(stage_import_error)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
else:
# In Python speichert `=` hier einen Wert in der Konstante `STAGE_IMPORT_ERROR`.
    STAGE_IMPORT_ERROR = None
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 3. PHYSICAL CONSTANTS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `787.3` in der Konstante `LASER_WAVELENGTH_NM`. Das ist die verwendete Laserwellenlänge.
LASER_WAVELENGTH_NM = 787.3
# In Python speichert `=` hier den festen Wert `0.299792458` in der Konstante `SPEED_OF_LIGHT_MM_PS`. Das ist die Lichtgeschwindigkeit in mm pro ps.
SPEED_OF_LIGHT_MM_PS = 0.299792458
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `1` in der Konstante `PHASE_DIRECTION_SIGN`. Damit wird festgelegt, welche Phasenrichtung positiv ist.
PHASE_DIRECTION_SIGN = 1
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `0.05` in der Konstante `MIN_SIGNAL_RADIUS`. Das ist der kleinste nutzbare Radius im Phasenraum.
MIN_SIGNAL_RADIUS = 0.05
# In Python speichert `=` hier den festen Wert `0.004` in der Konstante `MIN_VISIBLE_FRINGE_AMPLITUDE_V`. Das ist die kleinste sichtbare Fringe-Höhe.
MIN_VISIBLE_FRINGE_AMPLITUDE_V = 0.004
# In Python speichert `=` hier den festen Wert `0.060` in der Konstante `MAX_VISIBLE_FRINGE_AMPLITUDE_V`. Das ist die größte sichtbare Fringe-Höhe.
MAX_VISIBLE_FRINGE_AMPLITUDE_V = 0.060
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den festen Wert `0.000600` in der Konstante `DEFAULT_STAGE_SPEED_MM_S`. Das ist die Standardgeschwindigkeit für den Stage.
DEFAULT_STAGE_SPEED_MM_S = 0.000600
# `def` definiert in Python eine Funktion oder Methode. Hier: compute_fringe_distance_mm
def compute_fringe_distance_mm(wavelength_nm):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
    return (wavelength_nm / 2) / 1_000_000
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: wrap_to_pi
def wrap_to_pi(angle_rad):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
    return (angle_rad + math.pi) % (2 * math.pi) - math.pi
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: completed_signed_fringes
def completed_signed_fringes(fringe_position):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
    if fringe_position == 0:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return 0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `sign`.
    sign = 1 if fringe_position > 0 else -1
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
    return sign * math.floor(abs(fringe_position))
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
# 3.2 HELPER CLASSES AND DATACLASSES
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
@dataclass
# `class` definiert in Python eine Klasse. Hier entsteht `HomodyneSample` als Bauplan für das Fenster und die Logik.
class HomodyneSample:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    timestamp: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    raw_s1: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    raw_s2: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    s1: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    s2: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    radius: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    phase_rad: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    unwrapped_phase_rad: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    delta_phase_rad: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    fringe_position: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    signed_fringes: int
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    fringe_delta: int
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    direction: str
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    valid: bool
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `NIPhotodiodeReader` als Bauplan für das Fenster und die Logik.
class NIPhotodiodeReader:
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 4.1 INITIALIZATION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python speichert `=` hier einen Wert in `channel_s1`.
        channel_s1=PHOTODIODE_CHANNEL_S1,
# In Python speichert `=` hier einen Wert in `channel_s2`.
        channel_s2=PHOTODIODE_CHANNEL_S2
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# In Python speichert `=` einen Wert in `channel_s1`.
        self.channel_s1 = channel_s1
# In Python speichert `=` einen Wert in `channel_s2`.
        self.channel_s2 = channel_s2
# In Python speichert `=` hier erstmal keinen Wert in `task`.
        self.task = None
# In Python speichert `=` hier erstmal keinen Wert in `nidaqmx`.
        self.nidaqmx = None
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: connect
    def connect(self):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        import nidaqmx
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `nidaqmx`.
        self.nidaqmx = nidaqmx
# In Python speichert `=` einen Wert in `task`.
        self.task = nidaqmx.Task()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.task.ai_channels.add_ai_voltage_chan(self.channel_s1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.task.ai_channels.add_ai_voltage_chan(self.channel_s2)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return True
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: read
    def read(self):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.task is None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raise RuntimeError("NI task is not connected.")
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `values`.
        values = self.task.read()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if len(values) != 2:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raise RuntimeError(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                "Expected two analog input values from the NI task."
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return float(values[0]), float(values[1])
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: close
    def close(self):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.task is not None:
# In Python schließt `close()` eine geöffnete Verbindung wieder.
            self.task.close()
# In Python speichert `=` hier erstmal keinen Wert in `task`.
            self.task = None
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `SingleSignalFringeCounter` als Bauplan für das Fenster und die Logik.
class SingleSignalFringeCounter:
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 4.1 INITIALIZATION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self, sample_interval_s=0.005):
# In Python speichert `=` einen Wert in `sample_interval_s`.
        self.sample_interval_s = sample_interval_s
# In Python speichert `=` einen Wert in `min_voltage`.
        self.min_voltage = 0.0
# In Python speichert `=` einen Wert in `max_voltage`.
        self.max_voltage = 0.0
# In Python speichert `=` einen Wert in `offset_voltage`.
        self.offset_voltage = 0.0
# In Python speichert `=` einen Wert in `scale_voltage`.
        self.scale_voltage = 1.0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `fringe_amplitude_voltage`. geschätzte Fringe-Höhe.
        self.fringe_amplitude_voltage = DEFAULT_FRINGE_AMPLITUDE_V
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
# In Python speichert `=` einen Wert in `dark_threshold`. Schwelle für dunkel.
        self.dark_threshold = 0.0
# In Python speichert `=` einen Wert in `bright_threshold`. Schwelle für hell.
        self.bright_threshold = 0.0
# In Python speichert `=` hier den booleschen Startwert aus in `fringes_visible`.
        self.fringes_visible = False
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier eine leere Liste in `smoothed_voltage_history`. kleines Fenster geglätteter Spannungen.
        self.smoothed_voltage_history = []
# In Python speichert `=` hier den booleschen Startwert aus in `was_dark`. Merker für den Dunkelzustand.
        self.was_dark = False
# In Python speichert `=` einen Wert in `dark_counter`. Zähler für dunkle Frames.
        self.dark_counter = 0
# In Python speichert `=` einen Wert in `bright_counter`. Zähler für helle Frames.
        self.bright_counter = 0
# In Python speichert `=` einen Wert in `last_count_time`. Zeitpunkt des letzten Zählereignisses.
        self.last_count_time = 0.0
# In Python speichert `=` einen Wert in `accumulated_fringes`. bisher gezählte Fringe-Anzahl.
        self.accumulated_fringes = 0
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: calibrate
    def calibrate(self, s1_values):
# In Python speichert `=` hier den booleschen Startwert aus in `fringes_visible`.
        self.fringes_visible = False
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not s1_values:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `smoothed_samples`.
        smoothed_samples = []
# `for` startet in Python eine Schleife über mehrere Werte.
        for index in range(len(s1_values)):
# In Python speichert `=` hier einen berechneten Wert in `start_index`.
            start_index = max(0, index - 2)
# In Python speichert `=` hier einen berechneten Wert in `end_index`.
            end_index = min(len(s1_values), index + 3)
# In Python speichert `=` hier einen Wert in `window`.
            window = s1_values[start_index:end_index]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            smoothed_samples.append(sum(window) / len(window))
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `min_voltage`.
        self.min_voltage = min(smoothed_samples)
# In Python speichert `=` einen Wert in `max_voltage`.
        self.max_voltage = max(smoothed_samples)
# In Python speichert `=` einen berechneten Wert in `offset_voltage`.
        self.offset_voltage = (self.min_voltage + self.max_voltage) / 2
# In Python speichert `=` einen berechneten Wert in `scale_voltage`.
        self.scale_voltage = (self.max_voltage - self.min_voltage) / 2
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.scale_voltage <= 1e-12:
# In Python speichert `=` einen Wert in `scale_voltage`.
            self.scale_voltage = 1.0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `minima`.
        minima = []
# In Python speichert `=` hier einen Startwert in `maxima`.
        maxima = []
# In Python speichert `=` hier einen Startwert in `extrema`.
        extrema = []
# `for` startet in Python eine Schleife über mehrere Werte.
        for index in range(1, len(smoothed_samples) - 1):
# In Python speichert `=` hier einen berechneten Wert in `prev_val`.
            prev_val = smoothed_samples[index - 1]
# In Python speichert `=` hier einen Wert in `curr_val`.
            curr_val = smoothed_samples[index]
# In Python speichert `=` hier einen berechneten Wert in `next_val`.
            next_val = smoothed_samples[index + 1]
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if (curr_val <= prev_val and curr_val < next_val) or (curr_val < prev_val and curr_val <= next_val):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                minima.append(curr_val)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                extrema.append(("min", curr_val))
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if (curr_val >= prev_val and curr_val > next_val) or (curr_val > prev_val and curr_val >= next_val):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                maxima.append(curr_val)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                extrema.append(("max", curr_val))
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `amplitude`.
        amplitude = DEFAULT_FRINGE_AMPLITUDE_V
# In Python speichert `=` hier einen Startwert in `visible_amplitude`.
        visible_amplitude = False
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if minima and maxima:
# In Python speichert `=` hier einen Startwert in `compressed_extrema`.
            compressed_extrema = []
# `for` startet in Python eine Schleife über mehrere Werte.
            for kind, value in extrema:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if compressed_extrema and compressed_extrema[-1][0] == kind:
# In Python speichert `=` hier einen berechneten Wert in `prev_kind, prev_val`.
                    prev_kind, prev_val = compressed_extrema[-1]
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if kind == "min" and value < prev_val:
# In Python speichert `=` hier einen Wert in `compressed_extrema[-1]`.
                        compressed_extrema[-1] = (prev_kind, value)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if kind == "max" and value > prev_val:
# In Python speichert `=` hier einen Wert in `compressed_extrema[-1]`.
                        compressed_extrema[-1] = (prev_kind, value)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    continue
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                compressed_extrema.append((kind, value))
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `amplitudes`.
            amplitudes = []
# `for` startet in Python eine Schleife über mehrere Werte.
            for index in range(1, len(compressed_extrema)):
# In Python speichert `=` hier einen berechneten Wert in `prev_kind, prev_val`.
                prev_kind, prev_val = compressed_extrema[index - 1]
# In Python speichert `=` hier einen Wert in `curr_kind, curr_val`.
                curr_kind, curr_val = compressed_extrema[index]
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if prev_kind != curr_kind:
# In Python speichert `=` hier einen berechneten Wert in `amp`.
                    amp = abs(curr_val - prev_val)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        MIN_VISIBLE_FRINGE_AMPLITUDE_V
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        <= amp
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        <= MAX_VISIBLE_FRINGE_AMPLITUDE_V
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    ):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        amplitudes.append(amp)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if amplitudes:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                amplitudes.sort()
# In Python speichert `=` hier einen berechneten Wert in `upper_half`.
                upper_half = amplitudes[len(amplitudes) // 2:]
# In Python speichert `=` hier einen berechneten Wert in `amplitude`.
                amplitude = sum(upper_half) / len(upper_half)
# In Python speichert `=` hier einen Startwert in `visible_amplitude`.
                visible_amplitude = True
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `fringe_amplitude_voltage`. geschätzte Fringe-Höhe.
        self.fringe_amplitude_voltage = amplitude
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
            detection_amplitude_voltage * 0.98
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `fringe_rearm_threshold_voltage`. Schwelle, ab der die Erkennung wieder bereit ist.
        self.fringe_rearm_threshold_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            detection_amplitude_voltage * 0.98
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `fringes_visible`.
        self.fringes_visible = visible_amplitude
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `value_range`.
        value_range = self.max_voltage - self.min_voltage
# In Python speichert `=` einen berechneten Wert in `dark_threshold`. Schwelle für dunkel.
        self.dark_threshold = self.min_voltage + value_range * DARK_LEVEL_FRACTION
# In Python speichert `=` einen berechneten Wert in `bright_threshold`. Schwelle für hell.
        self.bright_threshold = self.min_voltage + value_range * BRIGHT_LEVEL_FRACTION
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.reset()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: reset
    def reset(self):
# In Python speichert `=` hier erstmal keinen Wert in `fringe_trough_voltage`. gemerkter Tiefpunkt des Signals.
        self.fringe_trough_voltage = None
# In Python speichert `=` hier erstmal keinen Wert in `fringe_peak_voltage`. gemerkter Hochpunkt des Signals.
        self.fringe_peak_voltage = None
# In Python speichert `=` hier eine leere Liste in `smoothed_voltage_history`. kleines Fenster geglätteter Spannungen.
        self.smoothed_voltage_history = []
# In Python speichert `=` hier den booleschen Startwert aus in `was_dark`. Merker für den Dunkelzustand.
        self.was_dark = False
# In Python speichert `=` einen Wert in `dark_counter`. Zähler für dunkle Frames.
        self.dark_counter = 0
# In Python speichert `=` einen Wert in `bright_counter`. Zähler für helle Frames.
        self.bright_counter = 0
# In Python speichert `=` einen Wert in `last_count_time`. Zeitpunkt des letzten Zählereignisses.
        self.last_count_time = 0.0
# In Python speichert `=` einen Wert in `accumulated_fringes`. bisher gezählte Fringe-Anzahl.
        self.accumulated_fringes = 0
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: update
    def update(self, voltage):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.smoothed_voltage_history.append(voltage)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if len(self.smoothed_voltage_history) > SMOOTHING_WINDOW_LENGTH:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.smoothed_voltage_history.pop(0)
# In Python speichert `=` hier einen Wert in `smooth_voltage`.
        smooth_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sum(self.smoothed_voltage_history) / len(self.smoothed_voltage_history)
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

# In Python speichert `=` hier einen berechneten Wert in `cooldown_ok`.
        cooldown_ok = (time.time() - self.last_count_time) > FRINGE_COOLDOWN
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
                self.fringe_peak_voltage - smooth_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ) >= self.fringe_rearm_threshold_voltage
# In Python speichert `=` hier einen Wert in `below_dark_level`.
            below_dark_level = smooth_voltage <= self.dark_threshold
# In Python speichert `=` hier einen Wert in `started_near_trough`.
            started_near_trough = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.fringe_peak_voltage - self.fringe_trough_voltage
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

# In Python speichert `=` hier einen berechneten Wert in `rise_from_trough`.
        rise_from_trough = smooth_voltage - self.fringe_trough_voltage
# In Python speichert `=` hier einen Wert in `peak_is_large_enough`.
        peak_is_large_enough = rise_from_trough >= self.fringe_rise_threshold_voltage
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
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return True
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return False
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `HomodyneQuadratureCounter` als Bauplan für das Fenster und die Logik.
class HomodyneQuadratureCounter:
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 4.1 INITIALIZATION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python speichert `=` hier einen Wert in `phase_direction_sign`.
        phase_direction_sign=PHASE_DIRECTION_SIGN,
# In Python speichert `=` hier einen Wert in `min_signal_radius`.
        min_signal_radius=MIN_SIGNAL_RADIUS,
# In Python speichert `=` hier einen Startwert in `fringe_distance_mm`.
        fringe_distance_mm=None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# In Python speichert `=` einen Wert in `lock`.
        self.lock = threading.Lock()
# In Python speichert `=` einen berechneten Wert in `phase_direction_sign`.
        self.phase_direction_sign = 1 if phase_direction_sign >= 0 else -1
# In Python speichert `=` einen Wert in `min_signal_radius`.
        self.min_signal_radius = min_signal_radius
# In Python speichert `=` einen Wert in `fringe_distance_mm`. Abstand zwischen zwei Fringes.
        self.fringe_distance_mm = fringe_distance_mm
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `offset_s1`.
        self.offset_s1 = 0.0
# In Python speichert `=` einen Wert in `offset_s2`.
        self.offset_s2 = 0.0
# In Python speichert `=` einen Wert in `scale_s1`.
        self.scale_s1 = 1.0
# In Python speichert `=` einen Wert in `scale_s2`.
        self.scale_s2 = 1.0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier erstmal keinen Wert in `previous_phase_rad`.
        self.previous_phase_rad = None
# In Python speichert `=` einen Wert in `unwrapped_phase_rad`.
        self.unwrapped_phase_rad = 0.0
# In Python speichert `=` einen Wert in `signed_fringes`.
        self.signed_fringes = 0
# In Python speichert `=` einen Wert in `total_abs_fringes`.
        self.total_abs_fringes = 0
# In Python speichert `=` hier den booleschen Startwert aus in `s1_fringes_visible`.
        self.s1_fringes_visible = False
# In Python speichert `=` hier den booleschen Startwert aus in `s2_fringes_visible`.
        self.s2_fringes_visible = False
# In Python speichert `=` einen Wert in `current_direction`.
        self.current_direction = "none"
# In Python speichert `=` einen Wert in `center_s1`.
        self.center_s1 = 0.0
# In Python speichert `=` einen Wert in `center_s2`.
        self.center_s2 = 0.0
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: calibrate_from_samples
    def calibrate_from_samples(self, raw_samples):
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.lock:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not raw_samples:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                raise ValueError("No calibration samples were collected.")
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `s1_values`.
            s1_values = [sample[0] for sample in raw_samples]
# In Python speichert `=` hier einen Wert in `s2_values`.
            s2_values = [sample[1] for sample in raw_samples]
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen berechneten Wert in `offset_s1`.
            self.offset_s1 = (min(s1_values) + max(s1_values)) / 2
# In Python speichert `=` einen berechneten Wert in `offset_s2`.
            self.offset_s2 = (min(s2_values) + max(s2_values)) / 2
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen berechneten Wert in `scale_s1`.
            self.scale_s1 = (max(s1_values) - min(s1_values)) / 2
# In Python speichert `=` einen berechneten Wert in `scale_s2`.
            self.scale_s2 = (max(s2_values) - min(s2_values)) / 2
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.scale_s1 <= 1e-12:
# In Python speichert `=` einen Wert in `scale_s1`.
                self.scale_s1 = 1.0
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.scale_s2 <= 1e-12:
# In Python speichert `=` einen Wert in `scale_s2`.
                self.scale_s2 = 1.0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `center_s1`.
            self.center_s1 = self.offset_s1
# In Python speichert `=` einen Wert in `center_s2`.
            self.center_s2 = self.offset_s2
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self._reset_unlocked()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: set_signal_visibility
    def set_signal_visibility(self, s1_visible, s2_visible):
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.lock:
# In Python speichert `=` einen Wert in `s1_fringes_visible`.
            self.s1_fringes_visible = bool(s1_visible)
# In Python speichert `=` einen Wert in `s2_fringes_visible`.
            self.s2_fringes_visible = bool(s2_visible)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.signals_visible_unlocked():
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self._reset_unlocked()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: signals_visible_unlocked
    def signals_visible_unlocked(self):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.s1_fringes_visible and self.s2_fringes_visible
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: signals_visible
    def signals_visible(self):
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.lock:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return self.signals_visible_unlocked()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: reset
    def reset(self):
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.lock:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self._reset_unlocked()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: _reset_unlocked
    def _reset_unlocked(self):
# In Python speichert `=` hier erstmal keinen Wert in `previous_phase_rad`.
        self.previous_phase_rad = None
# In Python speichert `=` einen Wert in `unwrapped_phase_rad`.
        self.unwrapped_phase_rad = 0.0
# In Python speichert `=` einen Wert in `signed_fringes`.
        self.signed_fringes = 0
# In Python speichert `=` einen Wert in `total_abs_fringes`.
        self.total_abs_fringes = 0
# In Python speichert `=` hier eine leere Liste in `delta_phase_history`.
        self.delta_phase_history = []
# In Python speichert `=` einen Wert in `current_direction`.
        self.current_direction = "none"
# In Python speichert `=` einen Wert in `center_s1`.
        self.center_s1 = self.offset_s1
# In Python speichert `=` einen Wert in `center_s2`.
        self.center_s2 = self.offset_s2
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: normalize
    def normalize(self, raw_s1, raw_s2):
# In Python speichert `=` hier einen berechneten Wert in `s1`.
        s1 = (raw_s1 - self.offset_s1) / self.scale_s1
# In Python speichert `=` hier einen berechneten Wert in `s2`.
        s2 = (raw_s2 - self.offset_s2) / self.scale_s2
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return s1, s2
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: update
    def update(self, raw_s1, raw_s2):
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.lock:
# In Python speichert `=` hier einen Wert in `timestamp`.
            timestamp = time.time()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
            # Slowly update the center tracking to follow DC drift
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.center_s1 is None or self.center_s1 == 0.0:
# In Python speichert `=` einen Wert in `center_s1`.
                self.center_s1 = raw_s1
# In Python speichert `=` einen Wert in `center_s2`.
                self.center_s2 = raw_s2
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `alpha`.
                alpha = 0.002  # time constant ~ 500 samples = 2.5 seconds
# In Python speichert `=` einen berechneten Wert in `center_s1`.
                self.center_s1 = alpha * raw_s1 + (1 - alpha) * self.center_s1
# In Python speichert `=` einen berechneten Wert in `center_s2`.
                self.center_s2 = alpha * raw_s2 + (1 - alpha) * self.center_s2
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `s1_centered`.
            s1_centered = (raw_s1 - self.center_s1) / (self.scale_s1 if self.scale_s1 > 1e-12 else 1.0)
# In Python speichert `=` hier einen berechneten Wert in `s2_centered`.
            s2_centered = (raw_s2 - self.center_s2) / (self.scale_s2 if self.scale_s2 > 1e-12 else 1.0)
# In Python speichert `=` hier einen Wert in `radius`.
            radius = math.hypot(s1_centered, s2_centered)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `s1, s2`.
            s1, s2 = self.normalize(raw_s1, raw_s2)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.signals_visible_unlocked():
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return HomodyneSample(
# In Python speichert `=` hier einen Wert in `timestamp`.
                    timestamp=timestamp,
# In Python speichert `=` hier einen Wert in `raw_s1`.
                    raw_s1=raw_s1,
# In Python speichert `=` hier einen Wert in `raw_s2`.
                    raw_s2=raw_s2,
# In Python speichert `=` hier einen Wert in `s1`.
                    s1=s1,
# In Python speichert `=` hier einen Wert in `s2`.
                    s2=s2,
# In Python speichert `=` hier einen Wert in `radius`.
                    radius=radius,
# In Python speichert `=` hier einen Wert in `phase_rad`.
                    phase_rad=0.0,
# In Python speichert `=` hier einen Wert in `unwrapped_phase_rad`.
                    unwrapped_phase_rad=self.unwrapped_phase_rad,
# In Python speichert `=` hier einen Wert in `delta_phase_rad`.
                    delta_phase_rad=0.0,
# In Python speichert `=` hier einen berechneten Wert in `fringe_position`.
                    fringe_position=self.unwrapped_phase_rad / (2 * math.pi),
# In Python speichert `=` hier einen Wert in `signed_fringes`.
                    signed_fringes=self.signed_fringes,
# In Python speichert `=` hier einen Wert in `fringe_delta`.
                    fringe_delta=0,
# In Python speichert `=` hier einen Wert in `direction`.
                    direction="fringes_not_visible",
# In Python speichert `=` hier einen Startwert in `valid`.
                    valid=False
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if radius < self.min_signal_radius:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return HomodyneSample(
# In Python speichert `=` hier einen Wert in `timestamp`.
                    timestamp=timestamp,
# In Python speichert `=` hier einen Wert in `raw_s1`.
                    raw_s1=raw_s1,
# In Python speichert `=` hier einen Wert in `raw_s2`.
                    raw_s2=raw_s2,
# In Python speichert `=` hier einen Wert in `s1`.
                    s1=s1,
# In Python speichert `=` hier einen Wert in `s2`.
                    s2=s2,
# In Python speichert `=` hier einen Wert in `radius`.
                    radius=radius,
# In Python speichert `=` hier einen Wert in `phase_rad`.
                    phase_rad=0.0,
# In Python speichert `=` hier einen Wert in `unwrapped_phase_rad`.
                    unwrapped_phase_rad=self.unwrapped_phase_rad,
# In Python speichert `=` hier einen Wert in `delta_phase_rad`.
                    delta_phase_rad=0.0,
# In Python speichert `=` hier einen berechneten Wert in `fringe_position`.
                    fringe_position=self.unwrapped_phase_rad / (2 * math.pi),
# In Python speichert `=` hier einen Wert in `signed_fringes`.
                    signed_fringes=self.signed_fringes,
# In Python speichert `=` hier einen Wert in `fringe_delta`.
                    fringe_delta=0,
# In Python speichert `=` hier einen Wert in `direction`.
                    direction="signal_low",
# In Python speichert `=` hier einen Startwert in `valid`.
                    valid=False
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `phase_rad`.
            phase_rad = self.phase_direction_sign * math.atan2(s2_centered, s1_centered)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.previous_phase_rad is None:
# In Python speichert `=` einen Wert in `previous_phase_rad`.
                self.previous_phase_rad = phase_rad
# In Python speichert `=` hier einen Wert in `delta_phase_rad`.
                delta_phase_rad = 0.0
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `delta_phase_rad`.
                delta_phase_rad = wrap_to_pi(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    phase_rad - self.previous_phase_rad
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python speichert `=` einen Wert in `unwrapped_phase_rad +`.
                self.unwrapped_phase_rad += delta_phase_rad
# In Python speichert `=` einen Wert in `previous_phase_rad`.
                self.previous_phase_rad = phase_rad
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `fringe_position`.
            fringe_position = self.unwrapped_phase_rad / (2 * math.pi)
# In Python speichert `=` hier einen Wert in `new_signed_fringes`.
            new_signed_fringes = completed_signed_fringes(fringe_position)
# In Python speichert `=` hier einen berechneten Wert in `fringe_delta`.
            fringe_delta = new_signed_fringes - self.signed_fringes
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if fringe_delta != 0:
# In Python speichert `=` einen Wert in `total_abs_fringes +`.
                self.total_abs_fringes += abs(fringe_delta)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `signed_fringes`.
            self.signed_fringes = new_signed_fringes
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.delta_phase_history.append(delta_phase_rad)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if len(self.delta_phase_history) > 120:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.delta_phase_history.pop(0)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `avg_delta_phase`.
            avg_delta_phase = sum(self.delta_phase_history) / len(self.delta_phase_history)
# Leerzeile zur besseren Lesbarkeit.
            
# Originalkommentar oder Abschnittsüberschrift.
            # Hysteresis parameters for direction detection to avoid jitter
# In Python speichert `=` hier einen Wert in `threshold`.
            threshold = 0.003
# In Python speichert `=` hier einen Wert in `release_threshold`.
            release_threshold = 0.001
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.current_direction == "none":
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if avg_delta_phase > threshold:
# In Python speichert `=` einen Wert in `current_direction`.
                    self.current_direction = "forward"
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
                elif avg_delta_phase < -threshold:
# In Python speichert `=` einen Wert in `current_direction`.
                    self.current_direction = "backward"
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
            elif self.current_direction == "forward":
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if avg_delta_phase < release_threshold:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if avg_delta_phase < -threshold:
# In Python speichert `=` einen Wert in `current_direction`.
                        self.current_direction = "backward"
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
                    else:
# In Python speichert `=` einen Wert in `current_direction`.
                        self.current_direction = "none"
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
            elif self.current_direction == "backward":
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if avg_delta_phase > -release_threshold:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if avg_delta_phase > threshold:
# In Python speichert `=` einen Wert in `current_direction`.
                        self.current_direction = "forward"
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
                    else:
# In Python speichert `=` einen Wert in `current_direction`.
                        self.current_direction = "none"
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `direction`.
            direction = self.current_direction
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return HomodyneSample(
# In Python speichert `=` hier einen Wert in `timestamp`.
                timestamp=timestamp,
# In Python speichert `=` hier einen Wert in `raw_s1`.
                raw_s1=raw_s1,
# In Python speichert `=` hier einen Wert in `raw_s2`.
                raw_s2=raw_s2,
# In Python speichert `=` hier einen Wert in `s1`.
                s1=s1,
# In Python speichert `=` hier einen Wert in `s2`.
                s2=s2,
# In Python speichert `=` hier einen Wert in `radius`.
                radius=radius,
# In Python speichert `=` hier einen Wert in `phase_rad`.
                phase_rad=phase_rad,
# In Python speichert `=` hier einen Wert in `unwrapped_phase_rad`.
                unwrapped_phase_rad=self.unwrapped_phase_rad,
# In Python speichert `=` hier einen Wert in `delta_phase_rad`.
                delta_phase_rad=delta_phase_rad,
# In Python speichert `=` hier einen Wert in `fringe_position`.
                fringe_position=fringe_position,
# In Python speichert `=` hier einen Wert in `signed_fringes`.
                signed_fringes=self.signed_fringes,
# In Python speichert `=` hier einen Wert in `fringe_delta`.
                fringe_delta=fringe_delta,
# In Python speichert `=` hier einen Wert in `direction`.
                direction=direction,
# In Python speichert `=` hier einen Startwert in `valid`.
                valid=True
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: signed_distance_mm
    def signed_distance_mm(self):
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.lock:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.fringe_distance_mm is None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                or not self.signals_visible_unlocked()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return None
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.unwrapped_phase_rad
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                / (2 * math.pi)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                * self.fringe_distance_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: correction_to_zero_mm
    def correction_to_zero_mm(self, stage_direction_sign=1):
# In Python speichert `=` hier einen Wert in `distance_mm`.
        distance_mm = self.signed_distance_mm()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if distance_mm is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return None
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return -stage_direction_sign * distance_mm
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `HomodyneMonitor` als Bauplan für das Fenster und die Logik.
class HomodyneMonitor:
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 4.1 INITIALIZATION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python speichert `=` hier einen Wert in `channel_s1`.
        channel_s1=PHOTODIODE_CHANNEL_S1,
# In Python speichert `=` hier einen Wert in `channel_s2`.
        channel_s2=PHOTODIODE_CHANNEL_S2,
# In Python speichert `=` hier einen Wert in `wavelength_nm`.
        wavelength_nm=LASER_WAVELENGTH_NM,
# In Python speichert `=` hier einen Wert in `phase_direction_sign`.
        phase_direction_sign=PHASE_DIRECTION_SIGN
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# In Python speichert `=` hier einen Wert in `fringe_distance_mm`.
        fringe_distance_mm = compute_fringe_distance_mm(wavelength_nm)
# In Python speichert `=` einen Wert in `reader`.
        self.reader = NIPhotodiodeReader(channel_s1, channel_s2)
# In Python speichert `=` einen Wert in `counter`.
        self.counter = HomodyneQuadratureCounter(
# In Python speichert `=` hier einen Wert in `phase_direction_sign`.
            phase_direction_sign=phase_direction_sign,
# In Python speichert `=` hier einen Wert in `fringe_distance_mm`.
            fringe_distance_mm=fringe_distance_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `single_counter`.
        self.single_counter = SingleSignalFringeCounter(sample_interval_s=SAMPLE_INTERVAL_S)
# In Python speichert `=` einen Wert in `s2_visibility_counter`.
        self.s2_visibility_counter = SingleSignalFringeCounter(
# In Python speichert `=` hier einen Wert in `sample_interval_s`.
            sample_interval_s=SAMPLE_INTERVAL_S
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: connect
    def connect(self):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.reader.connect()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: calibrate
    def calibrate(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python speichert `=` hier einen Wert in `seconds`.
        seconds=CALIBRATION_SECONDS,
# In Python speichert `=` hier einen Wert in `sample_interval_s`.
        sample_interval_s=SAMPLE_INTERVAL_S,
# In Python speichert `=` hier einen Wert in `should_continue`.
        should_continue=None,
# In Python speichert `=` hier einen Startwert in `sample_callback`.
        sample_callback=None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# In Python speichert `=` hier einen Startwert in `samples`.
        samples = []
# In Python speichert `=` hier einen Wert in `start_time`.
        start_time = time.time()
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
        while time.time() - start_time < seconds:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if should_continue is not None and not should_continue():
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                break
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `val`.
            val = self.reader.read()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            samples.append(val)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if sample_callback is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                sample_callback(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    val,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    time.time() - start_time,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    seconds
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            time.sleep(sample_interval_s)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not samples and should_continue is not None and not should_continue():
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return None
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.counter.calibrate_from_samples(samples)
# In Python speichert `=` hier einen Wert in `s1_values`.
        s1_values = [sample[0] for sample in samples]
# In Python speichert `=` hier einen Wert in `s2_values`.
        s2_values = [sample[1] for sample in samples]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.single_counter.calibrate(s1_values)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.s2_visibility_counter.calibrate(s2_values)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.counter.set_signal_visibility(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.single_counter.fringes_visible,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.s2_visibility_counter.fringes_visible
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return samples
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: read
    def read(self):
# In Python speichert `=` hier einen Wert in `raw_s1, raw_s2`.
        raw_s1, raw_s2 = self.reader.read()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.single_counter.update(raw_s2)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.counter.update(raw_s1, raw_s2)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: close
    def close(self):
# In Python schließt `close()` eine geöffnete Verbindung wieder.
        self.reader.close()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: run_gui
def run_gui():
# In Python speichert `=` hier einen Wert in `gui`.
    gui = HomodyneGui()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    gui.run()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: run_print_loop
def run_print_loop():
# In Python speichert `=` hier einen Wert in `monitor`.
    monitor = HomodyneMonitor()
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
    try:
# In Python baut `connect()` die Verbindung zur Hardware auf.
        monitor.connect()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        print("NI connected on Dev1/ai0 and Dev1/ai1.")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        print("Calibrating photodiode offsets and amplitudes...")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        print("Move the stage during calibration so the circle is sampled.")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        monitor.calibrate()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        print("Monitoring. Stop with Ctrl+C.")
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
        while True:
# In Python speichert `=` hier einen Wert in `sample`.
            sample = monitor.read()
# In Python speichert `=` hier einen Wert in `distance_mm`.
            distance_mm = monitor.counter.signed_distance_mm()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if distance_mm is None:
# In Python speichert `=` hier einen berechneten Wert in `distance_text`.
                distance_text = "n/a"
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen berechneten Wert in `distance_text`.
                distance_text = f"{distance_mm:+.9f} mm"
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            print(
# In Python speichert `=` hier einen Wert in `"phase`.
                "phase="
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{sample.unwrapped_phase_rad:+.4f} rad, "
# In Python speichert `=` hier einen Wert in `"fringe_position`.
                "fringe_position="
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{sample.fringe_position:+.4f}, "
# In Python speichert `=` hier einen Wert in `"signed_fringes`.
                "signed_fringes="
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{sample.signed_fringes:+d}, "
# In Python speichert `=` hier einen Wert in `"fringe_delta`.
                "fringe_delta="
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{sample.fringe_delta:+d}, "
# In Python speichert `=` hier einen Wert in `"direction`.
                "direction="
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{sample.direction}, "
# In Python speichert `=` hier einen Wert in `"distance`.
                "distance="
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{distance_text}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            time.sleep(SAMPLE_INTERVAL_S)
# Leerzeile zur besseren Lesbarkeit.

# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
    except KeyboardInterrupt:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        print("\nStopped.")
# `finally` läuft in Python immer, auch wenn vorher ein Fehler aufgetreten ist.
    finally:
# In Python schließt `close()` eine geöffnete Verbindung wieder.
        monitor.close()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 4. APP CLASS (UI)
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `HomodyneGui` als Bauplan für das Fenster und die Logik.
class HomodyneGui:
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if ctk is None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raise RuntimeError(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                "customtkinter is not installed. Install requirements.txt first."
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft man eine Funktion auf: Hier wird das Farbschema eingestellt.
        ctk.set_appearance_mode("light")
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `root`.
        self.root = ctk.CTk()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.root.title("Homodyne Quadrature Monitor")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.root.geometry("900x850")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.root.minsize(760, 650)
# In Python ruft `.` die Methode `configure` auf, um die Farbe eines UI-Elements zu ändern.
        self.root.configure(fg_color="white")
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #creates a scrollable frame inside the window
# In Python erzeugt `()` ein neues Objekt: Hier ein scrollbarer Bereich.
        self.scroll = ctk.CTkScrollableFrame(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.root,
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

# In Python speichert `=` einen Wert in `laser_wavelength_nm`. gespeicherte Laserwellenlänge.
        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
# In Python speichert `=` das Berechnungsergebnis in `fringe_distance_mm`. Abstand zwischen zwei Fringes.
        self.fringe_distance_mm = compute_fringe_distance_mm(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.laser_wavelength_nm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen berechneten Wert in `stage_step_mm`.
        self.stage_step_mm = self.fringe_distance_mm / 4
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `monitor`.
        self.monitor = HomodyneMonitor(
# In Python speichert `=` hier einen Wert in `wavelength_nm`.
            wavelength_nm=self.laser_wavelength_nm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier den booleschen Startwert aus in `monitoring`.
        self.monitoring = False
# In Python speichert `=` hier erstmal keinen Wert in `measurement_thread`.
        self.measurement_thread = None
# In Python speichert `=` hier eine leere Liste in `raw_s1_history`.
        self.raw_s1_history = []
# In Python speichert `=` hier eine leere Liste in `raw_s2_history`.
        self.raw_s2_history = []
# In Python speichert `=` einen Wert in `sample_display_lock`.
        self.sample_display_lock = threading.Lock()
# In Python speichert `=` hier erstmal keinen Wert in `pending_sample`.
        self.pending_sample = None
# In Python speichert `=` hier erstmal keinen Wert in `pending_distance_mm`.
        self.pending_distance_mm = None
# In Python speichert `=` hier den booleschen Startwert aus in `sample_display_scheduled`.
        self.sample_display_scheduled = False
# In Python speichert `=` einen Wert in `last_sample_display_time`.
        self.last_sample_display_time = 0.0
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Data recording variables
# In Python speichert `=` hier den booleschen Startwert aus in `recording`. Merker, ob gerade aufgenommen wird.
        self.recording = False
# In Python speichert `=` hier eine leere Liste in `recorded_data`. gesammelte Daten für den Export.
        self.recorded_data = []
# In Python speichert `=` hier erstmal keinen Wert in `recording_start_time`. Startzeit der Aufnahme.
        self.recording_start_time = None
# Leerzeile zur besseren Lesbarkeit.
        
# Originalkommentar oder Abschnittsüberschrift.
        # Measurement state variables
# In Python speichert `=` hier den booleschen Startwert aus in `measuring`.
        self.measuring = False
# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
        self.calibrating = False
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das neu erzeugte Stage-Objekt in einer Variable.
        self.stage = StageController() if StageController is not None else None
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Geschwindigkeit setzt.
            self.stage.set_velocity(DEFAULT_STAGE_SPEED_MM_S, 0.0)
# In Python speichert `=` hier den booleschen Startwert aus in `stage_connected`. Verbindungsstatus des Stage.
        self.stage_connected = False
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage is not None:
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
            try:
# In Python ruft `.` eine Methode auf, die die Verbindung herstellt.
                self.stage_connected = self.stage.connect()
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
            except Exception as stage_err:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                print("Stage connection error:", stage_err)
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
# In Python speichert `=` hier den booleschen Startwert aus in `stage_command_active`.
        self.stage_command_active = False
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier erstmal keinen Wert in `latest_sample`. letzte Messprobe.
        self.latest_sample = None
# In Python speichert `=` hier erstmal keinen Wert in `latest_distance_mm`.
        self.latest_distance_mm = None
# In Python speichert `=` hier erstmal keinen Wert in `last_error_text`. letzte Fehlermeldung.
        self.last_error_text = None
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #for stage locking
# In Python speichert `=` einen Wert in `lock_active`.
        self.lock_active = False # state of the position lock
# In Python speichert `=` einen Wert in `lock_reference_distance_mm`.
        self.lock_reference_distance_mm = 0.0
# In Python speichert `=` einen Wert in `lock_reference_phase_rad`.
        self.lock_reference_phase_rad = 0.0
# In Python speichert `=` einen Wert in `lock_reference_fringes`.
        self.lock_reference_fringes = 0
# In Python speichert `=` einen Wert in `lock_stage_position_mm`.
        self.lock_stage_position_mm = 0.0
# In Python speichert `=` einen Wert in `lock_ref_single_fringes`.
        self.lock_ref_single_fringes = 0
# In Python speichert `=` einen Wert in `stage_position_mm`.
        self.stage_position_mm = 0.0
# In Python speichert `=` hier den booleschen Startwert aus in `lock_correction_active`.
        self.lock_correction_active = False
# In Python speichert `=` einen Wert in `lock_last_correction_time`.
        self.lock_last_correction_time = 0.0
# In Python speichert `=` hier erstmal keinen Wert in `lock_target_position_mm`.
        self.lock_target_position_mm = None
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.build_ui()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_comparison_labels() # renewing the text in the UI matching the initial update of the comparison labels with 0 values using e.g self.current_stage_movement_for_compare which is 0 at the beginning
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_stage_position_once() # reads the current stage position and updates the label, this is important to have the correct position at the beginning
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            STAGE_STATUS_POLL_MS,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.poll_stage_status
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
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
# In Python erzeugt `()` ein Label-Objekt.
        self.status = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.scroll,
# In Python speichert `=` hier einen Wert in `text`.
            text="Status: stopped",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.status.pack(pady=(16, 12))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        control_frame = ctk.CTkFrame(self.scroll, fg_color="#EEEEEE")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        control_frame.pack(fill="x", padx=18, pady=8)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        control_frame.grid_columnconfigure(0, weight=2)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        control_frame.grid_columnconfigure(1, weight=1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        control_frame.grid_columnconfigure(2, weight=1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        control_frame.grid_columnconfigure(3, weight=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_start = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            control_frame,
# Button zum Starten und Stoppen der Messung.
            text="START MONITORING",
# In Python speichert `=` hier einen Wert in `width`.
            width=150,
# Hier wird der Button in Python mit der Methode für Start/Stopp verbunden.
            command=self.toggle_monitoring,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12, "bold")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_start.grid(row=0, column=0, padx=8, pady=14, sticky="ew")
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_lock = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            control_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="LOCK",
# In Python speichert `=` hier einen Wert in `width`.
            width=110,
# Hier wird der Button in Python mit der Methode für Start/Stopp verbunden.
            command=self.toggle_lock,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12, "bold")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_lock.grid(row=0, column=1, padx=8, pady=14, sticky="ew")
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_reset = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            control_frame,
# Button zum Zurücksetzen der Werte.
            text="RESET",
# In Python speichert `=` hier einen Wert in `width`.
            width=110,
# In Python speichert `=` hier einen Wert in `command`.
            command=self.reset_monitor,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=ORANGE_COLOR,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12, "bold")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_reset.grid(row=0, column=2, padx=8, pady=14, sticky="ew")
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_record = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            control_frame,
# Button zum Starten der Aufnahme.
            text="START RECORDING",
# In Python speichert `=` hier einen Wert in `width`.
            width=150,
# Hier wird der Button in Python mit der Methode für Start/Stopp verbunden.
            command=self.toggle_recording,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color="#555555",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12, "bold")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_record.grid(row=0, column=3, padx=8, pady=14, sticky="ew")
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
            padx=18,
# In Python speichert `=` hier einen Wert in `pady`.
            pady=8
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
# In Python speichert `=` hier einen Wert in `text`.
            text="Set wavelength (nm)",
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
        self.label_fringe_distance = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text=self.fringe_distance_text(),
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_fringe_distance.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="Step size (mm):",
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
            f"{self.stage_step_mm:.9f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="Velocity (mm):",
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
        if self.stage_connected and self.stage is not None:
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
        self.btn_min.grid(row=0, column=0, padx=1)
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
        self.btn_left.grid(row=0, column=1, padx=1)
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
        self.btn_center.grid(row=0, column=2, padx=1)
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
        self.btn_right.grid(row=0, column=3, padx=1)
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
        self.btn_max.grid(row=0, column=4, padx=1)
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
# In Python speichert `=` hier einen Wert in `text`.
            text="Target or Distance (mm):",
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
        self.target_button_frame.pack(fill="x", padx=12, pady=1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.target_button_frame.grid_columnconfigure(0, weight=1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.target_button_frame.grid_columnconfigure(1, weight=1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.target_button_frame.grid_columnconfigure(2, weight=1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.target_button_frame.grid_columnconfigure(3, weight=1)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_target_abs = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.target_button_frame,
# Button zum Fahren auf eine Zielposition.
            text="Go to target",
# In Python speichert `=` hier einen Wert in `width`.
            width=120,
# Hier wird der Button in Python mit der Zielpositions-Methode verbunden.
            command=self.move_to_target,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_target_abs.grid(row=0, column=0, padx=1, sticky="ew")
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_target_rel = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.target_button_frame,
# Button zum Fahren um eine Distanz.
            text="Move distance",
# In Python speichert `=` hier einen Wert in `width`.
            width=120,
# Hier wird der Button in Python mit der Distanz-Methode verbunden.
            command=self.move_distance,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_target_rel.grid(row=0, column=1, padx=1, sticky="ew")
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_stop = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.target_button_frame,
# Button für den Sofortstopp der Stage.
            text="STOP STAGE",
# In Python speichert `=` hier einen Wert in `width`.
            width=120,
# Hier wird der Button in Python mit der Stopp-Methode verbunden.
            command=self.stop_stage,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=RED_COLOR,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11, "bold")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_stop.grid(row=0, column=3, padx=1, sticky="ew")
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

# In Python speichert `=` einen Wert in `all_buttons`.
        self.all_buttons = [
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.btn_reset,
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

# In Python erzeugt `()` einen Rahmen.
        self.cols_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.cols_frame.pack(fill="both", expand=True, padx=18, pady=8)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.cols_frame.grid_columnconfigure(0, weight=3, uniform="cols")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.cols_frame.grid_columnconfigure(1, weight=2, uniform="cols")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.cols_frame.grid_rowconfigure(0, weight=1)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.left_col = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.right_col = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        plot_frame = ctk.CTkFrame(self.left_col, fg_color="#EEEEEE")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        plot_frame.pack(fill="x", expand=False, pady=4)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        plot_header_frame = ctk.CTkFrame(plot_frame, fg_color="transparent")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        plot_header_frame.pack(fill="x", padx=10, pady=(10, 4))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            plot_header_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="Raw Signal",
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
            plot_header_frame,
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

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if plt is None or FigureCanvasTkAgg is None:
# In Python erzeugt `()` ein Label-Objekt.
            ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                plot_frame,
# In Python speichert `=` hier einen Wert in `text`.
                text="Matplotlib is required for live plotting.",
# In Python speichert `=` hier einen Wert in `font`.
                font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
            ).pack(pady=8)
# In Python speichert `=` hier erstmal keinen Wert in `plot_canvas`.
            self.plot_canvas = None
# In Python speichert `=` hier erstmal keinen Wert in `plot_axis`.
            self.plot_axis = None
# In Python speichert `=` hier erstmal keinen Wert in `plot_axes`.
            self.plot_axes = None
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python erzeugt `()` eine Matplotlib-Figur.
            self.plot_figure = plt.Figure(figsize=(5.0, 2.6), dpi=100)
# In Python speichert `=` hier einen Wert in `axes`.
            axes = self.plot_figure.subplots(2, 1, sharex=True)
# In Python speichert `=` einen Wert in `plot_axis`.
            self.plot_axis = axes[0]
# In Python speichert `=` einen Wert in `plot_axes`.
            self.plot_axes = {
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                'S1_raw': axes[0],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                'S2_raw': axes[1]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            }
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `plot_specs`.
            plot_specs = {
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                'S1_raw': ("S1 raw voltage", 'blue', 'S1 raw', 'S1 clean'),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                'S2_raw': ("S2 raw voltage", 'green', 'S2 raw', 'S2 clean')
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            }
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `plot_lines`.
            self.plot_lines = {}
# `for` startet in Python eine Schleife über mehrere Werte.
            for key in ['S1_raw', 'S2_raw']:
# In Python speichert `=` hier einen Wert in `axis`.
                axis = self.plot_axes[key]
# In Python speichert `=` hier einen Wert in `title, color, label_raw, label_clean`.
                title, color, label_raw, label_clean = plot_specs[key]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                axis.set_title(title, fontsize=9)
# In Python wird mit `.` ein UI-Element im Layout platziert.
                axis.grid(True, linestyle=':', alpha=0.6)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                axis.set_ylabel("Voltage", fontsize=8)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                axis.tick_params(labelsize=8)
# In Python speichert `=` einen Wert in `plot_lines[key]`.
                self.plot_lines[key] = axis.plot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    [],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    [],
# In Python speichert `=` hier einen Wert in `color`.
                    color=color,
# In Python speichert `=` hier einen Wert in `alpha`.
                    alpha=1.0,
# In Python speichert `=` hier einen Wert in `label`.
                    label=label_raw
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )[0]
# In Python speichert `=` einen Wert in `plot_lines[key + '_clean']`.
                self.plot_lines[key + '_clean'] = axis.plot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    [],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    [],
# In Python speichert `=` hier einen Wert in `color`.
                    color=color,
# In Python speichert `=` hier einen Wert in `linewidth`.
                    linewidth=1.5,
# In Python speichert `=` hier einen Wert in `label`.
                    label=label_clean
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )[0]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.plot_lines[key + '_clean'].set_visible(False)
# In Python speichert `=` einen Wert in `plot_lines[key + '_fit']`.
                self.plot_lines[key + '_fit'] = axis.plot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    [],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    [],
# In Python speichert `=` hier einen Wert in `color`.
                    color='orange' if key == 'S1_raw' else 'magenta',
# In Python speichert `=` hier einen Wert in `linestyle`.
                    linestyle='--',
# In Python speichert `=` hier einen berechneten Wert in `label`.
                    label=label_raw.split()[0] + ' fit'
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )[0]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                axis.legend(loc="upper right", prop={"size": 8})
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            axes[1].set_xlabel("Samples", fontsize=8)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_figure.subplots_adjust(
# In Python speichert `=` hier einen Wert in `left`.
                left=0.12,
# In Python speichert `=` hier einen Wert in `right`.
                right=0.98,
# In Python speichert `=` hier einen Wert in `top`.
                top=0.88,
# In Python speichert `=` hier einen Wert in `bottom`.
                bottom=0.18,
# In Python speichert `=` hier einen Wert in `hspace`.
                hspace=0.55
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python erzeugt `()` die Einbettung des Plots ins Tk-Fenster.
            self.plot_canvas = FigureCanvasTkAgg(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.plot_figure,
# In Python speichert `=` hier einen Wert in `master`.
                master=plot_frame
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_canvas.draw()
# In Python speichert `=` hier einen Wert in `plot_widget`.
            plot_widget = self.plot_canvas.get_tk_widget()
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
            plot_widget.configure(height=260)
# In Python wird mit `.` ein UI-Element im Layout platziert.
            plot_widget.pack(fill="x", expand=False, padx=8, pady=(4, 8))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.single_fringe_frame = ctk.CTkFrame(self.right_col, fg_color="#EEEEEE")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.single_fringe_frame.pack(fill="x", pady=4, padx=8)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.single_fringe_frame,
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="Single-Signal Fringe Counter (Signal 1)",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 14, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=(8, 4))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_single_fringes = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.single_fringe_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="S1 Fringe Count: 0",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_single_fringes.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_single_distance = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.single_fringe_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="S1 Calculated Distance: 0.000000 mm",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_single_distance.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_single_thresholds = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.single_fringe_frame,
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="Signal amplitudes: S1 = n/a, S2 = n/a",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR,
# In Python speichert `=` hier einen Wert in `wraplength`.
            wraplength=320
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_single_thresholds.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.plot_frame_circle = ctk.CTkFrame(self.right_col, fg_color="#EEEEEE")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.plot_frame_circle.pack(fill="both", expand=True, pady=4)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_frame_circle,
# In Python speichert `=` hier einen Wert in `text`.
            text="Lissajous",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 15, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=(10, 4))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_lissajous_direction = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_frame_circle,
# In Python speichert `=` hier einen Wert in `text`.
            text="STILL",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 22, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lissajous_direction.pack(pady=(2, 6))
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if plt is None or FigureCanvasTkAgg is None:
# In Python speichert `=` hier erstmal keinen Wert in `plot_canvas_circle`.
            self.plot_canvas_circle = None
# In Python speichert `=` hier erstmal keinen Wert in `axis_circle`.
            self.axis_circle = None
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python erzeugt `()` eine Matplotlib-Figur.
            self.plot_figure_circle = plt.Figure(figsize=(4.0, 4.0), dpi=100)
# In Python speichert `=` einen Wert in `axis_circle`.
            self.axis_circle = self.plot_figure_circle.add_subplot(111)
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.axis_circle.set_title("Lissajous Circle (S1 vs S2)")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.axis_circle.set_xlabel("S1 (normalized)")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.axis_circle.set_ylabel("S2 (normalized)")
# In Python wird mit `.` ein UI-Element im Layout platziert.
            self.axis_circle.grid(True, linestyle=':', alpha=0.6)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.axis_circle.set_aspect('equal', adjustable='box')
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.axis_circle.set_xlim(-1.5, 1.5)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.axis_circle.set_ylim(-1.5, 1.5)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `ref_theta`.
            ref_theta = [t * 2 * math.pi / 100 for t in range(101)]
# In Python speichert `=` hier einen Wert in `ref_x`.
            ref_x = [math.cos(t) for t in ref_theta]
# In Python speichert `=` hier einen Wert in `ref_y`.
            ref_y = [math.sin(t) for t in ref_theta]
# Originalkommentar oder Abschnittsüberschrift.
            # keep a handle so we can scale the reference circle when autoscaling axes
# In Python speichert `=` einen Wert in `plot_lines['ref_circle']`.
            self.plot_lines['ref_circle'] = self.axis_circle.plot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                ref_x,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                ref_y,
# In Python speichert `=` hier einen Wert in `color`.
                color='gray',
# In Python speichert `=` hier einen Wert in `linestyle`.
                linestyle='--',
# In Python speichert `=` hier einen Wert in `alpha`.
                alpha=0.5,
# In Python speichert `=` hier einen Wert in `label`.
                label='Ref Circle'
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )[0]
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `plot_lines['circle_trace']`.
            self.plot_lines['circle_trace'] = self.axis_circle.plot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                [],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                [],
# In Python speichert `=` hier einen Wert in `color`.
                color='purple',
# In Python speichert `=` hier einen Wert in `alpha`.
                alpha=0.6,
# In Python speichert `=` hier einen Wert in `label`.
                label='Trace'
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )[0]
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `plot_lines['circle_current']`.
            self.plot_lines['circle_current'] = self.axis_circle.plot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                [],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                [],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                'ro',
# In Python speichert `=` hier einen Wert in `markersize`.
                markersize=8,
# In Python speichert `=` hier einen Wert in `label`.
                label='Current'
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )[0]
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `plot_lines['circle_pointer']`.
            self.plot_lines['circle_pointer'] = self.axis_circle.plot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                [],
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                [],
# In Python speichert `=` hier einen Wert in `color`.
                color='orange',
# In Python speichert `=` hier einen Wert in `linestyle`.
                linestyle='-',
# In Python speichert `=` hier einen Wert in `linewidth`.
                linewidth=2,
# In Python speichert `=` hier einen Wert in `label`.
                label='Pointer'
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )[0]
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `plot_quiver`.
            self.plot_quiver = self.axis_circle.quiver(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                [0], [0], [0], [0],
# In Python speichert `=` hier einen Wert in `angles`.
                angles='xy', scale_units='xy', scale=1,
# In Python speichert `=` hier einen Wert in `color`.
                color='green', width=0.015, headwidth=4, headlength=5
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_quiver.set_visible(False)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
            # self.axis_circle.legend(loc="upper right")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_figure_circle.tight_layout()
# In Python erzeugt `()` die Einbettung des Plots ins Tk-Fenster.
            self.plot_canvas_circle = FigureCanvasTkAgg(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.plot_figure_circle,
# In Python speichert `=` hier einen Wert in `master`.
                master=self.plot_frame_circle
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_canvas_circle.draw()
# In Python wird mit `.` ein UI-Element im Layout platziert.
            self.plot_canvas_circle.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Create dummy labels that are not packed to avoid AttributeError in other methods
# In Python erzeugt `()` einen Rahmen.
        dummy_parent = ctk.CTkFrame(self.right_col)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_phase = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_s1_norm = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_s2_norm = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_unwrapped_phase = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_fringe_position = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_fringes = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_direction = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_distance = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_lock_status = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_lock_reference = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_lock_drift = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_lock_correction = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_stage_status = ctk.CTkLabel(dummy_parent)
# In Python erzeugt `()` ein Label-Objekt.
        self.label_stage_position_lock = ctk.CTkLabel(dummy_parent)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.compare_frame = ctk.CTkFrame(self.left_col, fg_color="#EEEEEE")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.compare_frame.pack(fill="x", pady=4, padx=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.compare_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="Stage Movement Comparison",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 14, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=(8, 4))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Rahmen.
        self.compare_driven_frame = ctk.CTkFrame(self.compare_frame, fg_color="transparent")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.compare_driven_frame.pack(pady=2)
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
        self.label_compare_driven.grid(row=0, column=0, padx=14)
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
        self.label_still_to_drive.grid(row=0, column=1, padx=14)
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
        self.label_compare_calculated.pack(pady=2)
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
        self.label_compare_difference.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_measurement = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.compare_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="START MEASUREMENT",
# Hier wird der Button in Python mit der Methode für Start/Stopp verbunden.
            command=self.toggle_measurement,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12, "bold")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_measurement.pack(pady=(6, 10))
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Create Lock Box Frame under start measurement
# In Python erzeugt `()` einen Rahmen.
        self.lock_box_frame = ctk.CTkFrame(self.left_col, fg_color="#EEEEEE")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.lock_box_frame.pack(fill="x", pady=8, padx=0)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.lock_box_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="Stage Lock",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 14, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(pady=(8, 4))
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_lock_status_box = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.lock_box_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="Lock Status: off",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_status_box.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_fringes_since_locking = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.lock_box_frame,
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="Fringes since locking: n/a",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_fringes_since_locking.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        self.label_correction_since_locking = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.lock_box_frame,
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="Correction since locking: n/a",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_correction_since_locking.pack(pady=2)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` einen Button.
        self.btn_lock_box = ctk.CTkButton(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.lock_box_frame,
# In Python speichert `=` hier einen Wert in `text`.
            text="LOCK",
# Hier wird der Button in Python mit der Methode für Start/Stopp verbunden.
            command=self.toggle_lock,
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12, "bold")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        self.btn_lock_box.pack(pady=(6, 8))
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `channel_text`.
        channel_text = (
# In Python speichert `=` hier einen Wert in `f"Channels: S1`.
            f"Channels: S1={PHOTODIODE_CHANNEL_S1}, "
# In Python speichert `=` hier einen Wert in `f"S2`.
            f"S2={PHOTODIODE_CHANNEL_S2}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
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
        ).pack(pady=(8, 8))
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: make_value_label
    def make_value_label(self, parent, name, initial_value):
# In Python erzeugt `()` einen Rahmen.
        row = ctk.CTkFrame(parent, fg_color="transparent")
# In Python wird mit `.` ein UI-Element im Layout platziert.
        row.pack(fill="x", padx=18, pady=5)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            row,
# In Python speichert `=` hier einen Wert in `text`.
            text=f"{name}:",
# In Python speichert `=` hier einen Wert in `width`.
            width=180,
# In Python speichert `=` hier einen Wert in `anchor`.
            anchor="w",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12, "bold"),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird mit `.` ein UI-Element im Layout platziert.
        ).pack(side="left")
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Label-Objekt.
        label = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            row,
# In Python speichert `=` hier einen Wert in `text`.
            text=initial_value,
# In Python speichert `=` hier einen Wert in `anchor`.
            anchor="w",
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 12),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        label.pack(side="left", fill="x", expand=True)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return label
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: make_formula_label
    def make_formula_label(self, parent, text):
# In Python erzeugt `()` ein Label-Objekt.
        label = ctk.CTkLabel(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            parent,
# In Python speichert `=` hier einen Wert in `text`.
            text=text,
# In Python speichert `=` hier einen Wert in `anchor`.
            anchor="w",
# In Python speichert `=` hier einen Wert in `justify`.
            justify="left",
# In Python speichert `=` hier einen Wert in `wraplength`.
            wraplength=620,
# In Python speichert `=` hier einen Wert in `font`.
            font=("Arial", 11),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird mit `.` ein UI-Element im Layout platziert.
        label.pack(fill="x", padx=18, pady=2)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return label
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: fringe_distance_text
    def fringe_distance_text(self):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            f"Fringe distance: {self.fringe_distance_mm:.9f} mm "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            f"({self.fringe_distance_mm * 1000:.6f} um)"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Liest eine Zahl aus einem Eingabefeld.
    def parse_entry_float(self, entry):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return float(entry.get().replace(",", "."))
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.lock_active:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: unlock before changing wavelength",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # get the new laser wavelenght from the UI
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `wavelength_nm`.
            wavelength_nm = self.parse_entry_float(self.wavelength_entry)
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except ValueError:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: invalid wavelength value",
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
                text="Status: wavelength must be positive",
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
# In Python speichert `=` einen berechneten Wert in `stage_step_mm`.
        self.stage_step_mm = self.fringe_distance_mm / 4
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `monitor.counter.fringe_distance_mm`.
        self.monitor.counter.fringe_distance_mm = self.fringe_distance_mm
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_fringe_distance.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=self.fringe_distance_text()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Originalkommentar oder Abschnittsüberschrift.
        #clear old suggested stepsize
# In Python wird mit `.` ein Eingabefeld geleert.
        self.step_entry.delete(0, "end")
# In Python wird mit `.` Text in ein Eingabefeld geschrieben.
        self.step_entry.insert(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            f"{self.stage_step_mm:.9f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"Status: wavelength set to "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{self.laser_wavelength_nm:.1f} nm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: apply_stage_step_size
    def apply_stage_step_size(self):
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `step_mm`.
            step_mm = self.parse_entry_float(self.step_entry)
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except ValueError:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: invalid stage step size",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `step_mm`.
        step_mm = abs(step_mm)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if step_mm <= 0:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: stage step size must be positive",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `stage_step_mm`.
        self.stage_step_mm = step_mm
# In Python wird mit `.` ein Eingabefeld geleert.
        self.step_entry.delete(0, "end")
# In Python wird mit `.` Text in ein Eingabefeld geschrieben.
        self.step_entry.insert(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            f"{self.stage_step_mm:.9f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Status: stage step set to {self.stage_step_mm:.9f} mm",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: limited_stage_correction_mm
    def limited_stage_correction_mm(self, correction_mm):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_step_mm <= 0:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return correction_mm
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `sign`.
        sign = 1 if correction_mm >= 0 else -1
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return sign * min(abs(correction_mm), self.stage_step_mm)
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
# In Python speichert `=` hier einen Wert in `state`.
        state = "normal" if enabled else "disabled"
# `for` startet in Python eine Schleife über mehrere Werte.
        for button in self.all_buttons:
# In Python ruft `.` die Methode `configure` auf, um einen Button zu aktivieren oder zu sperren.
            button.configure(state=state)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: finish_stage_command_ui
    def finish_stage_command_ui(self):
# In Python speichert `=` hier den booleschen Startwert aus in `stage_command_active`.
        self.stage_command_active = False
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.set_buttons_enabled(True)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: queue_sample_display
    def queue_sample_display(self, sample, distance_mm, force=False):
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.sample_display_lock:
# In Python speichert `=` einen Wert in `pending_sample`.
            self.pending_sample = sample
# In Python speichert `=` einen Wert in `pending_distance_mm`.
            self.pending_distance_mm = distance_mm
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.sample_display_scheduled:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `now`.
            now = time.monotonic()
# In Python speichert `=` hier einen berechneten Wert in `elapsed_s`.
            elapsed_s = now - self.last_sample_display_time
# In Python speichert `=` hier einen Wert in `delay_s`.
            delay_s = 0.0 if force else max(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0.0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                UI_UPDATE_INTERVAL_S - elapsed_s
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier den booleschen Startwert ein in `sample_display_scheduled`.
            self.sample_display_scheduled = True
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            int(delay_s * 1000),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.flush_sample_display
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: flush_sample_display
    def flush_sample_display(self):
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.sample_display_lock:
# In Python speichert `=` hier einen Wert in `sample`.
            sample = self.pending_sample
# In Python speichert `=` hier einen Wert in `distance_mm`.
            distance_mm = self.pending_distance_mm
# In Python speichert `=` hier erstmal keinen Wert in `pending_sample`.
            self.pending_sample = None
# In Python speichert `=` hier erstmal keinen Wert in `pending_distance_mm`.
            self.pending_distance_mm = None
# In Python speichert `=` hier den booleschen Startwert aus in `sample_display_scheduled`.
            self.sample_display_scheduled = False
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `last_sample_display_time`.
        self.last_sample_display_time = time.monotonic()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if sample is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.update_sample_display(sample, distance_mm)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: set_status_from_thread
    def set_status_from_thread(self, text, color=TEXT_COLOR):
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=text,
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=color
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: set_stage_status_from_thread
    def set_stage_status_from_thread(self, text, color=TEXT_COLOR):
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            lambda:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_stage_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=text,
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=color
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: set_stage_position_from_thread
    def set_stage_position_from_thread(self, position_mm):
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python speichert `=` hier einen Wert in `lambda p`.
            lambda p=position_mm:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_stage_position.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Stage Position: {p:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ) if p is not None else None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: wait_for_stage_motion
    def wait_for_stage_motion(self, timeout_s=STAGE_MOVE_TIMEOUT_S):
# In Python speichert `=` hier einen Wert in `start_time`.
        start_time = time.monotonic()
# In Python speichert `=` hier einen Wert in `last_position_update_s`.
        last_position_update_s = 0.0
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
        while self.stage is not None and self.stage.is_moving:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if time.monotonic() - start_time > timeout_s:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
                self.stage.stop()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                raise RuntimeError("stage move timeout")
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `position_mm`.
            position_mm = self.stage.current_position
# In Python speichert `=` hier einen Wert in `now`.
            now = time.monotonic()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if now - last_position_update_s >= STAGE_POLL_INTERVAL_S:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.set_stage_position_from_thread(position_mm)
# In Python speichert `=` hier einen Wert in `last_position_update_s`.
                last_position_update_s = now
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            time.sleep(STAGE_POLL_INTERVAL_S)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage is None or not self.stage_connected:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return None
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
        position_mm = self.stage.get_position()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.set_stage_position_from_thread(position_mm)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return position_mm
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: toggle_monitoring
    def toggle_monitoring(self):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.monitoring:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stop_monitoring()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.start_monitoring()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Startet oder stoppt die Aufzeichnung.
    def toggle_recording(self):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        import time
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        from tkinter import messagebox
# Leerzeile zur besseren Lesbarkeit.
        
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.recording:
# Originalkommentar oder Abschnittsüberschrift.
            # Stop recording and save
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
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# Originalkommentar oder Abschnittsüberschrift.
            # Start recording
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.monitoring:
# In Python öffnet das `messagebox`-Modul ein Dialogfenster für den Benutzer.
                messagebox.showwarning(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    "Aufnahme",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    "Bitte starten Sie zuerst das Monitoring (START MONITORING)."
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.
            
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
            initialfile=f"messung_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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
                        "Raw_S1_V",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Raw_S2_V",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Norm_S1",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Norm_S2",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Phase_rad",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Unwrapped_Phase_rad",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Lissajous_Distance_mm",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Calculated_Distance_mm",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        "Fringe_Count",
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
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: toggle_measurement
    def toggle_measurement(self):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        from tkinter import messagebox
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.lock_active:
# In Python öffnet das `messagebox`-Modul ein Dialogfenster für den Benutzer.
            messagebox.showwarning(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                "Messung",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                "Messung kann nicht gestartet werden, da der Lock aktiv ist."
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.monitoring:
# In Python öffnet das `messagebox`-Modul ein Dialogfenster für den Benutzer.
            messagebox.showwarning(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                "Messung",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                "Bitte starten Sie zuerst das Photodioden-Monitoring (START MONITORING)."
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.measuring:
# Originalkommentar oder Abschnittsüberschrift.
            # Stop measurement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stop_measurement()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# Originalkommentar oder Abschnittsüberschrift.
            # Start measurement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.start_measurement()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: start_measurement
    def start_measurement(self):
# In Python speichert `=` einen Wert in `recorded_data`. gesammelte Daten für den Export.
        self.recorded_data = []  # Clear recorded data if any
# Originalkommentar oder Abschnittsüberschrift.
        # Reset counters
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.monitor is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.monitor.counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.monitor.single_counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.monitor.s2_visibility_counter.reset()
# Leerzeile zur besseren Lesbarkeit.
            
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'lp_s1'):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            del self.lp_s1
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'lp_s2'):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            del self.lp_s2
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'lp_clean_s1'):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            del self.lp_clean_s1
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'lp_clean_s2'):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            del self.lp_clean_s2
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier eine leere Liste in `clean_s1_history`.
        self.clean_s1_history = []
# In Python speichert `=` hier eine leere Liste in `clean_s2_history`.
        self.clean_s2_history = []
# In Python speichert `=` hier erstmal keinen Wert in `latest_sample`. letzte Messprobe.
        self.latest_sample = None
# In Python speichert `=` hier erstmal keinen Wert in `latest_distance_mm`.
        self.latest_distance_mm = None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.reset_calculation_display()
# Leerzeile zur besseren Lesbarkeit.
        
# In Python speichert `=` hier den booleschen Startwert ein in `measuring`.
        self.measuring = True
# In Python speichert `=` hier den booleschen Startwert ein in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
        self.calibrating = True
# Leerzeile zur besseren Lesbarkeit.
        
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
        self.btn_measurement.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="STOP MEASUREMENT",
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: stop_measurement
    def stop_measurement(self):
# In Python speichert `=` hier den booleschen Startwert aus in `measuring`.
        self.measuring = False
# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
        self.calibrating = False
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.stop_calibration_stage_motion()
# Leerzeile zur besseren Lesbarkeit.
        
# Originalkommentar oder Abschnittsüberschrift.
        # Reset UI button
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
        self.btn_measurement.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="START MEASUREMENT",
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.
        
# Originalkommentar oder Abschnittsüberschrift.
        # Reset UI status
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Status: monitoring running",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
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

# In Python speichert `=` einen Wert in `monitor`.
        self.monitor = HomodyneMonitor(
# In Python speichert `=` hier einen Wert in `wavelength_nm`.
            wavelength_nm=self.laser_wavelength_nm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` hier den booleschen Startwert ein in `monitoring`.
        self.monitoring = True
# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
        self.calibrating = False
# In Python speichert `=` hier den booleschen Startwert aus in `measuring`.
        self.measuring = False
# In Python speichert `=` hier erstmal keinen Wert in `latest_sample`. letzte Messprobe.
        self.latest_sample = None
# In Python speichert `=` hier erstmal keinen Wert in `latest_distance_mm`.
        self.latest_distance_mm = None
# In Python speichert `=` hier erstmal keinen Wert in `last_error_text`. letzte Fehlermeldung.
        self.last_error_text = None
# In Python speichert `=` hier eine leere Liste in `raw_s1_history`.
        self.raw_s1_history = []
# In Python speichert `=` hier eine leere Liste in `raw_s2_history`.
        self.raw_s2_history = []
# In Python speichert `=` hier eine leere Liste in `clean_s1_history`.
        self.clean_s1_history = []
# In Python speichert `=` hier eine leere Liste in `clean_s2_history`.
        self.clean_s2_history = []
# In Python speichert `=` hier eine leere Liste in `baseline_samples`.
        self.baseline_samples = []
# In Python speichert `=` einen Wert in `baseline_s1`.
        self.baseline_s1 = 0.0
# In Python speichert `=` einen Wert in `baseline_s2`.
        self.baseline_s2 = 0.0
# In Python speichert `=` hier den booleschen Startwert aus in `baseline_recorded`. Merker, ob die Baseline schon gemessen wurde.
        self.baseline_recorded = False
# In Python speichert `=` hier eine leere Liste in `calibration_raw_samples`. gesammelte Rohdaten der Kalibrierung.
        self.calibration_raw_samples = []
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.sample_display_lock:
# In Python speichert `=` hier erstmal keinen Wert in `pending_sample`.
            self.pending_sample = None
# In Python speichert `=` hier erstmal keinen Wert in `pending_distance_mm`.
            self.pending_distance_mm = None
# In Python speichert `=` hier den booleschen Startwert aus in `sample_display_scheduled`.
            self.sample_display_scheduled = False
# In Python speichert `=` einen Wert in `last_sample_display_time`.
        self.last_sample_display_time = 0.0
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.reset_calculation_display()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.disable_lock(update_status=False)
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
        self.btn_start.configure(
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
        self.set_buttons_enabled(True)
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `Thread(...)` einen Hintergrundthread.
        self.measurement_thread = threading.Thread(
# In Python speichert `=` hier einen Wert in `target`.
            target=self.measurement_loop,
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.recording:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.toggle_recording()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.measuring:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stop_measurement()
# In Python speichert `=` hier den booleschen Startwert aus in `monitoring`.
        self.monitoring = False
# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
        self.calibrating = False
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.disable_lock(update_status=False)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.stop_stage_correction()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.stop_calibration_stage_motion()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected and self.stage is not None and self.stage.is_moving:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
            self.stage.stop()
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
    # 5.6 READ STEP SIZE FROM THE UI
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Liest die Schrittweite.
    def get_step_size(self):
# Originalkommentar oder Abschnittsüberschrift.
        #convert the user input from the UI into something readable for the program
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `value`.
            value = self.parse_entry_float(self.step_entry)
# In Python speichert `=` hier einen Wert in `value`.
            value = abs(value)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if value <= 0:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                raise ValueError
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return value
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
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `value`.
            value = self.parse_entry_float(self.speed_entry)
# In Python speichert `=` hier einen Wert in `value`.
            value = abs(value)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if value <= 0:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                raise ValueError
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return value
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
    # 5.6.2 APPLY STAGE SPEED
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Übernimmt die Stage-Geschwindigkeit.
    def apply_stage_speed(self, update_status=True):
# In Python speichert `=` hier einen Wert in `speed_mm_s`.
        speed_mm_s = self.get_stage_speed()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if speed_mm_s is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# In Python wird mit `.` ein Eingabefeld geleert.
        self.speed_entry.delete(0, "end")
# In Python wird mit `.` Text in ein Eingabefeld geschrieben.
        self.speed_entry.insert(0, f"{speed_mm_s:.6f}")
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected or self.stage is None:
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.lock_active:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text="Stage-Bewegung blockiert: Lock ist aktiv.",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected or self.stage is None:
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_remaining_known:
# In Python speichert `=` hier einen Wert in `remaining_text`.
                remaining_text = f"{self.stage_remaining_to_drive:.6f} mm"
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `remaining_text`.
                remaining_text = "target unknown"
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Stage is already moving, still to drive {remaining_text}",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.apply_stage_speed(update_status=False)
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
        target_mm = self.stage.clamp_position(target_mm)
# In Python speichert `=` hier einen berechneten Wert in `move_mm`.
        move_mm = target_mm - start_pos
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `stage_start_position`. Startposition der Bewegung.
        self.stage_start_position = start_pos
# In Python speichert `=` einen Wert in `stage_movement_before_move`. Strecke vor der aktuellen Bewegung.
        self.stage_movement_before_move = self.total_stage_movement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.set_stage_target_position(target_mm, start_pos)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.reset_stage_speed_tracking(start_pos)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if abs(move_mm) < 1e-12:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.update_stage_labels(start_pos, 0.0, self.stage_movement_before_move)
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected or self.stage is None:
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
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_to(start_pos + move_mm, start_pos=start_pos)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 6.3 MOVE STAGE TO TARGET IN STEPS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt in kleinen Schritten zu einem Ziel.
    def start_stage_move_to_stepped(self, target_mm, step_mm=None, pause_s=STEP_PAUSE_S, label_prefix="Moving"):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.prepare_stage_for_move():
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
        start_pos = self.stage.get_position()
# In Python speichert `=` hier einen Wert in `target_mm`.
        target_mm = self.stage.clamp_position(target_mm) # clamps target distance by the maximum movement range of the stage
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

# In Python speichert `=` einen Wert in `stage_start_position`. Startposition der Bewegung.
        self.stage_start_position = start_pos
# In Python speichert `=` einen Wert in `stage_movement_before_move`. Strecke vor der aktuellen Bewegung.
        self.stage_movement_before_move = self.total_stage_movement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.set_stage_target_position(target_mm, start_pos)
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
            step_mm = abs(float(step_mm))
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
    def start_stage_move_by_steps(self, move_mm, step_mm=None, pause_s=STEP_PAUSE_S, label_prefix="Moving"):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected or self.stage is None:
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
    def stage_stepped_move_worker(self, start_pos, target_mm, step_mm, pause_s, label_prefix):
# In Python speichert `=` hier einen berechneten Wert in `step_sign`.
        step_sign = 1 if target_mm > start_pos else -1
# In Python speichert `=` hier einen Wert in `current_pos`.
        current_pos = start_pos
# In Python speichert `=` hier einen berechneten Wert in `remaining`.
        remaining = abs(target_mm - start_pos)
# In Python speichert `=` hier einen Wert in `moved`.
        moved = 0.0
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"{label_prefix} to {target_mm:.6f} mm in {step_mm:.9f} mm steps",
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
            next_step = min(step_mm, remaining)
# In Python speichert `=` hier einen berechneten Wert in `next_target`.
            next_target = current_pos + step_sign * next_step
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.stage.move_absolute(next_target):
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                self.root.after(
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
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                self.root.after(0, self.clear_stage_target_position)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
            while self.stage.is_moving:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                time.sleep(0.005 if pause_s <= 0 else 0.01)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `step_distance`.
            step_distance = abs(next_target - current_pos) # how far did this step move
# In Python speichert `=` hier einen Wert in `moved +`.
            moved += step_distance # add this value to step distance
# In Python speichert `=` hier einen Wert in `current_pos`.
            current_pos = next_target
# In Python speichert `=` hier einen berechneten Wert in `remaining`.
            remaining = abs(target_mm - current_pos)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen berechneten Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
            self.total_stage_movement = self.stage_movement_before_move + moved
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=current_pos, m=moved, b=self.stage_movement_before_move: # lambda=anonymous function because after expects a function that will be called later and not a function output
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

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
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
# Originalkommentar oder Abschnittsüberschrift.
        #how much did the stage move befor the current movement? use this as base
# In Python speichert `=` hier einen Wert in `movement_base`.
        movement_base = self.stage_movement_before_move
# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
        while self.stage.is_moving:
# In Python ruft `.` eine Methode auf, die die Position liest.
            pos = self.stage.get_position()
# In Python speichert `=` hier einen berechneten Wert in `moved`.
            moved = abs(pos - self.stage_start_position)
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=pos, m=moved, b=movement_base:
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
# In Python speichert `=` einen berechneten Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
        self.total_stage_movement = movement_base + moved
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
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
# In Python speichert `=` hier einen berechneten Wert in `moved`.
        moved = abs(pos - self.stage_start_position)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_stage_labels(pos, moved, self.stage_movement_before_move)
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.start_stage_move_to(self.stage.min_position)
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
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_by(-self.get_step_size())
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
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_to_stepped(0.0)
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
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_by(self.get_step_size())
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.start_stage_move_to(self.stage.max_position)
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
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `target_mm`.
            target_mm = self.parse_entry_float(self.target_entry)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if target_mm < 0:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                raise ValueError("Target position cannot be negative")
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
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_to(target_mm)
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
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python speichert `=` hier einen Wert in `distance_mm`.
            distance_mm = self.parse_entry_float(self.target_entry)
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
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.start_stage_move_by(distance_mm)
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
            self.stage.stop()
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Position liest.
            pos = self.stage.get_position()
# In Python speichert `=` einen Wert in `stage_position_mm`.
            self.stage_position_mm = pos
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
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Position liest.
                pos = self.stage.get_position()
# In Python speichert `=` einen Wert in `stage_position_mm`.
                self.stage_position_mm = pos
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
                elif self.stage_remaining_known and self.stage_remaining_to_drive <= 0:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                    self.label_stage_speed.configure(
# Anzeige der momentanen Geschwindigkeit.
                        text="Movement Speed: 0.000000 mm/s"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# `finally` läuft in Python immer, auch wenn vorher ein Fehler aufgetreten ist.
        finally:
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if movement_base is None:
# In Python speichert `=` hier einen Wert in `movement_base`.
            movement_base = self.total_stage_movement
# In Python speichert `=` hier einen berechneten Wert in `current_total_stage_movement`.
        current_total_stage_movement = movement_base + abs(moved)
# In Python speichert `=` einen Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
        self.total_stage_movement = max(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.total_stage_movement,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            current_total_stage_movement
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `current_stage_movement_for_compare`. aktuelle Vergleichsstrecke.
        self.current_stage_movement_for_compare = current_total_stage_movement
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
            text=f"Accumulated Movement: {current_total_stage_movement:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_still_to_drive_label(pos)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_stage_speed_label(pos)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_comparison_labels(current_total_stage_movement)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Speichert ein Ziel.
    def set_stage_target_position(self, target_mm, current_pos=None):
# In Python speichert `=` einen Wert in `stage_target_position`. aktuelle Zielposition.
        self.stage_target_position = target_mm
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if current_pos is None:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Position liest.
                current_pos = self.stage.get_position()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `current_pos`.
                current_pos = target_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_still_to_drive_label(current_pos)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Löscht das Ziel.
    def clear_stage_target_position(self):
# In Python speichert `=` hier erstmal keinen Wert in `stage_target_position`. aktuelle Zielposition.
        self.stage_target_position = None
# In Python speichert `=` einen Wert in `stage_remaining_to_drive`. Reststrecke bis zum Ziel.
        self.stage_remaining_to_drive = 0.0
# In Python speichert `=` hier den booleschen Startwert ein in `stage_remaining_known`. Merker, ob die Reststrecke bekannt ist.
        self.stage_remaining_known = True
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
# In Python speichert `=` hier einen Wert in `target_position`.
        target_position = self.get_active_stage_target_position()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if target_position is None:
# In Python speichert `=` einen Wert in `stage_remaining_to_drive`. Reststrecke bis zum Ziel.
            self.stage_remaining_to_drive = 0.0
# In Python speichert `=` einen Wert in `stage_remaining_known`. Merker, ob die Reststrecke bekannt ist.
            self.stage_remaining_known = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                not self.stage_connected
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                or self.stage is None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                or not self.stage.is_moving
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` hier den booleschen Startwert ein in `stage_remaining_known`. Merker, ob die Reststrecke bekannt ist.
            self.stage_remaining_known = True
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if pos is None:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Position liest.
                    pos = self.stage.get_position()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
                else:
# In Python speichert `=` hier einen Wert in `pos`.
                    pos = target_position
# In Python speichert `=` einen berechneten Wert in `stage_remaining_to_drive`. Reststrecke bis zum Ziel.
            self.stage_remaining_to_drive = abs(target_position - pos)
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
                label_text = f"Still to drive: {self.stage_remaining_to_drive:.6f} mm"
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `label_text`.
                label_text = "Still to drive: target unknown"
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_still_to_drive.configure(text=label_text)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Gibt das gespeicherte Ziel zurück.
    def get_active_stage_target_position(self):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_target_position is not None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return self.stage_target_position
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
# In Python speichert `=` hier einen Wert in `now`.
        now = time.time()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.last_stage_speed_time is None or self.last_stage_speed_position is None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.reset_stage_speed_tracking(pos)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `dt`.
        dt = now - self.last_stage_speed_time
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if dt <= 0:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `speed_mm_s`.
        speed_mm_s = abs(pos - self.last_stage_speed_position) / dt
# In Python speichert `=` einen Wert in `last_stage_speed_time`. Zeitbasis für die Geschwindigkeitsmessung.
        self.last_stage_speed_time = now
# In Python speichert `=` einen Wert in `last_stage_speed_position`. Positionsbasis für die Geschwindigkeitsmessung.
        self.last_stage_speed_position = pos
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
        elif self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Position liest.
            self.stage_reference_position = self.stage.get_position()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` einen Wert in `stage_reference_position`. Referenzposition für Berechnungen.
            self.stage_reference_position = 0.0
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_moved.configure(text="Accumulated Movement: 0.000000 mm")
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_speed.configure(text="Movement Speed: 0.000000 mm/s")
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.measuring or self.calibrating:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_compare_driven.configure(text="Driven: 0.000000 mm")
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_still_to_drive.configure(text="Still to drive: 0.000000 mm")
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_compare_calculated.configure(text="Calculated from Fringes: 0.000000 mm")
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_compare_difference.configure(text="Difference: 0.000000 mm", text_color=TEXT_COLOR)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if driven_mm is None:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage_connected and self.stage is not None:
# In Python speichert `=` hier einen Wert in `current_pos`.
                current_pos = self.stage.current_position
# In Python speichert `=` hier einen Wert in `start_pos`.
                start_pos = getattr(self, 'stage_measurement_start_position', current_pos)
# In Python speichert `=` hier einen berechneten Wert in `driven_mm`.
                driven_mm = abs(current_pos - start_pos)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` hier einen Wert in `driven_mm`.
                driven_mm = self.current_stage_movement_for_compare
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `driven_distance_mm`.
        driven_distance_mm = abs(driven_mm)
# In Python speichert `=` hier einen Wert in `calculated_mm`.
        calculated_mm = 0.0
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.monitor is not None and self.monitor.counter is not None:
# In Python speichert `=` hier einen Wert in `dist`.
            dist = self.monitor.counter.signed_distance_mm()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if dist is not None:
# In Python speichert `=` hier einen Wert in `calculated_mm`.
                calculated_mm = abs(dist)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `difference_mm`.
        difference_mm = driven_distance_mm - calculated_mm
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected or self.stage is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
        current_position = self.stage.get_position()
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
            self.set_stage_target_position(final_target, current_position)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.reset_stage_speed_tracking(current_position)
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                    text=f"Continuous move to {final_target:.6f} mm at {VELOCITY_MM_S} mm/s",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.stage.move_absolute(final_target):
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                self.root.after(
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
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                self.root.after(0, self.clear_stage_target_position)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
            while self.stage.is_moving and self.monitoring:
# In Python ruft `.` eine Methode auf, die die Position liest.
                pos = self.stage.get_position()
# In Python speichert `=` hier einen berechneten Wert in `moved`.
                moved = abs(pos - self.stage_start_position)
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                self.root.after(
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
# In Python speichert `=` einen berechneten Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
            self.total_stage_movement = self.stage_movement_before_move + moved
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=pos:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.finish_stage_move(p)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
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
            self.set_stage_target_position(stepped_target, current_position)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.reset_stage_speed_tracking(current_position)
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=f"Stepped move: {STEPS} steps of {STEP_SIZE_MM} mm",
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
                if not self.monitoring:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    break
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `next_position`.
                next_position = self.stage.clamp_position(current_pos + STEP_SIZE_MM)
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    0,
# In Python speichert `=` hier einen Wert in `lambda s`.
                    lambda s=step, n=next_position:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                    self.status.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                        text=f"Step {s + 1}/{STEPS}: move to {n:.7f} mm",
# In Python speichert `=` hier einen Wert in `text_color`.
                        text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if not self.stage.move_absolute(next_position):
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                    self.root.after(
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
                while self.stage.is_moving and self.monitoring:
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

# In Python speichert `=` einen berechneten Wert in `total_stage_movement`. gesamte bisher gefahrene Strecke.
                self.total_stage_movement = self.stage_movement_before_move + moved
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                self.root.after(
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

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
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
# In Python speichert `=` hier einen Startwert in `previous_velocity`.
        previous_velocity = None
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.stage_connected or self.stage is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
            start_pos = self.stage.get_position() # current stage position as movement start
# In Python speichert `=` hier einen berechneten Wert in `forward_target`.
            forward_target = self.stage.clamp_position(start_pos + CALIBRATION_STAGE_DISTANCE_MM)
# In Python speichert `=` hier einen Wert in `back_target`.
            back_target = self.stage.clamp_position(start_pos)
# In Python speichert `=` hier einen berechneten Wert in `sweep_distance_mm`.
            sweep_distance_mm = abs(forward_target - start_pos)
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

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                    text=f"Calibration sweep: {sweep_distance_mm:.5f} mm at {calibration_speed_mm_s:.6f} mm/s",
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
            while self.monitoring and self.calibrating:
# `for` startet in Python eine Schleife über mehrere Werte.
                for target in (forward_target, back_target):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if not self.monitoring or not self.calibrating:
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
                    while self.stage.is_moving and self.monitoring and self.calibrating:
# In Python ruft `.` eine Methode auf, die die Position liest.
                        current_pos = self.stage.get_position()
# In Python speichert `=` hier einen berechneten Wert in `moved`.
                        moved = accumulated_movement_mm + abs(current_pos - leg_start_pos)
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                        self.root.after(
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
                    if not self.monitoring or not self.calibrating:
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
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                    self.root.after(
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
            if self.stage_connected and self.stage is not None and self.stage.is_moving:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
                self.stage.stop()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if previous_velocity is not None and self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Geschwindigkeit setzt.
                self.stage.set_velocity(previous_velocity)
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die die Position liest.
            pos = self.stage.get_position()
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected or self.stage is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.clear_stage_target_position()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage.is_moving:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
            self.stage.stop()
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected and self.stage is not None and self.stage.is_moving:
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
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
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
            if self.stage_connected and self.stage is not None:
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if hasattr(self, "label_stage_position_lock"):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_stage_position_lock.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=f"Stage Position: {pos:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

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

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.set_buttons_enabled(True)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.monitoring:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: monitoring running",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: start_ui_loop
    def start_ui_loop(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(int(UI_UPDATE_INTERVAL_S * 1000), self.update_ui_loop)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: update_ui_loop
    def update_ui_loop(self):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.monitoring and not self.calibrating:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lissajous_direction.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="STILL",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.sample_display_lock:
# In Python speichert `=` hier einen Wert in `sample`.
            sample = self.latest_sample
# In Python speichert `=` hier einen Wert in `distance_mm`.
            distance_mm = self.latest_distance_mm
# In Python speichert `=` hier einen Wert in `s1_hist`.
            s1_hist = list(self.raw_s1_history)
# In Python speichert `=` hier einen Wert in `s2_hist`.
            s2_hist = list(self.raw_s2_history)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `single_fringes`.
            single_fringes = self.monitor.single_counter.accumulated_fringes
# In Python speichert `=` hier einen berechneten Wert in `single_distance`.
            single_distance = single_fringes * self.fringe_distance_mm
# In Python speichert `=` hier einen Wert in `single_amp`.
            single_amp = self.monitor.single_counter.fringe_amplitude_voltage
# In Python speichert `=` hier einen Wert in `s2_amp`.
            s2_amp = self.monitor.s2_visibility_counter.fringe_amplitude_voltage
# In Python speichert `=` hier einen Wert in `s1_rise`.
            s1_rise = self.monitor.single_counter.fringe_rise_threshold_voltage
# In Python speichert `=` hier einen Wert in `s2_rise`.
            s2_rise = self.monitor.s2_visibility_counter.fringe_rise_threshold_voltage
# In Python speichert `=` hier einen Wert in `s1_visible`.
            s1_visible = self.monitor.single_counter.fringes_visible
# In Python speichert `=` hier einen Wert in `s2_visible`.
            s2_visible = self.monitor.s2_visibility_counter.fringes_visible
# In Python speichert `=` hier einen Wert in `lissajous_ready`.
            lissajous_ready = self.monitor.counter.signals_visible()
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `calibrating`.
            calibrating = self.calibrating
# In Python speichert `=` hier einen Wert in `progress_text`.
            progress_text = getattr(self, 'calibration_progress_text', None)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if calibrating:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if progress_text:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(text=progress_text, text_color=ORANGE_COLOR)
# In Python ruft `.` eine eigene Methode auf.
            self.update_plot()
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
        elif sample is not None:
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_single_fringes.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"S1 Fringe Count: {single_fringes}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_single_distance.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"S1 Calculated Distance: {single_distance:+.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` hier einen Wert in `lissajous_text`.
            lissajous_text = "ready" if lissajous_ready else "blocked"
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_single_thresholds.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"S1 amp {single_amp:.6f} V, rise {s1_rise:.6f} V "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"({'visible' if s1_visible else 'not visible'}), "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"S2 amp {s2_amp:.6f} V, rise {s2_rise:.6f} V "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"({'visible' if s2_visible else 'not visible'}), "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    f"Lissajous {lissajous_text}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_phase.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"phase_rad = atan2(S2_norm, S1_norm) = {sample.phase_rad:+.5f} rad" if sample.valid else "phase_rad = invalid"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_s1_norm.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"S1_norm = (raw_S1 - offset_S1) / scale_S1 = {sample.s1:+.6f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_s2_norm.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"S2_norm = (raw_S2 - offset_S2) / scale_S2 = {sample.s2:+.6f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_unwrapped_phase.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"unwrapped_phase_rad += delta_phase_rad = {sample.unwrapped_phase_rad:+.5f} rad"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_fringe_position.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"fringe_position = unwrapped_phase_rad / (2*pi) = {sample.fringe_position:+.4f}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_fringes.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text=f"signed_fringes = {sample.signed_fringes:+d}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `dir_text`.
            dir_text = "Still"
# In Python speichert `=` hier einen Wert in `dir_color`.
            dir_color = ORANGE_COLOR
# In Python speichert `=` hier einen Wert in `lissajous_dir_text`.
            lissajous_dir_text = "STILL"
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if sample.direction == "forward":
# In Python speichert `=` hier einen Wert in `dir_text`.
                dir_text = "Forward →"
# In Python speichert `=` hier einen Wert in `dir_color`.
                dir_color = GREEN_COLOR
# In Python speichert `=` hier einen Wert in `lissajous_dir_text`.
                lissajous_dir_text = "FORWARD"
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
            elif sample.direction == "backward":
# In Python speichert `=` hier einen Wert in `dir_text`.
                dir_text = "Backward ←"
# In Python speichert `=` hier einen Wert in `dir_color`.
                dir_color = RED_COLOR
# In Python speichert `=` hier einen Wert in `lissajous_dir_text`.
                lissajous_dir_text = "BACKWARD"
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
            elif sample.direction == "signal_low":
# In Python speichert `=` hier einen Wert in `dir_text`.
                dir_text = "Signal Low"
# In Python speichert `=` hier einen Wert in `dir_color`.
                dir_color = RED_COLOR
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
            elif sample.direction == "fringes_not_visible":
# In Python speichert `=` hier einen Wert in `dir_text`.
                dir_text = "Fringes Not Visible"
# In Python speichert `=` hier einen Wert in `dir_color`.
                dir_color = RED_COLOR
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_direction.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Direction: {dir_text}",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=dir_color
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_lissajous_direction.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=lissajous_dir_text,
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=dir_color
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if distance_mm is None:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_distance.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                    text="distance_mm = fringe_position * fringe_distance_mm = n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_distance.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                    text=f"distance_mm = fringe_position * fringe_distance_mm = {distance_mm:+.9f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if sample.fringe_delta != 0:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_fringes.configure(text_color=GREEN_COLOR)
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    250,
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                    lambda: self.label_fringes.configure(text_color=TEXT_COLOR)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.update_lock_display(sample, distance_mm)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.lock_active:
# In Python speichert `=` hier einen Wert in `fringes_diff`.
                fringes_diff = sample.signed_fringes if sample is not None else 0
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_fringes_since_locking.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                    text=f"Fringes since locking: {fringes_diff:+d}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if self.stage_connected and self.stage is not None:
# In Python speichert `=` hier einen berechneten Wert in `diff_mm`.
                    diff_mm = self.stage_position_mm - self.lock_stage_position_mm
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                    self.label_correction_since_locking.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                        text=f"Correction since locking: {diff_mm:+.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
                else:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                    self.label_correction_since_locking.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                        text="Correction since locking: n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.update_comparison_labels()
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine eigene Methode auf.
            self.update_plot()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python ruft `.` eine eigene Methode auf.
            self.update_plot()
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(int(UI_UPDATE_INTERVAL_S * 1000), self.update_ui_loop)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: measurement_loop
    def measurement_loop(self):
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python baut `connect()` die Verbindung zur Hardware auf.
            self.monitor.connect()
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                lambda:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text="Status: monitoring running",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(0, self.start_ui_loop)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `calibration_samples`.
            calibration_samples = []
# In Python speichert `=` hier einen Startwert in `calibration_start_time`.
            calibration_start_time = None
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
            while self.monitoring:
# In Python speichert `=` hier einen Wert in `raw_s1, raw_s2`.
                raw_s1, raw_s2 = self.monitor.reader.read()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if not self.baseline_recorded:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.baseline_samples.append((raw_s1, raw_s2))
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                    self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        0,
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                        lambda: self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                            text="Status: recording baseline noise...",
# In Python speichert `=` hier einen Wert in `text_color`.
                            text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if len(self.baseline_samples) >= 200:
# In Python speichert `=` einen berechneten Wert in `baseline_s1`.
                        self.baseline_s1 = sum(s[0] for s in self.baseline_samples) / len(self.baseline_samples)
# In Python speichert `=` einen berechneten Wert in `baseline_s2`.
                        self.baseline_s2 = sum(s[1] for s in self.baseline_samples) / len(self.baseline_samples)
# In Python speichert `=` hier den booleschen Startwert ein in `baseline_recorded`. Merker, ob die Baseline schon gemessen wurde.
                        self.baseline_recorded = True
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                        self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            0,
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                            lambda: self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                                text="Status: monitoring running",
# In Python speichert `=` hier einen Wert in `text_color`.
                                text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `clean_s1`.
                clean_s1 = raw_s1 - self.baseline_s1
# In Python speichert `=` hier einen berechneten Wert in `clean_s2`.
                clean_s2 = raw_s2 - self.baseline_s2
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `alpha`.
                alpha = 0.3
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if not hasattr(self, 'lp_clean_s1'):
# In Python speichert `=` einen Wert in `lp_clean_s1`.
                    self.lp_clean_s1 = clean_s1
# In Python speichert `=` einen Wert in `lp_clean_s2`.
                    self.lp_clean_s2 = clean_s2
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
                else:
# In Python speichert `=` einen berechneten Wert in `lp_clean_s1`.
                    self.lp_clean_s1 = alpha * clean_s1 + (1.0 - alpha) * self.lp_clean_s1
# In Python speichert `=` einen berechneten Wert in `lp_clean_s2`.
                    self.lp_clean_s2 = alpha * clean_s2 + (1.0 - alpha) * self.lp_clean_s2
# Leerzeile zur besseren Lesbarkeit.

# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
                with self.sample_display_lock:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.raw_s1_history.append(raw_s1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.raw_s2_history.append(raw_s2)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.clean_s1_history.append(self.lp_clean_s1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.clean_s2_history.append(self.lp_clean_s2)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if self.measuring or self.lock_active:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                    if self.calibrating:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                        if calibration_start_time is None:
# Originalkommentar oder Abschnittsüberschrift.
                            # No extra stage motion for calibration
# In Python speichert `=` hier einen Wert in `calibration_start_time`.
                            calibration_start_time = time.time()
# In Python speichert `=` hier einen Startwert in `calibration_samples`.
                            calibration_samples = []
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                                0,
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                                lambda: self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                                    text=f"Status: calibrating {CALIBRATION_SECONDS:.1f}s...",
# In Python speichert `=` hier einen Wert in `text_color`.
                                    text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        calibration_samples.append((clean_s1, clean_s2))
# In Python speichert `=` hier einen berechneten Wert in `elapsed_s`.
                        elapsed_s = time.time() - calibration_start_time
# Leerzeile zur besseren Lesbarkeit.
                        
# Originalkommentar oder Abschnittsüberschrift.
                        # Set progress text without double-appending raw history
# In Python speichert `=` einen berechneten Wert in `calibration_progress_text`.
                        self.calibration_progress_text = f"Status: calibrating {elapsed_s:.1f}/{CALIBRATION_SECONDS:.1f}s..."
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                        if elapsed_s >= CALIBRATION_SECONDS:
# Originalkommentar oder Abschnittsüberschrift.
                            # Calibrate the counter from the collected samples
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            self.monitor.counter.calibrate_from_samples(calibration_samples)
# In Python speichert `=` hier einen Wert in `s1_vals`.
                            s1_vals = [s[0] for s in calibration_samples]
# In Python speichert `=` hier einen Wert in `s2_vals`.
                            s2_vals = [s[1] for s in calibration_samples]
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            self.monitor.single_counter.calibrate(s1_vals)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            self.monitor.s2_visibility_counter.calibrate(s2_vals)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            self.monitor.counter.set_signal_visibility(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                                self.monitor.single_counter.fringes_visible,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                                self.monitor.s2_visibility_counter.fringes_visible
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            )
# Leerzeile zur besseren Lesbarkeit.
                            
# Originalkommentar oder Abschnittsüberschrift.
                            # Reset fringe counts to 0 starting from the end of calibration
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            self.monitor.single_counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            self.monitor.s2_visibility_counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            self.monitor.counter.reset()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
                            # Record stage reference position at the start of measurement
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                            if self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Position liest.
                                self.stage_measurement_start_position = self.stage.get_position()
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
                            self.calibrating = False
# In Python speichert `=` hier einen Startwert in `calibration_start_time`.
                            calibration_start_time = None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            self.stop_calibration_stage_motion()
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
                            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                                0,
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
                                lambda: self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                                    text="Status: measurement running",
# In Python speichert `=` hier einen Wert in `text_color`.
                                    text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            )
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
                    else:
# Originalkommentar oder Abschnittsüberschrift.
                        # Calibration is complete, do normal fringe counting
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        self.monitor.single_counter.update(self.lp_clean_s1)
# In Python speichert `=` hier einen Wert in `sample`.
                        sample = self.monitor.counter.update(self.lp_clean_s1, self.lp_clean_s2)
# In Python speichert `=` hier einen Wert in `distance_mm`.
                        distance_mm = self.monitor.counter.signed_distance_mm()
# Leerzeile zur besseren Lesbarkeit.

# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
                        with self.sample_display_lock:
# In Python speichert `=` einen Wert in `latest_sample`. letzte Messprobe.
                            self.latest_sample = sample
# In Python speichert `=` einen Wert in `latest_distance_mm`.
                            self.latest_distance_mm = distance_mm
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if self.recording:
# In Python speichert `=` hier einen berechneten Wert in `elapsed`.
                    elapsed = time.time() - self.recording_start_time
# Originalkommentar oder Abschnittsüberschrift.
                    # Non-blocking read of the last queried stage position
# In Python speichert `=` hier einen Wert in `stage_pos`.
                    stage_pos = self.stage.current_position if (self.stage_connected and self.stage is not None) else 0.0
# In Python speichert `=` hier einen Wert in `s_obj`.
                    s_obj = sample if ('sample' in locals() and sample is not None) else None
# In Python speichert `=` hier einen Wert in `cur_single_fringes`.
                    cur_single_fringes = self.monitor.single_counter.accumulated_fringes if self.monitor else 0
# In Python speichert `=` hier einen berechneten Wert in `cur_single_distance`.
                    cur_single_distance = cur_single_fringes * self.fringe_distance_mm
# In Python speichert `=` hier einen Wert in `cur_phase_distance`.
                    cur_phase_distance = distance_mm if ('distance_mm' in locals() and distance_mm is not None) else 0.0
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.recorded_data.append((
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        elapsed,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        raw_s1,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        raw_s2,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        s_obj.s1 if s_obj else 0.0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        s_obj.s2 if s_obj else 0.0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        s_obj.phase_rad if s_obj else 0.0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        s_obj.unwrapped_phase_rad if s_obj else 0.0,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        cur_phase_distance,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        cur_single_distance,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        cur_single_fringes,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        stage_pos
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    ))
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                time.sleep(SAMPLE_INTERVAL_S)
# Leerzeile zur besseren Lesbarkeit.

# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except Exception as error:
# In Python speichert `=` einen Wert in `last_error_text`. letzte Fehlermeldung.
            self.last_error_text = str(error)
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
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
# In Python speichert `=` hier den booleschen Startwert aus in `monitoring`.
            self.monitoring = False
# In Python speichert `=` hier den booleschen Startwert aus in `calibrating`. Merker, ob gerade die Kalibrierung läuft.
            self.calibrating = False
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stop_calibration_stage_motion()
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
            try:
# In Python schließt `close()` eine geöffnete Verbindung wieder.
                self.monitor.close()
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
            except Exception:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                pass
# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(0, self.finish_stopped_ui)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # 7.8 HANDLE CALIBRATION SAMPLE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Gibt einen Kalibrierungswert an die Anzeige weiter.
    def handle_calibration_sample(self, raw_sample, elapsed_s, total_s):
# In Python speichert `=` hier einen Wert in `raw_s1, raw_s2`.
        raw_s1, raw_s2 = raw_sample
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.sample_display_lock:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.calibration_raw_samples.append(raw_sample)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.raw_s1_history.append(raw_s1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.raw_s2_history.append(raw_s2)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if len(self.raw_s1_history) > 300:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.raw_s1_history.pop(0)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.raw_s2_history.pop(0)
# In Python speichert `=` einen berechneten Wert in `calibration_progress_text`.
            self.calibration_progress_text = f"Status: calibrating {elapsed_s:.1f}/{total_s:.1f}s..."
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: reset_calculation_display
    def reset_calculation_display(self):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_single_fringes.configure(text="S1 Fringe Count: 0")
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_single_distance.configure(text="S1 Calculated Distance: 0.000000 mm")
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_single_thresholds.configure(text="Signal amplitudes: S1 = n/a, S2 = n/a")
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_phase.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="phase_rad = atan2(S2_norm, S1_norm) = n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_s1_norm.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="S1_norm = (raw_S1 - offset_S1) / scale_S1 = n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_s2_norm.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="S2_norm = (raw_S2 - offset_S2) / scale_S2 = n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_unwrapped_phase.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="unwrapped_phase_rad += delta_phase_rad = 0.00000 rad"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_fringe_position.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="fringe_position = unwrapped_phase_rad / (2*pi) = 0.0000"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_fringes.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="signed_fringes = 0"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_direction.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Direction: Still"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lissajous_direction.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="STILL",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_distance.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="distance_mm = fringe_position * fringe_distance_mm = n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: toggle_lock
    def toggle_lock(self):
# Originalkommentar oder Abschnittsüberschrift.
        #get all errors
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.lock_active:
# Originalkommentar oder Abschnittsüberschrift.
            #refuse manual step movement because lock is active
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.disable_lock()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.monitoring:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: start monitoring before lock",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stage_command_active
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            or self.lock_correction_active
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            or (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.stage is not None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                and self.stage_connected
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                and self.stage.is_moving
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ):
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: wait for stage movement before lock",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: stage not connected, cannot lock",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Check if we have a calibrated fringe amplitude
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.monitor is not None and self.monitor.single_counter is not None:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if not self.monitor.single_counter.fringes_visible:
# Originalkommentar oder Abschnittsüberschrift.
                # Prompt the user for the default fringe amplitude (V)
# In Python speichert `=` hier einen Wert in `val`.
                val = sd.askfloat(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    "Default Fringe Amplitude",
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    "No calibrated fringe value found.\n\nPlease enter the default fringe amplitude in Volts (e.g. 0.010):",
# In Python speichert `=` hier einen Wert in `parent`.
                    parent=self.root,
# In Python speichert `=` hier einen Wert in `initialvalue`.
                    initialvalue=0.010,
# In Python speichert `=` hier einen Wert in `minvalue`.
                    minvalue=0.0001,
# In Python speichert `=` hier einen Wert in `maxvalue`.
                    maxvalue=2.0
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if val is None:
# Originalkommentar oder Abschnittsüberschrift.
                    # User cancelled the dialog, abort locking
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                    return
# Leerzeile zur besseren Lesbarkeit.
                
# Originalkommentar oder Abschnittsüberschrift.
                # Configure counters with this default value
# In Python speichert `=` einen Wert in `monitor.single_counter.fringe_amplitude_voltage`.
                self.monitor.single_counter.fringe_amplitude_voltage = val
# In Python speichert `=` hier den booleschen Startwert ein in `monitor.single_counter.fringes_visible`.
                self.monitor.single_counter.fringes_visible = True
# Leerzeile zur besseren Lesbarkeit.
                
# In Python speichert `=` einen Wert in `monitor.s2_visibility_counter.fringe_amplitude_voltage`.
                self.monitor.s2_visibility_counter.fringe_amplitude_voltage = val
# In Python speichert `=` hier den booleschen Startwert ein in `monitor.s2_visibility_counter.fringes_visible`.
                self.monitor.s2_visibility_counter.fringes_visible = True
# Leerzeile zur besseren Lesbarkeit.
                
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.monitor.counter.set_signal_visibility(True, True)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
            # In all cases (either reusing the last calibration or setting the default value),
# Originalkommentar oder Abschnittsüberschrift.
            # enforce the strict 98% rise/rearm thresholds:
# In Python speichert `=` hier einen Wert in `amp`.
            amp = self.monitor.single_counter.fringe_amplitude_voltage
# In Python speichert `=` einen berechneten Wert in `monitor.single_counter.fringe_rise_threshold_voltage`.
            self.monitor.single_counter.fringe_rise_threshold_voltage = amp * 0.98
# In Python speichert `=` einen berechneten Wert in `monitor.single_counter.fringe_rearm_threshold_voltage`.
            self.monitor.single_counter.fringe_rearm_threshold_voltage = amp * 0.98
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `amp_s2`.
            amp_s2 = self.monitor.s2_visibility_counter.fringe_amplitude_voltage
# In Python speichert `=` einen berechneten Wert in `monitor.s2_visibility_counter.fringe_rise_threshold_voltage`.
            self.monitor.s2_visibility_counter.fringe_rise_threshold_voltage = amp_s2 * 0.98
# In Python speichert `=` einen berechneten Wert in `monitor.s2_visibility_counter.fringe_rearm_threshold_voltage`.
            self.monitor.s2_visibility_counter.fringe_rearm_threshold_voltage = amp_s2 * 0.98
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Keep stage stationary
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
            self.stage.stop()
# In Python ruft `.` eine Methode auf, die die Position liest.
            self.lock_stage_position_mm = self.stage.get_position()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` einen Wert in `lock_stage_position_mm`.
            self.lock_stage_position_mm = 0.0
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Reset counters so locking starts at exactly 0
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.monitor is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.monitor.counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.monitor.single_counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.monitor.s2_visibility_counter.reset()
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den booleschen Startwert ein in `lock_active`.
        self.lock_active = True
# In Python speichert `=` einen Wert in `lock_reference_distance_mm`.
        self.lock_reference_distance_mm = 0.0
# In Python speichert `=` einen Wert in `lock_reference_phase_rad`.
        self.lock_reference_phase_rad = 0.0
# In Python speichert `=` einen Wert in `lock_reference_fringes`.
        self.lock_reference_fringes = 0
# In Python speichert `=` hier erstmal keinen Wert in `latest_sample`. letzte Messprobe.
        self.latest_sample = None
# In Python speichert `=` einen Wert in `latest_distance_mm`.
        self.latest_distance_mm = 0.0
# In Python speichert `=` einen Wert in `lock_ref_single_fringes`.
        self.lock_ref_single_fringes = 0
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
        self.btn_lock.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="UNLOCK",
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'btn_lock_box'):
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
            self.btn_lock_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="UNLOCK",
# In Python speichert `=` hier einen Wert in `fg_color`.
                fg_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'label_lock_status_box'):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Lock Status: active",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Lock: on",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
        self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Status: locked",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    #return everything to unlock state
# `def` definiert in Python eine Funktion oder Methode. Hier: disable_lock
    def disable_lock(self, update_status=True):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.stop_stage_correction()
# In Python speichert `=` einen Wert in `lock_active`.
        self.lock_active = False # disable position lock
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
        self.btn_lock.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="LOCK",
# In Python speichert `=` hier einen Wert in `fg_color`.
            fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'btn_lock_box'):
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
            self.btn_lock_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="LOCK",
# In Python speichert `=` hier einen Wert in `fg_color`.
                fg_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Lock Status: off",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_fringes_since_locking.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text="Fringes since locking: n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_correction_since_locking.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
                text="Correction since locking: n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Lock: off",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_reference.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="Reference: n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_drift.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="Drift: n/a"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_correction.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text="Correction to lock: n/a",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if update_status:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: lock off",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: update_lock_display
    def update_lock_display(self, sample, distance_mm):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.lock_active or distance_mm is None or sample is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `drift_mm`.
        drift_mm = distance_mm - self.lock_reference_distance_mm
# In Python speichert `=` hier einen berechneten Wert in `correction_mm`.
        correction_mm = -STAGE_CORRECTION_SIGN * drift_mm
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_reference.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"Reference: "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{self.lock_reference_distance_mm:+.9f} mm, "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"{self.lock_reference_fringes:+d} fringes"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_drift.configure(
# In Python speichert `=` hier einen berechneten Wert in `text`.
            text=f"Drift: {drift_mm:+.9f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_correction.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"Correction to lock: {correction_mm:+.9f} mm "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                f"(next step {correction_mm:+.9f} mm)"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ),
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=ORANGE_COLOR if abs(drift_mm) > 0 else GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.maybe_start_lock_correction(drift_mm, correction_mm, sample)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    #extremely small drift is ignored
# `def` definiert in Python eine Funktion oder Methode. Hier: lock_deadband_mm
    def lock_deadband_mm(self):
# In Python speichert `=` hier einen Wert in `fringe_distance_mm`.
        fringe_distance_mm = self.monitor.counter.fringe_distance_mm
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if fringe_distance_mm is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return 1e-7
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return max(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            abs(fringe_distance_mm) * LOCK_TRIGGER_FRINGES,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            1e-7
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: maybe_start_lock_correction
    def maybe_start_lock_correction(self, drift_mm, correction_mm, sample):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.lock_active:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage_connected or self.stage is None:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_stage_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Stage: not connected, cannot correct lock",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if sample is None or sample.signed_fringes == 0:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if hasattr(self, 'label_lock_status_box'):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text="Lock Status: active",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `fringe_distance_mm`.
        fringe_distance_mm = self.monitor.counter.fringe_distance_mm
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if fringe_distance_mm is None:
# In Python speichert `=` hier einen Wert in `fringe_distance_mm`.
            fringe_distance_mm = 0.000316
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `fringes_str`.
        fringes_str = f"+{sample.signed_fringes}" if sample.signed_fringes > 0 else f"{sample.signed_fringes}"
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # 1. Check if deviation is below threshold
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if abs(sample.signed_fringes) < LOCK_TRIGGER_FRINGES:
# In Python speichert `=` hier einen Wert in `msg`.
            msg = f"{fringes_str} fringe, but below threshold so didnt count"
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if hasattr(self, 'label_lock_status_box'):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=f"Lock Status: {msg}",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # 2. Check invalid direction
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if sample.direction not in ["forward", "backward"]:
# In Python speichert `=` hier einen Wert in `msg`.
            msg = f"{fringes_str} fringe but still, so no correction"
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_lock_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Lock: {msg}",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if hasattr(self, 'label_lock_status_box'):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=f"Lock Status: {msg}",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # 3. Check busy state
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.lock_correction_active
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            or self.stage_command_active
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            or self.stage.is_moving
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ):
# In Python speichert `=` hier einen Wert in `msg`.
            msg = f"{fringes_str} fringe but still, so no correction"
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if hasattr(self, 'label_lock_status_box'):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=f"Lock Status: {msg}",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # 4. Check cooldown
# In Python speichert `=` hier einen Wert in `now`.
        now = time.time()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if now - self.lock_last_correction_time < LOCK_CORRECTION_COOLDOWN_S:
# In Python speichert `=` hier einen Wert in `msg`.
            msg = f"{fringes_str} fringe but still, so no correction"
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if hasattr(self, 'label_lock_status_box'):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=f"Lock Status: {msg}",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Determine the corrective step (opposite to the drift to apply true negative feedback)
# Originalkommentar oder Abschnittsüberschrift.
        # Drift (+) -> correction (-)
# Originalkommentar oder Abschnittsüberschrift.
        # Drift (-) -> correction (+)
# In Python speichert `=` hier einen berechneten Wert in `correction_step_mm`.
        correction_step_mm = - (sample.signed_fringes * fringe_distance_mm)
# Leerzeile zur besseren Lesbarkeit.
        
# Originalkommentar oder Abschnittsüberschrift.
        # Clamp the correction step to a maximum of 2 fringes (0.0008 mm) from the lock position
# In Python speichert `=` hier einen Wert in `max_lock_deviation_mm`.
        max_lock_deviation_mm = 0.0008
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if correction_step_mm > max_lock_deviation_mm:
# In Python speichert `=` hier einen Wert in `correction_step_mm`.
            correction_step_mm = max_lock_deviation_mm
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
        elif correction_step_mm < -max_lock_deviation_mm:
# In Python speichert `=` hier einen berechneten Wert in `correction_step_mm`.
            correction_step_mm = -max_lock_deviation_mm
# Leerzeile zur besseren Lesbarkeit.
        
# Originalkommentar oder Abschnittsüberschrift.
        # Calculate target relative to the saved lock position reference (not current_position_mm)
# In Python speichert `=` hier einen Wert in `target_position_mm`.
        target_position_mm = self.stage.clamp_position(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.lock_stage_position_mm + correction_step_mm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die die Position liest.
        current_position_mm = self.stage.get_position()
# In Python speichert `=` hier einen berechneten Wert in `actual_correction_mm`.
        actual_correction_mm = target_position_mm - current_position_mm
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if abs(actual_correction_mm) < 1e-12:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_lock_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Lock: correction blocked by stage limit",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if hasattr(self, 'label_lock_status_box'):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text="Lock Status: blocked by limit",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den booleschen Startwert ein in `lock_correction_active`.
        self.lock_correction_active = True
# In Python speichert `=` einen Wert in `lock_target_position_mm`.
        self.lock_target_position_mm = target_position_mm
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.stage.move_absolute(target_position_mm):
# In Python speichert `=` hier den booleschen Startwert aus in `lock_correction_active`.
            self.lock_correction_active = False
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_lock_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Lock: stage correction failed",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if hasattr(self, 'label_lock_status_box'):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text="Lock Status: correction failed",
# In Python speichert `=` hier einen Wert in `text_color`.
                    text_color=RED_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Success message format: "+1 fringe corrected by -0.000316 mm"
# In Python speichert `=` hier einen berechneten Wert in `msg`.
        msg = f"{fringes_str} fringe corrected by {correction_step_mm:+.6f} mm"
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Lock: {msg}",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'label_lock_status_box'):
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_lock_status_box.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Lock Status: {msg}",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Stage: lock correction running",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=ORANGE_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_position.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text=f"Stage target: {target_position_mm:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `Thread(...)` einen Hintergrundthread.
        threading.Thread(
# In Python speichert `=` hier einen Wert in `target`.
            target=self.lock_correction_worker,
# In Python speichert `=` hier einen Startwert in `daemon`.
            daemon=True
# In Python startet `start()` einen bereits erzeugten Thread.
        ).start()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Überwacht die Lock-Korrektur.
    def lock_correction_worker(self):
# `while` startet in Python eine Schleife, die so lange läuft, wie die Bedingung wahr ist.
        while (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.lock_correction_active
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            and self.stage is not None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            and self.stage.is_moving
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ):
# In Python speichert `=` hier einen Wert in `position_mm`.
            position_mm = self.stage.current_position
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
            self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                0,
# In Python speichert `=` hier einen Wert in `lambda p`.
                lambda p=position_mm:
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
                self.label_stage_position.configure(
# In Python speichert `=` hier einen Wert in `text`.
                    text=f"Stage position: {p:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            time.sleep(0.05)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `position_mm`.
        position_mm = None
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.stage is not None and self.stage_connected:
# In Python ruft `.` eine Methode auf, die die Position liest.
            position_mm = self.stage.get_position()
# Leerzeile zur besseren Lesbarkeit.

# In Python plant `after(...)` eine spätere Ausführung im GUI-Loop, damit das Fenster nicht einfriert.
        self.root.after(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            0,
# In Python speichert `=` hier einen Wert in `lambda p`.
            lambda p=position_mm:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.finish_lock_correction(p)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Beendet die Lock-Korrektur.
    def finish_lock_correction(self, position_mm):
# In Python speichert `=` hier den booleschen Startwert aus in `lock_correction_active`.
        self.lock_correction_active = False
# In Python speichert `=` den aktuellen Zeitstempel in `lock_last_correction_time`.
        self.lock_last_correction_time = time.time()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if position_mm is not None:
# In Python speichert `=` einen Wert in `stage_position_mm`.
            self.stage_position_mm = position_mm
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
            self.label_stage_position.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text=f"Stage position: {position_mm:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.lock_active:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Reset counters to clear any transient/aliased counts during the movement
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.monitor is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.monitor.counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.monitor.single_counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.monitor.s2_visibility_counter.reset()
# Leerzeile zur besseren Lesbarkeit.

# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_stage_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Stage: connected",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_status.configure(
# In Python speichert `=` hier einen Wert in `text`.
            text="Lock: correction done",
# In Python speichert `=` hier einen Wert in `text_color`.
            text_color=GREEN_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Bricht die Lock-Korrektur ab.
    def stop_stage_correction(self):
# In Python speichert `=` hier einen Wert in `was_correcting`.
        was_correcting = self.lock_correction_active
# In Python speichert `=` hier den booleschen Startwert aus in `lock_correction_active`.
        self.lock_correction_active = False
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if was_correcting and self.stage_connected and self.stage is not None:
# In Python ruft `.` eine Methode auf, die die Bewegung stoppt.
            self.stage.stop()
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.recording:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.toggle_recording()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.measuring:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.stop_measurement()
# In Python ruft `.` eine Methode auf, die das UI-Element anpasst.
        self.btn_start.configure(
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
# Leerzeile zur besseren Lesbarkeit.

# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
        elif not self.lock_active:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: stopped",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt den Monitor zurück.
    def reset_monitor(self):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.monitor.counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.monitor.single_counter.reset()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.monitor.s2_visibility_counter.reset()
# In Python speichert `=` hier erstmal keinen Wert in `latest_sample`. letzte Messprobe.
        self.latest_sample = None
# In Python speichert `=` hier erstmal keinen Wert in `latest_distance_mm`.
        self.latest_distance_mm = None
# In Python speichert `=` hier eine leere Liste in `raw_s1_history`.
        self.raw_s1_history = []
# In Python speichert `=` hier eine leere Liste in `raw_s2_history`.
        self.raw_s2_history = []
# In Python speichert `=` hier eine leere Liste in `clean_s1_history`.
        self.clean_s1_history = []
# In Python speichert `=` hier eine leere Liste in `clean_s2_history`.
        self.clean_s2_history = []
# In Python speichert `=` hier eine leere Liste in `baseline_samples`.
        self.baseline_samples = []
# In Python speichert `=` einen Wert in `baseline_s1`.
        self.baseline_s1 = 0.0
# In Python speichert `=` einen Wert in `baseline_s2`.
        self.baseline_s2 = 0.0
# In Python speichert `=` hier den booleschen Startwert aus in `baseline_recorded`. Merker, ob die Baseline schon gemessen wurde.
        self.baseline_recorded = False
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'lp_clean_s1'):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            del self.lp_clean_s1
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if hasattr(self, 'lp_clean_s2'):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            del self.lp_clean_s2
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.sample_display_lock:
# In Python speichert `=` hier erstmal keinen Wert in `pending_sample`.
            self.pending_sample = None
# In Python speichert `=` hier erstmal keinen Wert in `pending_distance_mm`.
            self.pending_distance_mm = None
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.reset_calculation_display()
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_status.configure(text="Lock: off", text_color=TEXT_COLOR)
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_reference.configure(text="Reference: n/a")
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_drift.configure(text="Drift: n/a")
# In Python ruft `.` eine Methode auf, die ein Label aktualisiert.
        self.label_lock_correction.configure(text="Correction to lock: n/a", text_color=TEXT_COLOR)
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.disable_lock(update_status=False)
# In Python ruft `.` eine eigene Methode auf.
        self.update_plot(reset=True)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not self.monitoring:
# In Python ruft `.` eine Methode auf, die den Text der Statusanzeige ändert.
            self.status.configure(
# In Python speichert `=` hier einen Wert in `text`.
                text="Status: reset",
# In Python speichert `=` hier einen Wert in `text_color`.
                text_color=TEXT_COLOR
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
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
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.plot_axes is None or self.axis_circle is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if reset:
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S1_raw'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S2_raw'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S1_raw_clean'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S2_raw_clean'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S1_raw_fit'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S2_raw_fit'].set_data([], [])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S1_raw_fit'].set_visible(False)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S2_raw_fit'].set_visible(False)
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_trace'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_current'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_pointer'].set_data([], [])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_quiver.set_visible(False)
# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
            self.plot_canvas.draw_idle()
# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
            self.plot_canvas_circle.draw_idle()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.sample_display_lock:
# In Python speichert `=` hier einen Wert in `s1_hist`.
            s1_hist = list(self.raw_s1_history)
# In Python speichert `=` hier einen Wert in `s2_hist`.
            s2_hist = list(self.raw_s2_history)
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.update_plot_data(s1_hist, s2_hist)
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
            self.plot_lines['S1_raw'].set_alpha(0.3)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S2_raw'].set_alpha(0.3)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S1_raw_clean'].set_visible(True)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S2_raw_clean'].set_visible(True)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# Umschalter für geglättete Daten.
            self.btn_toggle_clean.configure(text="Cleaned Signal: OFF", fg_color="#555555")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S1_raw'].set_alpha(1.0)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S2_raw'].set_alpha(1.0)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S1_raw_clean'].set_visible(False)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S2_raw_clean'].set_visible(False)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axes['S1_raw'].legend(loc="upper right", prop={"size": 8})
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axes['S2_raw'].legend(loc="upper right", prop={"size": 8})
# In Python ruft `.` eine eigene Methode auf.
        self.update_plot()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: update_plot_data
    def update_plot_data(self, s1_hist, s2_hist):
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.plot_axes is None or self.axis_circle is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen berechneten Wert in `window_start`.
        window_start = max(0, len(s1_hist) - PLOT_SAMPLE_WINDOW)
# In Python speichert `=` hier einen Wert in `s1_hist`.
        s1_hist = s1_hist[window_start:]
# In Python speichert `=` hier einen Wert in `s2_hist`.
        s2_hist = s2_hist[window_start:]
# In Python speichert `=` hier einen Wert in `x`.
        x = list(range(len(s1_hist)))
# Leerzeile zur besseren Lesbarkeit.

# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
        self.plot_lines['S1_raw'].set_data(x, s1_hist)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.show_cleaned and len(self.clean_s1_history) == len(x):
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S1_raw_clean'].set_data(x, self.clean_s1_history)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S1_raw_clean'].set_data([], [])
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axes['S1_raw'].relim()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axes['S1_raw'].autoscale_view()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if x:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_axes['S1_raw'].set_xlim(0, max(PLOT_SAMPLE_WINDOW - 1, len(x) - 1))
# Leerzeile zur besseren Lesbarkeit.

# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
        self.plot_lines['S2_raw'].set_data(x, s2_hist)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if self.show_cleaned and len(self.clean_s2_history) == len(x):
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S2_raw_clean'].set_data(x, self.clean_s2_history)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S2_raw_clean'].set_data([], [])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axes['S2_raw'].relim()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_axes['S2_raw'].autoscale_view()
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if x:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_axes['S2_raw'].set_xlim(0, max(PLOT_SAMPLE_WINDOW - 1, len(x) - 1))
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not (self.measuring or self.lock_active):
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_trace'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_current'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_pointer'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S1_raw_fit'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S2_raw_fit'].set_data([], [])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S1_raw_fit'].set_visible(False)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S2_raw_fit'].set_visible(False)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_quiver.set_visible(False)
# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
            self.plot_canvas.draw_idle()
# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
            self.plot_canvas_circle.draw_idle()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Startwert in `s1_norm_history`.
        s1_norm_history = []
# In Python speichert `=` hier einen Startwert in `s2_norm_history`.
        s2_norm_history = []
# `with` öffnet in Python einen Kontext, der Ressourcen danach automatisch sauber schließt.
        with self.monitor.counter.lock:
# In Python speichert `=` hier einen Wert in `offset_s1`.
            offset_s1 = self.monitor.counter.offset_s1
# In Python speichert `=` hier einen Wert in `scale_s1`.
            scale_s1 = self.monitor.counter.scale_s1
# In Python speichert `=` hier einen Wert in `offset_s2`.
            offset_s2 = self.monitor.counter.offset_s2
# In Python speichert `=` hier einen Wert in `scale_s2`.
            scale_s2 = self.monitor.counter.scale_s2
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # If offsets/scales are default/zero, estimate them dynamically from current history
# Originalkommentar oder Abschnittsüberschrift.
        # so that the fit line is drawn exactly at the height of the raw signal
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if offset_s1 == 0.0 or scale_s1 == 1.0:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if s1_hist:
# In Python speichert `=` hier einen berechneten Wert in `offset_s1`.
                offset_s1 = sum(s1_hist) / len(s1_hist)
# In Python speichert `=` hier einen Wert in `mean_s1`.
                mean_s1 = offset_s1
# In Python speichert `=` hier einen berechneten Wert in `var_s1`.
                var_s1 = sum((r - mean_s1)**2 for r in s1_hist) / len(s1_hist)
# In Python speichert `=` hier einen Wert in `std_s1`.
                std_s1 = math.sqrt(var_s1)
# In Python speichert `=` hier einen berechneten Wert in `scale_s1`.
                scale_s1 = std_s1 * 1.414
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if scale_s1 < 0.01:
# In Python speichert `=` hier einen Wert in `scale_s1`.
                    scale_s1 = 0.1
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if offset_s2 == 0.0 or scale_s2 == 1.0:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if s2_hist:
# In Python speichert `=` hier einen berechneten Wert in `offset_s2`.
                offset_s2 = sum(s2_hist) / len(s2_hist)
# In Python speichert `=` hier einen Wert in `mean_s2`.
                mean_s2 = offset_s2
# In Python speichert `=` hier einen berechneten Wert in `var_s2`.
                var_s2 = sum((r - mean_s2)**2 for r in s2_hist) / len(s2_hist)
# In Python speichert `=` hier einen Wert in `std_s2`.
                std_s2 = math.sqrt(var_s2)
# In Python speichert `=` hier einen berechneten Wert in `scale_s2`.
                scale_s2 = std_s2 * 1.414
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if scale_s2 < 0.01:
# In Python speichert `=` hier einen Wert in `scale_s2`.
                    scale_s2 = 0.1
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Determine peak-to-peak variation to check if there is signal activity to fit
# In Python speichert `=` hier einen berechneten Wert in `peak_to_peak_s1`.
        peak_to_peak_s1 = max(s1_hist) - min(s1_hist) if s1_hist else 0.0
# In Python speichert `=` hier einen berechneten Wert in `peak_to_peak_s2`.
        peak_to_peak_s2 = max(s2_hist) - min(s2_hist) if s2_hist else 0.0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `is_measuring`.
        is_measuring = getattr(self, 'measuring', False) or getattr(self, 'calibrating', False)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if not is_measuring and (peak_to_peak_s1 < 0.05 or peak_to_peak_s2 < 0.05):
# Originalkommentar oder Abschnittsüberschrift.
            # Draw flat gray lines at raw signal averages
# In Python speichert `=` hier einen berechneten Wert in `mean_s1`.
            mean_s1 = sum(s1_hist) / len(s1_hist) if s1_hist else 0.0
# In Python speichert `=` hier einen berechneten Wert in `mean_s2`.
            mean_s2 = sum(s2_hist) / len(s2_hist) if s2_hist else 0.0
# In Python speichert `=` hier einen berechneten Wert in `fit_s1`.
            fit_s1 = [mean_s1] * len(s1_hist)
# In Python speichert `=` hier einen berechneten Wert in `fit_s2`.
            fit_s2 = [mean_s2] * len(s2_hist)
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S1_raw_fit'].set_color('gray')
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S2_raw_fit'].set_color('gray')
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S1_raw_fit'].set_data(x, fit_s1)
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['S2_raw_fit'].set_data(x, fit_s2)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S1_raw_fit'].set_visible(True)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_lines['S2_raw_fit'].set_visible(True)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
            # Clear Lissajous circle trace so it doesn't show noise circle
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_trace'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_current'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_pointer'].set_data([], [])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_quiver.set_visible(False)
# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
            self.plot_canvas.draw_idle()
# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
            self.plot_canvas_circle.draw_idle()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.

# `for` startet in Python eine Schleife über mehrere Werte.
        for r1, r2 in zip(s1_hist, s2_hist):
# In Python speichert `=` hier einen berechneten Wert in `s1`.
            s1 = (r1 - offset_s1) / (scale_s1 if scale_s1 > 1e-12 else 1.0)
# In Python speichert `=` hier einen berechneten Wert in `s2`.
            s2 = (r2 - offset_s2) / (scale_s2 if scale_s2 > 1e-12 else 1.0)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            s1_norm_history.append(s1)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            s2_norm_history.append(s2)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Compute the phase at each normalized sample
# In Python speichert `=` hier einen Wert in `phases`.
        phases = [math.atan2(y, x) for x, y in zip(s1_norm_history, s2_norm_history)]
# Leerzeile zur besseren Lesbarkeit.
        
# Originalkommentar oder Abschnittsüberschrift.
        # Unwrap the phases to avoid jumps during fitting
# In Python speichert `=` hier einen Startwert in `unwrapped_phases`.
        unwrapped_phases = []
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if phases:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            unwrapped_phases.append(phases[0])
# `for` startet in Python eine Schleife über mehrere Werte.
            for i in range(1, len(phases)):
# In Python speichert `=` hier einen berechneten Wert in `diff`.
                diff = phases[i] - phases[i-1]
# In Python speichert `=` hier einen berechneten Wert in `diff`.
                diff = (diff + math.pi) % (2 * math.pi) - math.pi
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                unwrapped_phases.append(unwrapped_phases[-1] + diff)
# Leerzeile zur besseren Lesbarkeit.
        
# Originalkommentar oder Abschnittsüberschrift.
        # Fit a line (linear regression) to the phase of the last 20 samples to filter out noise
# In Python speichert `=` hier einen Wert in `fitted_phases`.
        fitted_phases = list(unwrapped_phases)
# In Python speichert `=` hier den festen Wert `20` in der Konstante `N`.
        N = 20
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if len(unwrapped_phases) >= N:
# In Python speichert `=` hier einen Wert in `sum_x`.
            sum_x = sum(float(j) for j in range(N))
# In Python speichert `=` hier einen berechneten Wert in `sum_x2`.
            sum_x2 = sum(float(j)**2 for j in range(N))
# In Python speichert `=` hier einen berechneten Wert in `denom`.
            denom = N * sum_x2 - sum_x**2
# Leerzeile zur besseren Lesbarkeit.
            
# `for` startet in Python eine Schleife über mehrere Werte.
            for i in range(N - 1, len(unwrapped_phases)):
# In Python speichert `=` hier einen berechneten Wert in `y`.
                y = unwrapped_phases[i - N + 1 : i + 1]
# In Python speichert `=` hier einen Wert in `sum_y`.
                sum_y = sum(y)
# In Python speichert `=` hier einen berechneten Wert in `sum_xy`.
                sum_xy = sum(float(j) * y[j] for j in range(N))
# In Python speichert `=` hier einen berechneten Wert in `a`.
                a = (N * sum_xy - sum_x * sum_y) / denom
# In Python speichert `=` hier einen berechneten Wert in `b`.
                b = (sum_y - a * sum_x) / N
# Originalkommentar oder Abschnittsüberschrift.
                # Value at the end of the window (index N-1)
# In Python speichert `=` hier einen berechneten Wert in `fitted_phases[i]`.
                fitted_phases[i] = a * (N - 1) + b
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Reconstruct the smoothed/fitted sine and cosine (perfect unit circle!)
# In Python speichert `=` hier einen Wert in `smoothed_s1`.
        smoothed_s1 = [math.cos(p) for p in fitted_phases]
# In Python speichert `=` hier einen Wert in `smoothed_s2`.
        smoothed_s2 = [math.sin(p) for p in fitted_phases]
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Use unit circle values directly for plotting to keep it perfectly undistorted
# In Python speichert `=` hier einen Wert in `display_s1`.
        display_s1 = smoothed_s1
# In Python speichert `=` hier einen Wert in `display_s2`.
        display_s2 = smoothed_s2
# Leerzeile zur besseren Lesbarkeit.

# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
        self.plot_lines['circle_trace'].set_data(display_s1, display_s2)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        # Scale fit back to raw voltage levels for raw S1 and S2 plots
# In Python speichert `=` hier einen berechneten Wert in `fit_s1`.
        fit_s1 = [s * scale_s1 + offset_s1 for s in smoothed_s1]
# In Python speichert `=` hier einen berechneten Wert in `fit_s2`.
        fit_s2 = [s * scale_s2 + offset_s2 for s in smoothed_s2]
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_lines['S1_raw_fit'].set_color('orange')
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_lines['S2_raw_fit'].set_color('magenta')
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
        self.plot_lines['S1_raw_fit'].set_data(x, fit_s1)
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
        self.plot_lines['S2_raw_fit'].set_data(x, fit_s2)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_lines['S1_raw_fit'].set_visible(True)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.plot_lines['S2_raw_fit'].set_visible(True)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
        if display_s1:
# In Python speichert `=` hier einen berechneten Wert in `curr_x`.
            curr_x = display_s1[-1]
# In Python speichert `=` hier einen berechneten Wert in `curr_y`.
            curr_y = display_s2[-1]
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_current'].set_data([curr_x], [curr_y])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_pointer'].set_data([0, curr_x], [0, curr_y])
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
            # Ensure the axes limits are always a bit larger than the actual plotted values
# In Python speichert `=` hier einen Wert in `max_extent`.
            max_extent = 1.0
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if display_s1 and display_s2:
# In Python speichert `=` hier einen Wert in `max_extent`.
                max_extent = max(max(abs(v) for v in display_s1), max(abs(v) for v in display_s2), 1.0)
# In Python speichert `=` hier einen berechneten Wert in `target_limit`.
            target_limit = max_extent * 1.15
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.axis_circle.set_xlim(-target_limit, target_limit)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.axis_circle.set_ylim(-target_limit, target_limit)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if 'ref_circle' in self.plot_lines and self.plot_lines['ref_circle'] is not None:
# In Python speichert `=` hier einen berechneten Wert in `theta`.
                theta = [t * 2 * math.pi / 100 for t in range(101)]
# In Python speichert `=` hier einen Wert in `ref_r`.
                ref_r = 1.0
# In Python speichert `=` hier einen berechneten Wert in `ref_x`.
                ref_x = [ref_r * math.cos(t) for t in theta]
# In Python speichert `=` hier einen berechneten Wert in `ref_y`.
                ref_y = [ref_r * math.sin(t) for t in theta]
# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
                try:
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
                    self.plot_lines['ref_circle'].set_data(ref_x, ref_y)
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
                except Exception:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    pass
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.latest_sample is not None and self.latest_sample.direction in ["forward", "backward"]:
# In Python speichert `=` hier einen Wert in `phi`.
                phi = math.atan2(curr_y, curr_x)
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
                if self.latest_sample.direction == "forward":
# In Python speichert `=` hier einen berechneten Wert in `dx, dy`.
                    dx, dy = -math.sin(phi), math.cos(phi)
# In Python speichert `=` hier einen Wert in `color`.
                    color = 'green'
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
                else:
# In Python speichert `=` hier einen berechneten Wert in `dx, dy`.
                    dx, dy = math.sin(phi), -math.cos(phi)
# In Python speichert `=` hier einen Wert in `color`.
                    color = 'red'
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier einen Wert in `arrow_len`.
                arrow_len = 0.35
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.plot_quiver.set_offsets([[curr_x, curr_y]])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.plot_quiver.set_UVC([arrow_len * dx], [arrow_len * dy])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.plot_quiver.set_color(color)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.plot_quiver.set_visible(True)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.plot_quiver.set_visible(False)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_current'].set_data([], [])
# In Python wird mit `.` eine Plot-Linie mit neuen Daten versorgt.
            self.plot_lines['circle_pointer'].set_data([], [])
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.plot_quiver.set_visible(False)
# Leerzeile zur besseren Lesbarkeit.

# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
        self.plot_canvas.draw_idle()
# In Python fordert `draw_idle()` ein spätes Neuzeichnen des Plots an.
        self.plot_canvas_circle.draw_idle()
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
# In Python speichert `=` hier den booleschen Startwert aus in `monitoring`.
        self.monitoring = False
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# In Python schließt `close()` eine geöffnete Verbindung wieder.
            self.monitor.close()
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except Exception:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            pass
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Block, in dem Fehler abgefangen werden können.
        try:
# `if` prüft in Python eine Bedingung und führt den Block nur dann aus.
            if self.stage is not None:
# In Python schließt `close()` eine geöffnete Verbindung wieder.
                self.stage.close()
# `except` fängt einen Fehler aus dem `try`-Block ab und erklärt, was dann passiert.
        except Exception:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            pass
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.root.destroy()
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: run
    def run(self):
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.root.mainloop()
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
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    run_gui()
