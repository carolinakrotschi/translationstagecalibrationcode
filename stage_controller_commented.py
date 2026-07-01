# -*- coding: utf-8 -*-
# =============================================================================
# KOMMENTIERTE MOTORSTEUERUNG (STAGE CONTROLLER)
# Dieses Dokument ist eine exakte Kopie von stage_controller.py, jedoch mit 
# sehr einfachen und ausführlichen Erklärungen für Einsteiger ohne Programmierkenntnisse.
# =============================================================================

# INHALTSVERZEICHNIS
# 1. Importierte Hilfsbibliotheken (Zusatzfunktionen aus Python)
# 2. Globale Voreinstellungen (Konstanten)
# 3. Hauptklasse "StageController" und deren Variablen
# 4. Verbindungsfunktionen (Motor mit dem Computer verbinden)
# 5. Referenzierung & Kalibrierung (Dem Motor sagen, wo er steht)
# 6. Positionsabfragen & Schutzlimits (Wo steht der Motor und wie weit darf er?)
# 7. Bewegungsbefehle (Wie fährt der Motor?)
# 8. Konfigurationen (Geschwindigkeit und Schrittweite einstellen)
# 9. Not-Aus & Verbindungsabbau (Sicherheit und Aufräumen)


# =============================================================================
# Sektion 1: Importierte Hilfsbibliotheken
# =============================================================================
# Hier laden wir vorgefertigte Funktionen, die nicht standardmäßig geladen sind.
# Das ist wie Werkzeug, das wir für die Arbeit bereitstellen.

import threading  # Ermöglicht das Ausführen von Dingen im Hintergrund (Multitasking), damit die Programmoberfläche nicht einfriert.
import time       # Ermöglicht es dem Programm, Zeitverzögerungen einzubauen (z.B. kurzes Warten).

# Dies ist die offizielle Hersteller-Bibliothek von PI (Physik Instrumente).
# Sie enthält die Befehle, die die Elektronik des Motors versteht.
from pipython import GCSError, GCSDevice, gcserror, pitools


# =============================================================================
# Sektion 2: Globale Voreinstellungen (Konstanten)
# =============================================================================
# Diese Werte sind im gesamten Dokument fest vorgegeben und ändern sich nicht.

STAGE_AXIS = "1"                     # Die Nummer der Motorachse am Controller. Meistens gibt es nur eine Achse (Achse "1").
STAGE_CONTROLLER_NAME = ""           # Der Name des Motorcontrollers (leer, da der automatische Finder genutzt wird).
AUTO_REFERENCE_ON_CONNECT = False    # Bestimmt, ob der Motor sich beim Verbinden sofort physikalisch kalibrieren soll.
DEFINE_POSITION_IF_UNREFERENCED = True # Falls der Motor nicht kalibriert ist, wird seine jetzige Position einfach als Nullpunkt definiert.
REFERENCE_MODE = "FRF"               # Die Methode zur Nullpunktsuche (FRF ist die Standard-Referenzfahrt des Herstellers).
REFERENCE_TIMEOUT_S = 180            # Maximale Wartezeit für die Kalibrierung (3 Minuten), bevor das Programm einen Fehler meldet.
MOVE_POSITION_TOLERANCE_MM = 0.000002 # Genauigkeits-Toleranz (2 Nanometer). Liegt die Position so nah am Ziel, gilt die Fahrt als beendet.


# =============================================================================
# Sektion 3: Hauptklasse "StageController"
# =============================================================================
# Eine Klasse ist wie ein Bauplan. Sie bündelt alle Funktionen und Daten,
# die mit der Steuerung des Tisches zu tun haben.

