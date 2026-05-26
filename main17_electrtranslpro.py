import os
import threading
import time
import numpy as np
import customtkinter as ctk

from PIL import Image, ImageDraw

from camera_handler import CameraHandler
from stage_controller import StageController
from fringe_counter import FringeCounter


LASER_WAVELENGTH_NM = 1576.3

FRINGE_DISTANCE_MM = (
    (LASER_WAVELENGTH_NM / 2) / 1_000_000
)

SPEED_OF_LIGHT_MM_PS = 0.299792458

TEXT_COLOR = "#0A4A51"
GREEN_COLOR = "#1EAD4F"
RED_COLOR = "#C0392B"

MANUAL_THRESHOLDS = False

MANUAL_DARK_THRESHOLD = 8
MANUAL_BRIGHT_THRESHOLD = 21


current_directory = os.path.dirname(
    os.path.abspath(__file__)
)

dll_path = os.path.join(
    current_directory,
    "Camera"
)

if os.name == "nt" and os.path.exists(dll_path):
    os.add_dll_directory(dll_path)


class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Interferometer")

        self.geometry("1050x700")

        ctk.set_appearance_mode("light")

        self.configure(fg_color="white")

        self.camera = CameraHandler()

        self.camera.connect()

        self.stage = StageController()

        self.stage.connect()

        self.motion_start_position = (
            self.stage.get_position()
        )

        self.stage_moved_mm = 0.0

        self.counter = FringeCounter()

        if MANUAL_THRESHOLDS:

            self.counter.dark_threshold = (
                MANUAL_DARK_THRESHOLD
            )

            self.counter.bright_threshold = (
                MANUAL_BRIGHT_THRESHOLD
            )

            self.counter.thresholds_ready = True

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="white"
        )

        self.scroll.pack(
            fill="both",
            expand=True
        )

        ctk.CTkLabel(
            self.scroll,
            text="Interferometer",
            font=("Arial", 28, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=20)

        self.stage_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.stage_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            self.stage_frame,
            text="Translation Stage",
            font=("Arial", 22, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=10)

        self.button_frame = ctk.CTkFrame(
            self.stage_frame,
            fg_color="transparent"
        )

        self.button_frame.pack(pady=10)

        self.btn_min = ctk.CTkButton(
            self.button_frame,
            text="|<",
            width=60,
            command=self.move_to_min
        )

        self.btn_min.grid(
            row=0,
            column=0,
            padx=5
        )

        self.btn_left = ctk.CTkButton(
            self.button_frame,
            text="<",
            width=60,
            command=self.step_negative
        )

        self.btn_left.grid(
            row=0,
            column=1,
            padx=5
        )

        self.btn_right = ctk.CTkButton(
            self.button_frame,
            text=">",
            width=60,
            command=self.step_positive
        )

        self.btn_right.grid(
            row=0,
            column=2,
            padx=5
        )

        self.btn_max = ctk.CTkButton(
            self.button_frame,
            text=">|",
            width=60,
            command=self.move_to_max
        )

        self.btn_max.grid(
            row=0,
            column=3,
            padx=5
        )

        ctk.CTkLabel(
            self.stage_frame,
            text="Step Size",
            font=("Arial", 16)
        ).pack()

        self.step_entry = ctk.CTkEntry(
            self.stage_frame,
            width=220
        )

        self.step_entry.insert(
            0,
            "0.020000000"
        )

        self.step_entry.pack(pady=5)

        ctk.CTkLabel(
            self.stage_frame,
            text="Target Value",
            font=("Arial", 16)
        ).pack()

        self.target_entry = ctk.CTkEntry(
            self.stage_frame,
            width=220
        )

        self.target_entry.insert(
            0,
            "0.000000000"
        )

        self.target_entry.pack(pady=5)

        self.move_target_btn = ctk.CTkButton(
            self.stage_frame,
            text="MOVE TO TARGET",
            command=self.move_to_target
        )

        self.move_target_btn.pack(pady=5)

        self.stop_btn = ctk.CTkButton(
            self.stage_frame,
            text="STOP",
            fg_color=RED_COLOR,
            command=self.stop_stage
        )

        self.stop_btn.pack(pady=5)

        self.label_current = ctk.CTkLabel(
            self.stage_frame,
            text="Current Value: 0.000000000 mm",
            font=("Arial", 18, "bold")
        )

        self.label_current.pack(pady=5)

        self.label_target = ctk.CTkLabel(
            self.stage_frame,
            text="Target Value: 0.000000000 mm",
            font=("Arial", 16)
        )

        self.label_target.pack(pady=5)

        self.data_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="#EEEEEE"
        )

        self.data_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.label_fringes = ctk.CTkLabel(
            self.data_frame,
            text="Fringes: 0",
            font=("Arial", 20, "bold")
        )

        self.label_fringes.pack(pady=5)

        self.label_mm = ctk.CTkLabel(
            self.data_frame,
            text="Distance: 0.000000 mm",
            font=("Arial", 18)
        )

        self.label_mm.pack(pady=5)

        self.label_um = ctk.CTkLabel(
            self.data_frame,
            text="Distance: 0.000 µm",
            font=("Arial", 18)
        )

        self.label_um.pack(pady=5)

        self.label_ps = ctk.CTkLabel(
            self.data_frame,
            text="Delay: 0.0000 ps",
            font=("Arial", 18)
        )

        self.label_ps.pack(pady=5)

        self.label_intensity = ctk.CTkLabel(
            self.data_frame,
            text="Intensity: 0.00",
            font=("Arial", 18)
        )

        self.label_intensity.pack(pady=5)

        self.label_thresholds = ctk.CTkLabel(
            self.data_frame,
            text="Thresholds waiting",
            font=("Arial", 16)
        )

        self.label_thresholds.pack(pady=5)

        self.label_distance_comparison = ctk.CTkLabel(
            self.data_frame,
            text=(
                "Comparison: Interferometer 0.000000 mm | "
                "Stage 0.000000 mm | Difference 0.000 µm"
            ),
            font=("Arial", 18, "bold")
        )

        self.label_distance_comparison.pack(pady=5)

        self.live_size = (500, 380)

        self.image_label = ctk.CTkLabel(
            self.scroll,
            text="",
            width=self.live_size[0],
            height=self.live_size[1]
        )

        self.image_label.pack(pady=20)

        threading.Thread(
            target=self.camera_loop,
            daemon=True
        ).start()

        threading.Thread(
            target=self.stage_loop,
            daemon=True
        ).start()

    def start_motion_measurement(self):

        self.counter.reset()

        self.motion_start_position = (
            self.stage.get_position()
        )

        self.stage_moved_mm = 0.0

        if not MANUAL_THRESHOLDS:

            self.counter.start_calibration()

    def step_positive(self):

        self.update_step_size()

        self.start_motion_measurement()

        self.stage.step_positive()

    def step_negative(self):

        self.update_step_size()

        self.start_motion_measurement()

        self.stage.step_negative()

    def move_to_min(self):

        self.start_motion_measurement()

        self.stage.move_to_min()

    def move_to_max(self):

        self.start_motion_measurement()

        self.stage.move_to_max()

    def move_to_target(self):

        try:

            target = float(
                self.target_entry.get()
            )

        except:
            return

        self.start_motion_measurement()

        self.stage.move_absolute(target)

    def stop_stage(self):

        self.stage.stop()

    def update_step_size(self):

        try:

            step = float(
                self.step_entry.get()
            )

            self.stage.step_size = step

        except:
            pass

    def stage_loop(self):

        while True:

            pos = self.stage.get_position()

            self.stage_moved_mm = (
                pos - self.motion_start_position
            )

            self.after(
                0,
                lambda p=pos:
                self.label_current.configure(
                    text=f"Current Value: {p:.9f} mm"
                )
            )

            self.after(
                0,
                lambda:
                self.label_target.configure(
                    text=(
                        f"Target Value: "
                        f"{self.stage.target_position:.9f} mm"
                    )
                )
            )

            time.sleep(0.03)

    def camera_loop(self):

        frame_counter = 0

        while True:

            img = self.camera.get_frame()

            if img is None:
                continue

            frame_counter += 1

            intensity = (
                self.camera
                .get_fringe_intensity_from_frame(img)
            )

            if intensity is not None:

                if self.stage.is_moving:

                    if self.counter.calibrating:

                        finished = (
                            self.counter
                            .process_calibration(
                                intensity
                            )
                        )

                        elapsed = (
                            time.time()
                            - self.counter
                            .calibration_start_time
                        )

                        self.after(
                            0,
                            lambda e=elapsed:
                            self.label_thresholds.configure(
                                text=(
                                    f"Calibrating "
                                    f"{e:.1f}/10 s"
                                )
                            )
                        )

                        if finished:

                            self.after(
                                0,
                                lambda:
                                self.label_thresholds.configure(
                                    text=(
                                        f"Dark: "
                                        f"{self.counter.dark_threshold:.2f} | "
                                        f"Bright: "
                                        f"{self.counter.bright_threshold:.2f}"
                                    )
                                )
                            )

                    else:

                        self.counter.update(
                            intensity
                        )

                self.after(
                    0,
                    lambda i=intensity:
                    self.label_intensity.configure(
                        text=f"Intensity: {i:.2f}"
                    )
                )

            fringes = (
                self.counter.accumulated_fringes
            )

            dist_mm = (
                fringes
                * FRINGE_DISTANCE_MM
            )

            dist_um = dist_mm * 1000

            delay_ps = (
                2 * dist_mm
            ) / SPEED_OF_LIGHT_MM_PS

            self.after(
                0,
                lambda:
                self.update_labels(
                    fringes,
                    dist_mm,
                    dist_um,
                    delay_ps
                )
            )

            if frame_counter % 10 == 0:

                self.after(
                    0,
                    lambda f=img:
                    self.update_image(f)
                )

    def update_labels(
        self,
        fringes,
        mm,
        um,
        ps
    ):

        stage_distance_mm = abs(
            self.stage_moved_mm
        )

        difference_mm = (
            mm - stage_distance_mm
        )

        difference_um = (
            difference_mm * 1000
        )

        self.label_fringes.configure(
            text=f"Fringes: {fringes}"
        )

        self.label_mm.configure(
            text=f"Distance: {mm:.6f} mm"
        )

        self.label_um.configure(
            text=f"Distance: {um:.3f} µm"
        )

        self.label_ps.configure(
            text=f"Delay: {ps:.4f} ps"
        )

        self.label_distance_comparison.configure(
            text=(
                f"Comparison: Interferometer {mm:.6f} mm | "
                f"Stage {stage_distance_mm:.6f} mm | "
                f"Difference {difference_um:.3f} µm"
            )
        )

    def update_image(self, img):

        display = img.astype(np.float32)

        display -= np.min(display)

        if np.max(display) > 0:
            display /= np.max(display)

        display = (
            display * 255
        ).astype(np.uint8)

        pil = Image.fromarray(display).convert(
            "RGB"
        )

        original_w, original_h = pil.size

        scale_x = (
            self.live_size[0] / original_w
        )

        scale_y = (
            self.live_size[1] / original_h
        )

        pil = pil.resize(self.live_size)

        draw = ImageDraw.Draw(pil)

        x1 = int(
            self.camera.roi_x * scale_x
        )

        y1 = int(
            self.camera.roi_y * scale_y
        )

        x2 = int(
            (
                self.camera.roi_x
                + self.camera.roi_w
            ) * scale_x
        )

        y2 = int(
            (
                self.camera.roi_y
                + self.camera.roi_h
            ) * scale_y
        )

        draw.rectangle(
            [x1, y1, x2, y2],
            outline="yellow",
            width=3
        )

        ctk_img = ctk.CTkImage(
            light_image=pil,
            size=self.live_size
        )

        self.image_label.configure(
            image=ctk_img
        )

        self.image_label.image = ctk_img

    def on_close(self):

        try:
            self.camera.close()
        except:
            pass

        try:
            self.stage.close()
        except:
            pass

        self.destroy()


if __name__ == "__main__":

    app = App()

    app.protocol(
        "WM_DELETE_WINDOW",
        app.on_close
    )

    app.mainloop()
