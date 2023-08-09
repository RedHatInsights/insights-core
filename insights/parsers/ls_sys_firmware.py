"""
LsSysFirmware - command ``ls /sys/firmware``
============================================

The ``ls -lanR /sys/firmware`` command provides information for the listing of
the ``/sys/firmware`` directory.

See :class:`insights.parsers.ls.FileListing` for more information.

"""

from insights import CommandParser, FileListing, parser
from insights.specs import Specs


@parser(Specs.ls_sys_firmware)
class LsSysFirmware(CommandParser, FileListing):
    """
    Parses output of ``ls -lanR /sys/firmware`` command.

    .. warning::

        For Insights Advisor Rules, it's recommended to use the
        :class:`insights.parsers.ls.LSlanR` and add the ``"/sys/firmware"`` to
        the filter list of `Specs.ls_lanR_dirs` instead.

    Sample directory listing::

        /sys/firmware:
        total 0
        drwxr-xr-x.  5 0 0 0 Dec 22 17:56 .
        dr-xr-xr-x. 13 0 0 0 Dec 22 17:56 ..
        drwxr-xr-x.  5 0 0 0 Dec 22 17:56 acpi
        drwxr-xr-x.  3 0 0 0 Dec 22 17:57 dmi
        drwxr-xr-x. 10 0 0 0 Dec 22 17:57 memmap

        /sys/firmware/acpi:
        total 0
        drwxr-xr-x. 5 0 0    0 Dec 22 17:56 .
        drwxr-xr-x. 5 0 0    0 Dec 22 17:56 ..
        drwxr-xr-x. 6 0 0    0 Feb 10 15:54 hotplug
        drwxr-xr-x. 2 0 0    0 Feb 10 15:54 interrupts
        -r--r--r--. 1 0 0 4096 Feb 10 15:54 pm_profile
        drwxr-xr-x. 3 0 0    0 Dec 22 17:56 tables

    Examples:
        >>> type(ls_sys_firmware)
        <class 'insights.parsers.ls_sys_firmware.LsSysFirmware'>
        >>> "acpi" in ls_sys_firmware
        False
        >>> "/sys/firmware/acpi" in ls_sys_firmware
        True
        >>> ls_sys_firmware.dirs_of("/sys/firmware")
        ['.', '..', 'acpi', 'dmi', 'memmap']
        >>> ls_sys_firmware.files_of("/sys/firmware/acpi")
        ['pm_profile']
    """
    __root_path = '/sys/firmware'
