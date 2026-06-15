"""
debug_device_type.py

Inspect the device to find its exact type and available methods.
"""

import sys
import traceback
import os

print("=" * 60)
print("DEVICE TYPE DETECTION")
print("=" * 60)

try:
    import clr
    from System.Reflection import Assembly
    
    kinesis_path = r"C:\Program Files\Thorlabs\Kinesis"
    dll_file = os.path.join(kinesis_path, "Thorlabs.MotionControl.DeviceManagerCLI.dll")
    
    asm = Assembly.LoadFrom(dll_file)
    from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
    
    DeviceManagerCLI.BuildDeviceList()
    devs = DeviceManagerCLI.GetDeviceList()
    
    if not devs or len(devs) == 0:
        print("No devices found!")
        sys.exit(1)
    
    dev_info = devs[0]
    print(f"\nDevice 0 info object type: {type(dev_info)}")
    print(f"Device 0 info object: {dev_info}")
    
    print("\n--- Device Properties ---")
    for attr in dir(dev_info):
        if not attr.startswith('_'):
            try:
                val = getattr(dev_info, attr)
                if not callable(val):
                    print(f"  {attr}: {val}")
            except:
                pass
    
    # Try to get DeviceID which often contains device type info
    try:
        dev_id = dev_info.DeviceID
        print(f"\n✓ DeviceID: {dev_id}")
    except:
        pass
    
    # Try to load via generic Motor CLI
    print("\n--- Trying Generic MotorCLI ---")
    try:
        motor_dll = os.path.join(kinesis_path, "Thorlabs.MotionControl.GenericMotorCLI.dll")
        if os.path.exists(motor_dll):
            print(f"Found: {motor_dll}")
            Assembly.LoadFrom(motor_dll)
            from Thorlabs.MotionControl.GenericMotorCLI import MotorController
            print("✓ Imported MotorController")
            
            serial = str(dev_info.SerialNumber or dev_info.Serial or dev_info)
            motor = MotorController.CreateDevice(serial)
            print(f"✓ Created device: {motor}")
        else:
            print(f"Not found: {motor_dll}")
    except Exception as e:
        print(f"GenericMotorCLI failed: {e}")
        traceback.print_exc()
    
    # Try to find and list all Thorlabs.MotionControl.* DLLs
    print("\n--- Available Motor DLLs ---")
    for f in os.listdir(kinesis_path):
        if 'MotionControl' in f and f.endswith('.dll') and ('Motor' in f or 'LTS' in f or 'Piezo' in f):
            print(f"  {f}")

except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)
