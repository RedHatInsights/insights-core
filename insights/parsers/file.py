"""
Determine file type commands
============================

Parser included in this module is:
BootLoaderOnDisk - Spec ``boot_loader_on_disk``
-----------------------------------------------
"""
from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.core.exceptions import SkipComponent


@parser(Specs.boot_loader_on_disk)
class BootLoaderOnDisk(CommandParser):
    """
    Class to parse the output of ``file -s <boot_device>`` command.

    Sample output of ``file -s <boot_device>`` command looks like::
        /dev/vda: x86 boot sector; partition 1: ID=0x83, active, starthead 0, startsector 2048, 167770079 sectors, code offset 0x63

    Examples:
        >>> type(boot_loader_on_disk)
        <class 'insights.parsers.file.BootLoaderOnDisk'>
        >>> "GRand Unified Bootloader" in boot_loader_on_disk.boot_loader
        False
        >>> "x86 boot sector" in boot_loader_on_disk.boot_loader
        True
        >>> boot_loader_on_disk.boot_device
        '/dev/vda'

    Attributes:
        boot_device (str): the boot device of the current RHEL system.
        boot_loader (str): the boot loader information on the boot device.
    """
    def parse_content(self, content):
        if len(content) != 1:
            raise SkipComponent("Command output should only contain one line.")

        data = content[0]

        if not data.startswith("/dev/"):
            raise SkipComponent("Content doesn't contain a valid device.")

        if len(data.split(": ", 1)) != 2:
            raise SkipComponent("Content format is invalid.")

        items = data.split(": ", 1)
        self.boot_device = items[0]
        self.boot_loader = items[1]
