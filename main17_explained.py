# ANFAENGER-ERKLAERUNG: Diese Datei wurde extra sehr ausfuehrlich kommentiert.
# Lies immer zuerst die Code-Zeile und direkt darunter die Kommentarzeile mit "Erklaerung".
# Mini-Woerterbuch: self = dieses App-Fenster/Objekt; def = Funktion/Methode definieren; if = falls; else = sonst; return = zurueckgeben/beenden.
# Mini-Woerterbuch: = speichert einen Wert; == vergleicht Werte; . ruft etwas in einem Objekt auf; () startet einen Aufruf; : startet einen eingerueckten Block.
# Kommentare beginnen mit #. Python ignoriert sie komplett; sie sind nur fuer dich zum Verstehen da.

MANUAL_THRESHOLDS = False
# Erklaerung: MANUAL_THRESHOLDS bekommt mit = einen neuen Wert; Schalter fuer die Schwellenwerte: False bedeutet automatische Kalibrierung, True wuerde feste Werte benutzen.

MANUAL_DARK_THRESHOLD = 7
# Erklaerung: MANUAL_DARK_THRESHOLD bekommt mit = einen neuen Wert; fester Zahlenwert fuer dunkel, falls manuelle Schwellenwerte eingeschaltet werden.
MANUAL_BRIGHT_THRESHOLD = 25
# Erklaerung: MANUAL_BRIGHT_THRESHOLD bekommt mit = einen neuen Wert; fester Zahlenwert fuer hell, falls manuelle Schwellenwerte eingeschaltet werden.


import os
# Erklaerung: import laedt ein Zusatzmodul; os hilft bei Dateipfaden und Betriebssystem-Funktionen.
import threading
# Erklaerung: threading erlaubt Hintergrundaufgaben, damit das Fenster nicht einfriert.
import time
# Erklaerung: time liefert Zeitfunktionen wie aktuelle Uhrzeit und kurze Pausen.
import numpy as np
# Erklaerung: numpy ist eine Zahlen-/Array-Bibliothek; as np gibt ihr den kurzen Namen np.
import customtkinter as ctk
# Erklaerung: customtkinter ist die UI-Bibliothek; as ctk ist die Abkuerzung im Code.

from PIL import Image, ImageDraw
# Erklaerung: from ... import laedt nur bestimmte Teile; Image ist fuer Bilder, ImageDraw fuer Zeichnen im Bild.

from camera_handler import CameraHandler
# Erklaerung: aus camera_handler.py wird CameraHandler geladen; diese Klasse kuemmert sich um die Kamera.
from stage_controller import StageController
# Erklaerung: aus stage_controller.py wird StageController geladen; diese Klasse kuemmert sich um die Translation Stage.


current_directory = os.path.dirname(os.path.abspath(__file__))
# Erklaerung: current_directory bekommt mit = einen neuen Wert; der Ordner, in dem diese Python-Datei liegt.
dll_path = os.path.join(current_directory, "Camera")
# Erklaerung: dll_path bekommt mit = einen neuen Wert; der Pfad zum Unterordner Camera, in dem Kameradateien/DLLs liegen.

if os.path.exists(dll_path):
# Erklaerung: if prueft eine Bedingung; os.path.exists fragt, ob der Camera-Ordner wirklich existiert.
    os.add_dll_directory(dll_path)
    # Erklaerung: fuegt den Camera-Ordner zur DLL-Suche hinzu, damit die Kamera-Treiber gefunden werden.


LASER_WAVELENGTH_NM = 1576.3
# Erklaerung: LASER_WAVELENGTH_NM bekommt mit = einen neuen Wert; die Laserwellenlaenge in Nanometern.

FRINGE_DISTANCE_MM = (
# Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
    (LASER_WAVELENGTH_NM / 2) / 1_000_000/2 #licht geht ja hin und zurueck, also 0.0004mm translationstage bewegen bedeutet nur ein halber fringe 0.000788
    # Erklaerung: rechnet aus der Laserwellenlaenge die Wegstrecke pro Signalwechsel; / teilt, 1_000_000 wandelt nm in mm um.
)
# Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

SPEED_OF_LIGHT_MM_PS = 0.299792458
# Erklaerung: SPEED_OF_LIGHT_MM_PS bekommt mit = einen neuen Wert; die Lichtgeschwindigkeit in Millimeter pro Pikosekunde fuer die Zeitverzoegerung.

TEXT_COLOR = "#0A4A51"
# Erklaerung: TEXT_COLOR bekommt mit = einen neuen Wert; die Standard-Schriftfarbe als Hex-Farbcode.
GREEN_COLOR = "#1EAD4F"
# Erklaerung: GREEN_COLOR bekommt mit = einen neuen Wert; die gruene Farbe fuer Erfolg oder laufenden Zustand.
RED_COLOR = "#C0392B"
# Erklaerung: RED_COLOR bekommt mit = einen neuen Wert; die rote Farbe fuer Fehler oder Stop.
ORANGE_COLOR = "#D35400"
# Erklaerung: ORANGE_COLOR bekommt mit = einen neuen Wert; die orange Farbe fuer Warnung oder Kalibrierung.

REQUIRED_DARK_FRAMES = 3
# Erklaerung: REQUIRED_DARK_FRAMES bekommt mit = einen neuen Wert; wie viele dunkle Bilder hintereinander benoetigt werden, bevor dunkel wirklich gilt.
REQUIRED_BRIGHT_FRAMES = 3
# Erklaerung: REQUIRED_BRIGHT_FRAMES bekommt mit = einen neuen Wert; wie viele helle Bilder hintereinander benoetigt werden, bevor hell wirklich gilt.

FRINGE_COOLDOWN = 0.08
# Erklaerung: FRINGE_COOLDOWN bekommt mit = einen neuen Wert; Mindestzeit in Sekunden zwischen zwei Fringe-Zaehlern, damit nicht doppelt gezaehlt wird.


