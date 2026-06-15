"""
test_generic_motor.py

Use GenericMotorCLI to connect to the LTS300 device (serial 45517804).
"""

import sys
import os
import traceback

print("=" * 60)
print("GENERIC MOTOR CLI TEST")
print("=" * 60)

try:
    import clr
    from System.Reflection import Assembly
    
    kinesis_path = r"C:\Program Files\Thorlabs\Kinesis"
    
    # Load and init GenericMotorCLI
    print("\n[1] Loading GenericMotorCLI...")
    motor_dll = os.path.join(kinesis_path, "Thorlabs.MotionControl.GenericMotorCLI.dll")
    asm = Assembly.LoadFrom(motor_dll)
    print("✓ Assembly loaded")
    
    # Find concrete motor CLI classes
    print("\n  Searching for concrete motor classes...")
    motor_classes = {}
    for t in asm.GetTypes():
        name = t.Name
        if 'MotorCLI' in name and not name.startswith('I'):  # Skip interfaces
            try:
                # Check if it's instantiable (not abstract)
                if not t.IsAbstract:
                    motor_classes[name] = t
                    print(f"    Found: {name}")
            except:
                pass
    
    if not motor_classes:
        print("    No concrete motor classes found!")
        sys.exit(1)
    
    # Try to instantiate one
    motor = None
    for class_name, cls in motor_classes.items():
        try:
            print(f"  Trying {class_name}...")
            motor = cls(serial)
            print(f"✓ {class_name} instantiated")
            break
        except Exception as e:
            print(f"  - {class_name} failed: {e}")
    
    if motor is None:
        print("✗ Could not instantiate any motor class")
        sys.exit(1)
    
    # Load DeviceManagerCLI
    print("\n[2] Loading DeviceManagerCLI...")
    mgr_dll = os.path.join(kinesis_path, "Thorlabs.MotionControl.DeviceManagerCLI.dll")
    Assembly.LoadFrom(mgr_dll)
    from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
    print("✓ DeviceManagerCLI imported")
    
    # Find device
    print("\n[3] Finding device...")
    DeviceManagerCLI.BuildDeviceList()
    devs = DeviceManagerCLI.GetDeviceList()
    
    if not devs or len(devs) == 0:
        print("✗ No devices found!")
        sys.exit(1)
    
    serial = str(devs[0])
    print(f"✓ Found device: {serial}")
    
    # Try to create and connect
    print("\n[4] Creating motor instance...")
    if motor is None:
        print("✗ Could not create motor instance")
        sys.exit(1)
    else:
        print(f"✓ Motor instance ready: {type(motor).__name__}")
    
    # Try common motor methods
    print("\n[5] Testing device methods...")
    methods_to_try = ['Connect', 'Initialise', 'Home', 'GetPosition', 'MoveToPosition', 'MoveTo']
    
    for method_name in methods_to_try:
        if hasattr(motor, method_name):
            print(f"  ✓ Has method: {method_name}")
        else:
            print(f"  - No method: {method_name}")
    
    # Try to connect (might already be initialized from constructor)
    print("\n[6] Device connection status...")
    try:
        if hasattr(motor, 'IsConnected'):
            is_conn = motor.IsConnected
            print(f"  IsConnected: {is_conn}")
        
        # Try explicit connect if available
        if hasattr(motor, 'Connect'):
            motor.Connect(serial)
            print(f"✓ Called Connect()")
        elif hasattr(motor, 'Initialise'):
            motor.Initialise(serial)
            print(f"✓ Called Initialise()")
        else:
            print("  (No explicit Connect/Initialise needed)")
    except Exception as e:
        print(f"  Connection attempt: {e}")
    
    # Try to read position
    print("\n[7] Reading position...")
    try:
        if hasattr(motor, 'GetPosition'):
            pos = motor.GetPosition()
            print(f"✓ Position (mm): {pos}")
        else:
            print("  (No GetPosition method)")
    except Exception as e:
        print(f"  GetPosition error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ TEST COMPLETE")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ Error: {e}")
    traceback.print_exc()
    sys.exit(1)
