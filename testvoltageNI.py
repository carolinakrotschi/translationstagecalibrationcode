#ausführen python testvoltageNI.py
#py -3 -m venv .venv
#.\.venv\Scripts\Activate.ps1
#python -m pip install --upgrade pip
#python -m pip install nidaqmx

#oder
#python -m pip install nidaqmx
#python testvoltageNI.py --list
#python testvoltageNI.py --channel Dev1/ai0
#https://www.ni.com/de/support/downloads/drivers/download.ni-daq-mx.html#590033




import argparse
import platform
import sys
import time

try:
    import nidaqmx
    from nidaqmx.errors import DaqError, DaqNotSupportedError
    from nidaqmx.system import System
except ModuleNotFoundError:
    print("nidaqmx is not installed for this Python.")
    print("Install it in the terminal, not inside this file:")
    print(f"{sys.executable} -m pip install nidaqmx")
    sys.exit(1)


DEFAULT_CHANNEL = "Dev1/ai0"


def list_devices():
    try:
        devices = list(System.local().devices)
    except DaqNotSupportedError as error:
        print_unsupported_platform_error(error)
        return
    except DaqError as error:
        print("Could not read NI devices.")
        print(error)
        return

    if not devices:
        print("No NI devices found.")
        print("Check NI MAX / NI Hardware Configuration Utility for the device name.")
        return

    print("NI devices:")
    for device in devices:
        print(f"- {device.name}")
        try:
            channels = [channel.name for channel in device.ai_physical_chans]
        except DaqError:
            channels = []

        if channels:
            print(f"  AI channels: {', '.join(channels)}")


def read_voltage(channel_name, delay_s, sample_count):
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(
            channel_name,
            min_val=-10.0,
            max_val=10.0
        )

        print(f"Reading voltage from {channel_name}. Press Ctrl+C to stop.")

        samples_read = 0
        while sample_count is None or samples_read < sample_count:
            value = task.read()
            print(f"Spannung: {value:.6f} V")
            samples_read += 1
            time.sleep(delay_s)


def print_unsupported_platform_error(error):
    print("NI-DAQmx is not available on this operating system.")
    print(f"Current system: {platform.system()} ({sys.platform})")
    print(error)
    print("\nRun this script on a Windows or supported Linux computer with NI-DAQmx installed.")


def main():
    parser = argparse.ArgumentParser(
        description="Read analog voltage from an NI-DAQmx input channel."
    )
    parser.add_argument(
        "--channel",
        default=DEFAULT_CHANNEL,
        help=f"NI analog input channel, for example {DEFAULT_CHANNEL}"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between software-timed reads in seconds."
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=None,
        help="Number of samples to read. Default: read until Ctrl+C."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List detected NI devices and analog input channels."
    )
    args = parser.parse_args()

    if args.list:
        list_devices()
        return

    try:
        read_voltage(args.channel, args.delay, args.samples)
    except KeyboardInterrupt:
        print("\nStopped.")
    except DaqNotSupportedError as error:
        print_unsupported_platform_error(error)
    except DaqError as error:
        print("NI-DAQmx error:")
        print(error)
        print("\nCheck that NI-DAQmx driver is installed and the channel name is correct.")
        print("You can list detected devices with:")
        print(f"{sys.executable} testvoltageNI.py --list")


if __name__ == "__main__":
    main()
