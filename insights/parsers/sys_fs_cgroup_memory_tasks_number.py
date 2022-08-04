"""
SysFsCgroupMemoryTasksNumber - Datasource ``sys_fs_cgroup_memory_tasks_number``
===============================================================================

This parser parse the output of the datasource ``sys_fs_cgroup_memory_tasks_number``.
This datasource is used to count the number of lines from output of the command
``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'``

"""

from insights import Parser, parser
from insights.specs import Specs


@parser(Specs.sys_fs_cgroup_memory_tasks_number)
class SysFsCgroupMemoryTasksNumber(Parser):
    """
    Class ``SysFsCgroupMemoryTasksNumber`` parses the the output of the datasource``sys_fs_cgroup_memory_tasks_number``.
    This datasource is used to count the number of lines from output of the command ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'``

    The typical output of this command is::
       260

    Attributes:

        number (int):    The number of `tasks` files under /usr/bin/find /sys/fs/cgroup/memory.

    Examples:
        >>> type(sys_fs_cgroup_memory_tasks_number)
        <class 'insights.parsers.sys_fs_cgroup_memory_tasks_number.SysFsCgroupMemoryTasksNumber'>
        >>> sys_fs_cgroup_memory_tasks_number.number
        260
    """

    def parse_content(self, content):
        self.number = int(content[0].strip())
