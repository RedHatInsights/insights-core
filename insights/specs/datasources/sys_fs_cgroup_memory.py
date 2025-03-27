"""
Custom datasources relate to `/sys/fs/cgroup/memory`
"""

import os

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """Local specs used only by sys_fs_cgroup_memory_tasks_number datasources"""

    sys_fs_cgroup_memory_tasks_raw = simple_command(
        "/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'"
    )
    """ Returns the output of command ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'`` """


@datasource(LocalSpecs.sys_fs_cgroup_memory_tasks_raw, HostContext)
def tasks_number(broker):
    """
    This datasource provides the numeber of "tasks" file collected
    from ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'``.

    Typical content of ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'`` command is::

        /sys/fs/cgroup/memory/user.slice/tasks
        /sys/fs/cgroup/memory/system.slice/rh-nginx120-nginx.service/tasks
        /sys/fs/cgroup/memory/system.slice/named.service/tasks
        /sys/fs/cgroup/memory/system.slice/rhel-push-plugin.service/tasks

    Returns:
        string: the number of "tasks" file under /sys/fs/cgroup/memory

    Raises:
        SkipComponent: When any exception occurs.
    """
    exceptions = [
        'no such file or directory',
    ]
    content = broker[LocalSpecs.sys_fs_cgroup_memory_tasks_raw].content
    if len(content) == 0 or not any(ex in content[0].lower() for ex in exceptions):
        return DatasourceProvider(
            content=str(len(content)),
            relative_path='insights_datasources/sys_fs_cgroup_memory_tasks_number',
        )
    raise SkipComponent


@datasource(HostContext)
def uniq_memory_swappiness(broker):
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

    return DatasourceProvider(
        content="\n".join(data_list),
        relative_path='insights_datasources/sys_fs_cgroup_uniq_memory_swappiness',
    )
