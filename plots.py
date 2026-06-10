import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import nidaqmx


channels = [
    ("S1", "Dev1/ai0"),
    ("S2", "Dev1/ai1"),
    ("Reference", "Dev1/ai2"),
]

max_points = 500
values_s1 = []
values_s2 = []
values_ref = []
all_values = [values_s1, values_s2, values_ref]


fig, axes = plt.subplots(3, 1, sharex=True, figsize=(9, 7))
lines = []

for axis, (name, channel) in zip(axes, channels):
    line = axis.plot([])[0]
    lines.append(line)

    axis.set_title(name + " (" + channel + ")")
    axis.set_ylabel("V")
    axis.grid(True)

axes[-1].set_xlabel("Messpunkte")
fig.tight_layout()


with nidaqmx.Task() as task:
    for name, channel in channels:
        task.ai_channels.add_ai_voltage_chan(channel)

    def update_plot(frame):
        new_values = task.read()

        for values, new_value in zip(all_values, new_values):
            values.append(new_value)

            if len(values) > max_points:
                values.pop(0)

        for axis, line, values in zip(axes, lines, all_values):
            x_values = range(len(values))
            line.set_data(x_values, values)
            axis.relim()
            axis.autoscale_view()

        return lines

    animation = FuncAnimation(fig, update_plot, interval=50)
    plt.show()
