"""
Custom datasources related to block devices.
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.lsblk import LSBlock


@datasource(LSBlock, HostContext)
def boot_device(broker):
    """
    This datasource parsers the output of ``lsblk`` to get the boot device.

    Returns:
        str: Returns a string like ``/dev/sda``.
    """
    block_devices = broker[LSBlock]
    boot_devices = block_devices.search(MOUNTPOINT="/boot")
    if not boot_devices:
        boot_devices = block_devices.search(MOUNTPOINT="/")

    if not boot_devices or len(boot_devices) > 1:
        raise SkipComponent

    boot_device_name = boot_devices[0].parent_names[0]
    content = "/dev/{0}".format(boot_device_name)
    return content
