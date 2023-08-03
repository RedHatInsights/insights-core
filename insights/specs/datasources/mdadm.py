"""
Custom datasource relevant mdadm command
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.mdstat import Mdstat


@datasource(Mdstat, HostContext)
def md_raid_arrays(broker):
    """
    Return the md RAID Array device names.

    Sample data returned::

        ["md1", "md2", "md3"]

    Returns:
        List[str]: Sorted list of md RAID Array device names.

    Raises:
        SkipComponent: Raised if no RAID Array name is available
    """
    md_raid_arrays = broker[Mdstat].mds.keys()
    if md_raid_arrays:
        return sorted(md_raid_arrays)
    raise SkipComponent