class StageController:

    # Das ist der Initialisierer (das Start-Rezept). Er wird aufgerufen,
    # wenn wir die Motorsteuerung im Hauptprogramm erstellen.
    def __init__(self, controller_name=STAGE_CONTROLLER_NAME):
        # Hier legen wir Variablen (Zustände) an, die sich das Programm merkt:
        self.controller_name = controller_name  # Speichert den Controllernamen.
        self.device = None                      # Das eigentliche Verbindungsobjekt zum Motor (anfangs leer).
        self.connected = False                  # Merkt sich, ob die Verbindung zum Motor steht (Ja/Nein).
        self.last_error = ""                    # Speichert die letzte Fehlermeldung, falls etwas schiefgeht.
        self.connection_description = ""        # Beschreibung der Verbindung (z. B. welcher USB-Anschluss verwendet wird).
        self.current_position = 0.0             # Die aktuelle Position des Tisches (in Millimetern).
        self.target_position = 0.0              # Die gewünschte Zielposition des Tisches (in Millimetern).
        self.step_size = 0.020000000            # Die Standard-Schrittweite für manuelle Klicks (20 Mikrometer).
        self.velocity = 0.0006                  # Die Standard-Geschwindigkeit (0,6 Mikrometer pro Sekunde - sehr langsam für Messungen).
        self.is_moving = False                  # Merkt sich, ob der Motor gerade fährt (Ja/Nein).
        self.min_position = 0                   # Die absolut minimal erlaubte Position (0 mm - Schutzgrenze).
        self.max_position = 50                  # Die absolut maximal erlaubte Position (50 mm - Schutzgrenze).


# =============================================================================
# Sektion 4: Verbindungsfunktionen
# =============================================================================

    # Diese Funktion stellt die Verbindung zum physikalischen Motor her.
    # WIESO: Ohne Verbindung können wir keine Befehle senden. Wir müssen sicherstellen,
    # dass das Gerät angeschlossen, eingeschaltet und bereit zur Bewegung ist.
    def connect(self):
        # Wenn wir schon verbunden sind, müssen wir nichts tun und geben Erfolg (True) zurück.
        if self.connected:
            return True

        self.last_error = ""

        # SICHERHEITSCHECK: Die Verbindung zum PI-Controller MUSS zwingend im Haupt-Thread (Hauptprozess) 
        # der Benutzeroberfläche gestartet werden. Läuft das im Hintergrund, schlägt die Treiberkommunikation fehl.
        if threading.current_thread() is not threading.main_thread():
            self.last_error = "Stage connection must be started from the main thread"
            print(self.last_error)
            return False

        try:
            # Wir erstellen das softwareseitige Gerät über die Hersteller-Bibliothek
            self.device = GCSDevice(self.controller_name)
            
            # Wir rufen unsere interne Suchfunktion auf, um den Motor an USB/Netzwerk zu finden
            self._connect_first_available_device()
            
            # Wir bereiten die Achse vor (Servo einschalten, Nullpunkt prüfen)
            self._prepare_axis_for_motion()
            
            # Wir fragen die aktuelle Position des Motors ab
            pos = self.device.qPOS(STAGE_AXIS)
            self.connected = True
            self.current_position = float(pos[STAGE_AXIS])
            
            # Wir setzen die Standard-Geschwindigkeit für Bewegungen
            self.set_velocity(self.velocity)
            return True

        except Exception as error:
            # Falls ein Fehler auftritt (z.B. Kabel gezogen), fangen wir ihn hier ab,
            # damit das Programm nicht abstürzt.
            self.last_error = f"Stage connection error: {error}"
            print(self.last_error)
            self.connected = False
            self.is_moving = False

            # Wenn die Verbindung fehlschlug, versuchen wir, den Kommunikationskanal sauber zu schließen.
            try:
                if self.device is not None:
                    self.device.CloseConnection()
            except Exception:
                pass

            self.device = None
            return False

    # Sucht automatisch nach einem angeschlossenen Motor.
    # WIESO: Damit der Benutzer nicht raten muss, an welchem USB-Port oder welcher IP-Adresse
    # das Gerät angeschlossen ist. Die Funktion sucht erst nach USB-Geräten, dann im Netzwerk.
    def _connect_first_available_device(self):
        errors = []

        # Schritt A: Suchen nach USB-Geräten
        try:
            usb_devices = list(self.device.EnumerateUSB())
        except Exception as error:
            usb_devices = []
            errors.append(f"USB enumeration failed: {error}")

        # Wenn ein USB-Gerät gefunden wurde, verbinden wir uns mit dem ersten in der Liste
        if usb_devices:
            self.connection_description = usb_devices[0]
            print(f"Connecting first PI USB stage: {self.connection_description}")
            self.device.ConnectUSB(self.connection_description)
            return

        # Schritt B: Suchen nach Netzwerk-Geräten (TCP/IP), falls kein USB-Gerät da war
        try:
            tcpip_devices = list(self.device.EnumerateTCPIPDevices())
        except Exception as error:
            tcpip_devices = []
            errors.append(f"TCP/IP enumeration failed: {error}")

        # Wenn ein Netzwerkgerät gefunden wurde, verbinden wir uns damit
        if tcpip_devices:
            self.connection_description = tcpip_devices[0]
            print(f"Connecting first PI TCP/IP stage: {self.connection_description}")
            self.device.ConnectTCPIPByDescription(self.connection_description)
            return

        # Wenn gar nichts gefunden wurde, brechen wir mit einer Fehlermeldung ab
        detail = "; ".join(errors)
        if detail:
            raise RuntimeError(f"No PI stage found via USB or TCP/IP ({detail})")

        raise RuntimeError("No PI stage found via USB or TCP/IP")


