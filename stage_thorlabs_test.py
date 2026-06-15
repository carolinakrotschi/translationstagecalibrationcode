"""
stage_thorlabs_test.py

Small runnable test to verify Thorlabs Kinesis access via
stage_controller_thorlabs.StageControllerThorlabs.

Usage:
  python stage_thorlabs_test.py

This script will:
- load the Thorlabs controller wrapper
- build the Kinesis device list
- create the first LTS / Integrated Stepper stage
- read its current position
"""

import sys
import traceback

from stage_controller_thorlabs import StageControllerThorlabs


def main():
    print("=" * 60)
    print("STAGE CONTROLLER THORLABS TEST")
    print("=" * 60)

    sc = StageControllerThorlabs()

    try:
        print("\nLoading Kinesis device list...")
        sc.connect()
        print("[OK] Kinesis device list loaded")
    except Exception as e:
        print("[FAIL] connect() failed:", e)
        traceback.print_exc()
        sys.exit(1)

    print(f"\nDevices found: {len(sc._device_list)}")
    for i, device in enumerate(sc._device_list):
        print(f"  [{i}] Serial={device}")

    try:
        print("\nOpening first LTS / Integrated Stepper device...")
        dev = sc.create_first_device()
        print(f"[OK] Device opened: {dev}")
    except Exception as e:
        print(f"[FAIL] create_first_device() failed: {e}")
        traceback.print_exc()
        sc.close()
        sys.exit(1)

    try:
        pos = sc.read_device_position()
        print(f"[OK] Current position: {pos} mm")
    except Exception as e:
        print(f"[WARN] Could not read position: {e}")

    print("\nCleaning up...")
    sc.close()
    print("[OK] Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
