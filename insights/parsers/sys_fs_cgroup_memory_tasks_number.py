"""
SysFsCgroupMemoryTasksNumber - Command ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks' | wc -l``
====================================================================================================

This parser reads the output of ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks' | wc -l``.

"""

from insights import Parser, parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.sys_fs_cgroup_memory_tasks_number)
class SysFsCgroupMemoryTasksNumber(Parser, list):
    """
    Class ``SysFsCgroupMemoryTasksNumber`` parses the content of the
    ``/usr/bin/find /sys/fs/cgroup/memory -name 'tasks' | wc -l`` file.

    This command is used to check the number of `tasks` files under /usr/bin/find /sys/fs/cgroup/memory::

        number (string):    The number of `tasks` under /usr/bin/find /sys/fs/cgroup/memory.

    Sample output::

        260


    Examples:
        >>> type(sys_fs_cgroup_memory_tasks_number)
        <class 'insights.parsers.sys_fs_cgroup_memory_tasks_number.SysFsCgroupMemoryTasksNumber'>
        >>> sys_fs_cgroup_memory_tasks_number.number
        260
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("No output")

        if not content[0].strip().isdigit():
            raise SkipException("Output is invalid")

        self.number = int(content[0].strip())
