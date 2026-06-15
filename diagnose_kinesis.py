"""
diagnose_kinesis.py - FIXED for pythonnet 3.1.0

Quick diagnostic script to check Kinesis + pythonnet setup.
Run: python diagnose_kinesis.py
"""

import sys
import traceback
import os

print("=" * 60)
print("KINESIS DIAGNOSTIC CHECK")
print("=" * 60)

# Check Python version and bitness
print(f"\nPython executable: {sys.executable}")
print(f"Python bitness: {64 if sys.maxsize > 2**32 else 32}-bit")

# Check pythonnet
print("\n[1] Checking pythonnet...")
try:
    import clr
    print("✓ pythonnet OK")
except ImportError as e:
    print(f"✗ pythonnet missing: {e}")
    sys.exit(1)

# Check DeviceManagerCLI by loading DLL directly
print("\n[2] Checking Kinesis DeviceManagerCLI...")
try:
    # Use System.Reflection.Assembly.LoadFrom for direct DLL loading (works in pythonnet 3.1.0)
    from System.Reflection import Assembly
    
    kinesis_path = r"C:\Program Files\Thorlabs\Kinesis"
    dll_file = os.path.join(kinesis_path, "Thorlabs.MotionControl.DeviceManagerCLI.dll")
    
    if not os.path.exists(dll_file):
        raise RuntimeError(f"DLL not found: {dll_file}")
    
    print(f"  Loading DLL: {dll_file}")
    asm = Assembly.LoadFrom(dll_file)
    print(f"✓ Assembly loaded: {asm.GetName().Name}")
    
    # Now import DeviceManagerCLI
    from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
    print("✓ DeviceManagerCLI imported OK")
except Exception as e:
    print(f"✗ Failed to import DeviceManagerCLI:")
    traceback.print_exc()
    sys.exit(1)

# Check devices
print("\n[3] Checking for connected devices...")
try:
    DeviceManagerCLI.BuildDeviceList()
    devs = DeviceManagerCLI.GetDeviceList()
    dev_count = 0 if devs is None else len(devs)
    print(f"✓ Found {dev_count} device(s)")
    
    if devs and dev_count > 0:
        for i, d in enumerate(devs):
            sn = getattr(d, 'SerialNumber', None) or getattr(d, 'Serial', None) or str(d)
            name = getattr(d, 'DisplayName', None) or getattr(d, 'Name', None) or ''
            print(f"  [{i}] Serial={sn}, Name={name}")
    else:
        print("  (no devices connected or not yet initialized)")
except Exception as e:
    print(f"✗ Failed to list devices:")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL CHECKS PASSED")
print("=" * 60)
