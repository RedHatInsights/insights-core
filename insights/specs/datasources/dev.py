"""
Custom datasources to get the device names.
"""

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.blkid import BlockIDInfo
from insights.combiners.virt_what import VirtWhat


@datasource(BlockIDInfo, VirtWhat, HostContext)
def physical_devices(broker):
    """
    This datasource get the name of the physical_devices.

    Returns:
        list: the names of the physical_devices

    Raises:
        SkipComponent: there is physical_device
    """
    blockdinfo = broker[BlockIDInfo]
    virtwhat = broker[VirtWhat]
    result = []
    if virtwhat.is_physical:
        for item in blockdinfo.data:
            device_name = item["NAME"]
            if device_name.startswith("/dev/sd") or device_name.startswith("/dev/hd"):
                main_dev_name = ''.join([i for i in device_name if not i.isdigit()])
                result.append(main_dev_name)
    if result:
        return sorted(list(set(result)))
    raise SkipComponent("No physical device")
