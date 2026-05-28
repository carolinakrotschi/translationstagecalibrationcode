import os  # Operating system path utilities
import sys  # System functions
current_directory = os.path.dirname(os.path.abspath(__file__))  # Get script directory
dll_path = os.path.join(current_directory, 'Camera')  # Set path to Camera drivers folder
if os.path.exists(dll_path):  # Check if Camera folder exists
    os.add_dll_directory(dll_path)  # Add drivers to system path
    print(f"Successfully loaded drivers from: {dll_path}")  # Confirm driver loading
else:  # If folder not found
    print(f"ERROR: Hardware driver folder not found at {dll_path}")  # Error message
try:  # Try to import camera SDK
    from thorlabs_tsi_sdk.tl_camera import TLCameraSDK  # Import Thorlabs camera SDK
    print("Thorlabs SDK successfully imported.")  # Success message
except Exception as e:  # If import fails
    print(f"SDK Import/Init Warning: {e}")  # Print error details
    print("CameraHandler will switch to simulation mode if needed.")  # Fallback message

import pandas as pd  # Data analysis and CSV export
import matplotlib.pyplot as plt  # Plot graphs and images
import numpy as np  # Numerical computing
import customtkinter as ctk  # Modern GUI framework
import serial  # Serial communication with translation stages
import threading  # Run hardware tasks without freezing UI
import time  # Time delays and wait loops
import csv  # Handle CSV data logging
import os  # File and folder path management
from datetime import datetime  # Timestamp measurements
from PIL import Image  # Image handling
from pipython import GCSDevice, pitools  # PI stage controller libraries
from camera_handler import CameraHandler  # Custom camera management class
from scipy.signal import find_peaks  # Peak detection in signal processing

# CONFIGURATION
LASER_WAVELENGTH_NM = 632.8  # HeNe laser wavelength (nanometers)
# Movement of half a wavelength produces one full fringe shift
FRINGE_DISTANCE_MM = (LASER_WAVELENGTH_NM / 2) / 1_000_000  # Convert nm to mm
TRAVELLING_RANGE = 50.0  # Maximum stage travel distance (mm)
SPEED_OF_LIGHT_MM_PS = 0.299792458  # Speed of light (mm per picosecond)

# Files
DATA_FOLDER = "data"  # Data storage folder
LOG_FILE = os.path.join(DATA_FOLDER, "measurement_log.csv")  # CSV log file path

