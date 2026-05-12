# =========================================================
# INTERFEROMETER OSCILLOSCOPE MONITOR
#
# Fringe Detection über Photodiode + Oszilloskop
#
# Statt Kamera:
# - direkte Spannungsmessung
# - extrem hohe Samplingrate
# - viel robuster
#
# Benötigt:
# pip install pyvisa pyvisa-py numpy customtkinter
#
# =========================================================

import threading
import time
import numpy as np
import customtkinter as ctk
import pyvisa


# =========================================================
# PHYSICS
# =========================================================

LASER_WAVELENGTH_NM = 632.8

FRINGE_DISTANCE_MM = (
    (LASER_WAVELENGTH_NM / 2)
    / 1_000_000
)

SPEED_OF_LIGHT_MM_PS = 0.299792458


# =========================================================
# COLORS
# =========================================================

TEXT_COLOR = "#0A4A51"

GREEN_COLOR = "#1EAD4F"

RED_COLOR = "#C0392B"


# =========================================================
# OSCILLOSCOPE HANDLER
# =========================================================

class OscilloscopeHandler:

    def __init__(self):

        self.scope = None

        self.connected = False

        self.simulation_mode = False

        # ---------------------------------------------
        # VISA
        # ---------------------------------------------

        try:

            self.rm = pyvisa.ResourceManager()

            resources = self.rm.list_resources()

            print("Available VISA devices:")

            for r in resources:
                print(r)

            if len(resources) == 0:

                raise Exception("No oscilloscope found")

            # Erstes Gerät öffnen
            self.scope = self.rm.open_resource(resources[0])

            self.scope.timeout = 2000

            self.connected = True

            print("Oscilloscope connected")

        except Exception as e:

            print("Oscilloscope error:", e)

            print("Using simulation mode")

            self.simulation_mode = True

            self.connected = True

        # ---------------------------------------------
        # SIMULATION
        # ---------------------------------------------

        self.sim_phase = 0

    # =====================================================
    # READ SIGNAL
    # =====================================================

    def get_signal_value(self):

        # -------------------------------------------------
        # SIMULATION MODE
        # -------------------------------------------------

        if self.simulation_mode:

            self.sim_phase += 0.25

            signal = (
                500
                + 220 * np.sin(self.sim_phase)
                + np.random.normal(0, 15)
            )

            return float(signal)

        # -------------------------------------------------
        # REAL OSCILLOSCOPE
        # -------------------------------------------------

        try:

            # Beispiel:
            # viele Scopes unterstützen:
            #
            # MEASure:VAVerage?
            #
            # oder:
            #
            # MEASure:VMAX?
            #
            # oder:
            #
            # CURVe?
            #
            # Das hängt vom Scope ab.

            value = self.scope.query(
                "MEASure:VAVerage?"
            )

            return float(value)

        except Exception as e:

            print("Read error:", e)

            return None

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        try:

            if self.scope is not None:
                self.scope.close()

        except Exception as e:

            print("Scope close error:", e)


# =========================================================
# APP
# =========================================================

class InterferometerApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        # -------------------------------------------------
        # STATES
        # -------------------------------------------------

        self.is_monitoring = False

        self.signal_history = []

        self.history_size = 9

        self.accumulated_fringes = 0

        # -------------------------------------------------
        # PEAK DETECTOR
        # -------------------------------------------------

        self.state = "SEARCH_VALLEY"

        self.last_valley = None

        self.last_peak = None

        self.last_count_time = 0

        self.min_amplitude = 25

        self.cooldown = 0.001

        # -------------------------------------------------
        # OSCILLOSCOPE
        # -------------------------------------------------

        self.scope_handler = OscilloscopeHandler()

        self.scope_connected = self.scope_handler.connected

        # -------------------------------------------------
        # WINDOW
        # -------------------------------------------------

        self.title("Interferometer Oscilloscope Monitor")

        self.geometry("700x700")

        ctk.set_appearance_mode("light")

        self.configure(fg_color="white")

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        ctk.CTkLabel(
            self,
            text="Interferometer Oscilloscope Monitor",
            font=("Arial", 26, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=20)

        # -------------------------------------------------
        # START BUTTON
        # -------------------------------------------------

        self.btn = ctk.CTkButton(
            self,
            text="START MONITORING",
            command=self.toggle,
            height=45,
            width=240,
            font=("Arial", 16, "bold"),
            fg_color=TEXT_COLOR
        )

        self.btn.pack(pady=10)

        # -------------------------------------------------
        # RESET BUTTON
        # -------------------------------------------------

        self.restart_btn = ctk.CTkButton(
            self,
            text="RESET",
            command=self.restart,
            height=40,
            width=220,
            font=("Arial", 14, "bold"),
            fg_color="#D35400"
        )

        self.restart_btn.pack(pady=5)

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status = ctk.CTkLabel(
            self,
            text="Status: Stopped",
            font=("Arial", 15),
            text_color=TEXT_COLOR
        )

        self.status.pack(pady=10)

        # -------------------------------------------------
        # INFO FRAME
        # -------------------------------------------------

        self.frame = ctk.CTkFrame(
            self,
            fg_color="#EEEEEE"
        )

        self.frame.pack(
            pady=20,
            padx=25,
            fill="x"
        )

        # -------------------------------------------------
        # SIGNAL
        # -------------------------------------------------

        self.label_signal = ctk.CTkLabel(
            self.frame,
            text="Signal: 0.00",
            font=("Arial", 18, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_signal.pack(pady=10)

        # -------------------------------------------------
        # FRINGES
        # -------------------------------------------------

        self.label_fringes = ctk.CTkLabel(
            self.frame,
            text="Fringes: 0",
            font=("Arial", 20, "bold"),
            text_color=TEXT_COLOR
        )

        self.label_fringes.pack(pady=10)

        # -------------------------------------------------
        # DISTANCE
        # -------------------------------------------------

        self.label_mm = ctk.CTkLabel(
            self.frame,
            text="Distance: 0.000000 mm",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_mm.pack(pady=5)

        # -------------------------------------------------
        # TIME DELAY
        # -------------------------------------------------

        self.label_ps = ctk.CTkLabel(
            self.frame,
            text="Time Delay: 0.0000 ps",
            font=("Arial", 16),
            text_color=TEXT_COLOR
        )

        self.label_ps.pack(pady=5)

    # =====================================================
    # START / STOP
    # =====================================================

    def toggle(self):

        if not self.is_monitoring:

            if not self.scope_connected:

                self.status.configure(
                    text="Scope not connected",
                    text_color="red"
                )

                return

            self.restart_values()

            self.is_monitoring = True

            self.btn.configure(
                text="STOP",
                fg_color=RED_COLOR
            )

            self.status.configure(
                text="Running",
                text_color="green"
            )

            threading.Thread(
                target=self.loop,
                daemon=True
            ).start()

        else:

            self.is_monitoring = False

            self.btn.configure(
                text="START MONITORING",
                fg_color=TEXT_COLOR
            )

            self.status.configure(
                text="Stopped",
                text_color=TEXT_COLOR
            )

    # =====================================================
    # RESET
    # =====================================================

    def restart(self):

        self.restart_values()

    # =====================================================
    # RESET VALUES
    # =====================================================

    def restart_values(self):

        self.signal_history = []

        self.accumulated_fringes = 0

        self.state = "SEARCH_VALLEY"

        self.last_valley = None

        self.last_peak = None

        self.last_count_time = 0

    # =====================================================
    # MAIN LOOP
    # =====================================================

    def loop(self):

        while self.is_monitoring:

            signal = self.scope_handler.get_signal_value()

            if signal is None:
                continue

            fringe_counted = self.update_fringes(signal)

            # -------------------------------------------------
            # PHYSICS
            # -------------------------------------------------

            dist_mm = (
                self.accumulated_fringes
                * FRINGE_DISTANCE_MM
            )

            time_ps = (
                2 * dist_mm
            ) / SPEED_OF_LIGHT_MM_PS

            # -------------------------------------------------
            # GUI
            # -------------------------------------------------

            self.after(
                0,
                lambda s=signal, c=fringe_counted:
                self.update_signal_label(s, c)
            )

            self.after(
                0,
                lambda f=self.accumulated_fringes:
                self.label_fringes.configure(
                    text=f"Fringes: {f}"
                )
            )

            self.after(
                0,
                lambda d=dist_mm:
                self.label_mm.configure(
                    text=f"Distance: {d:.6f} mm"
                )
            )

            self.after(
                0,
                lambda p=time_ps:
                self.label_ps.configure(
                    text=f"Time Delay: {p:.4f} ps"
                )
            )

    # =====================================================
    # PEAK DETECTOR
    # =====================================================

    def update_fringes(self, value):

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        self.signal_history.append(value)

        if len(self.signal_history) > self.history_size:
            self.signal_history.pop(0)

        if len(self.signal_history) < 7:
            return False

        signal = np.array(self.signal_history)

        # -------------------------------------------------
        # MEDIAN SMOOTHING
        # -------------------------------------------------

        smooth_signal = []

        for i in range(2, len(signal) - 2):

            window = signal[i - 2:i + 3]

            smooth_signal.append(np.median(window))

        smooth_signal = np.array(smooth_signal)

        if len(smooth_signal) < 3:
            return False

        # -------------------------------------------------
        # LAST 3 POINTS
        # -------------------------------------------------

        a = smooth_signal[-3]

        b = smooth_signal[-2]

        c = smooth_signal[-1]

        current_time = time.time()

        cooldown_ok = (
            current_time - self.last_count_time
        ) > self.cooldown

        # -------------------------------------------------
        # VALLEY
        # -------------------------------------------------

        is_valley = (
            b < a
            and b < c
        )

        # -------------------------------------------------
        # PEAK
        # -------------------------------------------------

        is_peak = (
            b > a
            and b > c
        )

        # -------------------------------------------------
        # SEARCH VALLEY
        # -------------------------------------------------

        if self.state == "SEARCH_VALLEY":

            if is_valley:

                self.last_valley = b

                self.state = "SEARCH_PEAK"

        # -------------------------------------------------
        # SEARCH PEAK
        # -------------------------------------------------

        elif self.state == "SEARCH_PEAK":

            if is_peak:

                self.last_peak = b

                amplitude = (
                    self.last_peak
                    - self.last_valley
                )

                if (
                    amplitude > self.min_amplitude
                    and cooldown_ok
                ):

                    self.accumulated_fringes += 1

                    self.last_count_time = current_time

                    self.state = "SEARCH_VALLEY"

                    return True

                else:

                    self.state = "SEARCH_VALLEY"

        return False

    # =====================================================
    # UPDATE SIGNAL LABEL
    # =====================================================

    def update_signal_label(self, signal, fringe_counted):

        self.label_signal.configure(
            text=f"Signal: {signal:.2f}"
        )

        if fringe_counted:

            self.label_signal.configure(
                text_color=GREEN_COLOR
            )

            self.after(
                100,
                lambda:
                self.label_signal.configure(
                    text_color=TEXT_COLOR
                )
            )

    # =====================================================
    # CLOSE
    # =====================================================

    def on_close(self):

        self.is_monitoring = False

        try:

            self.scope_handler.close()

        except Exception as e:

            print("Close error:", e)

        self.destroy()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    app = InterferometerApp()

    app.protocol(
        "WM_DELETE_WINDOW",
        app.on_close
    )

    app.mainloop()