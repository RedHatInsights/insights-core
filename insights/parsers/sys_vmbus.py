"""
``/sys/bus/vmbus/`` VMBus info
==============================

SysVmbusDeviceID - file ``/sys/bus/vmbus/devices/*/device_id``
--------------------------------------------------------------

SysVmbusClassID - file ``/sys/bus/vmbus/devices/*/class_id``
------------------------------------------------------------
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs

# Please refer to
# https://github.com/torvalds/linux/blob/master/tools/hv/lsvmbus#L23 for
# full list of Class ID mapping.
VMBUS_DEV_DICT = {
    '44c4f61d-4444-4400-9d52-802e27ede19f': 'PCI Express pass-through',
    'da0a7802-e377-4aac-8e77-0558eb1073f8': 'Synthetic framebuffer adapter'
}


@parser(Specs.sys_vmbus_device_id)
class SysVmbusDeviceID(Parser):
    """Parse the file ``/sys/bus/vmbus/devices/*/device_id``

    Sample content::

        {47505500-0001-0000-3130-444531444234}

    Raises:
        SkipComponent: When nothing need to parse.

    Attributes:
        id(str): Device ID

    Examples::

        >>> vmbus_device.id
        '47505500-0001-0000-3130-444531444234'
    """
    def parse_content(self, content):
        if not content or len(content) != 1:
            raise SkipComponent()
        self.id = content[0].strip('{}\n')


@parser(Specs.sys_vmbus_class_id)
class SysVmbusClassID(Parser):
    """Parse the file ``/sys/bus/vmbus/devices/*/class_id``

    Sample content::

        {44c4f61d-4444-4400-9d52-802e27ede19f}

    Raises:
        SkipComponent: When nothing need to parse.

    Attributes:
        id(str): Class ID
        desc(str): Description

    Examples::

        >>> vmbus_class.id
        '44c4f61d-4444-4400-9d52-802e27ede19f'
        >>> vmbus_class.desc
        'PCI Express pass-through'
    """
    def parse_content(self, content):
        if not content or len(content) != 1:
            raise SkipComponent()
        self.id = content[0].strip('{}\n')
        self.desc = VMBUS_DEV_DICT.get(self.id, 'Unknown')