# =============================================================================
# Sektion 5: Referenzierung & Kalibrierung
# =============================================================================

    # Bereitet den Motor physikalisch auf Bewegungen vor.
    # WIESO: Ein Präzisionsmotor muss nach dem Einschalten wissen, wo er steht (Nullpunkt).
    # Diese Funktion schaltet den Motorstrom ein (Servo) und stellt sicher, dass der Nullpunkt kalibriert ist.
    def _prepare_axis_for_motion(self):
        # 1. Motorstrom (Servo) einschalten, damit sich die Achse bewegen lässt
        self._set_servo(True)

        # 2. Prüfen, ob der Motor weiß, wo er steht (ob er "referenziert" ist)
        if not self._is_referenced():
            if DEFINE_POSITION_IF_UNREFERENCED:
                # Schnelle Methode: Die jetzige Position wird einfach als Nullpunkt definiert.
                self._define_current_position_as_zero()
            elif AUTO_REFERENCE_ON_CONNECT:
                # Gründliche Methode: Motor fährt an den physikalischen Endanschlag, um den Nullpunkt zu suchen.
                self._reference_axis()
            else:
                raise RuntimeError(
                    f"PI stage axis {STAGE_AXIS} is not referenced"
                )

        # 3. Nochmals Servo aktivieren zur Sicherheit
        self._set_servo(True)

    # Schaltet den Servomotor (den Haltestrom) ein oder aus.
    # WIESO: Nur bei eingeschaltetem Servo hält der Motor seine Position stabil und führt Fahrbefehle aus.
    # Ist er aus, ist der Motor entspannt und lässt sich (falls nicht selbsthemmend) per Hand verschieben.
    def _set_servo(self, enabled):
        try:
            self.device.SVO(STAGE_AXIS, bool(enabled))
        except Exception as error:
            print(f"Stage servo warning: {error}")

    # Fragt den Controller, ob der Nullpunkt der Achse kalibriert ist.
    # WIESO: Bevor wir präzise mm-Befehle senden, müssen wir sicherstellen, dass das Koordinatensystem stimmt.
    def _is_referenced(self):
        try:
            referenced = self.device.qFRF(STAGE_AXIS)
            return bool(referenced[STAGE_AXIS])
        except Exception as error:
            print(f"Stage reference status warning: {error}")
            return False

    # Definiert die aktuelle physikalische Position des Tisches künstlich als 0.0 mm.
    # WIESO: Erspart uns die langsame Referenzfahrt zum Endanschlag. Sehr nützlich für schnelle Tests,
    # da wir die aktuelle Position einfach als relativen Startpunkt festlegen.
    def _define_current_position_as_zero(self):
        print(f"Defining current PI stage axis {STAGE_AXIS} position as 0.0")
        self.device.RON(STAGE_AXIS, False) # Referenzierungs-Modus temporär abschalten
        self.device.POS(STAGE_AXIS, 0.0)   # Aktuellen Punkt als Null definieren

    # Führt eine echte, physikalische Fahrt zum Nullpunkt-Sensor durch.
    # WIESO: Nur so kennt der Motor seinen echten, absolut exakten physikalischen Nullpunkt.
    # Diese Funktion blockiert das Programm, bis der Endanschlag gefunden wurde (Referenzfahrt).
    def _reference_axis(self):
        print(f"Referencing PI stage axis {STAGE_AXIS} with {REFERENCE_MODE}...")

        # Je nach Modus senden wir den entsprechenden Fahrbefehl an den Controller
        if REFERENCE_MODE == "FRF":
            self.device.FRF(STAGE_AXIS)
        elif REFERENCE_MODE == "FNL":
            self.device.FNL(STAGE_AXIS)
        elif REFERENCE_MODE == "FPL":
            self.device.FPL(STAGE_AXIS)
        else:
            raise RuntimeError(f"Unsupported PI reference mode: {REFERENCE_MODE}")

        # Das Programm wartet hier aktiv, bis der Motor den Sensor gefunden hat (oder Timeout)
        pitools.waitonreferencing(
            self.device,
            STAGE_AXIS,
            timeout=REFERENCE_TIMEOUT_S
        )

        # Sicherheitstest: Ist die Achse danach wirklich kalibriert?
        if not self._is_referenced():
            raise RuntimeError(
                f"PI stage axis {STAGE_AXIS} is still unreferenced after "
                f"{REFERENCE_MODE}"
            )


