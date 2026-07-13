# Originalkommentar oder Abschnittsüberschrift.
# TABLE OF CONTENTS
# Originalkommentar oder Abschnittsüberschrift.
# 1. Imports
# Originalkommentar oder Abschnittsüberschrift.
# 2. StageController class
# Originalkommentar oder Abschnittsüberschrift.
# 3. Axis referencing
# Originalkommentar oder Abschnittsüberschrift.
# 4. Position querying
# Originalkommentar oder Abschnittsüberschrift.
# 5. Motion commands
# Originalkommentar oder Abschnittsüberschrift.
# 6. Velocity and step size
# Originalkommentar oder Abschnittsüberschrift.
# 7. Cleanup
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 1. IMPORTS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import threading
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import time
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
from pipython import GCSError, GCSDevice, gcserror, pitools
# Leerzeile zur besseren Lesbarkeit.

# Leerzeile zur besseren Lesbarkeit.

# Das ist die Achse, auf der die Stage angesprochen wird.
STAGE_AXIS = "1"
# Name des Stage-Controllers; leer heißt, er wird automatisch gesucht.
STAGE_CONTROLLER_NAME = "" #is found automatically, thats why its empty
# Damit wird festgelegt, ob die Stage beim Verbinden automatisch referenziert wird.
AUTO_REFERENCE_ON_CONNECT = False
# Damit wird festgelegt, ob eine unbekannte Position einfach als Null gesetzt wird.
DEFINE_POSITION_IF_UNREFERENCED = True
# Das ist die Referenzmethode für den Stage.
REFERENCE_MODE = "FRF" #frf is the standard reference drive of the PI stage
# So lange wird höchstens auf die Referenzierung gewartet.
REFERENCE_TIMEOUT_S = 180
# So klein darf die Positionsabweichung beim Beenden der Fahrt noch sein.
MOVE_POSITION_TOLERANCE_MM = 0.000002
# Leerzeile zur besseren Lesbarkeit.

# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 2. STAGECONTROLLER CLASS  
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `class` definiert in Python eine Klasse. Hier entsteht `StageController` als Bauplan für ein Objekt.
class StageController:
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self, controller_name=STAGE_CONTROLLER_NAME):
# Originalkommentar oder Abschnittsüberschrift.
        #initialize all the variables
# In Python speichert `=` einen Wert in `controller_name`. Name des verwendeten Controllers.
        self.controller_name = controller_name
# In Python speichert `=` hier erstmal keinen Wert in `device`. Hardwareobjekt der Stage.
        self.device = None
# In Python speichert `=` hier den booleschen Startwert aus in `connected`. Verbindungsstatus der Hardware.
        self.connected = False
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
        self.last_error = ""
# In Python speichert `=` einen Wert in `connection_description`. Beschreibung des verbundenen Geräts.
        self.connection_description = ""
# In Python speichert `=` einen Wert in `current_position`. aktuelle Position der Stage.
        self.current_position = 0.0
# In Python speichert `=` einen Wert in `target_position`. Zielposition der Stage.
        self.target_position = 0.0
# In Python speichert `=` einen Wert in `step_size`. Schrittweite für manuelle Fahrten.
        self.step_size = 0.020000000
# In Python speichert `=` einen Wert in `velocity`. gesetzte Fahrgeschwindigkeit.
        self.velocity = 0.0006
# In Python speichert `=` einen Wert in `acceleration`. gesetzte Beschleunigung.
        self.acceleration = 0.0
# In Python speichert `=` hier den booleschen Startwert aus in `is_moving`. Merker, ob die Stage gerade fährt.
        self.is_moving = False
# In Python speichert `=` einen Wert in `min_position`. minimale erlaubte Position.
        self.min_position = 0.0
# In Python speichert `=` einen Wert in `max_position`. maximale erlaubte Position.
        self.max_position = 50.0
# Originalkommentar oder Abschnittsüberschrift.
    #connects the actual motor to the software
