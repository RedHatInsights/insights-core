"""
Custom datasource relevant mount command
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
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