# =============================================================================
# Sektion 6: Positionsabfragen & Schutzlimits
# =============================================================================

    # Fragt die aktuelle Position des Tisches in Millimetern ab.
    # WIESO: Wir müssen der Benutzeroberfläche und den Messroutinen ständig mitteilen,
    # wo sich der Tisch im Moment befindet.
    def get_position(self):
        if not self.connected or self.device is None:
            return self.current_position

        try:
            # Direkte Hardwareabfrage beim Controller
            pos = self.device.qPOS(STAGE_AXIS)
            self.current_position = float(pos[STAGE_AXIS])
        except Exception as error:
            self.last_error = f"Stage position error: {error}"
            print(self.last_error)

        return self.current_position

    # Begrenzt eine Position auf die Sicherheitsgrenzen des Tisches (0 bis 50 mm).
    # WIESO: Um zu verhindern, dass das Programm den Tisch über seine mechanischen Grenzen fährt,
    # was den Motor oder die Mechanik beschädigen würde.
    def clamp_position(self, pos):
        # Falls pos kleiner als 0 ist, wird 0 genommen. Falls pos größer als 50 ist, wird 50 genommen.
        return max(self.min_position, min(self.max_position, float(pos)))


# =============================================================================
# Sektion 7: Bewegungsbefehle
# =============================================================================

    # Fährt den Tisch an eine absolute Position (z. B. "fahre exakt auf Position 15.0 mm").
    # WIESO: Hauptfunktion zur Positionierung des Tisches während der Messungen.
    # HINWEIS: Fährt im Hintergrund (separater Thread), damit das Hauptprogramm bedienbar bleibt.
    def move_absolute(self, target_mm):
        # Sicherheitschecks:
        if not self.connected or self.device is None:
            self.last_error = "Stage not connected"
            return False

        if self.is_moving:
            self.last_error = "Stage is already moving"
            return False

        # Begrenzen der Zielposition auf den erlaubten Bereich (0-50 mm)
        target_mm_clamped = self.clamp_position(target_mm)
        self.target_position = target_mm_clamped
        self.is_moving = True

        # Das ist die eigentliche Arbeitsfunktion, die im Hintergrund ausgeführt wird
        def worker():
            try:
                # Sende den Fahrbefehl (MOV = Move absolute)
                self.device.MOV(STAGE_AXIS, target_mm_clamped)

                # Solange der Motor noch fährt, aktualisieren wir unsere Positionsvariable
                while self.device.IsMoving()[STAGE_AXIS]:
                    self.current_position = self.get_position()
                    time.sleep(0.02) # Kurze Pause, um den Prozessor nicht zu überlasten

                # Letzte Abfrage nach dem Ankommen
                self.current_position = self.get_position()

            except Exception as error:
                self.last_error = f"Stage move error: {error}"
                print(self.last_error)

            finally:
                # In jedem Fall (Erfolg oder Fehler) setzen wir den Fahrstatus wieder auf False
                self.is_moving = False

        # Hier starten wir den Hintergrundprozess (Thread)
        threading.Thread(target=worker, daemon=True).start()
        return True

    # Fährt den Tisch an eine absolute Position, wartet aber blockierend, bis der Tisch da ist.
    # WIESO: Wird für kritische Prozesse genutzt (z. B. Kalibrierung), wo das Programm erst 
    # fortfahren darf, wenn der Tisch absolut sicher seine Zielposition erreicht hat.
    def move_absolute_blocking(
        self,
        target_mm,
        timeout_s,
        should_continue=None,
        progress_callback=None,
        poll_s=0.05
    ):
        if not self.connected or self.device is None:
            self.last_error = "Stage not connected"
            return False

        target_mm_clamped = self.clamp_position(target_mm)
        self.target_position = target_mm_clamped
        self.is_moving = True
        
        # Berechnen, wann das Zeitlimit (Timeout) überschritten ist
        deadline_s = time.time() + float(timeout_s)

        try:
            # Starten der Bewegung
            self.device.MOV(STAGE_AXIS, target_mm_clamped)

            # Warteschleife
            while True:
                # Falls das Hauptprogramm signalisiert, dass abgebrochen werden soll (z. B. Not-Aus)
                if should_continue is not None and not should_continue():
                    self.stop() # Sofort anhalten
                    return False

                position_mm = self.get_position()
                
                # Falls eine Rückmeldefunktion übergeben wurde, senden wir die aktuelle Position an die UI
                if progress_callback is not None:
                    progress_callback(position_mm)

                # Sind wir nah genug am Ziel? (Weniger als 2 Nanometer Abstand)
                if abs(position_mm - target_mm_clamped) <= MOVE_POSITION_TOLERANCE_MM:
                    return True

                # Alternativ fragen wir den Controller, ob er meldet, dass er "On Target" (am Ziel) ist
                try:
                    on_target = self.device.qONT(STAGE_AXIS)
                    if bool(on_target[STAGE_AXIS]):
                        self.current_position = self.get_position()
                        if progress_callback is not None:
                            progress_callback(self.current_position)
                        return True
                except Exception:
                    pass

                # Zeitlimit-Prüfung
                if time.time() >= deadline_s:
                    self.last_error = (
                        f"Stage move timeout at {position_mm:.6f} mm "
                        f"towards {target_mm_clamped:.6f} mm"
                    )
                    print(self.last_error)
                    self.stop()
                    return False

                time.sleep(poll_s)

        except Exception as error:
            self.last_error = f"Stage move error: {error}"
            print(self.last_error)
            self.stop()
            return False

        finally:
            self.is_moving = False

    # Fährt den Tisch um eine relative Distanz weiter (z.B. "fahre 2 mm vorwärts", bezogen auf wo er jetzt steht).
    # WIESO: Erleichtert das schrittweise Justieren, da man die Zielposition nicht selbst ausrechnen muss.
    def move_relative(self, distance_mm):
        # 1. Hole aktuelle Position
        current = self.get_position()
        # 2. Berechne neues Ziel
        target = current + distance_mm
        # 3. Führe absolute Bewegung zum neuen Ziel aus
        return self.move_absolute(target)

    # Macht einen Einzelschritt in positive Richtung (vorwärts).
    # WIESO: Für die manuelle Schritt-Steuerung per Knopfdruck (>) in der GUI.
    def step_positive(self):
        return self.move_relative(self.step_size)

    # Macht einen Einzelschritt in negative Richtung (rückwärts).
    # WIESO: Für die manuelle Schritt-Steuerung per Knopfdruck (<) in der GUI.
    def step_negative(self):
        return self.move_relative(-self.step_size)

    # Fährt direkt auf die maximal erlaubte Position (50 mm).
    # WIESO: Für die Schnellwahltaste (>|) in der Benutzeroberfläche.
    def move_to_max(self):
        return self.move_absolute(self.max_position)

    # Fährt direkt auf die minimal erlaubte Position (0 mm).
    # WIESO: Für die Schnellwahltaste (|<) in der Benutzeroberfläche.
    def move_to_min(self):
        return self.move_absolute(self.min_position)


