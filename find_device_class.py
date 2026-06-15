"""
find_device_class.py

Find the correct device class for serial 45517804.
LTS300 typically uses IntegratedStepperMotors family.
"""

import sys
import os
import traceback

print("=" * 60)
print("FINDING CORRECT DEVICE CLASS")
print("=" * 60)

try:
    import clr
    from System.Reflection import Assembly
    
    kinesis_path = r"C:\Program Files\Thorlabs\Kinesis"
    
    # Load DeviceManagerCLI
    dll_file = os.path.join(kinesis_path, "Thorlabs.MotionControl.DeviceManagerCLI.dll")
    Assembly.LoadFrom(dll_file)
    from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
    
    DeviceManagerCLI.BuildDeviceList()
    devs = DeviceManagerCLI.GetDeviceList()
    
    if not devs or len(devs) == 0:
        print("No devices found!")
        sys.exit(1)
    
    serial = str(devs[0])
    print(f"\n✓ Found device: {serial}")
    print(f"  Serial starts with: {serial[:2]}")
    
    # Try IntegratedStepperMotors (LTS300 family)
    print("\n--- Trying IntegratedStepperMotors ---")
    try:
        motor_dll = os.path.join(kinesis_path, "Thorlabs.MotionControl.IntegratedStepperMotors.dll")
        if os.path.exists(motor_dll):
            Assembly.LoadFrom(motor_dll)
            
            # Try different class names
            for class_name in ['IntegratedStepperMotor', 'IntegratedMotor', 'StepperMotor']:
                try:
                    cls = getattr(__import__('Thorlabs.MotionControl.IntegratedStepperMotors', fromlist=[class_name]), class_name, None)
                    if cls:
                        print(f"  Found class: {class_name}")
                        # Try to create device
                        try:
                            if hasattr(cls, 'CreateDevice'):
                                dev = cls.CreateDevice(serial)
                                print(f"  ✓ Created via CreateDevice: {dev}")
                            elif hasattr(cls, 'ConnectDevice'):
                                dev = cls()
                                dev.Connect(serial)
                                print(f"  ✓ Created via Connect: {dev}")
                        except Exception as e:
                            print(f"  - Couldn't instantiate: {e}")
                except:
                    pass
    except Exception as e:
        print(f"IntegratedStepperMotors load failed: {e}")
    
    # Try GenericMotorCLI - list all exported types
    print("\n--- GenericMotorCLI exported types ---")
    try:
        motor_dll = os.path.join(kinesis_path, "Thorlabs.MotionControl.GenericMotorCLI.dll")
        asm = Assembly.LoadFrom(motor_dll)
        
        types = asm.GetTypes()
        print(f"  Total types: {len(types)}")
        
        for t in types:
            if 'Motor' in t.Name or 'Device' in t.Name:
                print(f"    {t.Name}")
                # Try to use it
                try:
                    if hasattr(t, 'CreateDevice'):
                        dev = t.CreateDevice(serial)
                        print(f"      ✓ CreateDevice worked!")
                    elif hasattr(t, 'ConnectDevice'):
                        print(f"      - Has ConnectDevice method")
                except:
                    pass
    except Exception as e:
        print(f"GenericMotorCLI failed: {e}")
    
    # Try Benchtop StepperMotor
    print("\n--- Trying Benchtop.StepperMotor ---")
    try:
        motor_dll = os.path.join(kinesis_path, "Thorlabs.MotionControl.Benchtop.StepperMotor.dll")
        asm = Assembly.LoadFrom(motor_dll)
        types = asm.GetTypes()
        for t in types:
            if 'Motor' in t.Name or 'Device' in t.Name or 'Stepper' in t.Name:
                print(f"  Found: {t.Name}")
    except Exception as e:
        print(f"Benchtop.StepperMotor load failed: {e}")
    
    # Direct approach: try generic connect
    print("\n--- Direct DeviceManagerCLI methods ---")
    methods = [m for m in dir(DeviceManagerCLI) if 'Device' in m or 'Connect' in m or 'Get' in m]
    for m in methods[:20]:
        print(f"  {m}")

except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
