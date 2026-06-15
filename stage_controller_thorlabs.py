"""
stage_controller_thorlabs.py

Kinesis-only stage controller for Thorlabs LTS / Integrated Stepper stages.

Requirements:
- Thorlabs Kinesis 64-bit installed
- pythonnet installed in the Python environment
"""

from __future__ import annotations

import os
import sys
import time
from typing import List, Optional


class StageControllerThorlabs:
    """Small Thorlabs Kinesis wrapper for an LTS-style integrated stepper."""

    SETTINGS_TIMEOUT_MS = 10_000
    MOVE_TIMEOUT_MS = 60_000
    POLLING_INTERVAL_MS = 250

    def __init__(self, serial: Optional[str] = None, kinesis_path: Optional[str] = None):
        self.serial = serial
        self.kinesis_path = kinesis_path

        self._device_list: List[str] = []
        self.device_info = None
        self.device = None
        self.connected = False
        self.DeviceManagerCLI = None

        self.current_position = 0.0
        self.min_position = -15.0
        self.max_position = 15.0
        self.step_size = 0.0001
        self.velocity = 0.001
        self.is_moving = False

        self._polling_started = False
        self._dll_directory_handle = None
        self._assemblies_loaded = False

    @staticmethod
    def _standard_kinesis_paths() -> List[str]:
        return [
            r"C:\Program Files\Thorlabs\Kinesis",
            r"C:\Program Files (x86)\Thorlabs\Kinesis",
            os.path.join(os.getcwd(), "thorlabsstage", "dlls"),
        ]

    def _find_kinesis_path(self) -> str:
        if self.kinesis_path and os.path.isdir(self.kinesis_path):
            return self.kinesis_path

        for path in self._standard_kinesis_paths():
            if os.path.isdir(path):
                self.kinesis_path = path
                return path

        raise RuntimeError("Thorlabs Kinesis path not found.")

    def _load_assemblies(self) -> None:
        if self._assemblies_loaded:
            return

        try:
            import clr
        except ImportError as exc:
            raise RuntimeError("pythonnet is not installed. Install it with: pip install pythonnet") from exc

        kinesis_path = self._find_kinesis_path()

        if hasattr(os, "add_dll_directory"):
            self._dll_directory_handle = os.add_dll_directory(kinesis_path)

        if kinesis_path not in sys.path:
            sys.path.append(kinesis_path)
        os.environ["PATH"] = kinesis_path + os.pathsep + os.environ.get("PATH", "")

        references = [
            "Thorlabs.MotionControl.DeviceManagerCLI",
            "Thorlabs.MotionControl.GenericMotorCLI",
            "Thorlabs.MotionControl.IntegratedStepperMotorsCLI",
        ]

        for reference in references:
            dll_path = os.path.join(kinesis_path, reference + ".dll")
            if not os.path.exists(dll_path):
                raise RuntimeError(f"Required Kinesis DLL not found: {dll_path}")
            clr.AddReference(reference)

        self._assemblies_loaded = True

    @staticmethod
    def _net_decimal(value: float):
        from System import Decimal as NetDecimal
        from System.Globalization import CultureInfo

        return NetDecimal.Parse(str(float(value)), CultureInfo.InvariantCulture)

    def connect(self) -> bool:
        """Load Kinesis and build the device list."""
        self._load_assemblies()

        from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
        from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage

        DeviceManagerCLI.BuildDeviceList()

        all_devices = [str(device) for device in DeviceManagerCLI.GetDeviceList()]
        try:
            lts_devices = [str(device) for device in DeviceManagerCLI.GetDeviceList(LongTravelStage.DevicePrefix)]
        except Exception:
            lts_devices = [device for device in all_devices if device.startswith(str(LongTravelStage.DevicePrefix))]

        if not all_devices:
            raise RuntimeError("No Thorlabs Kinesis devices found.")

        if self.serial:
            if self.serial not in all_devices:
                raise RuntimeError(f"Requested serial {self.serial} was not found. Found: {all_devices}")
            selected_serial = self.serial
        elif lts_devices:
            selected_serial = lts_devices[0]
        else:
            raise RuntimeError(
                "No LTS / Integrated Stepper stage found. "
                f"Kinesis devices found: {all_devices}"
            )

        if not selected_serial.startswith(str(LongTravelStage.DevicePrefix)):
            raise RuntimeError(
                f"Serial {selected_serial} is not an LTS / Integrated Stepper device "
                f"(expected prefix {LongTravelStage.DevicePrefix})."
            )

        self._device_list = all_devices
        self.device_info = selected_serial
        self.serial = selected_serial
        self.DeviceManagerCLI = DeviceManagerCLI
        self.connected = True
        return True

    def create_first_device(self):
        """Create and open the selected LongTravelStage device."""
        if not self.connected:
            self.connect()

        if self.device is not None:
            return self.device

        from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage

        serial = str(self.serial or self.device_info)
        device = LongTravelStage.CreateLongTravelStage(serial)

        try:
            device.Connect(serial)
        except Exception as exc:
            raise RuntimeError(
                f"Kinesis found serial {serial} as an LTS / Integrated Stepper device, "
                "but could not open it. Close Kinesis/TestClient if it is running, "
                "check USB/power/driver state, then reconnect the stage. "
                f"Original error: {exc}"
            ) from exc

        try:
            device.WaitForSettingsInitialized(self.SETTINGS_TIMEOUT_MS)
        except Exception as exc:
            device.Disconnect(True)
            raise RuntimeError(f"Device {serial} did not initialize settings in time: {exc}") from exc

        try:
            device.LoadMotorConfiguration(serial)
        except Exception:
            # Some Kinesis installs already have usable settings after initialization.
            pass

        device.StartPolling(self.POLLING_INTERVAL_MS)
        self._polling_started = True
        time.sleep(0.5)

        device.EnableDevice()
        time.sleep(0.5)

        self.device = device
        self.current_position = self.read_device_position()
        return device

    def _require_device(self):
        if self.device is None:
            return self.create_first_device()
        return self.device

    def read_device_position(self) -> float:
        """Read the current stage position in mm."""
        device = self._require_device()

        try:
            device.RequestPosition()
            time.sleep(0.1)
        except Exception:
            pass

        self.current_position = float(device.Position)
        return self.current_position

    def move_absolute(self, position_mm: float) -> bool:
        """Move to an absolute position in mm."""
        if position_mm < self.min_position or position_mm > self.max_position:
            raise ValueError(
                f"Target {position_mm} mm outside allowed range "
                f"[{self.min_position}, {self.max_position}] mm."
            )

        device = self._require_device()
        self.is_moving = True
        try:
            device.MoveTo(self._net_decimal(position_mm), self.MOVE_TIMEOUT_MS)
            self.current_position = self.read_device_position()
            return True
        finally:
            self.is_moving = False

    def move_relative(self, distance_mm: float) -> bool:
        """Move by a relative distance in mm."""
        return self.move_absolute(self.read_device_position() + distance_mm)

    def stop(self):
        """Stop stage motion immediately."""
        if self.device is not None:
            try:
                self.device.StopImmediate()
            except Exception:
                self.device.Stop(self.MOVE_TIMEOUT_MS)
        self.is_moving = False

    def close(self):
        """Stop polling and disconnect the Kinesis device."""
        if self.device is not None:
            if self._polling_started:
                try:
                    self.device.StopPolling()
                except Exception:
                    pass
            try:
                self.device.Disconnect(True)
            except Exception:
                try:
                    self.device.Disconnect()
                except Exception:
                    pass

        self.device = None
        self._polling_started = False
        self.connected = False


if __name__ == "__main__":
    controller = StageControllerThorlabs()
    print("Connecting to Kinesis...")
    controller.connect()
    print(f"[OK] Found devices: {controller._device_list}")
    print("Opening first LTS stage...")
    controller.create_first_device()
    print(f"[OK] Position: {controller.read_device_position()} mm")
    controller.close()