# =============================================================================
# Sektion 8: Konfigurationen
# =============================================================================

    # Ändert die Schrittweite für die manuellen Tasten.
    # WIESO: Damit der Benutzer einstellen kann, ob ein Klick auf ">" den Tisch 
    # weit bewegt (z. B. 1 mm) oder nur minimal verschiebt (z. B. 0.001 mm).
    def set_step_size(self, step_size):
        self.step_size = float(step_size)

    # Setzt die Fahrgeschwindigkeit des Tisches oder gibt sie zurück.
    # WIESO: Während der Interferogramm-Messung muss der Tisch extrem langsam fahren, 
    # beim schnellen Positionieren soll er jedoch zügig fahren.
    # Wenn "vel" leer bleibt, fragen wir nur die aktuelle Geschwindigkeit ab.
    def set_velocity(self, vel=None):
        if vel is not None:
            self.velocity = float(vel)
            if self.connected and self.device is not None:
                try:
                    # Sende den Geschwindigkeitsbefehl (VEL) an die Hardware
                    self.device.VEL(STAGE_AXIS, self.velocity)
                except Exception as error:
                    self.last_error = f"Stage velocity error: {error}"
                    print(self.last_error)
                    return False
            return True

        # Wenn kein Wert übergeben wurde, geben wir den aktuell gespeicherten Wert zurück
        return self.velocity


