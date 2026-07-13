# Originalkommentar oder Abschnittsüberschrift.
# TABLE OF CONTENTS
# Originalkommentar oder Abschnittsüberschrift.
# 1. Imports and CLR bindings
# Originalkommentar oder Abschnittsüberschrift.
# 2. StageController class and connection
# Originalkommentar oder Abschnittsüberschrift.
# 3. Reference and homing helpers
# Originalkommentar oder Abschnittsüberschrift.
# 4. Position querying and limits
# Originalkommentar oder Abschnittsüberschrift.
# 5. Motion commands (absolute, relative)
# Originalkommentar oder Abschnittsüberschrift.
# 6. Velocity and parameter configurations
# Originalkommentar oder Abschnittsüberschrift.
# 7. Cleanup and connection close
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 1. IMPORTS AND CLR BINDINGS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import time
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import threading
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
import clr
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
from System import Decimal
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI.dll")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.GenericMotorCLI.dll")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.IntegratedStepperMotorsCLI.dll")
# Leerzeile zur besseren Lesbarkeit.

# In Python wird diese Zeile so ausgeführt, wie sie da steht.
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage
# Leerzeile zur besseren Lesbarkeit.

# Das ist die gewünschte Beschleunigung für den Stage.
REQUESTED_ACCELERATION = 1.0
# Das ist ein Ersatzwert für die Beschleunigung.
FALLBACK_MOVING_ACCELERATION = 1.0
# Das ist die kleinste erlaubte Beschleunigung.
MIN_ACCELERATION = 0.5
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 2. STAGECONTROLLER CLASS AND CONNECTION
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `class` definiert in Python eine Klasse. Hier entsteht `StageController` als Bauplan für ein Objekt.
class StageController:
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: __init__
    def __init__(self, serial_no="45517804"):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `serial_no`. Seriennummer des Stage-Geräts.
        self.serial_no = serial_no
# In Python speichert `=` hier erstmal keinen Wert in `device`. Hardwareobjekt der Stage.
        self.device = None
# In Python speichert `=` hier den booleschen Startwert aus in `connected`. Verbindungsstatus der Hardware.
        self.connected = False
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
        self.last_error = ""
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `current_position`. aktuelle Position der Stage.
        self.current_position = 0.0
# In Python speichert `=` einen Wert in `target_position`. Zielposition der Stage.
        self.target_position = 0.0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `step_size`. Schrittweite für manuelle Fahrten.
        self.step_size = 0.001
# In Python speichert `=` einen Wert in `velocity`. gesetzte Fahrgeschwindigkeit.
        self.velocity = 0.0006
# Das ist die gewünschte Beschleunigung für den Stage.
        self.requested_acceleration = REQUESTED_ACCELERATION
# In Python speichert `=` einen Wert in `acceleration`. gesetzte Beschleunigung.
        self.acceleration = 0.0
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den booleschen Startwert aus in `is_moving`. Merker, ob die Stage gerade fährt.
        self.is_moving = False
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `min_position`. minimale erlaubte Position.
        self.min_position = 0.0
# In Python speichert `=` einen Wert in `max_position`. maximale erlaubte Position.
        self.max_position = 300.0
# In Python speichert `=` hier den booleschen Startwert ein in `home_on_connect`. Merker, ob nach dem Verbinden gehomed wird.
        self.home_on_connect = True
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Sucht nach angeschlossenen Thorlabs-Geräten.
    def _get_discovered_serial_numbers(self):
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            DeviceManagerCLI.BuildDeviceList()
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            device_list = DeviceManagerCLI.GetDeviceList()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if device_list is None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return []
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
            try:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                count = int(getattr(device_list, "Count", 0))
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
            except Exception:
# In Python speichert `=` einen Startwert in einer Variable.
                count = None
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if count is not None:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return [
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                    str(device_list[i])
# `for` startet in Python eine Schleife über mehrere Werte.
                    for i in range(count)
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
                    if str(device_list[i]).strip()
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                ]
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return [str(item) for item in list(device_list) if str(item).strip()]
# Leerzeile zur besseren Lesbarkeit.

# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as e:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Could not enumerate Thorlabs devices: {e}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return []
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Wählt die zu benutzende Seriennummer aus.
    def _resolve_serial_number(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
        configured_serial = str(self.serial_no or "").strip()
# Sucht nach angeschlossenen Thorlabs-Geräten.
        discovered_serials = self._get_discovered_serial_numbers()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if configured_serial and configured_serial in discovered_serials:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return configured_serial
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if discovered_serials:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return discovered_serials[0]
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if configured_serial:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return configured_serial
# Leerzeile zur besseren Lesbarkeit.

# In Python bricht `raise` die Ausführung absichtlich mit einem Fehler ab.
        raise RuntimeError("No Thorlabs stage serial number available")
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    #connects the actual motor to the software
# `def` definiert in Python eine Funktion oder Methode. Hier: Stellt die Verbindung zur Mess- oder Stage-Hardware her.
    def connect(self):
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = ""
# Wählt die zu benutzende Seriennummer aus.
            resolved_serial = self._resolve_serial_number()
# In Python speichert `=` einen Wert in `serial_no`. Seriennummer des Stage-Geräts.
            self.serial_no = resolved_serial
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `device`. Hardwareobjekt der Stage.
            self.device = LongTravelStage.CreateLongTravelStage(
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                resolved_serial
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            )
# Leerzeile zur besseren Lesbarkeit.

# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(f"Connect to Thorlabs stage {resolved_serial}...")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.device.Connect(resolved_serial)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if not bool(getattr(self.device, "IsConnected", False)):
# Stellt die Verbindung zur Mess- oder Stage-Hardware her.
                raise RuntimeError("Device is not connected after Connect()")
# Leerzeile zur besseren Lesbarkeit.

# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
            time.sleep(1)
# Leerzeile zur besseren Lesbarkeit.

# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print("StartPolling...")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.device.StartPolling(250)
# Leerzeile zur besseren Lesbarkeit.

# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
            time.sleep(0.5)
# Leerzeile zur besseren Lesbarkeit.

# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print("EnableDevice...")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.device.EnableDevice()
# Leerzeile zur besseren Lesbarkeit.

# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
            time.sleep(0.5)
# Leerzeile zur besseren Lesbarkeit.

# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print("Wait settings...")
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if not self.device.IsSettingsInitialized():
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.device.WaitForSettingsInitialized(10000)
# Leerzeile zur besseren Lesbarkeit.

# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print("Load motor configuration...")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.device.LoadMotorConfiguration(resolved_serial)
# Leerzeile zur besseren Lesbarkeit.

# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
            time.sleep(1)
# Leerzeile zur besseren Lesbarkeit.

# Liest Daten von der Hardware.
            self._wait_until_ready()
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if self.home_on_connect:
# In Python gibt `print(...)` eine Meldung im Terminal aus.
                print("Homing stage...")
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.device.Home(180000)
# Liest Daten von der Hardware.
                self._wait_until_ready()
# In Python gibt `print(...)` eine Meldung im Terminal aus.
                print("Homing complete")
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python gibt `print(...)` eine Meldung im Terminal aus.
                print("Homing disabled, skipping homing.")
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` hier den booleschen Startwert ein in `connected`. Verbindungsstatus der Hardware.
            self.connected = True
# In Python speichert `=` das Ergebnis eines Methodenaufrufs in `current_position`. aktuelle Position der Stage.
            self.current_position = self.get_position()
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return True
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #in case of failure (cable unplugged, ...)
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as e:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Stage connection error: {e}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# In Python speichert `=` hier den booleschen Startwert aus in `connected`. Verbindungsstatus der Hardware.
            self.connected = False
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 3. REFERENCE AND HOMING HELPERS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Wartet, bis die Thorlabs-Hardware bereit ist.
    def _wait_until_ready(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
        time.sleep(2)
# Leerzeile zur besseren Lesbarkeit.

# `for` startet in Python eine Schleife über mehrere Werte.
        for _ in range(50):
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
            try:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                _ = self.device.Position
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return True
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            except:
# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
                time.sleep(0.1)
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return False
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: Fragt ab, ob die Stage noch referenziert werden muss.
    def needs_homing(self):
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return bool(self.device.NeedsHoming)
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as e:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Could not query NeedsHoming: {e}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 4. POSITION QUERYING AND LIMITS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
    #for the UI it is essential, that the current position is always available
# `def` definiert in Python eine Funktion oder Methode. Hier: get_position
    def get_position(self):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not self.connected:
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return self.current_position
# Leerzeile zur besseren Lesbarkeit.

# `for` startet in Python eine Schleife über mehrere Werte.
        for _ in range(5):
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
            try:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                pos_str = str(self.device.Position).replace(",", ".") #this gives the position
# In Python speichert `=` einen Wert in `current_position`. aktuelle Position der Stage.
                self.current_position = float(pos_str)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return self.current_position
# Originalkommentar oder Abschnittsüberschrift.
            #in case of failure (cable unplugged, ...)
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
            except Exception as e:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
                self.last_error = f"get_position error: {e}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
                print(self.last_error)
# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
                time.sleep(0.2)
# Leerzeile zur besseren Lesbarkeit.

# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.current_position
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    #limits the position to the physical limits of the stage (0.0 mm to 300.0 mm)
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
        if not self.connected:
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

# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
        self.last_error = ""
# Begrenzt eine Position auf den erlaubten Bereich.
        target_mm = self.clamp_position(target_mm)
# In Python speichert `=` einen Wert in `target_position`. Zielposition der Stage.
        self.target_position = target_mm
# In Python speichert `=` hier den booleschen Startwert ein in `is_moving`. Merker, ob die Stage gerade fährt.
        self.is_moving = True
# Leerzeile zur besseren Lesbarkeit.

# `def` definiert in Python eine Funktion oder Methode. Hier: worker
        def worker():
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
            try:
# In Python wandelt `Decimal(...)` eine Zahl in ein Genauigkeitsformat für das Hardware-API um.
                self.device.MoveTo(Decimal(float(target_mm)), 180000) #scan the motion command
# In Python speichert `=` das Ergebnis eines Methodenaufrufs in `current_position`. aktuelle Position der Stage.
                self.current_position = self.get_position() #after arrival, question the position again
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
            #in case of failure (cable unplugged, ...)
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
            except Exception as e:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
                self.last_error = f"Move error: {e}"
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
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    #moves stage by relative distance
# `def` definiert in Python eine Funktion oder Methode. Hier: Fährt die Stage relativ um eine Strecke weiter.
    def move_relative(self, delta):
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
        return self.move_absolute(self.get_position() + delta)
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 6. VELOCITY AND PARAMETER CONFIGURATIONS
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Setzt die Stage-Geschwindigkeit.
    def set_velocity(self, vel=None, acceleration_mm_s2=None):
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if vel is None:
# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
            try:
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
                if self.connected:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                    params = self.device.GetVelocityParams()
# In Python speichert `=` einen Wert in `velocity`. gesetzte Fahrgeschwindigkeit.
                    self.velocity = float(str(params.MaxVelocity).replace(",", "."))
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return self.velocity
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
            except Exception as e:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
                self.last_error = f"Get velocity error: {e}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
                print(self.last_error)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
                return self.velocity
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if not self.connected:
# In Python speichert `=` einen Wert in `velocity`. gesetzte Fahrgeschwindigkeit.
            self.velocity = abs(float(vel))
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if acceleration_mm_s2 is None:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                requested_acceleration = self.requested_acceleration
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                requested_acceleration = abs(float(acceleration_mm_s2))
# In Python speichert `=` einen Wert in `requested_acceleration`. angeforderte Beschleunigung für die Hardware.
            self.requested_acceleration = requested_acceleration
# In Python speichert `=` einen Wert in `acceleration`. gesetzte Beschleunigung.
            self.acceleration = requested_acceleration
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return True
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            params = self.device.GetVelocityParams()
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            params.MaxVelocity = Decimal(abs(float(vel)))
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if acceleration_mm_s2 is None:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                requested_acceleration = self.requested_acceleration
# `else` läuft in Python, wenn keine der vorherigen Bedingungen zutrifft.
            else:
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
                requested_acceleration = abs(float(acceleration_mm_s2))
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
            # Ensure minimum acceleration for Thorlabs hardware
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if requested_acceleration < MIN_ACCELERATION:
# Das ist die kleinste erlaubte Beschleunigung.
                requested_acceleration = MIN_ACCELERATION
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Wert in `requested_acceleration`. angeforderte Beschleunigung für die Hardware.
            self.requested_acceleration = requested_acceleration
# In Python speichert `=` einen Wert in `acceleration`. gesetzte Beschleunigung.
            self.acceleration = requested_acceleration
# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
            params.Acceleration = Decimal(self.acceleration)
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
            self.device.SetVelocityParams(params) #send velocity command to hardware
# In Python speichert `=` einen Wert in `velocity`. gesetzte Fahrgeschwindigkeit.
            self.velocity = vel
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return True
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #in case of failure (cable unplugged, ...)
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as e:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Velocity error: {e}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# `return` gibt in Python einen Wert zurück oder beendet die Funktion.
            return False
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
    #stops the stage (emergency stop when UI stop button is pressed)
# `def` definiert in Python eine Funktion oder Methode. Hier: Stoppt die Stage sofort.
    def stop(self):
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` einen Startwert in einer Variable.
        stopped = False
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if self.connected:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.device.StopImmediate()
# In Python speichert `=` einen Startwert in einer Variable.
                stopped = True
# Originalkommentar oder Abschnittsüberschrift.
        #in case of failure (cable unplugged, ...)
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as e:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Stop error: {e}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
        if stopped:
# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
            time.sleep(0.05)
# In Python speichert `=` einen Wert in `is_moving`. Merker, ob die Stage gerade fährt.
            self.is_moving = False #adjusts the position to the point where the stage stopped
# In Python speichert `=` das Ergebnis eines Methodenaufrufs in `current_position`. aktuelle Position der Stage.
            self.current_position = self.get_position()
# In Python speichert `=` einen Wert in `target_position`. Zielposition der Stage.
            self.target_position = self.current_position
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# Originalkommentar oder Abschnittsüberschrift.
# 7. CLEANUP AND CONNECTION CLOSE
# Originalkommentar oder Abschnittsüberschrift.
# -----------------------------------------------------------------------------
# `def` definiert in Python eine Funktion oder Methode. Hier: Schließt die Verbindung sauber.
    def close(self):
# Leerzeile zur besseren Lesbarkeit.

# `try` startet in Python einen Schutzblock für fehleranfälligen Code.
        try:
# `if` prüft in Python eine Bedingung und führt dann den Block aus.
            if self.device is not None:
# In Python wird diese Zeile so ausgeführt, wie sie da steht.
                self.device.StopPolling()
# Stellt die Verbindung zur Mess- oder Stage-Hardware her.
                self.device.Disconnect()
# In Python speichert `=` hier den booleschen Startwert aus in `connected`. Verbindungsstatus der Hardware.
                self.connected = False
# Leerzeile zur besseren Lesbarkeit.

# Originalkommentar oder Abschnittsüberschrift.
        #in case of failure (cable unplugged, ...)
# `except` fängt den Fehler ab, falls im `try`-Block etwas schiefgeht.
        except Exception as e:
# In Python speichert `=` einen Wert in `last_error`. letzte Fehlermeldung.
            self.last_error = f"Close error: {e}"
# In Python gibt `print(...)` eine Meldung im Terminal aus.
            print(self.last_error)
# Leerzeile zur besseren Lesbarkeit.

# In Python bedeutet das: Dieser Block läuft nur beim direkten Start der Datei.
if __name__ == "__main__":
# Leerzeile zur besseren Lesbarkeit.

# In Python speichert `=` das Ergebnis eines Ausdrucks oder Methodenaufrufs.
    stage = StageController("45517804")
# Leerzeile zur besseren Lesbarkeit.

# `if` prüft in Python eine Bedingung und führt dann den Block aus.
    if stage.connect():
# Leerzeile zur besseren Lesbarkeit.

# In Python gibt `print(...)` eine Meldung im Terminal aus.
        print("Position:", stage.get_position())
# Leerzeile zur besseren Lesbarkeit.

# Setzt die Stage-Geschwindigkeit.
        stage.set_velocity(20.0)
# Leerzeile zur besseren Lesbarkeit.

# Fährt die Stage zu einer absoluten Position.
        stage.move_absolute(150.0)
# Leerzeile zur besseren Lesbarkeit.

# `while` startet in Python eine Schleife, die sich wiederholt, solange die Bedingung stimmt.
        while stage.is_moving:
# In Python pausiert `time.sleep(...)` die Ausführung für eine kurze Zeit.
            time.sleep(0.1)
# Leerzeile zur besseren Lesbarkeit.

# In Python gibt `print(...)` eine Meldung im Terminal aus.
        print("Final position:", stage.get_position())
# Leerzeile zur besseren Lesbarkeit.

# Schließt die Verbindung sauber.
        stage.close()
