# Originalkommentar oder Abschnittsüberschrift.
# TABLE OF CONTENTS
# Originalkommentar oder Abschnittsüberschrift.
# 1. Imports
# Originalkommentar oder Abschnittsüberschrift.
# 2. Diode setup constants
# Originalkommentar oder Abschnittsüberschrift.
# 3. Helper functions
# Originalkommentar oder Abschnittsüberschrift.
# 4. Dataclasses and Reader/Counter/Handler classes
# Leerzeile zur besseren Lesbarkeit.

# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 1. IMPORTS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import math
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import time
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
from dataclasses import dataclass
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 2. DIODE SETUP CONSTANTS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# Das ist der Standardkanal für die Photodiode.
PHOTODIODE_CHANNEL = "Dev1/ai1"
# Das ist der Referenzkanal für die Photodiode.
PHOTODIODE_REF_CHANNEL = "Dev1/ai0"
# Leerzeile zur besseren Lesbarkeit.

# Damit wird festgelegt, ob eine Referenzdiode benutzt wird.
USE_REFERENCE_DIODE = True
# Leerzeile zur besseren Lesbarkeit.

# Das ist der Kanal für das Cosinus-Signal.
PHOTODIODE_COS_CHANNEL = "Dev1/ai0"
# Das ist der Kanal für das Sinus-Signal.
PHOTODIODE_SIN_CHANNEL = "Dev1/ai1"
# Leerzeile zur besseren Lesbarkeit.

# So lange läuft die Kalibrierung.
CALIBRATION_SECONDS = 5.0
# So oft wird ein neuer Messwert gelesen.
SAMPLE_INTERVAL_S = 0.005
# Das ist die verwendete Laserwellenlänge.
LASER_WAVELENGTH_NM = 787.3
# Damit wird festgelegt, welche Richtung als positiv zählt.
PHASE_DIRECTION_SIGN = 1
# Ab diesem Radius wird das Signal als brauchbar betrachtet.
MIN_SIGNAL_RADIUS = 0.05
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# CALCULATE THE FRINGE DISTANCE
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Berechnet aus der Laserwellenlänge den Abstand zwischen zwei Fringes.
def compute_fringe_distance_mm(wavelength_nm):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
    return (wavelength_nm / 2) / 1_000_000
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# WRAP THE PHASE ANGLE TO PI
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Normiert einen Winkel auf den Bereich von -pi bis +pi.
def wrap_to_pi(angle_rad):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
    return (angle_rad + math.pi) % (2 * math.pi) - math.pi
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# CALCULATE THE COMPLETED SIGNED FRINGES
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Rundet die Fringe-Position auf die bereits abgeschlossenen Fringes ab.
def completed_signed_fringes(fringe_position):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
    if fringe_position == 0:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return 0
# Leerzeile zur besseren Lesbarkeit.

# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
    sign = 1 if fringe_position > 0 else -1
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
    return sign * math.floor(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        abs(fringe_position)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 4. DATACLASSES AND READER/COUNTER/HANDLER CLASSES
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
@dataclass
# `class` definiert in Python eine Klasse. Hier entsteht `SingleDiodeCalibration` als Bauplan für ein Objekt.
class SingleDiodeCalibration:
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    min_voltage: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    max_voltage: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    offset_voltage: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    scale_voltage: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    sample_count: int
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
@dataclass
# `class` definiert in Python eine Klasse. Hier entsteht `SingleDiodeSample` als Bauplan für ein Objekt.
class SingleDiodeSample:
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    timestamp: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    raw_voltage: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    normalized_voltage: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    valid: bool
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `NISingleDiodeReader` als Bauplan für ein Objekt.
class NISingleDiodeReader:
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # INITIALIZE THE SINGLE DIODE CHANNEL
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self, channel=PHOTODIODE_CHANNEL):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `channel`. analoger Eingangskanal der Photodiode.
        self.channel = channel
