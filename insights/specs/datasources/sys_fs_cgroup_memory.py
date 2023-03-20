"""
Custom datasources for the files under /sys/fs/cgroup/memory
"""
import os

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider


@datasource(HostContext)
def sys_fs_cgroup_uniq_memory_swappiness(broker):
    """
    This datasource reads all the memory.swappiness files under /sys/fs/cgroup/memory directory
    one by one and returns the uniq memory swappiness setting of the all control groups.

    The output of this datasource looks like:
        10   1
        60   66

    Returns:
        str: Returns a multiline string in the format as ``value   count``.

    Raises:
        SkipComponent: When any exception occurs.
    """
    file_name = "memory.swappiness"
    data = {}

    for root, _, files in os.walk("/sys/fs/cgroup/memory"):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'r') as setting:
                key = setting.read().strip()
                data[key] = data.get(key, 0) + 1

    if not data:
        raise SkipComponent()

    data_list = []
    for value, count in data.items():
        data_list.append("{0}   {1}".format(value, count))

    return DatasourceProvider(content="\n".join(data_list), relative_path='insights_commands/sys_fs_cgroup_uniq_memory_swappiness')
