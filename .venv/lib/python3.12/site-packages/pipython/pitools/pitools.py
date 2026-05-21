#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of helpers for using a PI device."""
import inspect

from ..pidevice.common.gcscommands_helpers import isdeviceavailable
from ..pidevice.gcs2.gcs2commands import GCS2Commands
from ..pidevice.gcs30.gcs30commands import GCS30Commands
from .gcs2.gcs2pitools import GCS2Tools, GCS2DeviceStartup
from .gcs30.gcs30pitools import GCS30Tools, GCS30DeviceStartup
from .common.gcsbasepitools import GCSBaseTools


__signature__ = 0xf4fb68c25d47a2dc30aab1da9247f3a5

class PIInvalidDevice(Exception):
    """
    Exception for an invalid PI device
    """

# Function name "DeviceStartup" doesn't conform to snake_case naming style pylint: disable=C0103
def DeviceStartup(pidevice, **kwargs):
    """
    Gets an instance to an DeviceStartup object dependen on
    the Type'pidevice' (GCS2Commands or GCS30Commands)
    :param pidevice: instance of a GCS2Commands or GCS30Commands object
    :type pidevice: GCS2Commands or GCS30Commands
    :param kwargs: Optional arguments with keywords that are passed to sub functions.
    :return: instance to a DeviceStartop object
    :rtype: GCS2DeviceStartup or GCS30DeviceStartup
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2DeviceStartup(GCS2Tools(pidevice), **kwargs)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30DeviceStartup(GCS30Tools(pidevice), **kwargs)

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def startup(pidevice, stages=None, refmodes=None, servostates=True, controlmodes=None, **kwargs):
    """Define 'stages', stop all, enable servo on all connected axes and reference the axes with 'refmodes'.
    Defining stages and homing them is done only if necessary.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param stages:  Name of stage(s) to initialize as string or list (not tuple!) or 'None' to skip.
    @param refmodes: Referencing command(s) as string (for all stages) or list (not tuple!) or 'None' to skip.
                     Please see the manual of the controller for the valid reference procedure.
                     'refmodes' can be:
                         'FRF': References the stage using the reference position.
                         'FNL': References the stage using the negative limit switch.
                         'FPL': References the stage using the positive limit switch.
                         'POS': Sets the current position of the stage to 0.0.
                         'ATZ': Runs an auto zero procedure.
    @param servostates: Desired servo state(s) as Boolean (for all stages) or dict {axis : state, } or 'None' to skip.
                        For controllers with GCS 3.0 syntax:
                            If True the axis is switched to control mode 0x2.
                            If False the axis is switched to control mode 0x1.
    @param controlmodes: Only valid for controllers with GCS 3.0 syntax!
                         Switch the axis to the given control mode:
                             int (for all axes) or dict {axis : controlmode, } or 'None' to skip.
                         To skip any control mode switch make sure the servostate is also 'None'!
                         If 'controlmode' is set (not 'None') the parameter 'servostate' is ignored.
    @param kwargs: Optional arguments with keywords that are passed to sub functions.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).startup(stages, refmodes, servostates, **kwargs)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).startup(stages, refmodes, servostates, controlmodes, **kwargs)

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def enableaxes(pidevice, axes, **kwargs):
    """Enable all 'axes'.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes to enable.
    @param kwargs: Optional arguments with keywords that are passed to sub-functions.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).enableaxes(axes, **kwargs)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).enableaxes(axes, **kwargs)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def setservo(pidevice, axes, states=None, toignore=None, **kwargs):
    """Set servo of 'axes' to 'states'. Calls preparatory functions if necessary
    e.g., for enabling disabled axes or for relaxing the piezo with open-loop Nexline axes.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes or dictionary {axis : value, }.
    @param states: Boolean or list of Booleans or 'None' if 'axes' is a dictionary.
                   For controllers with GCS 3.0 syntax:
                       If True the axis is switched to control mode 0x2.
                       If False the axis is switched to control mode 0x1.
    @param toignore: GCS error(s) to ignore as integer or list of integers.
    @param kwargs: Optional arguments with keywords that are passed to sub-functions.
    @return: False if setting the servo failed.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).setservo(axes, states, toignore, **kwargs)


    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).setservo(axes, states, toignore, **kwargs)


    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def getservo(pidevice, axes):
    """Return dictionary of servo states or "False" if the qSVO command is not supported.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes to get values for or 'None' for all axes.
    @return: Dictionary of servo states of 'axes' as Booleans.
             For controllers with GCS 3.0 syntax:
                 If True the axis is switched into control mode 0x2.
                 If False the axis is switched into control mode 0x1.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).getservo(axes)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).getservo(axes)

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def moveandwait(pidevice, axes, values=None, timeout=300):
    """Call MOV with 'axes' and 'values' and wait for motion to finish.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes or dictionary of {axis : target, }.
    @param values: Optional list of values or value or None if axis is a dictionary.
    @param timeout: Seconds as float until SystemError is raised.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).moveandwait(axes, values, timeout)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).moveandwait(axes, values, timeout)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def movetomiddle(pidevice, axes=None):
    """Move 'axes' to their middle positions but do not wait until they are "on target".
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes to get values for or 'None' for all axes.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).movetomiddle(axes)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).movetomiddle(axes)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def ontarget(pidevice, axes):
    """Return dictionary of on-target states for open- or closed-loop 'axes'.
    If qOSN is not supported, open-loop axes will return True.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes to get values for or 'None' for all axes.
    @return: Dictionary of on-target states of 'axes' as Booleans {axis : on-target-state, }.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).ontarget(axes)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).ontarget(axes)

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def stopall(pidevice, **kwargs):
    """
    For GCS 2.0 controllers: Stop motion of all axes and give the "error 10" warning.
    For GCS 3.0 controllers: Stop all axes and wait until the affected axes have finished their stop procedures.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param kwargs: Optional arguments with keywords that are passed to sub functions.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).stopall(**kwargs)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).stopall(**kwargs)
        return


    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def getaxeslist(pidevice, axes):
    """Return list of 'axes'.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes or 'None' for all axes.
    @return: List of axes from 'axes' or all axes or empty list.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).getaxeslist(axes)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).getaxeslist(axes)

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def waitonready(pidevice, timeout=300, predelay=0, polldelay=0.1):
    """Wait until controller is in "ready" state, then query and raise controller error.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param timeout: Timeout in seconds, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonready(timeout, predelay, polldelay)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).waitonready(timeout, predelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


# Too many arguments pylint: disable=R0913
def waitontarget(pidevice, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all closed-loop 'axes' are on target.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes to wait for or 'None' for all axes.
    @param timeout: Timeout in seconds, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param postdelay: Additional delay time in seconds as float after reaching the desired state, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitontarget(axes, timeout, predelay, postdelay, polldelay)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).waitontarget(axes, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


# Too many arguments pylint: disable=R0913
def waitonreferencing(pidevice, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until referencing of 'axes' has finished or timeout is reached.
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes to wait for or 'None' for all axes.
    @param timeout: Timeout in seconds, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param postdelay: Additional delay time in seconds as float after reaching the desired state, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonreferencing(axes, timeout, predelay, postdelay, polldelay)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).waitonreferencing(axes, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")



def getmaxtravelrange(pidevice, axes):
    """
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes or 'None' for all axes.
    @return: Dictionary of {axis : maximum _travelrange, }.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).getmaxtravelrange(axes)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).getmaxtravelrange(axes)

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def getmintravelrange(pidevice, axes):
    """
    @param pidevice: instance of a GCS2Commands or GCS30Commands object
    @param axes: Axis as string or list/tuple of axes or 'None' for all axes.
    @return: Dictionary of {axis : minimum _travelrange, }.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).getmintravelrange(axes)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).getmintravelrange(axes)

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def writewavepoints(pidevice, wavetable, wavepoints, bunchsize=None):
    """Write 'wavepoints' for 'wavetable' in bunches of 'bunchsize'.
    The 'bunchsize' is device specific. Please refer to the controller manual.
    @param pidevice: instance of a GCS2Commands object
    @param wavetable: Wave table ID as integer.
    @param wavepoints: Single wavepoint as float convertible or list/tuple of them.
    @param bunchsize: Number of wavepoints per bunch or 'None' to send all 'wavepoints' in a single bunch.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).writewavepoints(wavetable, wavepoints, bunchsize)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def waitonfastalign(pidevice, name=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until the fast alignment process has finished.
    @param pidevice: instance of a GCS2Commands bject
    @param name: Name of the process as string or list/tuple of processes.
    @param timeout: Timeout in seconds as float.
    @param predelay: Time in seconds, as float until querying any state from controller, as float.
    @param postdelay: Additional delay time in seconds as float after reaching the desired state, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonfastalign(name, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def waitonwavegen(pidevice, wavegens=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """	Wait until all 'wavegens' have stopped running.
    @param pidevice: instance of a GCS2Commands object
    @param wavegens: Integer convertible or list/tuple of them or 'None' for all wave generators.
    @param timeout: Timeout in seconds, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param postdelay: Additional delay time in seconds as float after reaching the desired state, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonwavegen(wavegens, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def waitonautozero(pidevice, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' have finished their auto zero procedure.
    @param pidevice: instance of a GCS2Commands object
    @param axes: Axis as string or list/tuple of axes to wait for or 'None' for all axes.
    @param timeout: Timeout in seconds, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param postdelay: Additional delay time in seconds as float after reaching the desired state, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonautozero(axes, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


# Too many arguments pylint: disable=R0913
def waitonphase(pidevice, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on phase.
    @param pidevice: instance of a GCS2Commands object
    @param axes: Axis as string or list/tuple of axes to wait for or 'None' for all axes.
    @param timeout: Timeout in seconds, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param postdelay: Additional delay time in seconds as float after reaching the desired state, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonphase(axes, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


# Too many arguments pylint: disable=R0913
def waitonwalk(pidevice, channels, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until qOSN for channels is zero.
    @param pidevice: instance of a GCS2Commands object
    @param channels: Channel or list/tuple of channels to wait for motion to finish.
    @param timeout: Timeout in seconds, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param postdelay: Additional delay time in seconds as float after reaching the desired state, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonwalk(channels, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


# Too many arguments pylint: disable=R0913
def waitonoma(pidevice, axes=None, timeout=300, predelay=0, polldelay=0.1):
    """Waituntil open-loop of 'axes' has finished.
    @param pidevice: instance of a GCS2Commands object
    @param axes: Axis as string or list/tuple of axes to wait for or 'None' for all axes.
    @param timeout: Timeout in seconds, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonoma(axes, timeout, predelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


# Too many arguments pylint: disable=R0913
def waitontrajectory(pidevice, trajectories=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'trajectories' are done and all axes are on target.
    @param pidevice: instance of a GCS2Commands object
    @param trajectories: Integer convertible or list/tuple of them or 'None' for all trajectories.
    @param timeout: Timeout in seconds for trajectory and motion, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param postdelay: Additional delay time in seconds as float after reaching the desired state, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitontrajectory(trajectories, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def waitonmacro(pidevice, timeout=300, predelay=0, polldelay=0.1):
    """Wait until all macros are finished, then query and raise macro error.
    @param pidevice: instance of a GCS2Commands object
    @param timeout: Timeout in seconds, as float.
    @param predelay: Time in seconds as float until querying any state from controller, as float.
    @param polldelay: Delay time between polls in seconds, as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonmacro(timeout, predelay, polldelay)
        return

    raise PIInvalidDevice(
        f"Type {type(pidevice).__name__} of pidevice is not supported for '{inspect.stack()[0].function}'!")


def savegcsarray(filepath, header, data):
    """Save data recorder output to a GCS Array file.
    @param filepath: Full path to target file as string.
    @param header: Header information from qDRR() as dictionary or 'None'.
    @param data: Dataset as one or two-dimensional list of floats or NumPy array.
    """
    GCSBaseTools.savegcsarray(filepath, header, data)


def readgcsarray(filepath):
    """Read a GCS Array file and return header and data.
    Scan the file until the start of the data is found to accoun
    for account additional information at the start of the file.
    @param filepath: Full path to file as string.
    @return header: Header information from qDRR() as dictionary.
    @return data: Dataset as two column list of floats.
    """
    return GCSBaseTools.readgcsarray(filepath)


def itemstostr(data):
    """Convert 'data' into a string message.
    @param data: Dictionary or list or tuple or single item to convert.
    """
    return GCSBaseTools.itemstostr(data)


def piwrite(filepath, text):
    """Write 'text' to 'filepath' with preset encoding.
    @param filepath: Full path to file to write as string, existing file will be replaced.
    @param text: Text to write as string or list of strings (with trailing line feeds).
    """
    GCSBaseTools.piwrite(filepath, text)


def enum(*args, **kwargs):
    """Return an Enum object of 'args' (enumerated) and 'kwargs' that can convert the values back to its names."""
    return GCSBaseTools.enum(*args, **kwargs)
