"""
Custom datasource relevant mount command
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.fstab import FSTab
from insights.parsers.mount import ProcMounts


@datasource(ProcMounts, HostContext)
def xfs_mounts(broker):
    """
    Return the required mount points with 'xfs' type.

    Raises:
        SkipComponent: Raised if no 'xfs' mount points is available

    Returns:
        List[str]: Sorted list of 'xfs' mount points.
    """
    xfs_mnt = broker[ProcMounts].search(mount_type='xfs')
    if xfs_mnt:
        return sorted(m.mount_point for m in xfs_mnt)
    raise SkipComponent


@datasource(ProcMounts)
def dumpdev_list(broker):
    mnt = broker[ProcMounts]
    mounted_dev = [m.mounted_device for m in mnt if m.mount_type in ('ext2', 'ext3', 'ext4')]
    if mounted_dev:
        return sorted(mounted_dev)
    raise SkipComponent


@datasource(FSTab, HostContext)
def fstab_mounted(broker):
    """
    This datasource provides a list of the /etc/fstab mount points.

    Sample data returned::

        '/ /boot'

    Returns:
        list: List of the /etc/fstab mount points.

    Raises:
        SkipComponent: When there is not any mount point.
    """
    content = broker[FSTab].data
    if content:
        fs_mount_point = []
        for item in content:
            fs_mount_point.append(item['fs_file'])
        return ' '.join(fs_mount_point)

    raise SkipComponent
