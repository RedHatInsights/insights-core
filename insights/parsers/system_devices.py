"""
SystemDevices - file ``/etc/lvm/devices/system.devices``
========================================================
"""

from insights import Parser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.parsers import optlist_to_dict, SkipException


@parser(Specs.system_devices)
class SystemDevices(Parser, dict):
    """
    Parse the content of the ``/etc/lvm/devices/system.devices`` file.
    It returns a dict. The key is the device id, the value is a dict of
    other info.

    Sample input::

        VERSION=1.1.2
        IDTYPE=devname IDNAME=/dev/vda2 DEVNAME=/dev/vda2 PVID=phl0clFbAokp9UXqbIgI5YYQxuTIJVkD PART=2

    Sample output::

        {
            '/dev/vda2': {
                'IDTYPE': 'devname',
                'DEVNAME': '/dev/vda2',
                'PVID': 'phl0clFbAokp9UXqbIgI5YYQxuTIJVkD',
                'PART': '2'
            }
        }

    Example:
        >>> type(devices)
        <class 'insights.parsers.system_devices.SystemDevices'>
        >>> devices['/dev/vda2']['IDTYPE']
        'devname'
        >>> devices['/dev/vda2']['PVID']
        'phl0clFbAokp9UXqbIgI5YYQxuTIJVkD'

    Raises:
        SkipException: when there is no device info.
    """

    def parse_content(self, content):
        for line in content:
            if 'IDNAME' in line:
                dict_info = optlist_to_dict(line, opt_sep=None)
                self[dict_info.pop('IDNAME')] = dict_info
        if not self:
            raise SkipException("No valid content.")
