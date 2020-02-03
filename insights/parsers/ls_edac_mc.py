"""
LsEdacMC - command ``ls -lan /sys/devices/system/edac/mc``
==========================================================

The ``ls -lan /sys/devices/system/edac/mc`` command provides information for the listing of the
``/sys/devices/system/edac/mc`` directory. See the ``FileListing`` class for a more complete description of the
available features of the class.

Sample ``ls -lan /sys/devices/system/edac/mc`` output::

    /sys/devices/system/edac/mc:
    total 90
    drwxr-xr-x. 3 0 0 0 Jan 10 10:33 .
    drwxr-xr-x. 3 0 0 0 Jan 10 10:33 ..
    drwxr-xr-x. 2 0 0 0 Jan 10 10:33 power
    drwxr-xr-x. 2 0 0 0 Jan 10 10:33 mc0
    drwxr-xr-x. 2 0 0 0 Jan 10 10:33 mc1
    drwxr-xr-x. 2 0 0 0 Jan 10 10:33 mc2

Examples:
    >>> '/sys/devices/system/edac/mc' in ls_edac_mc
    True
    >>> ls_edac_mc.dirs_of('/sys/devices/system/edac/mc') == ['.', '..', 'power', 'mc0', 'mc1', 'mc2']
    True
"""

from insights.specs import Specs
from .. import parser, CommandParser, FileListing


@parser(Specs.ls_edac_mc)
class LsEdacMC(CommandParser, FileListing):
    """
    Parse the /sys/devices/system/edac/mc directory listing using a standard FileListing parser.
    """
    pass
