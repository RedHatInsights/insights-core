"""
LsvmBus - Command ``lsvmbus -vv``
=================================

This module parses the output of the command ``lsvmbus -vv``.
"""
import re

from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.lsvmbus)
class LsvmBus(CommandParser):
    """Parse the output of ``lsvmbus -vv`` as list.

    Typical output::

        VMBUS ID 18: Class_ID = {44c4f61d-4444-4400-9d52-802e27ede19f} - PCI Express pass-through
                Device_ID = {47505500-0001-0000-3130-444531303244}
                Sysfs path: /sys/bus/vmbus/devices/47505500-0001-0000-3130-444531303244
                Rel_ID=18, target_cpu=0
        VMBUS ID 26: Class_ID = {44c4f61d-4444-4400-9d52-802e27ede19f} - PCI Express pass-through
                Device_ID = {47505500-0002-0000-3130-444531303244}
                Sysfs path: /sys/bus/vmbus/devices/47505500-0002-0000-3130-444531303244
                Rel_ID=26, target_cpu=0
        VMBUS ID 73: Class_ID = {44c4f61d-4444-4400-9d52-802e27ede19f} - PCI Express pass-through
                Device_ID = {47505500-0003-0001-3130-444531303244}
                Sysfs path: /sys/bus/vmbus/devices/47505500-0003-0001-3130-444531303244
                Rel_ID=73, target_cpu=0
        VMBUS ID 74: Class_ID = {44c4f61d-4444-4400-9d52-802e27ede19f} - PCI Express pass-through
                Device_ID = {47505500-0004-0001-3130-444531303244}
                Sysfs path: /sys/bus/vmbus/devices/47505500-0004-0001-3130-444531303244
                Rel_ID=74, target_cpu=0

    Examples:

        >>> assert len(lsvmbus.devices) == 4
        >>> assert lsvmbus.devices[0].get('vmbus_id', None) == '18'
        >>> assert lsvmbus.devices[0].get('device_id', None) == '47505500-0001-0000-3130-444531303244'
        >>> assert lsvmbus.devices[0].get('rel_id', None) == '18'
        >>> assert lsvmbus.devices[0].get('sysfs_path', None) == '/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531303244'
        >>> assert lsvmbus.devices[0].get('target_cpu', None) == '0'

    Attributes:
        devices (list): List of ``dict`` for each device. For example::

                        [
                         {
                          'vmbus_id': '18',
                          'class_id': '44c4f61d-4444-4400-9d52-802e27ede19f',
                          'type': 'PCI Express pass-through',
                          'device_id': '47505500-0001-0000-3130-444531303244',
                          'sysfs_path': '/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531303244',
                          'rel_id': '18',
                          'target_cpu': '0'
                         },
                         {...}
                        ]

    """
    def parse_content(self, content):
        if not content:
            raise SkipException('No content.')
        self.devices = []
        parts = zip(*(iter(content),) * 4)
        patrn_vmbusid = re.compile(r"VMBUS ID (\d+)")
        patrn_type = re.compile("- (.*)")
        patrn_classid = re.compile("Class_ID = {(.*)}")
        patrn_deviceid = re.compile("Device_ID = {(.*)}")
        patrn_sysfspath = re.compile("Sysfs path: (.*)")
        patrn_relid = re.compile(r"Rel_ID=(\d+)")
        patrn_targetcpu = re.compile(r"target_cpu=(\d+)")
        for part in parts:
            self.devices.append(
                {
                    'vmbus_id': patrn_vmbusid.search(part[0]).groups()[0],
                    'class_id': patrn_classid.search(part[0]).groups()[0],
                    'type': patrn_type.search(part[0]).groups()[0],
                    'device_id': patrn_deviceid.search(part[1]).groups()[0],
                    'sysfs_path': patrn_sysfspath.search(part[2]).groups()[0],
                    'rel_id': patrn_relid.search(part[3]).groups()[0],
                    'target_cpu': patrn_targetcpu.search(part[3]).groups()[0],
                }
            )
