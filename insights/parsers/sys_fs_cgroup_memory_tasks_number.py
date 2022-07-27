"""
SysFsCgroupMemoryTasksNumber - Command ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'``
============================================================================================

This parser reads the file number from the output of ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'``.

"""

from insights import Parser, parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.sys_fs_cgroup_memory_tasks_number)
class SysFsCgroupMemoryTasksNumber(Parser, list):
    """
    Class ``SysFsCgroupMemoryTasksNumber`` parses the file number from the output of the
    ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks'`` command.

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
        if not content:
            raise SkipException("No output")

        self.number = int(content[0].strip())