# `def` definiert in Python eine Funktion oder Methode. Hier: Stellt die Verbindung zur Mess- oder Stage-Hardware her.
    def connect(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.connected:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return True
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
        self.last_error = ""
# Originalkommentar oder Abschnittsüberschrift.
        #the connection of the motor has to run in the main thread
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if threading.current_thread() is not threading.main_thread():
# Fehlermeldung, wenn die Stage-Verbindung im falschen Thread startet.
            self.last_error = "Stage connection must be started from the main thread"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# In Python speichert `=` einen Wert in `device`. Hardwareobjekt der Stage.
            self.device = GCSDevice(self.controller_name)
# Stellt die Verbindung zur Mess- oder Stage-Hardware her.
            self._connect_first_available_device()
# Bereitet die Achse für Bewegungen vor.
            self._prepare_axis_for_motion() #turn on servo, check zero point
# Das ist die Achse, auf der die Stage angesprochen wird.
            pos = self.device.qPOS(STAGE_AXIS)
# In Python speichert `=` hier den booleschen Startwert ein in `connected`. Verbindungsstatus der Hardware.
            self.connected = True
# Das ist die Achse, auf der die Stage angesprochen wird.
            self.current_position = float(pos[STAGE_AXIS])
# Setzt die Stage-Geschwindigkeit.
            self.set_velocity(self.velocity)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return True
# Originalkommentar oder Abschnittsüberschrift.
        #in case of failure (cable unplugged, ...)
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as error:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Stage connection error: {error}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# In Python speichert `=` hier den booleschen Startwert aus in `connected`. Verbindungsstatus der Hardware.
            self.connected = False
# In Python speichert `=` hier den booleschen Startwert aus in `is_moving`. Merker, ob die Stage gerade fährt.
            self.is_moving = False
# Originalkommentar oder Abschnittsüberschrift.
            #close the communication channel, if there is an error
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
            try:
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
                if self.device is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    self.device.CloseConnection()
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
            except Exception:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                pass
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier erstmal keinen Wert in `device`. Hardwareobjekt der Stage.
            self.device = None
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Verbindet sich mit dem ersten gefundenen USB-Gerät.
    def _connect_first_available_device(self):
# In Python speichert `=` einen Startwert in einer Variable.
        errors = []
# Originalkommentar oder Abschnittsüberschrift.
        #search for usb devices
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            usb_devices = list(self.device.EnumerateUSB())
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as error:
# In Python speichert `=` einen Startwert in einer Variable.
            usb_devices = []
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            errors.append(f"USB enumeration failed: {error}")
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if usb_devices:
# In Python speichert `=` einen Wert in `connection_description`. Beschreibung des verbundenen Geräts.
            self.connection_description = usb_devices[0]
# Stellt die Verbindung zur Mess- oder Stage-Hardware her.
            print(f"Connecting first PI USB stage: {self.connection_description}")
# Stellt die Verbindung zur Mess- oder Stage-Hardware her.
            self.device.ConnectUSB(self.connection_description)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return
# Leerzeile zur besseren Lesbarkeit.
    
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        detail = "; ".join(errors)
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if detail:
# Fehlermeldung, wenn keine PI-Stage gefunden wurde.
            raise RuntimeError(f"No PI stage found via USB ({detail})")
# Leerzeile zur besseren Lesbarkeit.

# Fehlermeldung, wenn keine PI-Stage gefunden wurde.
        raise RuntimeError("No PI stage found via USB")
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 3. AXIS REFERENCING 
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Bereitet die Achse für Bewegungen vor.
    def _prepare_axis_for_motion(self):
# Originalkommentar oder Abschnittsüberschrift.
        #turn on servo (motor current) --> only when servo is on, the motor can hold its position
# Schaltet die Servo-Funktion an oder aus.
        self._set_servo(True)
# Originalkommentar oder Abschnittsüberschrift.
        #does the motor know, where it stands at? this is calibrated here
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not self._is_referenced():
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if DEFINE_POSITION_IF_UNREFERENCED:
# Setzt die aktuelle Position als Nullpunkt.
                self._define_current_position_as_zero()
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
            elif AUTO_REFERENCE_ON_CONNECT:
# Führt die Referenzfahrt aus.
                self._reference_axis()
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python bricht `raise` die Ausführung absichtlich mit einem Fehler ab.
                raise RuntimeError(
# Das ist die Achse, auf der die Stage angesprochen wird.
                    f"PI stage axis {STAGE_AXIS} is not referenced"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                )
# Leerzeile zur besseren Lesbarkeit.

# Schaltet die Servo-Funktion an oder aus.
        self._set_servo(True)
# Originalkommentar oder Abschnittsüberschrift.
    #enables servo
# `def` definiert in Python eine Funktion oder Methode. Hier: Schaltet die Servo-Funktion an oder aus.
    def _set_servo(self, enabled):
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# Das ist die Achse, auf der die Stage angesprochen wird.
            self.device.SVO(STAGE_AXIS, bool(enabled))
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as error:
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(f"Stage servo warning: {error}")
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Prüft, ob die Achse bereits referenziert ist.
    def _is_referenced(self):
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# Das ist die Achse, auf der die Stage angesprochen wird.
            referenced = self.device.qFRF(STAGE_AXIS)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return bool(referenced[STAGE_AXIS])
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as error:
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(f"Stage reference status warning: {error}")
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Originalkommentar oder Abschnittsüberschrift.
    #for now we define the current position as zero, for quick tests (e.g. when starting the code 10 times in a row...)
# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt die aktuelle Position als Nullpunkt.
    def _define_current_position_as_zero(self):
# Das ist die Achse, auf der die Stage angesprochen wird.
        print(f"Defining current PI stage axis {STAGE_AXIS} position as 0.0")
# Das ist die Achse, auf der die Stage angesprochen wird.
        self.device.RON(STAGE_AXIS, False)
# Das ist die Achse, auf der die Stage angesprochen wird.
        self.device.POS(STAGE_AXIS, 0.0)
# Originalkommentar oder Abschnittsüberschrift.
    #then we properly reference the axis by moving the stage to zero
# `def` definiert in Python eine Funktion oder Methode. Hier: Führt die Referenzfahrt aus.
    def _reference_axis(self):
# Das ist die Achse, auf der die Stage angesprochen wird.
        print(f"Referencing PI stage axis {STAGE_AXIS} with {REFERENCE_MODE}...")
# Originalkommentar oder Abschnittsüberschrift.
        #reference the axis depending on the mode that was selected
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if REFERENCE_MODE == "FRF":
# Das ist die Achse, auf der die Stage angesprochen wird.
            self.device.FRF(STAGE_AXIS)
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
        elif REFERENCE_MODE == "FNL":
# Das ist die Achse, auf der die Stage angesprochen wird.
            self.device.FNL(STAGE_AXIS)
# `elif` prüft eine weitere Bedingung, wenn die vorherige nicht wahr war.
        elif REFERENCE_MODE == "FPL":
# Das ist die Achse, auf der die Stage angesprochen wird.
            self.device.FPL(STAGE_AXIS)
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
        else:
# Das ist die Referenzmethode für den Stage.
            raise RuntimeError(f"Unsupported PI reference mode: {REFERENCE_MODE}")
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        pitools.waitonreferencing(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.device,
# Das ist die Achse, auf der die Stage angesprochen wird.
            STAGE_AXIS,
# So lange wird höchstens auf die Referenzierung gewartet.
            timeout=REFERENCE_TIMEOUT_S
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        )
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not self._is_referenced():
# In Python bricht `raise` die Ausführung absichtlich mit einem Fehler ab.
            raise RuntimeError(
# Das ist die Achse, auf der die Stage angesprochen wird.
                f"PI stage axis {STAGE_AXIS} is still unreferenced after "
# Das ist die Referenzmethode für den Stage.
                f"{REFERENCE_MODE}"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 4. POSITION QUERYING 
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    #for the UI it is essential, that the current position is always available
# `def` definiert in Python eine Funktion oder Methode. Hier: get_position
    def get_position(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not self.connected or self.device is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return self.current_position
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# Das ist die Achse, auf der die Stage angesprochen wird.
            pos = self.device.qPOS(STAGE_AXIS) #this gibes the position
# Das ist die Achse, auf der die Stage angesprochen wird.
            self.current_position = float(pos[STAGE_AXIS])
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as error:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Stage position error: {error}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.current_position
# Originalkommentar oder Abschnittsüberschrift.
    #limits the position to the physical limits of the stage (0mm to 50 mm)
# `def` definiert in Python eine Funktion oder Methode. Hier: Begrenzt eine Position auf den erlaubten Bereich.
    def clamp_position(self, pos):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return max(self.min_position, min(self.max_position, float(pos)))
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 5. MOTION COMMANDS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    #for driving to an absolute position, does that in the background, so that the UI is still usable
# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt die Stage zu einer absoluten Position.
    def move_absolute(self, target_mm):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not self.connected or self.device is None:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = "Stage not connected"
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if self.is_moving:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = "Stage is already moving"
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# Begrenzt eine Position auf den erlaubten Bereich.
        target_mm_clamped = self.clamp_position(target_mm)
# In Python speichert `=` einen Wert in `target_position`. Zielposition der Stage.
        self.target_position = target_mm_clamped
# In Python speichert `=` hier den booleschen Startwert ein in `is_moving`. Merker, ob die Stage gerade fährt.
        self.is_moving = True
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: worker
        def worker():
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
            try:
# Das ist die Achse, auf der die Stage angesprochen wird.
                self.device.MOV(STAGE_AXIS, target_mm_clamped) #scan the motion command
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die sich wiederholt, solange die Bedingung stimmt.
                while self.device.IsMoving()[STAGE_AXIS]:
# In Python speichert `=` das Ergebnis eines Methodenaufrufs in `current_position`. aktuelle Position der Stage.
                    self.current_position = self.get_position()
# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
                    time.sleep(0.02)
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das Ergebnis eines Methodenaufrufs in `current_position`. aktuelle Position der Stage.
                self.current_position = self.get_position() #after arrival, question the position again
# Leerzeile zur besseren Lesbarkeit.

# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
            except Exception as error:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
                self.last_error = f"Stage move error: {error}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
                print(self.last_error)
# Leerzeile zur besseren Lesbarkeit.

# `finally` wird in Python immer ausgeführt, egal ob ein Fehler passiert ist.
            finally:
# In Python speichert `=` einen Wert in `is_moving`. Merker, ob die Stage gerade fährt.
                self.is_moving = False #at the end, when the stage is not moving anymore, set is_moving to false, so that the UI knows that the stage is not moving anymore
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
        threading.Thread(target=worker, daemon=True).start()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return True
# Originalkommentar oder Abschnittsüberschrift.
    #this is used for calibration, when the stage gets moving to one position, but all the commands in the UI should be blocked
# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt die Stage blockierend und wartet bis zum Ziel.
    def move_absolute_blocking(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        self,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        target_mm,
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
        timeout_s,
# In Python speichert `=` einen Wert in einer Variable.
        should_continue=None,
# In Python speichert `=` einen Wert in einer Variable.
        progress_callback=None,
# In Python speichert `=` einen Wert in einer Variable.
        poll_s=0.05
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
    ):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not self.connected or self.device is None:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = "Stage not connected"
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# Begrenzt eine Position auf den erlaubten Bereich.
        target_mm_clamped = self.clamp_position(target_mm)
# In Python speichert `=` einen Wert in `target_position`. Zielposition der Stage.
        self.target_position = target_mm_clamped
# In Python speichert `=` hier den booleschen Startwert ein in `is_moving`. Merker, ob die Stage gerade fährt.
        self.is_moving = True
# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
        deadline_s = time.time() + float(timeout_s)
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# Das ist die Achse, auf der die Stage angesprochen wird.
            self.device.MOV(STAGE_AXIS, target_mm_clamped) #starting the movement
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die sich wiederholt, solange die Bedingung stimmt.
            while True:
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
                if should_continue is not None and not should_continue(): #if the ui signals, the movement should be stopped, stop
# Stoppt die Stage sofort.
                    self.stop()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                    return False
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                position_mm = self.get_position()
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
                if progress_callback is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    progress_callback(position_mm)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
                if abs(position_mm - target_mm_clamped) <= MOVE_POSITION_TOLERANCE_MM: #if the position is reached within the tolerance, stop
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                    return True
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
                try:
# Das ist die Achse, auf der die Stage angesprochen wird.
                    on_target = self.device.qONT(STAGE_AXIS) #check if the stage is on target
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
                    if bool(on_target[STAGE_AXIS]):
# In Python speichert `=` das Ergebnis eines Methodenaufrufs in `current_position`. aktuelle Position der Stage.
                        self.current_position = self.get_position()
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
                        if progress_callback is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                            progress_callback(self.current_position)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                        return True
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
                except Exception:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    pass
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
                if time.time() >= deadline_s:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
                    self.last_error = (
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        f"Stage move timeout at {position_mm:.6f} mm "
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                        f"towards {target_mm_clamped:.6f} mm"
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    )
# In Python gibt `print(...)` eine Meldung im Terminal aus.
                    print(self.last_error)
# Stoppt die Stage sofort.
                    self.stop()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                    return False
# Leerzeile zur besseren Lesbarkeit.

# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
                time.sleep(poll_s)
# Leerzeile zur besseren Lesbarkeit.

# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as error:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Stage move error: {error}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# Stoppt die Stage sofort.
            self.stop()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `finally` wird in Python immer ausgeführt, egal ob ein Fehler passiert ist.
        finally:
# In Python speichert `=` hier den booleschen Startwert aus in `is_moving`. Merker, ob die Stage gerade fährt.
            self.is_moving = False
# Originalkommentar oder Abschnittsüberschrift.
    #moves stage by relative distance
# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt die Stage relativ um eine Strecke weiter.
    def move_relative(self, distance_mm):
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        current = self.get_position()
# In Python berechnet `=` einen Wert und speichert ihn in einer Variable.
        target = current + distance_mm
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.move_absolute(target)
# Originalkommentar oder Abschnittsüberschrift.
    #single steps
# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt die Stage einen Schritt vorwärts.
    def step_positive(self):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.move_relative(self.step_size)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt die Stage einen Schritt rückwärts.
    def step_negative(self):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.move_relative(-self.step_size)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt die Stage an die Maximalposition.
    def move_to_max(self):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.move_absolute(self.max_position)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt die Stage an die Minimalposition.
    def move_to_min(self):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.move_absolute(self.min_position)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 6. VELOCITY 
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    #sets step size for the manual buttons
# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt die Schrittweite für die manuellen Buttons.
    def set_step_size(self, step_size):
# In Python speichert `=` einen Wert in `step_size`. Schrittweite für manuelle Fahrten.
        self.step_size = float(step_size)
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt die Stage-Geschwindigkeit.
    def set_velocity(self, vel=None, acceleration_mm_s2=None):
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if vel is not None:
# In Python speichert `=` einen Wert in `velocity`. gesetzte Fahrgeschwindigkeit.
            self.velocity = float(vel)
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if acceleration_mm_s2 is None:
# In Python speichert `=` einen Wert in `acceleration`. gesetzte Beschleunigung.
                self.acceleration = 0.0
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` einen Wert in `acceleration`. gesetzte Beschleunigung.
                self.acceleration = abs(float(acceleration_mm_s2))
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if self.connected and self.device is not None:
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
                try:
# Das ist die Achse, auf der die Stage angesprochen wird.
                    self.device.VEL(STAGE_AXIS, self.velocity) #send velocity command to hardware
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
                except Exception as error:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
                    self.last_error = f"Stage velocity error: {error}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
                    print(self.last_error)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                    return False
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return True
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.velocity
# Originalkommentar oder Abschnittsüberschrift.
    #stops the stage (emergency stop when UI stop button is pressed)
# `def` definiert in Python eine Funktion oder Methode. Hier: Stoppt die Stage sofort.
    def stop(self):
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not self.connected or self.device is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.device.STP()
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except GCSError as error:
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if error != gcserror.E10_PI_CNTR_STOP:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
                self.last_error = f"Stage stop error: {error}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
                print(self.last_error)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return False
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as error:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Stage stop error: {error}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `is_moving`. Merker, ob die Stage gerade fährt.
        self.is_moving = False #adjusts the position to the point where the stage stopped
# In Python speichert `=` das Ergebnis eines Methodenaufrufs in `current_position`. aktuelle Position der Stage.
        self.current_position = self.get_position()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return True
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 7. CLEANUP
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt die Verbindung sauber.
    def close(self):
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if self.device is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.device.CloseConnection()
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as error:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Stage close error: {error}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# `finally` wird in Python immer ausgeführt, egal ob ein Fehler passiert ist.
        finally:
# In Python speichert `=` hier den booleschen Startwert aus in `connected`. Verbindungsstatus der Hardware.
            self.connected = False
# In Python speichert `=` hier den booleschen Startwert aus in `is_moving`. Merker, ob die Stage gerade fährt.
            self.is_moving = False
# In Python speichert `=` einen Wert in `connection_description`. Beschreibung des verbundenen Geräts.
            self.connection_description = ""
# In Python speichert `=` hier erstmal keinen Wert in `device`. Hardwareobjekt der Stage.
            self.device = None
