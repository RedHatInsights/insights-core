"""
InitProcessCgroup - Command ``/usr/bin/cat /proc/1/cgroup``
================================================================

This parser reads the output of ``/usr/bin/cat /proc/1/cgroup``.
This command shows the cgroup detail of init process. The format
of the content is like key-value. We can also use this info to
check if the archive is from container or host.
"""

from .. import parser, CommandParser, get_active_lines
from insights.specs import Specs


@parser(Specs.init_process_cgroup)
class InitProcessCgroup(CommandParser):
    """
    Class ``InitProcessCgroup`` parses the content of the ``/usr/bin/cat /proc/1/cgroup`` command output.
    A small sample of the content of this file looks like::

        11:hugetlb:/
        10:memory:/
        9:devices:/
        8:pids:/
        7:perf_event:/
        6:net_prio,net_cls:/
        5:blkio:/
        4:freezer:/
        3:cpuacct,cpu:/
        2:cpuset:/
        1:name=systemd:/

    Examples:
        >>> type(cgroupinfo)
        <class 'insights.parsers.is_container.InitProcessCgroup'>
        >>> cgroupinfo["memory"]
        ["10", "/"]
        >>> cgroupinfo.is_container
        False

    """

    def parse_content(self, content):
        self.data = {}
        self.is_container = False
        for line in get_active_lines(content):
            values = line.split(":")
            self.data[values[1]] = [values[0], values[2]]
            if "system.slice/docker-" in values[2]:
                self.is_container = True