class InterferometerApp(ctk.CTk):
# Erklaerung: class erstellt einen Bauplan; InterferometerApp erbt von ctk.CTk, also von einem Fenster.

    def __init__(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; __init__ ist der Name. Initialisierung: baut das Fenster auf, verbindet Kamera/Stage und setzt Startwerte.

        super().__init__()
        # Erklaerung: ruft die Initialisierung der Elternklasse ctk.CTk auf, damit das Fenster korrekt entsteht.

        self.title("Interferometer Monitor")
        # Erklaerung: setzt den Fenstertitel; self meint dieses App-Fenster.

        self.geometry("900x1000")
        # Erklaerung: setzt die Fenstergroesse auf 900 Pixel breit und 1000 Pixel hoch.

        ctk.set_appearance_mode("light")
        # Erklaerung: stellt CustomTkinter auf helles Design.

        self.configure(fg_color="white")
        # Erklaerung: configure aendert Eigenschaften des Fensters; fg_color="white" macht den Hintergrund weiss.

        self.scroll = ctk.CTkScrollableFrame(
        # Erklaerung: erstellt einen scrollbaren Bereich von CustomTkinter. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self,
            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
            fg_color="white"
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.scroll.pack(
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            fill="both",
            # Erklaerung: fill= ist ein benanntes Argument und sagt, in welche Richtung sich das Element ausdehnen darf. Das Komma trennt diese Angabe von der naechsten.
            expand=True,
            # Erklaerung: expand= ist ein benanntes Argument und sagt, ob das Element freien Platz mitnutzt. Das Komma trennt diese Angabe von der naechsten.
            padx=2,
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand. Das Komma trennt diese Angabe von der naechsten.
            pady=2
            # Erklaerung: pady= ist ein benanntes Argument und setzt vertikalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.is_monitoring = False
        # Erklaerung: self.is_monitoring bekommt mit = einen neuen Wert; merkt sich, ob die Messung gerade laeuft.

        self.accumulated_fringes = 0
        # Erklaerung: self.accumulated_fringes bekommt mit = einen neuen Wert; zaehlt alle erkannten Interferenzstreifen seit dem letzten Reset.

        self.was_dark = False
        # Erklaerung: loescht den dunklen Zustand, damit erst wieder ein neuer Dunkel-Hell-Wechsel noetig ist.

        self.last_count_time = 0
        # Erklaerung: self.last_count_time bekommt mit = einen neuen Wert; Zeitpunkt, wann zuletzt ein Fringe gezaehlt wurde.

        self.dark_counter = 0
        # Erklaerung: setzt den Dunkel-Zaehler wieder auf null.

        self.bright_counter = 0
        # Erklaerung: setzt den Hell-Zaehler wieder auf null.

        self.intensity_history = []
        # Erklaerung: self.intensity_history bekommt mit = einen neuen Wert; Liste der letzten Intensitaetswerte zum Glaetten des Signals.

        self.dark_threshold = MANUAL_DARK_THRESHOLD
        # Erklaerung: self.dark_threshold bekommt mit = einen neuen Wert; Grenzwert, unter dem das Signal als dunkel gilt.

        self.bright_threshold = MANUAL_BRIGHT_THRESHOLD
        # Erklaerung: self.bright_threshold bekommt mit = einen neuen Wert; Grenzwert, ueber dem das Signal als hell gilt.

        self.calibrating = False
        # Erklaerung: beendet den Kalibrierungszustand.

        self.calibration_start_time = 0
        # Erklaerung: self.calibration_start_time bekommt mit = einen neuen Wert; Startzeitpunkt der Kalibrierung.

        self.calibration_values = []
        # Erklaerung: self.calibration_values bekommt mit = einen neuen Wert; Liste der Intensitaeten, die waehrend der Kalibrierung gesammelt werden.

        self.camera_handler = CameraHandler()
        # Erklaerung: self.camera_handler bekommt mit = einen neuen Wert; Objekt, das die Kamera bedient.

        self.camera_connected = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            self.camera_handler.connect()
            # Erklaerung: versucht, eine Verbindung zur Hardware herzustellen.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.stage = StageController()
        # Erklaerung: self.stage bekommt mit = einen neuen Wert; Objekt, das die elektronische Translation Stage bedient.

        self.stage_connected = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            self.stage.connect()
            # Erklaerung: versucht, eine Verbindung zur Hardware herzustellen.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.laser_wavelength_nm = LASER_WAVELENGTH_NM
        # Erklaerung: self.laser_wavelength_nm bekommt mit = einen neuen Wert; aktuelle Laserwellenlaenge, die fuer die Berechnung genutzt wird.
        self.fringe_distance_mm = self.compute_fringe_distance(
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            self.laser_wavelength_nm
            # Erklaerung: self.laser_wavelength_nm ist hier ein Wert/Parameter. aktuelle Laserwellenlaenge, die fuer die Berechnung genutzt wird.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        self.stage_start_position = 0.0
        # Erklaerung: self.stage_start_position bekommt mit = einen neuen Wert; Position der Stage am Anfang einer Bewegung.
        self.stage_reference_position = 0.0
        # Erklaerung: self.stage_reference_position bekommt mit = einen neuen Wert; Referenzposition fuer die Bewegungsanzeige.
        self.total_stage_movement = 0.0
        # Erklaerung: self.total_stage_movement bekommt mit = einen neuen Wert; gesamte bisher addierte Stage-Bewegung.
        self.stage_movement_before_move = 0.0
        # Erklaerung: self.stage_movement_before_move bekommt mit = einen neuen Wert; gespeicherte Bewegungssumme vor einer neuen Bewegung.
        self.current_stage_movement_for_compare = 0.0
        # Erklaerung: self.current_stage_movement_for_compare bekommt mit = einen neuen Wert; aktuelle gefahrene Strecke fuer den Vergleich mit der Fringe-Strecke.
        self.reset_stage_movement_after_move = False
        # Erklaerung: self.reset_stage_movement_after_move bekommt mit = einen neuen Wert; Schalter, ob die Bewegungsanzeige nach einer Bewegung zurueckgesetzt werden soll.
        self.center_stage_after_calibration_pending = False
        # Erklaerung: self.center_stage_after_calibration_pending bekommt mit = einen neuen Wert; merkt, dass die Stage nach der aktuellen Bewegung noch zur Mitte fahren soll.
        self.returning_stage_after_calibration = False
        # Erklaerung: self.returning_stage_after_calibration bekommt mit = einen neuen Wert; merkt, ob die Stage nach der Kalibrierung gerade zurueckfaehrt.
        self.calibration_motion_started = False
        # Erklaerung: self.calibration_motion_started bekommt mit = einen neuen Wert; merkt, ob die automatische Stage-Bewegung fuer die Kalibrierung schon gestartet wurde.

        ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.scroll,
            # Erklaerung: self.scroll ist hier ein Wert/Parameter. der scrollbare Hauptbereich im Fenster. Das Komma trennt diesen Wert vom naechsten.
            text="Interferometer Monitor",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 23, "bold"),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        ).pack(pady=5)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.btn = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.scroll,
            # Erklaerung: self.scroll ist hier ein Wert/Parameter. der scrollbare Hauptbereich im Fenster. Das Komma trennt diesen Wert vom naechsten.
            text="START MONITORING",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.toggle,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            width=180,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            height=30,
            # Erklaerung: height= ist ein benanntes Argument und legt die Hoehe des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            fg_color=TEXT_COLOR,
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 11, "bold")
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn.pack(pady=2)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.restart_btn = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.scroll,
            # Erklaerung: self.scroll ist hier ein Wert/Parameter. der scrollbare Hauptbereich im Fenster. Das Komma trennt diesen Wert vom naechsten.
            text="RESET",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.restart,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            width=140,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            height=28,
            # Erklaerung: height= ist ein benanntes Argument und legt die Hoehe des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            fg_color=ORANGE_COLOR
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.restart_btn.pack(pady=1)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.status = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.scroll,
            # Erklaerung: self.scroll ist hier ein Wert/Parameter. der scrollbare Hauptbereich im Fenster. Das Komma trennt diesen Wert vom naechsten.
            text="Status: Stopped",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 11),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.status.pack(pady=2)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.stage_frame = ctk.CTkFrame(
        # Erklaerung: erstellt einen Rahmen/Container fuer andere UI-Elemente. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.scroll,
            # Erklaerung: self.scroll ist hier ein Wert/Parameter. der scrollbare Hauptbereich im Fenster. Das Komma trennt diesen Wert vom naechsten.
            fg_color="#EEEEEE"
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.stage_frame.pack(
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            fill="x",
            # Erklaerung: fill= ist ein benanntes Argument und sagt, in welche Richtung sich das Element ausdehnen darf. Das Komma trennt diese Angabe von der naechsten.
            padx=5,
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand. Das Komma trennt diese Angabe von der naechsten.
            pady=4
            # Erklaerung: pady= ist ein benanntes Argument und setzt vertikalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            text="Electronic Translation Stage",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 15, "bold"),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        ).pack(pady=2)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.wavelength_entry = ctk.CTkEntry(
        # Erklaerung: erstellt ein Eingabefeld fuer Text/Zahlen. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            placeholder_text="Laser wavelength in nm",
            # Erklaerung: placeholder_text= ist ein benanntes Argument und legt den grauen Hinweistext im Eingabefeld fest. Das Komma trennt diese Angabe von der naechsten.
            width=250
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.wavelength_entry.pack(pady=1)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.
        self.wavelength_entry.insert(0, f"{self.laser_wavelength_nm:.1f}")
        # Erklaerung: fuegt Text in ein Eingabefeld ein.

        self.wavelength_button = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            text="Set wavelength",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            width=120,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.apply_wavelength,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            fg_color=TEXT_COLOR
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.wavelength_button.pack(pady=1)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.step_entry = ctk.CTkEntry(
        # Erklaerung: erstellt ein Eingabefeld fuer Text/Zahlen. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            placeholder_text="Step size in mm",
            # Erklaerung: placeholder_text= ist ein benanntes Argument und legt den grauen Hinweistext im Eingabefeld fest. Das Komma trennt diese Angabe von der naechsten.
            width=250
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.step_entry.pack(pady=1)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.
        self.step_entry.insert(
        # Erklaerung: fuegt Text in ein Eingabefeld ein. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            0,
            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
            f"{(self.fringe_distance_mm / 8):.7f}"
            # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.button_frame = ctk.CTkFrame(
        # Erklaerung: erstellt einen Rahmen/Container fuer andere UI-Elemente. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            fg_color="transparent"
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.button_frame.pack(pady=1)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            text="or",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 14, "bold"),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        ).pack(pady=3)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.target_entry = ctk.CTkEntry(
        # Erklaerung: erstellt ein Eingabefeld fuer Text/Zahlen. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            placeholder_text="Target value or distance in mm",
            # Erklaerung: placeholder_text= ist ein benanntes Argument und legt den grauen Hinweistext im Eingabefeld fest. Das Komma trennt diese Angabe von der naechsten.
            width=250
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.target_entry.pack(pady=1)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.
        self.target_entry.insert(0, "0.0000")
        # Erklaerung: fuegt Text in ein Eingabefeld ein.

        self.target_button_frame = ctk.CTkFrame(
        # Erklaerung: erstellt einen Rahmen/Container fuer andere UI-Elemente. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            fg_color="transparent"
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.target_button_frame.pack(pady=1)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.btn_target_abs = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.target_button_frame,
            # Erklaerung: self.target_button_frame ist hier ein Wert/Parameter. Rahmen fuer die Ziel-Buttons. Das Komma trennt diesen Wert vom naechsten.
            text="Go to target",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            width=140,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.move_to_target_by_steps,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            fg_color=TEXT_COLOR
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_target_abs.grid(
        # Erklaerung: platziert ein UI-Element in einem Tabellenraster aus Zeilen und Spalten. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            row=0,
            # Erklaerung: row= ist ein benanntes Argument und legt die Zeile im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            column=0,
            # Erklaerung: column= ist ein benanntes Argument und legt die Spalte im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            padx=1
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_target_rel = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.target_button_frame,
            # Erklaerung: self.target_button_frame ist hier ein Wert/Parameter. Rahmen fuer die Ziel-Buttons. Das Komma trennt diesen Wert vom naechsten.
            text="Move distance",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            width=140,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.move_distance_by_steps,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            fg_color=TEXT_COLOR
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_target_rel.grid(
        # Erklaerung: platziert ein UI-Element in einem Tabellenraster aus Zeilen und Spalten. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            row=0,
            # Erklaerung: row= ist ein benanntes Argument und legt die Zeile im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            column=1,
            # Erklaerung: column= ist ein benanntes Argument und legt die Spalte im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            padx=1
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_min = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.button_frame,
            # Erklaerung: self.button_frame ist hier ein Wert/Parameter. Rahmen, in dem die Stage-Bewegungsbuttons nebeneinander liegen. Das Komma trennt diesen Wert vom naechsten.
            text="|<",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            width=60,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.move_to_min,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            fg_color=TEXT_COLOR
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_min.grid(
        # Erklaerung: platziert ein UI-Element in einem Tabellenraster aus Zeilen und Spalten. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            row=0,
            # Erklaerung: row= ist ein benanntes Argument und legt die Zeile im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            column=0,
            # Erklaerung: column= ist ein benanntes Argument und legt die Spalte im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            padx=1
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_left = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.button_frame,
            # Erklaerung: self.button_frame ist hier ein Wert/Parameter. Rahmen, in dem die Stage-Bewegungsbuttons nebeneinander liegen. Das Komma trennt diesen Wert vom naechsten.
            text="<",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            width=60,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.step_negative,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            fg_color=TEXT_COLOR
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_left.grid(
        # Erklaerung: platziert ein UI-Element in einem Tabellenraster aus Zeilen und Spalten. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            row=0,
            # Erklaerung: row= ist ein benanntes Argument und legt die Zeile im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            column=1,
            # Erklaerung: column= ist ein benanntes Argument und legt die Spalte im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            padx=1
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_center = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.button_frame,
            # Erklaerung: self.button_frame ist hier ein Wert/Parameter. Rahmen, in dem die Stage-Bewegungsbuttons nebeneinander liegen. Das Komma trennt diesen Wert vom naechsten.
            text="0",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            width=60,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.move_to_center,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            fg_color=TEXT_COLOR
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_center.grid(
        # Erklaerung: platziert ein UI-Element in einem Tabellenraster aus Zeilen und Spalten. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            row=0,
            # Erklaerung: row= ist ein benanntes Argument und legt die Zeile im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            column=2,
            # Erklaerung: column= ist ein benanntes Argument und legt die Spalte im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            padx=1
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_right = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.button_frame,
            # Erklaerung: self.button_frame ist hier ein Wert/Parameter. Rahmen, in dem die Stage-Bewegungsbuttons nebeneinander liegen. Das Komma trennt diesen Wert vom naechsten.
            text=">",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            width=60,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.step_positive,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            fg_color=TEXT_COLOR
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_right.grid(
        # Erklaerung: platziert ein UI-Element in einem Tabellenraster aus Zeilen und Spalten. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            row=0,
            # Erklaerung: row= ist ein benanntes Argument und legt die Zeile im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            column=3,
            # Erklaerung: column= ist ein benanntes Argument und legt die Spalte im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            padx=1
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_max = ctk.CTkButton(
        # Erklaerung: erstellt einen klickbaren Button. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.button_frame,
            # Erklaerung: self.button_frame ist hier ein Wert/Parameter. Rahmen, in dem die Stage-Bewegungsbuttons nebeneinander liegen. Das Komma trennt diesen Wert vom naechsten.
            text=">|",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            width=60,
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            command=self.move_to_max,
            # Erklaerung: command= ist ein benanntes Argument und legt fest, welche Methode beim Klick ausgefuehrt wird. Das Komma trennt diese Angabe von der naechsten.
            fg_color=TEXT_COLOR
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.btn_max.grid(
        # Erklaerung: platziert ein UI-Element in einem Tabellenraster aus Zeilen und Spalten. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            row=0,
            # Erklaerung: row= ist ein benanntes Argument und legt die Zeile im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            column=4,
            # Erklaerung: column= ist ein benanntes Argument und legt die Spalte im grid-Layout fest. Das Komma trennt diese Angabe von der naechsten.
            padx=1
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.


        self.label_stage_position = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            text="Stage Position: 0.000000 mm",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 10),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_stage_position.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.label_stage_moved = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage_frame,
            # Erklaerung: self.stage_frame ist hier ein Wert/Parameter. Rahmen im Fenster fuer alle Stage-Bedienelemente. Das Komma trennt diesen Wert vom naechsten.
            text="Accumulated Movement: 0.000000 mm",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 11, "bold"),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_stage_moved.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.frame = ctk.CTkFrame(
        # Erklaerung: erstellt einen Rahmen/Container fuer andere UI-Elemente. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.scroll,
            # Erklaerung: self.scroll ist hier ein Wert/Parameter. der scrollbare Hauptbereich im Fenster. Das Komma trennt diesen Wert vom naechsten.
            fg_color="#EEEEEE"
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.frame.pack(
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            fill="x",
            # Erklaerung: fill= ist ein benanntes Argument und sagt, in welche Richtung sich das Element ausdehnen darf. Das Komma trennt diese Angabe von der naechsten.
            padx=5,
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand. Das Komma trennt diese Angabe von der naechsten.
            pady=4
            # Erklaerung: pady= ist ein benanntes Argument und setzt vertikalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_um = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.frame,
            # Erklaerung: self.frame ist hier ein Wert/Parameter. Rahmen fuer Messwerte wie Distanz, Zeit und Intensitaet. Das Komma trennt diesen Wert vom naechsten.
            text="Distance: 0.000 µm",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 13, "bold"),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        self.label_um.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.label_ps = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.frame,
            # Erklaerung: self.frame ist hier ein Wert/Parameter. Rahmen fuer Messwerte wie Distanz, Zeit und Intensitaet. Das Komma trennt diesen Wert vom naechsten.
            text="Time Delay: 0.0000 ps",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 11),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_ps.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.label_intensity = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.frame,
            # Erklaerung: self.frame ist hier ein Wert/Parameter. Rahmen fuer Messwerte wie Distanz, Zeit und Intensitaet. Das Komma trennt diesen Wert vom naechsten.
            text="Intensity: 0.00",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 11),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        self.label_intensity.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.label_thresholds = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.frame,
            # Erklaerung: self.frame ist hier ein Wert/Parameter. Rahmen fuer Messwerte wie Distanz, Zeit und Intensitaet. Das Komma trennt diesen Wert vom naechsten.
            text="Thresholds: waiting",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 10),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_thresholds.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.label_accumulated_fringes = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.frame,
            # Erklaerung: self.frame ist hier ein Wert/Parameter. Rahmen fuer Messwerte wie Distanz, Zeit und Intensitaet. Das Komma trennt diesen Wert vom naechsten.
            text="Accumulated Fringes Count: 0",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 13, "bold"),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_accumulated_fringes.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.compare_frame = ctk.CTkFrame(
        # Erklaerung: erstellt einen Rahmen/Container fuer andere UI-Elemente. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.scroll,
            # Erklaerung: self.scroll ist hier ein Wert/Parameter. der scrollbare Hauptbereich im Fenster. Das Komma trennt diesen Wert vom naechsten.
            fg_color="#EEEEEE"
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.compare_frame.pack(
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            fill="x",
            # Erklaerung: fill= ist ein benanntes Argument und sagt, in welche Richtung sich das Element ausdehnen darf. Das Komma trennt diese Angabe von der naechsten.
            padx=5,
            # Erklaerung: padx= ist ein benanntes Argument und setzt horizontalen Aussenabstand. Das Komma trennt diese Angabe von der naechsten.
            pady=4
            # Erklaerung: pady= ist ein benanntes Argument und setzt vertikalen Aussenabstand.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.compare_frame,
            # Erklaerung: self.compare_frame ist hier ein Wert/Parameter. Rahmen fuer den Vergleich zwischen gefahrenem Weg und berechnetem Weg. Das Komma trennt diesen Wert vom naechsten.
            text="Distance Comparison",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 15, "bold"),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        ).pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.label_compare_driven = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.compare_frame,
            # Erklaerung: self.compare_frame ist hier ein Wert/Parameter. Rahmen fuer den Vergleich zwischen gefahrenem Weg und berechnetem Weg. Das Komma trennt diesen Wert vom naechsten.
            text="Driven: 0.000000 mm",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 11),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_compare_driven.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.label_compare_calculated = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.compare_frame,
            # Erklaerung: self.compare_frame ist hier ein Wert/Parameter. Rahmen fuer den Vergleich zwischen gefahrenem Weg und berechnetem Weg. Das Komma trennt diesen Wert vom naechsten.
            text="Calculated: 0.000000 mm",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 11),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_compare_calculated.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.label_compare_difference = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.compare_frame,
            # Erklaerung: self.compare_frame ist hier ein Wert/Parameter. Rahmen fuer den Vergleich zwischen gefahrenem Weg und berechnetem Weg. Das Komma trennt diesen Wert vom naechsten.
            text="Difference: 0.000000 mm",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 13, "bold"),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_compare_difference.pack(pady=0)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.live_size = (320, 220)
        # Erklaerung: self.live_size bekommt mit = einen neuen Wert; gewuenschte Anzeige-Groesse des Kamerabildes.

        ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.scroll,
            # Erklaerung: self.scroll ist hier ein Wert/Parameter. der scrollbare Hauptbereich im Fenster. Das Komma trennt diesen Wert vom naechsten.
            text="Live Camera",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            font=("Arial", 15, "bold"),
            # Erklaerung: font= ist ein benanntes Argument und legt Schriftart, Groesse und optional Fettdruck fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        ).pack(pady=(5, 2))
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.image_label = ctk.CTkLabel(
        # Erklaerung: erstellt ein Text-/Bild-Label im Fenster. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.scroll,
            # Erklaerung: self.scroll ist hier ein Wert/Parameter. der scrollbare Hauptbereich im Fenster. Das Komma trennt diesen Wert vom naechsten.
            text="No Image",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            width=self.live_size[0],
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            height=self.live_size[1],
            # Erklaerung: height= ist ein benanntes Argument und legt die Hoehe des Elements fest. Das Komma trennt diese Angabe von der naechsten.
            fg_color="#111111",
            # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest. Das Komma trennt diese Angabe von der naechsten.
            text_color="white"
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.image_label.pack(pady=5)
        # Erklaerung: platziert ein UI-Element mit dem pack-Layout im Fenster.

        self.update_comparison_labels()
        # Erklaerung: aktualisiert die Vergleichsanzeigen mit den aktuellen gespeicherten Werten.

        self.update_stage_position_once()
        # Erklaerung: liest direkt einmal die aktuelle Stage-Position und zeigt sie an.

    def toggle(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; toggle ist der Name. Startet oder stoppt das Monitoring, je nachdem, ob es gerade laeuft.

        if not self.is_monitoring:
        # Erklaerung: prueft, ob das Monitoring gestoppt wurde.

            if not self.camera_connected:
            # Erklaerung: prueft, ob keine Kamera verbunden ist.

                self.status.configure(
                # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    text="Camera not connected",
                    # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                    text_color=RED_COLOR
                    # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                return
                # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

            self.restart_values_only()
            # Erklaerung: setzt die Messzaehler zurueck, ohne das Fenster neu zu starten.

            self.is_monitoring = True
            # Erklaerung: self.is_monitoring bekommt mit = einen neuen Wert; merkt sich, ob die Messung gerade laeuft.

            if MANUAL_THRESHOLDS:
            # Erklaerung: prueft, ob manuelle Schwellenwerte benutzt werden sollen.

                self.dark_threshold = (
                # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                    MANUAL_DARK_THRESHOLD
                    # Erklaerung: MANUAL_DARK_THRESHOLD ist hier ein Wert/Parameter. fester Zahlenwert fuer dunkel, falls manuelle Schwellenwerte eingeschaltet werden.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                self.bright_threshold = (
                # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                    MANUAL_BRIGHT_THRESHOLD
                    # Erklaerung: MANUAL_BRIGHT_THRESHOLD ist hier ein Wert/Parameter. fester Zahlenwert fuer hell, falls manuelle Schwellenwerte eingeschaltet werden.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                self.label_thresholds.configure(
                # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    text=(
                    # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                        f"Manual Dark: "
                        # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                        f"{self.dark_threshold:.2f} | "
                        # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                        f"Manual Bright: "
                        # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                        f"{self.bright_threshold:.2f}"
                        # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                    )
                    # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                self.status.configure(
                # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    text="Monitoring running",
                    # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                    text_color=GREEN_COLOR
                    # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            else:
            # Erklaerung: else bedeutet sonst; dieser Block laeuft, wenn die if-Bedingung vorher falsch war.

                self.calibrating = True
                # Erklaerung: self.calibrating bekommt mit = einen neuen Wert; merkt sich, ob gerade die automatische Schwellenwert-Kalibrierung laeuft.

                self.calibration_values = []
                # Erklaerung: self.calibration_values bekommt mit = einen neuen Wert; Liste der Intensitaeten, die waehrend der Kalibrierung gesammelt werden.

                self.calibration_start_time = time.time()
                # Erklaerung: self.calibration_start_time bekommt mit = einen neuen Wert; Startzeitpunkt der Kalibrierung.

                self.status.configure(
                # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    text="Calibrating thresholds...",
                    # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                    text_color=ORANGE_COLOR
                    # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            self.btn.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="STOP MONITORING",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                fg_color=RED_COLOR
                # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            threading.Thread(
            # Erklaerung: erstellt einen Hintergrund-Thread fuer eine Aufgabe, die parallel zum Fenster laufen soll.
                target=self.loop,
                # Erklaerung: target= ist ein benanntes Argument und legt die Funktion fest, die im Hintergrund-Thread laufen soll. Das Komma trennt diese Angabe von der naechsten.
                daemon=True
                # Erklaerung: daemon= ist ein benanntes Argument und sorgt dafuer, dass der Thread das Programm beim Schliessen nicht blockiert.
            ).start()
            # Erklaerung: startet den gerade erstellten Thread.

        else:
        # Erklaerung: else bedeutet sonst; dieser Block laeuft, wenn die if-Bedingung vorher falsch war.

            self.is_monitoring = False
            # Erklaerung: self.is_monitoring bekommt mit = einen neuen Wert; merkt sich, ob die Messung gerade laeuft.

            if self.stage_connected:
            # Erklaerung: prueft, ob die Stage verbunden ist.
                self.stage.stop()
                # Erklaerung: sendet einen Stop-Befehl an die Stage.

            self.btn.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="START MONITORING",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                fg_color=TEXT_COLOR
                # Erklaerung: fg_color= ist ein benanntes Argument und legt die Hintergrund-/Fuellfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="Stopped",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=TEXT_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def restart(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; restart ist der Name. setzt die Messwerte zurueck.

        self.restart_values_only()
        # Erklaerung: setzt die Messzaehler zurueck, ohne das Fenster neu zu starten.

    def restart_values_only(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; restart_values_only ist der Name. setzt Zaehler und Messwerte zurueck, ohne das ganze Fenster neu zu bauen.

        self.accumulated_fringes = 0
        # Erklaerung: self.accumulated_fringes bekommt mit = einen neuen Wert; zaehlt alle erkannten Interferenzstreifen seit dem letzten Reset.

        self.was_dark = False
        # Erklaerung: loescht den dunklen Zustand, damit erst wieder ein neuer Dunkel-Hell-Wechsel noetig ist.

        self.last_count_time = 0
        # Erklaerung: self.last_count_time bekommt mit = einen neuen Wert; Zeitpunkt, wann zuletzt ein Fringe gezaehlt wurde.

        self.dark_counter = 0
        # Erklaerung: setzt den Dunkel-Zaehler wieder auf null.

        self.bright_counter = 0
        # Erklaerung: setzt den Hell-Zaehler wieder auf null.

        self.intensity_history = []
        # Erklaerung: self.intensity_history bekommt mit = einen neuen Wert; Liste der letzten Intensitaetswerte zum Glaetten des Signals.

        self.calibrating = False
        # Erklaerung: beendet den Kalibrierungszustand.
        self.calibration_motion_started = False
        # Erklaerung: self.calibration_motion_started bekommt mit = einen neuen Wert; merkt, ob die automatische Stage-Bewegung fuer die Kalibrierung schon gestartet wurde.

        self.calibration_values = []
        # Erklaerung: self.calibration_values bekommt mit = einen neuen Wert; Liste der Intensitaeten, die waehrend der Kalibrierung gesammelt werden.

        self.reset_stage_movement_tracking()
        # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.

        self.reset_measurement_after_calibration()
        # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.

        if hasattr(self, "label_compare_driven"):
        # Erklaerung: if bedeutet "falls"; der eingerueckte Block darunter laeuft nur, wenn die Bedingung wahr ist.

            self.update_comparison_labels(0.0)
            # Erklaerung: aktualisiert den Vergleich zwischen Stage-Weg und Fringe-Weg.

    def start_stage_move_to(
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; start_stage_move_to ist der Name. startet eine Bewegung der Stage zu einer absoluten Zielposition.
        self,
        # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
        target_mm,
        # Erklaerung: target_mm ist hier ein Wert/Parameter. Zielposition der Stage in Millimetern. Das Komma trennt diesen Wert vom naechsten.
        start_pos=None,
        # Erklaerung: start_pos bekommt hier einen Wert rechts vom =. Startposition der Stage vor einer Bewegung.
        reset_after_move=False
        # Erklaerung: reset_after_move bekommt hier einen Wert rechts vom =. Schalter, ob nach der Bewegung Werte zurueckgesetzt werden sollen.
    ):
    # Erklaerung: Die Klammer beendet die Bedingung; der Doppelpunkt startet den eingerueckten Codeblock.

        if not self.stage_connected:
        # Erklaerung: prueft, ob die Stage nicht verbunden ist.

            if reset_after_move:
            # Erklaerung: prueft, ob nach der Bewegung ein Reset passieren soll.

                self.reset_stage_after_calibration()
                # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.

                return
                # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="Stage not connected",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=RED_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        if self.stage.is_moving:
        # Erklaerung: prueft, ob die Stage gerade schon faehrt.

            if reset_after_move:
            # Erklaerung: prueft, ob nach der Bewegung ein Reset passieren soll.

                self.center_stage_after_calibration_pending = True
                # Erklaerung: self.center_stage_after_calibration_pending bekommt mit = einen neuen Wert; merkt, dass die Stage nach der aktuellen Bewegung noch zur Mitte fahren soll.

                self.status.configure(
                # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    text=(
                    # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                        "Calibration done - stage returns to "
                        # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
                        "0.00000000000 mm after current move"
                        # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
                    ),
                    # Erklaerung: Diese Klammer beendet einen inneren Aufruf; das Komma trennt ihn vom naechsten Argument.
                    text_color=ORANGE_COLOR
                    # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            else:
            # Erklaerung: else bedeutet sonst; dieser Block laeuft, wenn die if-Bedingung vorher falsch war.

                self.status.configure(
                # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    text="Stage is already moving",
                    # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                    text_color=ORANGE_COLOR
                    # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        if start_pos is None:
        # Erklaerung: prueft, ob keine Startposition uebergeben wurde; None bedeutet kein Wert.

            start_pos = self.stage.get_position()
            # Erklaerung: liest die aktuelle Stage-Position und speichert sie als Startposition.

        target_mm = self.stage.clamp_position(target_mm)
        # Erklaerung: begrenzt die Zielposition auf den erlaubten Stage-Bereich.

        move_mm = target_mm - start_pos
        # Erklaerung: berechnet die Strecke vom Start bis zum Ziel.

        self.stage_start_position = start_pos
        # Erklaerung: self.stage_start_position bekommt mit = einen neuen Wert; Position der Stage am Anfang einer Bewegung.
        self.stage_movement_before_move = self.total_stage_movement
        # Erklaerung: self.stage_movement_before_move bekommt mit = einen neuen Wert; gespeicherte Bewegungssumme vor einer neuen Bewegung.
        self.reset_stage_movement_after_move = reset_after_move
        # Erklaerung: self.reset_stage_movement_after_move bekommt mit = einen neuen Wert; Schalter, ob die Bewegungsanzeige nach einer Bewegung zurueckgesetzt werden soll.

        if abs(move_mm) < 1e-12:
        # Erklaerung: abs nimmt den Betrag; 1e-12 ist fast null, also wird geprueft, ob kaum Bewegung noetig ist.

            if reset_after_move:
            # Erklaerung: prueft, ob nach der Bewegung ein Reset passieren soll.

                self.reset_stage_after_calibration(start_pos)
                # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.

                return
                # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

            else:
            # Erklaerung: else bedeutet sonst; dieser Block laeuft, wenn die if-Bedingung vorher falsch war.

                self.update_stage_labels(start_pos, 0.0)
                # Erklaerung: aktualisiert die Stage-Anzeigen mit Position und Bewegung.

            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="Stage already at target",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=TEXT_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        if not self.stage.move_absolute(target_mm):
        # Erklaerung: versucht absolut zur Zielposition zu fahren; not faengt einen Fehlschlag ab.

            self.reset_stage_movement_after_move = False
            # Erklaerung: self.reset_stage_movement_after_move bekommt mit = einen neuen Wert; Schalter, ob die Bewegungsanzeige nach einer Bewegung zurueckgesetzt werden soll.

            if reset_after_move:
            # Erklaerung: prueft, ob nach der Bewegung ein Reset passieren soll.

                self.reset_stage_after_calibration(start_pos)
                # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.

            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        self.status.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=f"Stage moving to {target_mm:.6f} mm",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        threading.Thread(
        # Erklaerung: erstellt einen Hintergrund-Thread fuer eine Aufgabe, die parallel zum Fenster laufen soll.
            target=self.stage_ui_loop,
            # Erklaerung: target= ist ein benanntes Argument und legt die Funktion fest, die im Hintergrund-Thread laufen soll. Das Komma trennt diese Angabe von der naechsten.
            daemon=True
            # Erklaerung: daemon= ist ein benanntes Argument und sorgt dafuer, dass der Thread das Programm beim Schliessen nicht blockiert.
        ).start()
        # Erklaerung: startet den gerade erstellten Thread.

    def start_stage_move_by(self, move_mm):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; start_stage_move_by ist der Name. startet eine relative Stage-Bewegung um eine bestimmte Strecke.

        start_pos = self.stage.get_position()
        # Erklaerung: liest die aktuelle Stage-Position und speichert sie als Startposition.

        self.start_stage_move_to(
        # Erklaerung: ruft die Methode auf, die eine absolute Stage-Bewegung startet. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            start_pos + move_mm,
            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
            start_pos=start_pos
            # Erklaerung: start_pos bekommt hier einen Wert rechts vom =. Startposition der Stage vor einer Bewegung.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def start_stage_move_to_stepped(self, target_mm):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; start_stage_move_to_stepped ist der Name. startet eine absolute Stage-Bewegung in mehreren kleinen Schritten.

        if not self.stage_connected:
        # Erklaerung: prueft, ob die Stage nicht verbunden ist.
            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="Stage not connected",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=RED_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        if self.stage.is_moving:
        # Erklaerung: prueft, ob die Stage gerade schon faehrt.
            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="Stage is already moving",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=ORANGE_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        start_pos = self.stage.get_position()
        # Erklaerung: liest die aktuelle Stage-Position und speichert sie als Startposition.
        target_mm = self.stage.clamp_position(target_mm)
        # Erklaerung: begrenzt die Zielposition auf den erlaubten Stage-Bereich.

        if abs(target_mm - start_pos) < 1e-12:
        # Erklaerung: if bedeutet "falls"; der eingerueckte Block darunter laeuft nur, wenn die Bedingung wahr ist.
            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="Stage already at target",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=TEXT_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        self.stage_start_position = start_pos
        # Erklaerung: self.stage_start_position bekommt mit = einen neuen Wert; Position der Stage am Anfang einer Bewegung.
        self.stage_movement_before_move = self.total_stage_movement
        # Erklaerung: self.stage_movement_before_move bekommt mit = einen neuen Wert; gespeicherte Bewegungssumme vor einer neuen Bewegung.

        threading.Thread(
        # Erklaerung: erstellt einen Hintergrund-Thread fuer eine Aufgabe, die parallel zum Fenster laufen soll.
            target=self.stage_stepped_move_worker,
            # Erklaerung: target= ist ein benanntes Argument und legt die Funktion fest, die im Hintergrund-Thread laufen soll. Das Komma trennt diese Angabe von der naechsten.
            args=(start_pos, target_mm),
            # Erklaerung: args= ist ein benanntes Argument und uebergibt Zusatzwerte an die Thread-Funktion. Das Komma trennt diese Angabe von der naechsten.
            daemon=True
            # Erklaerung: daemon= ist ein benanntes Argument und sorgt dafuer, dass der Thread das Programm beim Schliessen nicht blockiert.
        ).start()
        # Erklaerung: startet den gerade erstellten Thread.

    def start_stage_move_by_steps(self, move_mm):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; start_stage_move_by_steps ist der Name. startet eine relative Stage-Bewegung in mehreren kleinen Schritten.

        start_pos = self.stage.get_position()
        # Erklaerung: liest die aktuelle Stage-Position und speichert sie als Startposition.
        self.start_stage_move_to_stepped(
        # Erklaerung: ruft die Methode auf, die in kleinen Schritten zu einem Ziel faehrt. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            start_pos + move_mm
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def stage_stepped_move_worker(self, start_pos, target_mm):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; stage_stepped_move_worker ist der Name. arbeitet die Schrittbewegung im Hintergrund ab.

        step_mm = self.get_step_size()
        # Erklaerung: step_mm bekommt mit = einen neuen Wert; Schrittgroesse in Millimetern.
        delay_s = 0.25
        # Erklaerung: delay_s bekommt mit = einen neuen Wert; Wartezeit zwischen einzelnen Schritten in Sekunden.
        direction = 1 if target_mm > start_pos else -1
        # Erklaerung: direction bekommt mit = einen neuen Wert; Richtung der Bewegung: 1 fuer positiv, -1 fuer negativ.
        current_pos = start_pos
        # Erklaerung: current_pos bekommt mit = einen neuen Wert; aktuelle Position innerhalb einer Schrittbewegung.
        remaining = abs(target_mm - start_pos)
        # Erklaerung: remaining bekommt mit = einen neuen Wert; noch uebrige Strecke bis zum Ziel.
        moved = 0.0
        # Erklaerung: moved bekommt mit = einen neuen Wert; bisher gefahrene Strecke in dieser Bewegung.

        self.status.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=(
            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                f"Moving to {target_mm:.6f} mm in {step_mm:.6f} mm steps"
                # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
            ),
            # Erklaerung: Diese Klammer beendet einen inneren Aufruf; das Komma trennt ihn vom naechsten Argument.
            text_color=TEXT_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        while remaining > 1e-12:
        # Erklaerung: while bedeutet Schleife; der eingerueckte Block wiederholt sich, solange die Bedingung wahr ist.
            next_step = min(step_mm, remaining)
            # Erklaerung: next_step bekommt mit = einen neuen Wert; naechste Teilstrecke, maximal so gross wie die Schrittweite.
            next_target = current_pos + direction * next_step
            # Erklaerung: next_target bekommt mit = einen neuen Wert; naechste konkrete Zielposition fuer die Stage.

            if not self.stage.move_absolute(next_target):
            # Erklaerung: if bedeutet "falls"; der eingerueckte Block darunter laeuft nur, wenn die Bedingung wahr ist.
                self.status.configure(
                # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    text="Stage move failed",
                    # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                    text_color=RED_COLOR
                    # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
                return
                # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

            while self.stage.is_moving:
            # Erklaerung: while wiederholt den Block, solange die Stage noch faehrt.
                time.sleep(0.01)
                # Erklaerung: wartet 0.01 Sekunden in einer kurzen Schleife.

            step_distance = abs(next_target - current_pos)
            # Erklaerung: step_distance bekommt mit = einen neuen Wert; tatsaechlich gefahrene Strecke im aktuellen Schritt.
            moved += step_distance
            # Erklaerung: moved wird erhoeht; += bedeutet: alter Wert plus der Wert rechts daneben. bisher gefahrene Strecke in dieser Bewegung.
            current_pos = next_target
            # Erklaerung: current_pos bekommt mit = einen neuen Wert; aktuelle Position innerhalb einer Schrittbewegung.
            remaining = abs(target_mm - current_pos)
            # Erklaerung: remaining bekommt mit = einen neuen Wert; noch uebrige Strecke bis zum Ziel.

            self.total_stage_movement = (
            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                self.stage_movement_before_move + moved
                # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            self.after(
            # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                0,
                # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                lambda p=current_pos, m=moved, b=self.stage_movement_before_move:
                # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                self.update_stage_labels(p, m, b)
                # Erklaerung: aktualisiert die Stage-Anzeigen mit Position und Bewegung.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            if remaining > 1e-12:
            # Erklaerung: if bedeutet "falls"; der eingerueckte Block darunter laeuft nur, wenn die Bedingung wahr ist.
                time.sleep(delay_s)
                # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.

        self.after(
        # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            0,
            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
            lambda:
            # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text=f"Reached {current_pos:.6f} mm",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=GREEN_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def get_step_size(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; get_step_size ist der Name. liest die Schrittweite aus dem Eingabefeld und wandelt sie in eine Zahl um.

        try:
        # Erklaerung: try startet einen Bereich, in dem ein Fehler abgefangen werden kann.
            value = float(
            # Erklaerung: wandelt Text oder Zahl in eine Kommazahl um. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                self.step_entry.get().replace(",", ".")
                # Erklaerung: ersetzt deutsches Komma durch Punkt, damit Python die Zahl lesen kann.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            return abs(value)
            # Erklaerung: gibt den positiven Betrag der Schrittweite zurueck.
        except ValueError:
        # Erklaerung: faengt den Fehler ab, der entsteht, wenn Text nicht in eine Zahl umgewandelt werden kann.
            return 0.0001
            # Erklaerung: gibt als Notfallwert 0.0001 mm zurueck, wenn die Eingabe ungueltig ist.

    def compute_fringe_distance(self, wavelength_nm):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; compute_fringe_distance ist der Name. berechnet aus der Wellenlaenge die Strecke pro gezaehltem Fringe.

        return (wavelength_nm / 2) / 1_000_000 / 2
        # Erklaerung: berechnet die Fringe-Strecke: nm wird in mm umgerechnet und wegen Interferometer-Geometrie geteilt.

    def apply_wavelength(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; apply_wavelength ist der Name. uebernimmt die Wellenlaenge aus dem Eingabefeld und aktualisiert die Schrittweite.

        try:
        # Erklaerung: try startet einen Bereich, in dem ein Fehler abgefangen werden kann.
            wavelength_nm = float(
            # Erklaerung: wandelt Text oder Zahl in eine Kommazahl um. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                self.wavelength_entry.get().replace(",", ".")
                # Erklaerung: ersetzt deutsches Komma durch Punkt, damit Python die Zahl lesen kann.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        except ValueError:
        # Erklaerung: faengt den Fehler ab, der entsteht, wenn Text nicht in eine Zahl umgewandelt werden kann.
            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="Invalid wavelength value",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=RED_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        self.laser_wavelength_nm = wavelength_nm
        # Erklaerung: self.laser_wavelength_nm bekommt mit = einen neuen Wert; aktuelle Laserwellenlaenge, die fuer die Berechnung genutzt wird.
        self.fringe_distance_mm = self.compute_fringe_distance(
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            self.laser_wavelength_nm
            # Erklaerung: self.laser_wavelength_nm ist hier ein Wert/Parameter. aktuelle Laserwellenlaenge, die fuer die Berechnung genutzt wird.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        default_step = self.fringe_distance_mm / 4
        # Erklaerung: default_step bekommt mit = einen neuen Wert; automatisch vorgeschlagene Schrittweite passend zur Wellenlaenge.
        self.step_entry.delete(0, "end")
        # Erklaerung: loescht den bisherigen Inhalt des Schrittweiten-Eingabefelds.
        self.step_entry.insert(
        # Erklaerung: fuegt Text in ein Eingabefeld ein. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            0,
            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
            f"{default_step:.7f}"
            # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.status.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=f"Wavelength set to {self.laser_wavelength_nm:.1f} nm",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=GREEN_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def move_to_min(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; move_to_min ist der Name. faehrt die Stage zur Minimalposition.

        self.start_stage_move_to(
        # Erklaerung: ruft die Methode auf, die eine absolute Stage-Bewegung startet. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage.min_position
            # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def step_negative(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; step_negative ist der Name. faehrt die Stage einen Schritt in negativer Richtung.

        self.start_stage_move_by(
        # Erklaerung: ruft die Methode auf, die eine relative Stage-Bewegung startet. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            -self.get_step_size()
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def move_to_center(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; move_to_center ist der Name. faehrt die Stage zur Nullposition.

        self.start_stage_move_to(
        # Erklaerung: ruft die Methode auf, die eine absolute Stage-Bewegung startet. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            0.0
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def step_positive(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; step_positive ist der Name. faehrt die Stage einen Schritt in positiver Richtung.

        self.start_stage_move_by(
        # Erklaerung: ruft die Methode auf, die eine relative Stage-Bewegung startet. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.get_step_size()
            # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def move_to_max(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; move_to_max ist der Name. faehrt die Stage zur Maximalposition.

        self.start_stage_move_to(
        # Erklaerung: ruft die Methode auf, die eine absolute Stage-Bewegung startet. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.stage.max_position
            # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def move_to_target_by_steps(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; move_to_target_by_steps ist der Name. liest eine Zielposition und faehrt in Schritten dorthin.

        try:
        # Erklaerung: try startet einen Bereich, in dem ein Fehler abgefangen werden kann.
            target_mm = float(
            # Erklaerung: wandelt Text oder Zahl in eine Kommazahl um. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                self.target_entry.get().replace(",", ".")
                # Erklaerung: ersetzt deutsches Komma durch Punkt, damit Python die Zahl lesen kann.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        except ValueError:
        # Erklaerung: faengt den Fehler ab, der entsteht, wenn Text nicht in eine Zahl umgewandelt werden kann.
            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="Invalid target value",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=RED_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        self.start_stage_move_to_stepped(target_mm)
        # Erklaerung: ruft die Methode auf, die in kleinen Schritten zu einem Ziel faehrt.

    def move_distance_by_steps(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; move_distance_by_steps ist der Name. liest eine Strecke und faehrt diese Strecke in Schritten.

        try:
        # Erklaerung: try startet einen Bereich, in dem ein Fehler abgefangen werden kann.
            distance_mm = float(
            # Erklaerung: wandelt Text oder Zahl in eine Kommazahl um. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                self.target_entry.get().replace(",", ".")
                # Erklaerung: ersetzt deutsches Komma durch Punkt, damit Python die Zahl lesen kann.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        except ValueError:
        # Erklaerung: faengt den Fehler ab, der entsteht, wenn Text nicht in eine Zahl umgewandelt werden kann.
            self.status.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text="Invalid distance value",
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                text_color=RED_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        self.start_stage_move_by_steps(distance_mm)
        # Erklaerung: ruft die Methode auf, die in kleinen Schritten eine Strecke faehrt.

    def stop_stage(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; stop_stage ist der Name. stoppt die Stage-Bewegung.

        self.stage.stop()
        # Erklaerung: sendet einen Stop-Befehl an die Stage.

    def stage_ui_loop(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; stage_ui_loop ist der Name. aktualisiert waehrend einer Stage-Bewegung die Anzeigen im Fenster.

        movement_base = self.stage_movement_before_move
        # Erklaerung: movement_base bekommt mit = einen neuen Wert; Bewegungssumme, die schon vor der aktuellen Bewegung existierte.

        while self.stage.is_moving:
        # Erklaerung: while wiederholt den Block, solange die Stage noch faehrt.

            pos = self.stage.get_position()
            # Erklaerung: pos bekommt mit = einen neuen Wert; aktuelle Stage-Position.

            moved = abs(pos - self.stage_start_position)
            # Erklaerung: moved bekommt mit = einen neuen Wert; bisher gefahrene Strecke in dieser Bewegung.

            self.after(
            # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                0,
                # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                lambda p=pos, m=moved, b=movement_base:
                # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                self.update_stage_labels(p, m, b)
                # Erklaerung: aktualisiert die Stage-Anzeigen mit Position und Bewegung.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            time.sleep(0.05)
            # Erklaerung: wartet 0.05 Sekunden, damit nicht zu schnell abgefragt wird.

        pos = self.stage.get_position()
        # Erklaerung: pos bekommt mit = einen neuen Wert; aktuelle Stage-Position.

        moved = abs(pos - self.stage_start_position)
        # Erklaerung: moved bekommt mit = einen neuen Wert; bisher gefahrene Strecke in dieser Bewegung.
        self.total_stage_movement = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            movement_base + moved
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        if self.reset_stage_movement_after_move:
        # Erklaerung: if bedeutet "falls"; der eingerueckte Block darunter laeuft nur, wenn die Bedingung wahr ist.

            self.reset_stage_movement_after_move = False
            # Erklaerung: self.reset_stage_movement_after_move bekommt mit = einen neuen Wert; Schalter, ob die Bewegungsanzeige nach einer Bewegung zurueckgesetzt werden soll.

            self.after(
            # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                0,
                # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                lambda p=pos:
                # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                self.reset_stage_after_calibration(p)
                # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        else:
        # Erklaerung: else bedeutet sonst; dieser Block laeuft, wenn die if-Bedingung vorher falsch war.

            self.after(
            # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                0,
                # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                lambda p=pos, m=moved, b=movement_base:
                # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                self.update_stage_labels(p, m, b)
                # Erklaerung: aktualisiert die Stage-Anzeigen mit Position und Bewegung.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        if self.center_stage_after_calibration_pending:
        # Erklaerung: if bedeutet "falls"; der eingerueckte Block darunter laeuft nur, wenn die Bedingung wahr ist.

            self.center_stage_after_calibration_pending = False
            # Erklaerung: self.center_stage_after_calibration_pending bekommt mit = einen neuen Wert; merkt, dass die Stage nach der aktuellen Bewegung noch zur Mitte fahren soll.

            self.after(
            # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                0,
                # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                self.move_to_center_after_calibration
                # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def update_stage_position_once(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; update_stage_position_once ist der Name. liest einmal die aktuelle Stage-Position und zeigt sie an.

        if self.stage_connected:
        # Erklaerung: prueft, ob die Stage verbunden ist.

            pos = self.stage.get_position()
            # Erklaerung: pos bekommt mit = einen neuen Wert; aktuelle Stage-Position.

            self.label_stage_position.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text=f"Stage Position: {pos:.6f} mm"
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def update_stage_labels(self, pos, moved, movement_base=None):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; update_stage_labels ist der Name. aktualisiert Positions- und Bewegungsanzeigen.

        if movement_base is None:
        # Erklaerung: if bedeutet "falls"; der eingerueckte Block darunter laeuft nur, wenn die Bedingung wahr ist.
            movement_base = self.total_stage_movement
            # Erklaerung: movement_base bekommt mit = einen neuen Wert; Bewegungssumme, die schon vor der aktuellen Bewegung existierte.

        current_total_stage_movement = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            movement_base + abs(moved)
            # Erklaerung: nimmt den Betrag, also macht negative Strecken positiv.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        self.current_stage_movement_for_compare = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            current_total_stage_movement
            # Erklaerung: current_total_stage_movement ist hier ein Wert/Parameter. neue gesamte Stage-Bewegung inklusive aktueller Bewegung.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_stage_position.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=f"Stage Position: {pos:.6f} mm"
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_stage_moved.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=(
            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                f"Accumulated Movement: "
                # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                f"{current_total_stage_movement:.6f} mm"
                # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.update_comparison_labels(
        # Erklaerung: aktualisiert den Vergleich zwischen Stage-Weg und Fringe-Weg. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            current_total_stage_movement
            # Erklaerung: current_total_stage_movement ist hier ein Wert/Parameter. neue gesamte Stage-Bewegung inklusive aktueller Bewegung.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def reset_stage_movement_tracking(self, pos=None):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; reset_stage_movement_tracking ist der Name. setzt die gespeicherte Stage-Bewegung auf null.

        self.total_stage_movement = 0.0
        # Erklaerung: self.total_stage_movement bekommt mit = einen neuen Wert; gesamte bisher addierte Stage-Bewegung.
        self.stage_movement_before_move = 0.0
        # Erklaerung: self.stage_movement_before_move bekommt mit = einen neuen Wert; gespeicherte Bewegungssumme vor einer neuen Bewegung.
        self.current_stage_movement_for_compare = 0.0
        # Erklaerung: self.current_stage_movement_for_compare bekommt mit = einen neuen Wert; aktuelle gefahrene Strecke fuer den Vergleich mit der Fringe-Strecke.

        if pos is not None:
        # Erklaerung: prueft, ob eine Position uebergeben wurde; is not None bedeutet: es gibt einen Wert.
            self.stage_reference_position = pos
            # Erklaerung: self.stage_reference_position bekommt mit = einen neuen Wert; Referenzposition fuer die Bewegungsanzeige.
            self.label_stage_position.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text=f"Stage Position: {pos:.6f} mm"
                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        elif self.stage_connected:
        # Erklaerung: elif bedeutet sonst wenn; hier wird geprueft, ob die Stage verbunden ist.
            self.stage_reference_position = self.stage.get_position()
            # Erklaerung: self.stage_reference_position bekommt mit = einen neuen Wert; Referenzposition fuer die Bewegungsanzeige.
        else:
        # Erklaerung: else bedeutet sonst; dieser Block laeuft, wenn die if-Bedingung vorher falsch war.
            self.stage_reference_position = 0.0
            # Erklaerung: self.stage_reference_position bekommt mit = einen neuen Wert; Referenzposition fuer die Bewegungsanzeige.

        self.label_stage_moved.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text="Accumulated Movement: 0.000000 mm"
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.update_comparison_labels(0.0)
        # Erklaerung: aktualisiert den Vergleich zwischen Stage-Weg und Fringe-Weg.

    def reset_measurement_after_calibration(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; reset_measurement_after_calibration ist der Name. setzt die Fringe-Messung nach der Kalibrierung zurueck.

        self.accumulated_fringes = 0
        # Erklaerung: self.accumulated_fringes bekommt mit = einen neuen Wert; zaehlt alle erkannten Interferenzstreifen seit dem letzten Reset.
        self.was_dark = False
        # Erklaerung: loescht den dunklen Zustand, damit erst wieder ein neuer Dunkel-Hell-Wechsel noetig ist.
        self.last_count_time = 0
        # Erklaerung: self.last_count_time bekommt mit = einen neuen Wert; Zeitpunkt, wann zuletzt ein Fringe gezaehlt wurde.
        self.dark_counter = 0
        # Erklaerung: setzt den Dunkel-Zaehler wieder auf null.
        self.bright_counter = 0
        # Erklaerung: setzt den Hell-Zaehler wieder auf null.
        self.intensity_history = []
        # Erklaerung: self.intensity_history bekommt mit = einen neuen Wert; Liste der letzten Intensitaetswerte zum Glaetten des Signals.

        self.label_um.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text="Distance: 0.000 µm"
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_ps.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text="Time Delay: 0.0000 ps"
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_accumulated_fringes.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text="Accumulated Fringes Count: 0"
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.update_comparison_labels(0.0)
        # Erklaerung: aktualisiert den Vergleich zwischen Stage-Weg und Fringe-Weg.

    def finish_calibration_stage_reset(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; finish_calibration_stage_reset ist der Name. laesst die Stage nach der Kalibrierung zur Nullposition zurueckfahren.

        self.returning_stage_after_calibration = True
        # Erklaerung: self.returning_stage_after_calibration bekommt mit = einen neuen Wert; merkt, ob die Stage nach der Kalibrierung gerade zurueckfaehrt.

        self.status.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text="Calibration done - stage returning to 0.00000000000 mm",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=ORANGE_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.start_stage_move_to(
        # Erklaerung: ruft die Methode auf, die eine absolute Stage-Bewegung startet. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            0.0,
            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
            reset_after_move=True
            # Erklaerung: reset_after_move bekommt hier einen Wert rechts vom =. Schalter, ob nach der Bewegung Werte zurueckgesetzt werden sollen.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def calibration_stage_motion(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; calibration_stage_motion ist der Name. bewegt die Stage waehrend der Kalibrierung automatisch vor und zurueck.

        if not self.stage_connected:
        # Erklaerung: prueft, ob die Stage nicht verbunden ist.
            return
            # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

        start_pos = self.stage.get_position()
        # Erklaerung: liest die aktuelle Stage-Position und speichert sie als Startposition.
        step_mm = 0.0001
        # Erklaerung: step_mm bekommt mit = einen neuen Wert; Schrittgroesse in Millimetern.
        steps = 4
        # Erklaerung: steps bekommt mit = den Wert/Ausdruck rechts davon gespeichert.

        # move forward in 4 steps
        # Erklaerung: Diese Zeile ist ein Kommentar; Python ignoriert sie, sie erklaert nur etwas fuer Menschen.
        for i in range(1, steps + 1):
        # Erklaerung: for bedeutet Schleife ueber mehrere Werte; i nimmt nacheinander die Werte aus range(...) an.
            if not self.is_monitoring:
            # Erklaerung: prueft, ob das Monitoring gestoppt wurde.
                return
                # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

            target = start_pos + step_mm * i
            # Erklaerung: target= ist ein benanntes Argument und legt die Funktion fest, die im Hintergrund-Thread laufen soll.
            target = self.stage.clamp_position(target)
            # Erklaerung: target= ist ein benanntes Argument und legt die Funktion fest, die im Hintergrund-Thread laufen soll.

            if not self.stage.move_absolute(target):
            # Erklaerung: versucht zur Zielposition zu fahren; bei False wird abgebrochen.
                return
                # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

            while self.stage.is_moving and self.is_monitoring:
            # Erklaerung: wartet, solange die Stage faehrt und Monitoring noch aktiv ist.
                time.sleep(0.01)
                # Erklaerung: wartet 0.01 Sekunden in einer kurzen Schleife.

            time.sleep(0.25)
            # Erklaerung: wartet 0.25 Sekunden zwischen Stage-Schritten.

        # move back in 4 steps
        # Erklaerung: Diese Zeile ist ein Kommentar; Python ignoriert sie, sie erklaert nur etwas fuer Menschen.
        for i in range(steps - 1, -1, -1):
        # Erklaerung: for bedeutet Schleife ueber mehrere Werte; i nimmt nacheinander die Werte aus range(...) an.
            if not self.is_monitoring:
            # Erklaerung: prueft, ob das Monitoring gestoppt wurde.
                return
                # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

            target = start_pos + step_mm * i
            # Erklaerung: target= ist ein benanntes Argument und legt die Funktion fest, die im Hintergrund-Thread laufen soll.
            target = self.stage.clamp_position(target)
            # Erklaerung: target= ist ein benanntes Argument und legt die Funktion fest, die im Hintergrund-Thread laufen soll.

            if not self.stage.move_absolute(target):
            # Erklaerung: versucht zur Zielposition zu fahren; bei False wird abgebrochen.
                return
                # Erklaerung: verlaesst die aktuelle Methode sofort; danach wird in dieser Methode nichts mehr ausgefuehrt.

            while self.stage.is_moving and self.is_monitoring:
            # Erklaerung: wartet, solange die Stage faehrt und Monitoring noch aktiv ist.
                time.sleep(0.01)
                # Erklaerung: wartet 0.01 Sekunden in einer kurzen Schleife.

            time.sleep(0.25)
            # Erklaerung: wartet 0.25 Sekunden zwischen Stage-Schritten.

    def move_to_center_after_calibration(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; move_to_center_after_calibration ist der Name. startet die Rueckfahrt zur Mitte nach der Kalibrierung.

        self.returning_stage_after_calibration = True
        # Erklaerung: self.returning_stage_after_calibration bekommt mit = einen neuen Wert; merkt, ob die Stage nach der Kalibrierung gerade zurueckfaehrt.

        self.start_stage_move_to(
        # Erklaerung: ruft die Methode auf, die eine absolute Stage-Bewegung startet. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            0.0,
            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
            reset_after_move=True
            # Erklaerung: reset_after_move bekommt hier einen Wert rechts vom =. Schalter, ob nach der Bewegung Werte zurueckgesetzt werden sollen.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def reset_stage_after_calibration(self, pos=None):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; reset_stage_after_calibration ist der Name. setzt Stage- und Messanzeigen nach der Kalibrierungs-Rueckfahrt zurueck.

        self.reset_stage_movement_tracking(pos)
        # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.

        self.reset_measurement_after_calibration()
        # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.

        self.returning_stage_after_calibration = False
        # Erklaerung: self.returning_stage_after_calibration bekommt mit = einen neuen Wert; merkt, ob die Stage nach der Kalibrierung gerade zurueckfaehrt.

        self.status.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text="Monitoring running",
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
            text_color=GREEN_COLOR
            # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def update_comparison_labels(self, driven_mm=None):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; update_comparison_labels ist der Name. aktualisiert den Vergleich zwischen gefahrenem und berechnetem Weg.

        if driven_mm is None:
        # Erklaerung: wenn kein Wert uebergeben wurde, wird der gespeicherte Vergleichswert benutzt.

            driven_mm = self.current_stage_movement_for_compare
            # Erklaerung: driven_mm bekommt mit = einen neuen Wert; gefahrene Strecke, die angezeigt oder verglichen werden soll.

        driven_distance_mm = abs(driven_mm)
        # Erklaerung: driven_distance_mm bekommt mit = einen neuen Wert; positiver Betrag der gefahrenen Strecke.

        calculated_fringes = self.accumulated_fringes
        # Erklaerung: calculated_fringes bekommt mit = einen neuen Wert; Anzahl der gezaehlten Fringes fuer die Berechnung.

        calculated_mm = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            calculated_fringes
            # Erklaerung: calculated_fringes ist hier ein Wert/Parameter. Anzahl der gezaehlten Fringes fuer die Berechnung.
            * self.fringe_distance_mm
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        difference_mm = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            driven_distance_mm
            # Erklaerung: driven_distance_mm ist hier ein Wert/Parameter. positiver Betrag der gefahrenen Strecke.
            - calculated_mm
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_compare_driven.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=(
            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                f"Driven: {driven_distance_mm:.6f} mm"
                # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_compare_calculated.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=(
            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                f"Calculated: {calculated_mm:.6f} mm"
                # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_compare_difference.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=(
            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                f"Difference: {difference_mm:.6f} mm"
                # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def loop(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; loop ist der Name. Hauptschleife: holt Kamerabilder, misst Intensitaet, zaehlt Fringes und aktualisiert Anzeigen.

        frame_counter = 0
        # Erklaerung: startet den Bildzaehler bei null.

        while self.is_monitoring:
        # Erklaerung: Hauptschleife: laeuft immer weiter, solange Monitoring aktiv ist.

            img = self.camera_handler.get_frame()
            # Erklaerung: holt ein neues Bild von der Kamera.

            if img is None:
            # Erklaerung: prueft, ob kein gueltiges Kamerabild angekommen ist.
                continue
                # Erklaerung: springt zum naechsten Schleifendurchlauf und ueberspringt den Rest dieses Durchlaufs.

            frame_counter += 1
            # Erklaerung: erhoeht den Bildzaehler um 1.

            if frame_counter % 20 == 0:
            # Erklaerung: % ist Restrechnung; alle 20 Bilder wird das Livebild aktualisiert.

                self.after(
                # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    0,
                    # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                    lambda f=img:
                    # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                    self.update_image(f)
                    # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            intensity = (
            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                self.camera_handler
                # Erklaerung: self.camera_handler ist hier ein Wert/Parameter. Objekt, das die Kamera bedient.
                .get_fringe_intensity_from_frame(img)
                # Erklaerung: berechnet die Fringe-Helligkeit aus einem Kamerabild.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            if intensity is not None:
            # Erklaerung: arbeitet nur weiter, wenn eine gueltige Intensitaet berechnet wurde.

                fringe_counted = False
                # Erklaerung: merkt erstmal: in diesem Durchlauf wurde noch kein Fringe gezaehlt.

                if self.calibrating:
                # Erklaerung: prueft, ob gerade die automatische Kalibrierung laeuft.

                    if (not self.calibration_motion_started
                    # Erklaerung: if startet eine Bedingung; die Klammer erlaubt, die Bedingung ueber mehrere Zeilen zu schreiben.
                            and self.stage_connected):
                            # Erklaerung: Die schliessende Klammer beendet den Kopf; der Doppelpunkt startet den eingerueckten Block darunter.
                        self.calibration_motion_started = True
                        # Erklaerung: merkt, dass die Kalibrierbewegung der Stage jetzt gestartet wurde.
                        threading.Thread(
                        # Erklaerung: erstellt einen Hintergrund-Thread fuer eine Aufgabe, die parallel zum Fenster laufen soll.
                            target=self.calibration_stage_motion,
                            # Erklaerung: target= ist ein benanntes Argument und legt die Funktion fest, die im Hintergrund-Thread laufen soll. Das Komma trennt diese Angabe von der naechsten.
                            daemon=True
                            # Erklaerung: daemon= ist ein benanntes Argument und sorgt dafuer, dass der Thread das Programm beim Schliessen nicht blockiert.
                        ).start()
                        # Erklaerung: startet den gerade erstellten Thread.

                    self.calibration_values.append(
                    # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                        intensity
                        # Erklaerung: intensity ist hier ein Wert/Parameter. gemessene Helligkeit/Intensitaet im ROI-Bereich.
                    )
                    # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                    elapsed = (
                    # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                        time.time()
                        # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
                        - self.calibration_start_time
                        # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
                    )
                    # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                    self.after(
                    # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                        0,
                        # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                        lambda e=elapsed:
                        # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                        self.label_thresholds.configure(
                        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                            text=f"Calibrating {e:.1f}/5s"
                            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
                    )
                    # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                    if elapsed >= 5:
                    # Erklaerung: nach mindestens 5 Sekunden Kalibrierzeit werden die Schwellen berechnet.

                        min_val = min(
                        # Erklaerung: nimmt den kleineren Wert oder den kleinsten Wert einer Liste. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                            self.calibration_values
                            # Erklaerung: self.calibration_values ist hier ein Wert/Parameter. Liste der Intensitaeten, die waehrend der Kalibrierung gesammelt werden.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                        max_val = max(
                        # Erklaerung: nimmt den groesseren Wert oder den groessten Wert einer Liste. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                            self.calibration_values
                            # Erklaerung: self.calibration_values ist hier ein Wert/Parameter. Liste der Intensitaeten, die waehrend der Kalibrierung gesammelt werden.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                        value_range = (
                        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                            max_val - min_val
                            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                        self.dark_threshold = (
                        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                            min_val
                            # Erklaerung: min_val ist hier ein Wert/Parameter. kleinster Intensitaetswert waehrend der Kalibrierung.
                            + value_range * 0.125
                            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                        self.bright_threshold = (
                        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                            max_val
                            # Erklaerung: max_val ist hier ein Wert/Parameter. groesster Intensitaetswert waehrend der Kalibrierung.
                            - value_range * 0.30
                            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                        self.calibrating = False
                        # Erklaerung: beendet den Kalibrierungszustand.

                        self.after(
                        # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                            0,
                            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                            lambda:
                            # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                            self.label_thresholds.configure(
                            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                                text=(
                                # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                                    f"Dark: "
                                    # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                                    f"{self.dark_threshold:.2f} | "
                                    # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                                    f"Bright: "
                                    # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                                    f"{self.bright_threshold:.2f}"
                                    # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                                )
                                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
                            )
                            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                        self.after(
                        # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                            0,
                            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                            lambda:
                            # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                            self.status.configure(
                            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                                text="Monitoring running",
                                # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest. Das Komma trennt diese Angabe von der naechsten.
                                text_color=GREEN_COLOR
                                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
                            )
                            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                        self.after(
                        # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                            0,
                            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                            self.finish_calibration_stage_reset
                            # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                else:
                # Erklaerung: else bedeutet sonst; dieser Block laeuft, wenn die if-Bedingung vorher falsch war.

                    if not self.returning_stage_after_calibration:
                    # Erklaerung: zaehlt nur Fringes, wenn die Stage nicht gerade nach der Kalibrierung zurueckfaehrt.

                        fringe_counted = (
                        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                            self.update_accumulated_fringes(
                            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                                intensity
                                # Erklaerung: intensity ist hier ein Wert/Parameter. gemessene Helligkeit/Intensitaet im ROI-Bereich.
                            )
                            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
                        )
                        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

                self.after(
                # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    0,
                    # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                    lambda v=intensity, c=fringe_counted:
                    # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                    self.update_intensity_label(v, c)
                    # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            dist_mm = (
            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                self.accumulated_fringes
                # Erklaerung: self.accumulated_fringes ist hier ein Wert/Parameter. zaehlt alle erkannten Interferenzstreifen seit dem letzten Reset.
                * self.fringe_distance_mm
                # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            dist_um = dist_mm * 1000
            # Erklaerung: rechnet Millimeter in Mikrometer um; 1 mm sind 1000 Mikrometer.

            time_ps = (
            # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                2 * dist_mm
                # Erklaerung: 2 * bedeutet doppelte Strecke; beim Interferometer zaehlt Hin- und Rueckweg fuer die Zeitverzoegerung.
            ) / SPEED_OF_LIGHT_MM_PS
            # Erklaerung: teilt die optische Weglaenge durch die Lichtgeschwindigkeit und ergibt Pikosekunden.

            self.after(
            # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                0,
                # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                lambda:
                # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                self.update_values(
                # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                    dist_mm,
                    # Erklaerung: dist_mm ist hier ein Wert/Parameter. aus Fringes berechnete Distanz in Millimetern. Das Komma trennt diesen Wert vom naechsten.
                    dist_um,
                    # Erklaerung: dist_um ist hier ein Wert/Parameter. dieselbe Distanz in Mikrometern. Das Komma trennt diesen Wert vom naechsten.
                    time_ps
                    # Erklaerung: time_ps ist hier ein Wert/Parameter. aus der Distanz berechnete Zeitverzoegerung in Pikosekunden.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            self.after(
            # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                0,
                # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                lambda:
                # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                self.label_accumulated_fringes.configure(
                # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    text=(
                    # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
                        f"Accumulated Fringes Count: "
                        # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                        f"{self.accumulated_fringes}"
                        # Erklaerung: Das f vor dem Text bedeutet f-string: Werte in geschweiften Klammern werden in den Text eingesetzt.
                    )
                    # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def update_accumulated_fringes(
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; update_accumulated_fringes ist der Name. entscheidet anhand dunkel/hell, ob ein neuer Fringe gezaehlt wird.
        self,
        # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
        intensity
        # Erklaerung: intensity ist hier ein Wert/Parameter. gemessene Helligkeit/Intensitaet im ROI-Bereich.
    ):
    # Erklaerung: Die Klammer beendet die Bedingung; der Doppelpunkt startet den eingerueckten Codeblock.

        self.intensity_history.append(
        # Erklaerung: haengt einen neuen Intensitaetswert hinten an die Verlaufsliste an.
            intensity
            # Erklaerung: intensity ist hier ein Wert/Parameter. gemessene Helligkeit/Intensitaet im ROI-Bereich.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        if len(self.intensity_history) > 5:
        # Erklaerung: wenn mehr als 5 Werte gespeichert sind, wird die Liste wieder gekuerzt.
            self.intensity_history.pop(0)
            # Erklaerung: entfernt den aeltesten Wert aus der Liste.

        smooth_intensity = np.mean(
        # Erklaerung: berechnet den Mittelwert mit NumPy. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.intensity_history
            # Erklaerung: self.intensity_history ist hier ein Wert/Parameter. Liste der letzten Intensitaetswerte zum Glaetten des Signals.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        if smooth_intensity < self.dark_threshold:
        # Erklaerung: prueft, ob die geglaettete Intensitaet dunkel genug ist.

            self.dark_counter += 1
            # Erklaerung: erhoeht den Dunkel-Zaehler um 1.

        else:
        # Erklaerung: else bedeutet sonst; dieser Block laeuft, wenn die if-Bedingung vorher falsch war.

            self.dark_counter = 0
            # Erklaerung: setzt den Dunkel-Zaehler wieder auf null.

        if self.dark_counter >= REQUIRED_DARK_FRAMES:
        # Erklaerung: wenn genug dunkle Frames nacheinander da waren, gilt das Signal als dunkel.

            self.was_dark = True
            # Erklaerung: merkt sich, dass ein dunkler Zustand erkannt wurde.

        if smooth_intensity > self.bright_threshold:
        # Erklaerung: prueft, ob die geglaettete Intensitaet hell genug ist.

            self.bright_counter += 1
            # Erklaerung: erhoeht den Hell-Zaehler um 1.

        else:
        # Erklaerung: else bedeutet sonst; dieser Block laeuft, wenn die if-Bedingung vorher falsch war.

            self.bright_counter = 0
            # Erklaerung: setzt den Hell-Zaehler wieder auf null.

        cooldown_ok = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            time.time() - self.last_count_time
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        ) > FRINGE_COOLDOWN
        # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.

        if (
        # Erklaerung: if startet eine Bedingung; die Klammer erlaubt, die Bedingung ueber mehrere Zeilen zu schreiben.
            self.was_dark
            # Erklaerung: self.was_dark ist hier ein Wert/Parameter. merkt sich, ob das Signal zuletzt sicher dunkel war.
            and self.bright_counter
            # Erklaerung: and bedeutet "und"; alle verbundenen Bedingungen muessen wahr sein.
            >= REQUIRED_BRIGHT_FRAMES
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
            and cooldown_ok
            # Erklaerung: and bedeutet "und"; alle verbundenen Bedingungen muessen wahr sein.
        ):
        # Erklaerung: Die Klammer beendet die Bedingung; der Doppelpunkt startet den eingerueckten Codeblock.

            self.accumulated_fringes += 1
            # Erklaerung: zaehlt einen neuen Fringe dazu.

            self.was_dark = False
            # Erklaerung: loescht den dunklen Zustand, damit erst wieder ein neuer Dunkel-Hell-Wechsel noetig ist.

            self.last_count_time = time.time()
            # Erklaerung: speichert den aktuellen Zeitpunkt als letzten Zaehlzeitpunkt.

            self.dark_counter = 0
            # Erklaerung: setzt den Dunkel-Zaehler wieder auf null.

            self.bright_counter = 0
            # Erklaerung: setzt den Hell-Zaehler wieder auf null.

            return True
            # Erklaerung: meldet an den Aufrufer: Ja, ein Fringe wurde gezaehlt.

        return False
        # Erklaerung: meldet an den Aufrufer: Nein, kein Fringe wurde gezaehlt.

    def update_intensity_label(
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; update_intensity_label ist der Name. zeigt die aktuelle Intensitaet an und faerbt kurz gruen bei einem neuen Fringe.
        self,
        # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
        intensity,
        # Erklaerung: intensity ist hier ein Wert/Parameter. gemessene Helligkeit/Intensitaet im ROI-Bereich. Das Komma trennt diesen Wert vom naechsten.
        fringe_counted
        # Erklaerung: fringe_counted ist hier ein Wert/Parameter. merkt, ob in diesem Durchlauf ein neuer Fringe gezaehlt wurde.
    ):
    # Erklaerung: Die Klammer beendet die Bedingung; der Doppelpunkt startet den eingerueckten Codeblock.

        self.label_intensity.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=f"Intensity: {intensity:.2f}"
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        if fringe_counted:
        # Erklaerung: if bedeutet "falls"; der eingerueckte Block darunter laeuft nur, wenn die Bedingung wahr ist.

            self.label_intensity.configure(
            # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                text_color=GREEN_COLOR
                # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

            self.after(
            # Erklaerung: plant eine Aktion im Tkinter-Hauptfenster; wichtig fuer Updates aus Threads. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                250,
                # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
                lambda:
                # Erklaerung: lambda erstellt eine kleine namenlose Funktion; die Werte vor dem Doppelpunkt werden spaeter benutzt.
                self.label_intensity.configure(
                # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
                    text_color=TEXT_COLOR
                    # Erklaerung: text_color= ist ein benanntes Argument und legt die Schriftfarbe fest.
                )
                # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.
            )
            # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    def update_values(
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; update_values ist der Name. aktualisiert Distanz, Zeitverzoegerung und Vergleichsanzeigen.
        self,
        # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
        mm,
        # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
        um,
        # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
        ps
        # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
    ):
    # Erklaerung: Die Klammer beendet die Bedingung; der Doppelpunkt startet den eingerueckten Codeblock.

        self.label_um.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=f"Distance: {um:.3f} µm"
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.label_ps.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            text=f"Time Delay: {ps:.4f} ps"
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.update_comparison_labels()
        # Erklaerung: aktualisiert die Vergleichsanzeigen mit den aktuellen gespeicherten Werten.

    def update_image(self, img):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; update_image ist der Name. bereitet das Kamerabild fuer die Anzeige vor und zeichnet die ROI-Box ein.

        display = img.astype(np.float32)
        # Erklaerung: kopiert das Kamerabild in Gleitkommazahlen, damit Helligkeit sauber skaliert werden kann.

        display -= np.min(display)
        # Erklaerung: zieht den kleinsten Bildwert ab, damit das dunkelste Pixel bei 0 liegt.

        if np.max(display) > 0:
        # Erklaerung: prueft, ob es einen positiven Maximalwert gibt, bevor durch ihn geteilt wird.
            display /= np.max(display)
            # Erklaerung: teilt alle Pixel durch den Maximalwert, dadurch liegen sie zwischen 0 und 1.

        display = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            display * 255
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        ).astype(np.uint8)
        # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.

        pil = Image.fromarray(display).convert(
        # Erklaerung: wandelt ein NumPy-Array in ein PIL-Bild um. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            "RGB"
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        original_w, original_h = pil.size
        # Erklaerung: original_w, original_h bekommt mit = den Wert/Ausdruck rechts davon gespeichert.

        scale_x = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            self.live_size[0] / original_w
            # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        scale_y = (
        # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
            self.live_size[1] / original_h
            # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        pil = pil.resize(self.live_size)
        # Erklaerung: skaliert das Bild auf die gewuenschte Anzeige-Groesse.

        draw = ImageDraw.Draw(pil)
        # Erklaerung: erstellt ein Zeichenwerkzeug fuer das PIL-Bild.

        x1 = int(
        # Erklaerung: wandelt einen Wert in eine ganze Zahl um. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.camera_handler.roi_x * scale_x
            # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        y1 = int(
        # Erklaerung: wandelt einen Wert in eine ganze Zahl um. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            self.camera_handler.roi_y * scale_y
            # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        x2 = int(
        # Erklaerung: wandelt einen Wert in eine ganze Zahl um. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            (
            # Erklaerung: Die oeffnende Klammer startet einen Ausdruck ueber mehrere Zeilen.
                self.camera_handler.roi_x
                # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
                + self.camera_handler.roi_w
                # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
            ) * scale_x
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        y2 = int(
        # Erklaerung: wandelt einen Wert in eine ganze Zahl um. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            (
            # Erklaerung: Die oeffnende Klammer startet einen Ausdruck ueber mehrere Zeilen.
                self.camera_handler.roi_y
                # Erklaerung: self bedeutet dieses App-Objekt; der Punkt greift auf eine Eigenschaft oder Methode davon zu.
                + self.camera_handler.roi_h
                # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
            ) * scale_y
            # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        draw.rectangle(
        # Erklaerung: zeichnet ein Rechteck, hier die gelbe ROI-Markierung.
            [x1, y1, x2, y2],
            # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
            outline="yellow",
            # Erklaerung: outline= ist ein benanntes Argument und legt die Farbe der gezeichneten Umrandung fest. Das Komma trennt diese Angabe von der naechsten.
            width=3
            # Erklaerung: width= ist ein benanntes Argument und legt die Breite des Elements fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        ctk_img = ctk.CTkImage(
        # Erklaerung: erstellt ein Bildobjekt, das CustomTkinter anzeigen kann. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            light_image=pil,
            # Erklaerung: light_image= ist ein benanntes Argument und setzt das Bild fuer den hellen Darstellungsmodus. Das Komma trennt diese Angabe von der naechsten.
            size=self.live_size
            # Erklaerung: size= ist ein benanntes Argument und legt die Anzeige-Groesse des Bildes fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.image_label.configure(
        # Erklaerung: aendert Eigenschaften eines vorhandenen UI-Elements. Die offene Klammer bedeutet: die Angaben folgen in den naechsten Zeilen.
            image=ctk_img,
            # Erklaerung: image= ist ein benanntes Argument und setzt das Bild, das im Label angezeigt wird. Das Komma trennt diese Angabe von der naechsten.
            text=""
            # Erklaerung: text= ist ein benanntes Argument und legt den sichtbaren Text fest.
        )
        # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

        self.image_label.image = ctk_img
        # Erklaerung: speichert eine Referenz auf das Bild, damit es nicht von Python geloescht wird.

    def on_close(self):
    # Erklaerung: def bedeutet "definiere Funktion/Methode"; on_close ist der Name. raeumt Kamera und Stage beim Schliessen des Fensters auf.

        self.is_monitoring = False
        # Erklaerung: self.is_monitoring bekommt mit = einen neuen Wert; merkt sich, ob die Messung gerade laeuft.

        try:
        # Erklaerung: try startet einen Bereich, in dem ein Fehler abgefangen werden kann.
            self.camera_handler.close()
            # Erklaerung: schliesst die Kamera-Verbindung sauber.

        except:
        # Erklaerung: faengt jeden Fehler ab; hier wird beim Aufraeumen bewusst nichts weiter gemacht.
            pass
            # Erklaerung: pass bedeutet: tue absichtlich nichts; es ist ein Platzhalter.

        try:
        # Erklaerung: try startet einen Bereich, in dem ein Fehler abgefangen werden kann.
            self.stage.close()
            # Erklaerung: schliesst die Stage-Verbindung sauber.

        except:
        # Erklaerung: faengt jeden Fehler ab; hier wird beim Aufraeumen bewusst nichts weiter gemacht.
            pass
            # Erklaerung: pass bedeutet: tue absichtlich nichts; es ist ein Platzhalter.

        self.destroy()
        # Erklaerung: schliesst und zerstoert das Fenster.


if __name__ == "__main__":
# Erklaerung: dieser Block laeuft nur, wenn diese Datei direkt gestartet wird.

    app = InterferometerApp()
    # Erklaerung: erstellt die App aus der Klasse InterferometerApp.

    app.protocol(
    # Erklaerung: Die offene Klammer startet einen Funktionsaufruf oder Ausdruck ueber mehrere Zeilen.
        "WM_DELETE_WINDOW",
        # Erklaerung: Das Komma bedeutet: diese Angabe ist noch nicht die letzte; danach kommt noch etwas.
        app.on_close
        # Erklaerung: Diese Zeile ist Teil des Codes; Python fuehrt sie in dieser Reihenfolge aus.
    )
    # Erklaerung: Die schliessende Klammer beendet den mehrzeiligen Ausdruck oder Funktionsaufruf.

    app.mainloop()
    # Erklaerung: startet die Tkinter-Ereignisschleife; dadurch bleibt das Fenster offen und reagiert auf Klicks.