# In Python speichert `=` hier erstmal keinen Wert in `task`. NI-DAQmx-Task für die Messung.
        self.task = None
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CONNECT TO THE SINGLE DIODE HARDWARE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Stellt die Verbindung zur Mess- oder Stage-Hardware her.
    def connect(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python lädt `import` das NI-DAQmx-Modul erst dann, wenn es gebraucht wird.
        import nidaqmx
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `task`. NI-DAQmx-Task für die Messung.
        self.task = nidaqmx.Task()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.task.ai_channels.add_ai_voltage_chan(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.channel
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return True
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # READ THE RAW SINGLE DIODE VOLTAGE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Liest Daten von der Hardware.
    def read(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.task is None:
# Fehlermeldung, wenn keine NI-Verbindung offen ist.
            raise RuntimeError("NI diode task is not connected.")
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return float(
# Liest Daten von der Hardware.
            self.task.read()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CLOSE THE SINGLE DIODE CONNECTION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt die Verbindung sauber.
    def close(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.task is not None:
# Schließt die Verbindung sauber.
            self.task.close()
# In Python speichert `=` hier erstmal keinen Wert in `task`. NI-DAQmx-Task für die Messung.
            self.task = None
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `SingleDiodeCounter` als Bauplan für ein Objekt.
class SingleDiodeCounter:
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # INITIALIZE THE COUNTER VARIABLES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `min_voltage`. unterster gemessener Spannungswert.
        self.min_voltage = 0.0
# In Python speichert `=` einen Wert in `max_voltage`. oberster gemessener Spannungswert.
        self.max_voltage = 0.0
# In Python speichert `=` einen Wert in `offset_voltage`. Mittelwert aus Minimum und Maximum.
        self.offset_voltage = 0.0
# In Python speichert `=` einen Wert in `scale_voltage`. halbe Spannungsdifferenz zur Normierung.
        self.scale_voltage = 1.0
# In Python speichert `=` hier erstmal keinen Wert in `calibration`. gespeichertes Kalibrierungsobjekt.
        self.calibration = None
# In Python speichert `=` einen Wert in `sample_count`. Anzahl der verarbeiteten Messwerte.
        self.sample_count = 0
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CALCULATE CALIBRATION OFFSET AND SCALE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: calibrate_from_samples
    def calibrate_from_samples(self, raw_samples):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not raw_samples:
# Fehlermeldung, wenn keine Kalibrierungsdaten vorhanden sind.
            raise ValueError("No diode calibration samples were collected.")
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `min_voltage`. unterster gemessener Spannungswert.
        self.min_voltage = min(raw_samples)
# In Python speichert `=` einen Wert in `max_voltage`. oberster gemessener Spannungswert.
        self.max_voltage = max(raw_samples)
# In Python speichert `=` einen Wert in `offset_voltage`. Mittelwert aus Minimum und Maximum.
        self.offset_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.min_voltage + self.max_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / 2
# In Python speichert `=` einen Wert in `scale_voltage`. halbe Spannungsdifferenz zur Normierung.
        self.scale_voltage = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.max_voltage - self.min_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / 2
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.scale_voltage <= 1e-12:
# In Python speichert `=` einen Wert in `scale_voltage`. halbe Spannungsdifferenz zur Normierung.
            self.scale_voltage = 1.0
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Dataclass-Objekt und `=` speichert es in `calibration`.
        self.calibration = SingleDiodeCalibration(
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            min_voltage=self.min_voltage,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            max_voltage=self.max_voltage,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            offset_voltage=self.offset_voltage,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            scale_voltage=self.scale_voltage,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            sample_count=len(raw_samples)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Setzt Zähler und Zustände wieder zurück.
        self.reset()
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.calibration
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # RESET THE SAMPLE COUNT
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt Zähler und Zustände wieder zurück.
    def reset(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `sample_count`. Anzahl der verarbeiteten Messwerte.
        self.sample_count = 0
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # NORMALIZE THE VOLTAGE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Rechnet Rohwerte auf eine normierte Skala um.
    def normalize(self, raw_voltage):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raw_voltage - self.offset_voltage
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / self.scale_voltage
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CREATE A NORMALIZED SAMPLE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Verarbeitet neue Messwerte und erzeugt daraus ein Sample.
    def update(self, raw_voltage):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `sample_count +`.
        self.sample_count += 1
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return SingleDiodeSample(
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            timestamp=time.time(),
# In Python speichert `=` einen Wert in einer Variable.
            raw_voltage=raw_voltage,
# Rechnet Rohwerte auf eine normierte Skala um.
            normalized_voltage=self.normalize(raw_voltage),
# In Python speichert `=` einen Startwert in einer Variable.
            valid=True
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `SingleDiodeHandler` als Bauplan für ein Objekt.
class SingleDiodeHandler:
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # INITIALIZE THE SINGLE DIODE HANDLER
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self, channel=PHOTODIODE_CHANNEL):
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        self.reader = NISingleDiodeReader(
# In Python speichert `=` einen Wert in einer Variable.
            channel=channel
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `counter`.
        self.counter = SingleDiodeCounter()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CONNECT TO THE SINGLE DIODE HARDWARE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Stellt die Verbindung zur Mess- oder Stage-Hardware her.
    def connect(self):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.reader.connect()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CALIBRATE THE SINGLE DIODE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Sammelt Messwerte und berechnet daraus die Kalibrierung.
    def calibrate(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# So lange läuft die Kalibrierung.
        seconds=CALIBRATION_SECONDS,
# So oft wird ein neuer Messwert gelesen.
        sample_interval_s=SAMPLE_INTERVAL_S,
# In Python speichert `=` einen Wert in einer Variable.
        should_continue=None,
# In Python speichert `=` einen Startwert in einer Variable.
        sample_callback=None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Startwert in einer Variable.
        samples = []
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        start_time = time.time()
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die sich wiederholt, solange die Bedingung stimmt.
        while time.time() - start_time < seconds:
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if should_continue is not None and not should_continue():
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                break
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
            raw_voltage = self.reader.read()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            samples.append(raw_voltage)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if sample_callback is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                sample_callback(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    raw_voltage,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    time.time() - start_time,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    seconds
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
            time.sleep(sample_interval_s)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not samples and should_continue is not None and not should_continue():
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return None
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.counter.calibrate_from_samples(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            samples
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # READ AND NORMALIZE THE VOLTAGE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Liest Daten von der Hardware.
    def read(self):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.counter.update(
# Liest Daten von der Hardware.
            self.reader.read()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CLOSE THE SINGLE DIODE CONNECTION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt die Verbindung sauber.
    def close(self):
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        self.reader.close()
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
@dataclass
# `class` definiert in Python eine Klasse. Hier entsteht `DiodeCalibration` als Bauplan für ein Objekt.
class DiodeCalibration:
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    cos_min: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    cos_max: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    sin_min: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    sin_max: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    cos_offset: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    sin_offset: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    cos_scale: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    sin_scale: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    sample_count: int
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
@dataclass
# `class` definiert in Python eine Klasse. Hier entsteht `DiodeSample` als Bauplan für ein Objekt.
class DiodeSample:
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    timestamp: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    raw_cos: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    raw_sin: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    cos_value: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    sin_value: float
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
    total_abs_fringes: int
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    direction: str
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    valid: bool
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `NIDiodeReader` als Bauplan für ein Objekt.
class NIDiodeReader:
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # INITIALIZE THE QUADRATURE DIODE CHANNELS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# Das ist der Kanal für das Cosinus-Signal.
        cos_channel=PHOTODIODE_COS_CHANNEL,
# Das ist der Kanal für das Sinus-Signal.
        sin_channel=PHOTODIODE_SIN_CHANNEL
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `cos_channel`. Eingangskanal für das Cosinus-Signal.
        self.cos_channel = cos_channel
# In Python speichert `=` einen Wert in `sin_channel`. Eingangskanal für das Sinus-Signal.
        self.sin_channel = sin_channel
# In Python speichert `=` hier erstmal keinen Wert in `task`. NI-DAQmx-Task für die Messung.
        self.task = None
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CONNECT TO THE QUADRATURE DIODE HARDWARE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Stellt die Verbindung zur Mess- oder Stage-Hardware her.
    def connect(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python lädt `import` das NI-DAQmx-Modul erst dann, wenn es gebraucht wird.
        import nidaqmx
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `task`. NI-DAQmx-Task für die Messung.
        self.task = nidaqmx.Task()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.task.ai_channels.add_ai_voltage_chan(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.cos_channel
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.task.ai_channels.add_ai_voltage_chan(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.sin_channel
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return True
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # READ THE RAW VOLTAGES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Liest Daten von der Hardware.
    def read(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.task is None:
# Fehlermeldung, wenn keine NI-Verbindung offen ist.
            raise RuntimeError("NI diode task is not connected.")
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        values = self.task.read()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if len(values) != 2:
# In Python bricht `raise` die Ausführung absichtlich mit einem Fehler ab.
            raise RuntimeError(
# Fehlermeldung, wenn nicht genau zwei Eingangswerte kommen.
                "Expected two analog input values from the NI task."
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return float(values[0]), float(values[1])
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CLOSE THE QUADRATURE DIODE CONNECTION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt die Verbindung sauber.
    def close(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.task is not None:
# Schließt die Verbindung sauber.
            self.task.close()
# In Python speichert `=` hier erstmal keinen Wert in `task`. NI-DAQmx-Task für die Messung.
            self.task = None
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `DiodeQuadratureCounter` als Bauplan für ein Objekt.
class DiodeQuadratureCounter:
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # INITIALIZE THE COUNTER VARIABLES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# Das ist die verwendete Laserwellenlänge.
        wavelength_nm=LASER_WAVELENGTH_NM,
# Damit wird festgelegt, welche Richtung als positiv zählt.
        phase_direction_sign=PHASE_DIRECTION_SIGN,
# Ab diesem Radius wird das Signal als brauchbar betrachtet.
        min_signal_radius=MIN_SIGNAL_RADIUS
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# In Python berechnet `=` einen Wert und speichert ihn in `phase_direction_sign`. Vorzeichen für die Phasenrichtung.
        self.phase_direction_sign = 1 if phase_direction_sign >= 0 else -1
# In Python speichert `=` einen Wert in `min_signal_radius`. Minimalradius für gültige Signale.
        self.min_signal_radius = min_signal_radius
# Berechnet aus der Laserwellenlänge den Abstand zwischen zwei Fringes.
        self.fringe_distance_mm = compute_fringe_distance_mm(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            wavelength_nm
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `cos_offset`. Offset für das Cosinus-Signal.
        self.cos_offset = 0.0
# In Python speichert `=` einen Wert in `sin_offset`. Offset für das Sinus-Signal.
        self.sin_offset = 0.0
# In Python speichert `=` einen Wert in `cos_scale`. Skalierung für das Cosinus-Signal.
        self.cos_scale = 1.0
# In Python speichert `=` einen Wert in `sin_scale`. Skalierung für das Sinus-Signal.
        self.sin_scale = 1.0
# In Python speichert `=` hier erstmal keinen Wert in `calibration`. gespeichertes Kalibrierungsobjekt.
        self.calibration = None
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier erstmal keinen Wert in `previous_phase_rad`. vorheriger Phasenwinkel.
        self.previous_phase_rad = None
# In Python speichert `=` einen Wert in `unwrapped_phase_rad`. entfalteter Phasenwinkel ohne Sprünge.
        self.unwrapped_phase_rad = 0.0
# In Python speichert `=` einen Wert in `signed_fringes`. gezählte Fringes mit Vorzeichen.
        self.signed_fringes = 0
# In Python speichert `=` einen Wert in `total_abs_fringes`. gesamt gezählte Fringes ohne Vorzeichen.
        self.total_abs_fringes = 0
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CALCULATE CALIBRATION OFFSET AND SCALE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: calibrate_from_samples
    def calibrate_from_samples(self, raw_samples):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not raw_samples:
# Fehlermeldung, wenn keine Kalibrierungsdaten vorhanden sind.
            raise ValueError("No diode calibration samples were collected.")
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in einer Variable.
        cos_values = [
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sample[0]
# `for` startet in Python eine Schleife über mehrere Werte.
            for sample in raw_samples
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ]
# In Python speichert `=` einen Wert in einer Variable.
        sin_values = [
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sample[1]
# `for` startet in Python eine Schleife über mehrere Werte.
            for sample in raw_samples
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ]
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        cos_min = min(cos_values)
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        cos_max = max(cos_values)
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        sin_min = min(sin_values)
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        sin_max = max(sin_values)
# Leerzeile zur besseren Lesbarkeit.

# In Python berechnet `=` einen Wert und speichert ihn in `cos_offset`. Offset für das Cosinus-Signal.
        self.cos_offset = (cos_min + cos_max) / 2
# In Python berechnet `=` einen Wert und speichert ihn in `sin_offset`. Offset für das Sinus-Signal.
        self.sin_offset = (sin_min + sin_max) / 2
# In Python berechnet `=` einen Wert und speichert ihn in `cos_scale`. Skalierung für das Cosinus-Signal.
        self.cos_scale = (cos_max - cos_min) / 2
# In Python berechnet `=` einen Wert und speichert ihn in `sin_scale`. Skalierung für das Sinus-Signal.
        self.sin_scale = (sin_max - sin_min) / 2
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.cos_scale <= 1e-12:
# In Python speichert `=` einen Wert in `cos_scale`. Skalierung für das Cosinus-Signal.
            self.cos_scale = 1.0
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.sin_scale <= 1e-12:
# In Python speichert `=` einen Wert in `sin_scale`. Skalierung für das Sinus-Signal.
            self.sin_scale = 1.0
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Dataclass-Objekt und `=` speichert es in `calibration`.
        self.calibration = DiodeCalibration(
# In Python speichert `=` einen Wert in einer Variable.
            cos_min=cos_min,
# In Python speichert `=` einen Wert in einer Variable.
            cos_max=cos_max,
# In Python speichert `=` einen Wert in einer Variable.
            sin_min=sin_min,
# In Python speichert `=` einen Wert in einer Variable.
            sin_max=sin_max,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            cos_offset=self.cos_offset,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            sin_offset=self.sin_offset,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            cos_scale=self.cos_scale,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            sin_scale=self.sin_scale,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            sample_count=len(raw_samples)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Setzt Zähler und Zustände wieder zurück.
        self.reset()
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.calibration
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # RESET THE PHASE AND FRINGE COUNTS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt Zähler und Zustände wieder zurück.
    def reset(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier erstmal keinen Wert in `previous_phase_rad`. vorheriger Phasenwinkel.
        self.previous_phase_rad = None
# In Python speichert `=` einen Wert in `unwrapped_phase_rad`. entfalteter Phasenwinkel ohne Sprünge.
        self.unwrapped_phase_rad = 0.0
# In Python speichert `=` einen Wert in `signed_fringes`. gezählte Fringes mit Vorzeichen.
        self.signed_fringes = 0
# In Python speichert `=` einen Wert in `total_abs_fringes`. gesamt gezählte Fringes ohne Vorzeichen.
        self.total_abs_fringes = 0
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # NORMALIZE THE VOLTAGES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Rechnet Rohwerte auf eine normierte Skala um.
    def normalize(self, raw_cos, raw_sin):
# Leerzeile zur besseren Lesbarkeit.

# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
        cos_value = (raw_cos - self.cos_offset) / self.cos_scale
# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
        sin_value = (raw_sin - self.sin_offset) / self.sin_scale
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return cos_value, sin_value
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CALCULATE PHASE AND COUNT FRINGES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Verarbeitet neue Messwerte und erzeugt daraus ein Sample.
    def update(self, raw_cos, raw_sin):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        timestamp = time.time()
# Rechnet Rohwerte auf eine normierte Skala um.
        cos_value, sin_value = self.normalize(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raw_cos,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raw_sin
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        radius = math.hypot(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            cos_value,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sin_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if radius < self.min_signal_radius:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return DiodeSample(
# In Python speichert `=` einen Wert in einer Variable.
                timestamp=timestamp,
# In Python speichert `=` einen Wert in einer Variable.
                raw_cos=raw_cos,
# In Python speichert `=` einen Wert in einer Variable.
                raw_sin=raw_sin,
# In Python speichert `=` einen Wert in einer Variable.
                cos_value=cos_value,
# In Python speichert `=` einen Wert in einer Variable.
                sin_value=sin_value,
# In Python speichert `=` einen Wert in einer Variable.
                radius=radius,
# In Python speichert `=` einen Wert in einer Variable.
                phase_rad=0.0,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                unwrapped_phase_rad=self.unwrapped_phase_rad,
# In Python speichert `=` einen Wert in einer Variable.
                delta_phase_rad=0.0,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                fringe_position=(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.unwrapped_phase_rad / (2 * math.pi)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                ),
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                signed_fringes=self.signed_fringes,
# In Python speichert `=` einen Wert in einer Variable.
                fringe_delta=0,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                total_abs_fringes=self.total_abs_fringes,
# In Python speichert `=` einen Wert in einer Variable.
                direction="signal_low",
# In Python speichert `=` einen Startwert in einer Variable.
                valid=False
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
        phase_rad = self.phase_direction_sign * math.atan2(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            sin_value,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            cos_value
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.previous_phase_rad is None:
# In Python speichert `=` einen Wert in `previous_phase_rad`. vorheriger Phasenwinkel.
            self.previous_phase_rad = phase_rad
# In Python speichert `=` einen Wert in einer Variable.
            delta_phase_rad = 0.0
# Leerzeile zur besseren Lesbarkeit.

# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# Normiert einen Winkel auf den Bereich von -pi bis +pi.
            delta_phase_rad = wrap_to_pi(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                phase_rad - self.previous_phase_rad
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# In Python speichert `=` einen Wert in `unwrapped_phase_rad +`.
            self.unwrapped_phase_rad += delta_phase_rad
# In Python speichert `=` einen Wert in `previous_phase_rad`. vorheriger Phasenwinkel.
            self.previous_phase_rad = phase_rad
# Leerzeile zur besseren Lesbarkeit.

# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
        fringe_position = self.unwrapped_phase_rad / (2 * math.pi)
# Rundet die Fringe-Position auf die bereits abgeschlossenen Fringes ab.
        new_signed_fringes = completed_signed_fringes(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            fringe_position
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
        fringe_delta = new_signed_fringes - self.signed_fringes
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if fringe_delta != 0:
# In Python speichert `=` einen Wert in `total_abs_fringes +`.
            self.total_abs_fringes += abs(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                fringe_delta
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `signed_fringes`. gezählte Fringes mit Vorzeichen.
        self.signed_fringes = new_signed_fringes
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if delta_phase_rad > 0:
# In Python speichert `=` einen Wert in einer Variable.
            direction = "forward"
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
        elif delta_phase_rad < 0:
# In Python speichert `=` einen Wert in einer Variable.
            direction = "backward"
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` einen Wert in einer Variable.
            direction = "none"
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return DiodeSample(
# In Python speichert `=` einen Wert in einer Variable.
            timestamp=timestamp,
# In Python speichert `=` einen Wert in einer Variable.
            raw_cos=raw_cos,
# In Python speichert `=` einen Wert in einer Variable.
            raw_sin=raw_sin,
# In Python speichert `=` einen Wert in einer Variable.
            cos_value=cos_value,
# In Python speichert `=` einen Wert in einer Variable.
            sin_value=sin_value,
# In Python speichert `=` einen Wert in einer Variable.
            radius=radius,
# In Python speichert `=` einen Wert in einer Variable.
            phase_rad=phase_rad,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            unwrapped_phase_rad=self.unwrapped_phase_rad,
# In Python speichert `=` einen Wert in einer Variable.
            delta_phase_rad=delta_phase_rad,
# In Python speichert `=` einen Wert in einer Variable.
            fringe_position=fringe_position,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            signed_fringes=self.signed_fringes,
# In Python speichert `=` einen Wert in einer Variable.
            fringe_delta=fringe_delta,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            total_abs_fringes=self.total_abs_fringes,
# In Python speichert `=` einen Wert in einer Variable.
            direction=direction,
# In Python speichert `=` einen Startwert in einer Variable.
            valid=True
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CALCULATE THE SIGNED DISTANCE IN MM
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Berechnet aus der Phase eine Strecke in Millimeter.
    def signed_distance_mm(self):
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

# `class` definiert in Python eine Klasse. Hier entsteht `DiodeHandler` als Bauplan für ein Objekt.
class DiodeHandler:
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # INITIALIZE THE QUADRATURE DIODE HANDLER
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# Das ist der Kanal für das Cosinus-Signal.
        cos_channel=PHOTODIODE_COS_CHANNEL,
# Das ist der Kanal für das Sinus-Signal.
        sin_channel=PHOTODIODE_SIN_CHANNEL,
# Das ist die verwendete Laserwellenlänge.
        wavelength_nm=LASER_WAVELENGTH_NM,
# Damit wird festgelegt, welche Richtung als positiv zählt.
        phase_direction_sign=PHASE_DIRECTION_SIGN
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        self.reader = NIDiodeReader(
# In Python speichert `=` einen Wert in einer Variable.
            cos_channel=cos_channel,
# In Python speichert `=` einen Wert in einer Variable.
            sin_channel=sin_channel
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `counter`.
        self.counter = DiodeQuadratureCounter(
# In Python speichert `=` einen Wert in einer Variable.
            wavelength_nm=wavelength_nm,
# In Python speichert `=` einen Wert in einer Variable.
            phase_direction_sign=phase_direction_sign
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CONNECT TO THE QUADRATURE DIODE HARDWARE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Stellt die Verbindung zur Mess- oder Stage-Hardware her.
    def connect(self):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.reader.connect()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CALIBRATE THE QUADRATURE DIODES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Sammelt Messwerte und berechnet daraus die Kalibrierung.
    def calibrate(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# So lange läuft die Kalibrierung.
        seconds=CALIBRATION_SECONDS,
# So oft wird ein neuer Messwert gelesen.
        sample_interval_s=SAMPLE_INTERVAL_S,
# In Python speichert `=` einen Wert in einer Variable.
        should_continue=None,
# In Python speichert `=` einen Startwert in einer Variable.
        sample_callback=None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Startwert in einer Variable.
        samples = []
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        start_time = time.time()
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die sich wiederholt, solange die Bedingung stimmt.
        while time.time() - start_time < seconds:
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if should_continue is not None and not should_continue():
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                break
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
            raw_sample = self.reader.read()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            samples.append(raw_sample)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if sample_callback is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                sample_callback(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    raw_sample,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    time.time() - start_time,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    seconds
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
            time.sleep(sample_interval_s)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not samples and should_continue is not None and not should_continue():
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return None
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.counter.calibrate_from_samples(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            samples
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # READ AND PROCESS THE VOLTAGES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Liest Daten von der Hardware.
    def read(self):
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        raw_cos, raw_sin = self.reader.read()
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.counter.update(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raw_cos,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raw_sin
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CLOSE THE QUADRATURE DIODE CONNECTION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt die Verbindung sauber.
    def close(self):
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        self.reader.close()
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
@dataclass
# `class` definiert in Python eine Klasse. Hier entsteht `ReferenceDiodeCalibration` als Bauplan für ein Objekt.
class ReferenceDiodeCalibration:
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    min_ratio: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    max_ratio: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    offset_ratio: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    scale_ratio: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    sample_count: int
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
@dataclass
# `class` definiert in Python eine Klasse. Hier entsteht `ReferenceDiodeSample` als Bauplan für ein Objekt.
class ReferenceDiodeSample:
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    timestamp: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    raw_int: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    raw_ref: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ratio: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    normalized_ratio: float
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    valid: bool
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `NIReferenceDiodeReader` als Bauplan für ein Objekt.
class NIReferenceDiodeReader:
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # INITIALIZE THE REFERENCE DIODE CHANNELS
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self, int_channel=PHOTODIODE_CHANNEL, ref_channel=PHOTODE_REF_CHANNEL if 'PHOTODE_REF_CHANNEL' in globals() else PHOTODIODE_REF_CHANNEL):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `int_channel`. analoger Eingang für die Intensität.
        self.int_channel = int_channel
# In Python speichert `=` einen Wert in `ref_channel`. analoger Eingang für die Referenz.
        self.ref_channel = ref_channel
# In Python speichert `=` hier erstmal keinen Wert in `task`. NI-DAQmx-Task für die Messung.
        self.task = None
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CONNECT TO THE REFERENCE DIODE HARDWARE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Stellt die Verbindung zur Mess- oder Stage-Hardware her.
    def connect(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python lädt `import` das NI-DAQmx-Modul erst dann, wenn es gebraucht wird.
        import nidaqmx
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `task`. NI-DAQmx-Task für die Messung.
        self.task = nidaqmx.Task()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.task.ai_channels.add_ai_voltage_chan(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.int_channel
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self.task.ai_channels.add_ai_voltage_chan(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.ref_channel
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return True
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # READ THE RAW VOLTAGES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Liest Daten von der Hardware.
    def read(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.task is None:
# Fehlermeldung, wenn die Referenzdiode nicht verbunden ist.
            raise RuntimeError("NI reference diode task is not connected.")
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        values = self.task.read()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if len(values) != 2:
# In Python bricht `raise` die Ausführung absichtlich mit einem Fehler ab.
            raise RuntimeError(
# Fehlermeldung für zwei erwartete Referenzspannungen.
                "Expected two analog input values (Pint, Pl) from the NI task."
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return float(values[0]), float(values[1])
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CLOSE THE REFERENCE DIODE CONNECTION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt die Verbindung sauber.
    def close(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.task is not None:
# Schließt die Verbindung sauber.
            self.task.close()
# In Python speichert `=` hier erstmal keinen Wert in `task`. NI-DAQmx-Task für die Messung.
            self.task = None
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `ReferenceDiodeCounter` als Bauplan für ein Objekt.
class ReferenceDiodeCounter:
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # INITIALIZE THE COUNTER VARIABLES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `min_ratio`.
        self.min_ratio = 0.0
# In Python speichert `=` einen Wert in `max_ratio`.
        self.max_ratio = 0.0
# In Python speichert `=` einen Wert in `offset_ratio`.
        self.offset_ratio = 0.0
# In Python speichert `=` einen Wert in `scale_ratio`.
        self.scale_ratio = 1.0
# In Python speichert `=` hier erstmal keinen Wert in `calibration`. gespeichertes Kalibrierungsobjekt.
        self.calibration = None
# In Python speichert `=` einen Wert in `sample_count`. Anzahl der verarbeiteten Messwerte.
        self.sample_count = 0
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CALCULATE CALIBRATION OFFSET AND SCALE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: calibrate_from_samples
    def calibrate_from_samples(self, raw_samples):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not raw_samples:
# Fehlermeldung, wenn keine Referenz-Kalibrierung erfolgt ist.
            raise ValueError("No reference diode calibration samples were collected.")
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Startwert in einer Variable.
        ratios = []
# `for` startet in Python eine Schleife über mehrere Werte.
        for Pint, Pl in raw_samples:
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if abs(Pl) < 1e-6:
# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
                denom = 1e-6 if Pl >= 0 else -1e-6
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` einen Wert in einer Variable.
                denom = Pl
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ratios.append(Pint / denom)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `min_ratio`.
        self.min_ratio = min(ratios)
# In Python speichert `=` einen Wert in `max_ratio`.
        self.max_ratio = max(ratios)
# In Python speichert `=` einen Wert in `offset_ratio`.
        self.offset_ratio = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.min_ratio + self.max_ratio
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / 2
# In Python speichert `=` einen Wert in `scale_ratio`.
        self.scale_ratio = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.max_ratio - self.min_ratio
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / 2
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.scale_ratio <= 1e-12:
# In Python speichert `=` einen Wert in `scale_ratio`.
            self.scale_ratio = 1.0
# Leerzeile zur besseren Lesbarkeit.

# In Python erzeugt `()` ein Dataclass-Objekt und `=` speichert es in `calibration`.
        self.calibration = ReferenceDiodeCalibration(
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            min_ratio=self.min_ratio,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            max_ratio=self.max_ratio,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            offset_ratio=self.offset_ratio,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            scale_ratio=self.scale_ratio,
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            sample_count=len(raw_samples)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Setzt Zähler und Zustände wieder zurück.
        self.reset()
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.calibration
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # RESET THE SAMPLE COUNT
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt Zähler und Zustände wieder zurück.
    def reset(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `sample_count`. Anzahl der verarbeiteten Messwerte.
        self.sample_count = 0
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # NORMALIZE THE RATIO
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Rechnet Rohwerte auf eine normierte Skala um.
    def normalize(self, ratio):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            ratio - self.offset_ratio
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        ) / self.scale_ratio
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CALCULATE THE RATIO AND NORMALIZE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Verarbeitet neue Messwerte und erzeugt daraus ein Sample.
    def update(self, raw_int, raw_ref):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `sample_count +`.
        self.sample_count += 1
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if abs(raw_ref) < 1e-6:
# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
            denom = 1e-6 if raw_ref >= 0 else -1e-6
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# In Python speichert `=` einen Wert in einer Variable.
            denom = raw_ref
# Leerzeile zur besseren Lesbarkeit.

# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
        ratio = raw_int / denom
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return ReferenceDiodeSample(
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            timestamp=time.time(),
# In Python speichert `=` einen Wert in einer Variable.
            raw_int=raw_int,
# In Python speichert `=` einen Wert in einer Variable.
            raw_ref=raw_ref,
# In Python speichert `=` einen Wert in einer Variable.
            ratio=ratio,
# Rechnet Rohwerte auf eine normierte Skala um.
            normalized_ratio=self.normalize(ratio),
# In Python speichert `=` einen Startwert in einer Variable.
            valid=True
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `class` definiert in Python eine Klasse. Hier entsteht `ReferenceDiodeHandler` als Bauplan für ein Objekt.
class ReferenceDiodeHandler:
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # INITIALIZE THE REFERENCE DIODE HANDLER
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self, int_channel=PHOTODIODE_CHANNEL, ref_channel=PHOTODIODE_REF_CHANNEL):
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        self.reader = NIReferenceDiodeReader(
# In Python speichert `=` einen Wert in einer Variable.
            int_channel=int_channel,
# In Python speichert `=` einen Wert in einer Variable.
            ref_channel=ref_channel
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# In Python speichert `=` einen Wert in `counter`.
        self.counter = ReferenceDiodeCounter()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CONNECT TO THE REFERENCE DIODE HARDWARE
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Stellt die Verbindung zur Mess- oder Stage-Hardware her.
    def connect(self):
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.reader.connect()
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CALIBRATE THE REFERENCE DIODES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Sammelt Messwerte und berechnet daraus die Kalibrierung.
    def calibrate(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# So lange läuft die Kalibrierung.
        seconds=CALIBRATION_SECONDS,
# So oft wird ein neuer Messwert gelesen.
        sample_interval_s=SAMPLE_INTERVAL_S,
# In Python speichert `=` einen Wert in einer Variable.
        should_continue=None,
# In Python speichert `=` einen Startwert in einer Variable.
        sample_callback=None
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Startwert in einer Variable.
        samples = []
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        start_time = time.time()
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die sich wiederholt, solange die Bedingung stimmt.
        while time.time() - start_time < seconds:
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if should_continue is not None and not should_continue():
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                break
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
            raw_int, raw_ref = self.reader.read()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            samples.append((raw_int, raw_ref))
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if sample_callback is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                sample_callback(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    (raw_int, raw_ref),
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    time.time() - start_time,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    seconds
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
            time.sleep(sample_interval_s)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not samples and should_continue is not None and not should_continue():
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return None
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.counter.calibrate_from_samples(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            samples
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # READ AND PROCESS THE VOLTAGES
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Liest Daten von der Hardware.
    def read(self):
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        raw_int, raw_ref = self.reader.read()
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.counter.update(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raw_int,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            raw_ref
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    # CLOSE THE REFERENCE DIODE CONNECTION
# Originalkommentar oder Abschnittsüberschrift.
    # -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt die Verbindung sauber.
    def close(self):
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        self.reader.close()
# Leerzeile zur besseren Lesbarkeit.

