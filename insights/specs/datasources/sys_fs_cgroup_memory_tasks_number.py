"""
Custom datasources for the number of "tasks" files under /sys/fs/cgroup/memory
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by sys_fs_cgroup_memory_tasks_number datasources """

    sys_fs_cgroup_memory_tasks_raw = simple_command("/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'")
    """ Returns the output of command ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'`` """


@datasource(LocalSpecs.sys_fs_cgroup_memory_tasks_raw, HostContext)
def sys_fs_cgroup_memory_tasks_number_data_datasource(broker):
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
    exceptions = ['no such file or directory', ]
    content = broker[LocalSpecs.sys_fs_cgroup_memory_tasks_raw].content
    if len(content) == 0 or not any(ex in content[0].lower() for ex in exceptions):
        return DatasourceProvider(content=str(len(content)), relative_path='insights_commands/sys_fs_cgroup_memory_tasks_number')
    raise SkipComponent
