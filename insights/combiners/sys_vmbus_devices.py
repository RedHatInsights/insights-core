"""
VMBus device info
=================
"""
from insights.core.plugins import combiner
from insights.parsers.sys_vmbus import SysVmbusDeviceID, SysVmbusClassID


@combiner(SysVmbusDeviceID, SysVmbusClassID)
class SysVmBusDeviceInfo(object):
    '''
    Combiner to access all the VMBus devices.

    Attributes:
        devices (list): The list is dict.

    Sample output::

        [
         {
          'device_id': '47505500-0001-0000-3130-444531444234',
          'class_id': '44c4f61d-4444-4400-9d52-802e27ede19f',
          'description': 'PCI Express pass-through'
         }
        ]

    Examples:
        >>> len(output.devices)
        2
        >>> output.devices[0].get('device_id', '')
        '47505500-0001-0000-3130-444531444234'
        >>> output.devices[0].get('class_id', '')
        '44c4f61d-4444-4400-9d52-802e27ede19f'
        >>> output.devices[0].get('description', '')
        'PCI Express pass-through'
    '''
    def __init__(self, device_id, class_id):
        self.devices = []
        for d in device_id:
            for c in class_id:
                if d.id in c.file_path:
                    self.devices.append(
                        {
                            'device_id': d.id,
                            'class_id': c.id,
                            'description': c.desc
                        }
                    )
