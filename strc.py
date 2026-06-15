import clr

clr.AddReference(
    r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI.dll"
)

print("DLL loaded")

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI

print("Import OK")
import sys
print(sys.version)
import struct
print(struct.calcsize("P") * 8)
import clr
import sys

print(sys.executable)
print(sys.version)
import clr

clr.AddReference(
    r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI.dll"
)

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI

DeviceManagerCLI.BuildDeviceList()

devices = DeviceManagerCLI.GetDeviceList()

print("Found devices:")
import os

for f in os.listdir(r"C:\Program Files\Thorlabs\Kinesis"):
    if "Stepper" in f:
        print(f)

for d in devices:
    print(d)

from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage

serial = "45517804"

stage = LongTravelStage.CreateLongTravelStage(serial)

print(stage)