# =============================================================================
# Sektion 9: Not-Aus & Verbindungsabbau
# =============================================================================

    # Stoppt jegliche Bewegung des Motors augenblicklich.
    # WIESO: Das ist die wichtigste Sicherheitsfunktion! Bei Gefahr oder Klick auf "STOP STAGE"
    # muss die Achse sofort bremsen, um mechanische Beschädigungen zu verhindern.
    def stop(self):
        if not self.connected or self.device is None:
            return False

        try:
            # Sende Stopp-Signal (STP = Stop)
            self.device.STP()
        except GCSError as error:
            # Der Fehlercode E10_PI_CNTR_STOP signalisiert lediglich, dass der Tisch erfolgreich
            # gestoppt wurde (das ist eine Warnung vom Controller, kein echter Fehler).
            if error != gcserror.E10_PI_CNTR_STOP:
                self.last_error = f"Stage stop error: {error}"
                print(self.last_error)
                return False
        except Exception as error:
            self.last_error = f"Stage stop error: {error}"
            print(self.last_error)
            return False

        self.is_moving = False
        # Aktualisiere die Position auf den Punkt, an dem der Tisch stehengeblieben ist
        self.current_position = self.get_position()
        return True

    # Schließt die Verbindung zum Motorcontroller sauber.
    # WIESO: Gibt die USB- bzw. Netzwerkschnittstelle wieder frei. Falls man dies vergisst,
    # bleibt der Port blockiert und man kann sich beim nächsten Start nicht mehr verbinden.
    def close(self):
        try:
            if self.device is not None:
                # Hardwareverbindung trennen
                self.device.CloseConnection()
        except Exception as error:
            self.last_error = f"Stage close error: {error}"
            print(self.last_error)
        finally:
            # Alle Verbindungsvariablen zurücksetzen
            self.connected = False
            self.is_moving = False
            self.connection_description = ""
            self.device = None
