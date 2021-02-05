"""
LsvmBus - Command ``lsvmbus -vv``
=================================

This module parses the output of the command ``lsvmbus -vv``.

LsVMBus - datasource ``lsvmbus``
================================
"""
import re
from ast import literal_eval

from insights.util import deprecated
from insights import parser, Parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.lsvmbus)
class LsvmBus(CommandParser):
    """Parse the output of ``lsvmbus -vv`` as list.

    .. warning::
        This parser class is deprecated, please use
        :py:class:`insights.parser.lsvmbus.LsVMBus` instead.

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
    def __init__(self, *args, **kwargs):
        deprecated(LsvmBus, "Use the LsVMBus parser instead")
        super(LsvmBus, self).__init__(*args, **kwargs)

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


@parser(Specs.lsvmbus)
class LsVMBus(Parser, list):
    """This parser parses the output of ``lsvmbus`` datasource.

    Typical output from the datasource is::

        [
         {'device_id': '5620e0c7-8062-4dce-aeb7-520c7ef76171', 'class_id': 'da0a7802-e377-4aac-8e77-0558eb1073f8', 'description': 'Synthetic framebuffer adapter'},
         {'device_id': '47505500-0001-0000-3130-444531444234', 'class_id': '44c4f61d-4444-4400-9d52-802e27ede19f', 'description': 'PCI Express pass-through'},
         {'device_id': '4487b255-b88c-403f-bb51-d1f69cf17f87', 'class_id': '3375baf4-9e15-4b30-b765-67acb10d607b', 'description': 'Unknown'}
        ]


    Attributes:

        devices(list): List of ``dict``.

    Examples:
        >>> assert len(lsvmbus.devices) == 3
        >>> assert lsvmbus.devices[1].get('device_id', None) == '47505500-0001-0000-3130-444531444234'
        >>> assert lsvmbus.devices[1].get('description', None) == 'PCI Express pass-through'
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('No content.')

        self.devices = literal_eval(content[0])