class InterferometerApp(ctk.CTk):  # Main application class
    def __init__(self):  # Constructor method
        super().__init__()  # Initialize parent GUI class

        # PI STAGE
        self.pidevice = GCSDevice('C-663')  # Create PI controller object
        self.stage_connected = False  # Hardware connection flag
        self.axis = None  # Motor axis identifier
        self.connect_hardware()  # Attempt hardware connection

        # CAMERA
        self.camera_handler = CameraHandler()  # Camera management instance
        self.camera_connected = self.camera_handler.connect()  # Connect to camera

        # STATE CONTROL
        self.is_monitoring = False  # Monitoring thread control flag

        # UI SETUP
        self.title("Precision Interferometer Monitor")  # Window title
        self.geometry("500x600")  # Window size
        ctk.set_appearance_mode("light")  # Light theme
        self.configure(fg_color="#FFFFFF")  # White background

        # Header Label
        self.label_title = ctk.CTkLabel(self, text="Interferometer Monitor", font=("Arial", 22, "bold"), text_color="#0A4A51")  # Title label
        self.label_title.pack(pady=20)  # Place with spacing

        # Action Button (Toggle Button)
        self.btn_start = ctk.CTkButton(self, text="START MONITORING", command=self.toggle_monitoring, 
                                       font=("Arial", 14, "bold"), height=40, fg_color="#0A4A51")  # Start/stop button
        self.btn_start.pack(pady=20)  # Place with spacing

        # Status Display
        self.status_label = ctk.CTkLabel(self, text="Status: Hardware check...", text_color="#0A4A51")  # Status indicator
        self.status_label.pack(pady=5)  # Place with spacing

        # Result Display Area
        self.result_frame = ctk.CTkFrame(self, fg_color="#F0F0F0")  # Container for results
        self.result_frame.pack(pady=20, padx=20, fill="x")  # Place and fill

        self.label_dist_mm = ctk.CTkLabel(self.result_frame, text="Distance: 0.000000 mm", font=("Arial", 16))  # Distance in mm
        self.label_dist_mm.pack(pady=5)

        self.label_dist_um = ctk.CTkLabel(self.result_frame, text="Distance: 0.000 µm", font=("Arial", 16, "bold"), text_color="#0A4A51")  # Distance in micrometers
        self.label_dist_um.pack(pady=5)

        self.label_time_ps = ctk.CTkLabel(self.result_frame, text="Time Delay: 0.000 ps", font=("Arial", 16), text_color="#D35400")  # Time delay in picoseconds
        self.label_time_ps.pack(pady=5)

        # LOGO
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
        logo_path = os.path.join(script_dir, "assets", "logo.png")  # Logo file path
        if os.path.exists(logo_path):  # Check if logo exists
            self.logo_image = ctk.CTkImage(light_image=Image.open(logo_path), size=(300, 81))  # Load logo image
            ctk.CTkLabel(self, image=self.logo_image, text="").pack(pady=20)  # Display logo

    def connect_hardware(self):  # Connect to PI controller
        """connect to the PI Controller via USB."""
        try:  # Try connection
            self.pidevice.ConnectUSB(serialnum='0')  # Connect to first USB device
            pitools.startup(self.pidevice)  # Initialize stage (servo on, etc.)
            self.axis = self.pidevice.axes[0]  # Get first motor axis
            self.stage_connected = True  # Mark as connected
        except Exception as e:  # Connection failed
            self.stage_connected = False  # Mark as disconnected

    def toggle_monitoring(self):  # Start or stop monitoring
        """Starts or stops the live monitoring thread."""
        if not self.is_monitoring:  # If monitoring is off
            if not self.camera_connected:  # Camera not available
                self.status_label.configure(text="Error: Camera not connected", text_color="red")  # Show error
                return  # Exit function
            
            self.is_monitoring = True  # Enable monitoring
            self.btn_start.configure(text="STOP MONITORING", fg_color="#C0392B")  # Change button text/color
            self.status_label.configure(text="Status: Live Monitoring...", text_color="green")  # Show status
            threading.Thread(target=self.run_live_monitor, daemon=True).start()  # Start background thread
        else:  # If monitoring is on
            self.is_monitoring = False  # Disable monitoring
            self.btn_start.configure(text="START MONITORING", fg_color="#0A4A51")  # Reset button
            self.status_label.configure(text="Status: Stopped", text_color="#0A4A51")  # Show status

    def run_live_monitor(self):  # Monitor camera in background
        """Reads the camera in a loop and updates the UI in real-time."""
        try:  # Monitor loop
            fringe_count = 0  # Counter for fringe transitions
            intensity_history = []  # Store recent intensity values for smoothing
            history_size = 100  # Smoothing window size
            last_counted_peak_index = -1  # Store last counted peak index

            while self.is_monitoring:
                intensity = self.camera_handler.get_fringe_intensity()
                print(f"Current intensity: {intensity}")  # Debug: print current intensitz
            
                if intensity is not None:
                    intensity_history.append(intensity)
            
                    if len(intensity_history) > history_size:
                        intensity_history.pop(0)
            
                    if len(intensity_history) >= history_size:
                        signal = np.array(intensity_history)
            
                        # Moving average smoothing
                        window = 5
                        smoothed = np.convolve(signal, np.ones(window) / window, mode="valid")
            
                        mean_intensity = np.mean(smoothed)
                        std_intensity = np.std(smoothed)
            
                        threshold = mean_intensity + 0.5 * std_intensity
            
                        peaks, properties = find_peaks(
                            smoothed,
                            height=threshold,
                            distance=8,
                            prominence=0.3 * std_intensity
                        )
            
                        if len(peaks) > 0:
                            newest_peak = peaks[-1]
            
                            if newest_peak > last_counted_peak_index:
                                fringe_count += 1
                                last_counted_peak_index = newest_peak
            
                                dist_mm = fringe_count * FRINGE_DISTANCE_MM
                                dist_um = dist_mm * 1000
                                time_ps = (2 * dist_mm) / SPEED_OF_LIGHT_MM_PS
            
                                self.after(
                                    0,
                                    lambda d=dist_mm, u=dist_um, t=time_ps:
                                    self.update_display(d, u, t)
                                )
                time.sleep(0.05) # Polling interval (reduce frequency to match camera rate)
                
        except Exception as e:  # Error handling
            self.after(0, lambda err=e: self.status_label.configure(text=f"Error: {err}", text_color="red"))  # Show error

    def update_display(self, mm, um, ps):  # Update result labels
        """Updates the labels with the new calculated values."""
        self.label_dist_mm.configure(text=f"Distance: {mm:.6f} mm")  # Update mm display
        self.label_dist_um.configure(text=f"Distance: {um:.3f} µm")  # Update µm display
        self.label_time_ps.configure(text=f"Time Delay: {ps:.4f} ps")  # Update ps display

    def on_closing(self):  # Cleanup on exit
        """Ensures the hardware connection is closed when the window is shut."""
        self.is_monitoring = False  # Stop monitoring
        if self.stage_connected:  # If stage connected
            self.pidevice.CloseConnection()  # Release USB connection
        self.destroy()  # Close window

if __name__ == "__main__":  # Main entry point
    app = InterferometerApp()  # Create application
    app.protocol("WM_DELETE_WINDOW", app.on_closing)  # Set close handler
    app.mainloop()  # Start GUI event loop
