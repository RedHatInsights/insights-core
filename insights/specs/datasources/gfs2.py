"""
Custom datasources for gfs2 information
"""
from insights.components.rhel_version import IsRhel8, IsRhel7, IsRhel6
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.mount import Mount


@datasource(Mount, [IsRhel6, IsRhel7, IsRhel8], HostContext)
def mount_points(broker):
    """
    Function to search the output of ``mount`` to find all the gfs2 file
    systems.
    And only run the ``stat`` command on RHEL version that's less than
    8.3. With 8.3 and later, the command ``blkid`` will also output the
    block size info.

    Returns:
        list: a list of mount points of which the file system type is gfs2
    """
    gfs2_mount_points = []
    if (broker.get(IsRhel6) or broker.get(IsRhel7) or
            (broker.get(IsRhel8) and broker[IsRhel8].minor < 3)):
        mounts = broker.get(Mount, [])
        for mnt in mounts:
            if mnt.mount_type == "gfs2":
                gfs2_mount_points.append(mnt.mount_point)
    if gfs2_mount_points:
        return gfs2_mount_points

    raise SkipComponent
