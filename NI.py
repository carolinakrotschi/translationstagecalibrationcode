import nidaqmx
import nidaqmx.system

system = nidaqmx.system.System.local()

print("Geräte:")
for dev in system.devices:
    print(dev)





with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")

    while True:
        value = task.read()
        print(value)