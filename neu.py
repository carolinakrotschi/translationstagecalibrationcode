import clr
import time

clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.IntegratedStepperMotorsCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage

serial = "45517804"

DeviceManagerCLI.BuildDeviceList()

stage = LongTravelStage.CreateLongTravelStage(serial)

print("Connect...")
stage.Connect(serial)

# 🔥 wichtig: erst warten bis Device wirklich alive ist
time.sleep(1)

print("StartPolling...")
stage.StartPolling(250)

time.sleep(0.5)

print("EnableDevice...")
stage.EnableDevice()

time.sleep(0.5)

print("Wait settings...")
stage.WaitForSettingsInitialized(10000)

print("DONE")