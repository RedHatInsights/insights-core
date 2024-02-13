"""
Custom datasources to get a list of filesystems whose mount type is in ['ext2', 'ext3', 'ext4']
"""
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.mount import ProcMounts


@datasource(ProcMounts)
def dumpdev_list(broker):
    mnt = broker[ProcMounts]
    mounted_dev = [m.mounted_device for m in mnt if m.mount_type in ('ext2', 'ext3', 'ext4')]
    if mounted_dev:
        return mounted_dev
    raise SkipComponent()
