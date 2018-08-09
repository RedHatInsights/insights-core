"""
InitProcessCgroup - File ``/sys/fs/cgroup/cpuset/cpuset.cpus``
==============================================================

This parser reads the content of ``/sys/fs/cgroup/cpuset/cpuset.cpus``.
This file shows the default cgroup cpuset.cpu of system. The format
of the content is string including comma.
"""

from .. import parser, CommandParser, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.cpuset_cpus)
class CpusetCpus(CommandParser, LegacyItemAccess):
    """
    Class ``CpusetCpus`` parses the content of the ``/sys/fs/cgroup/cpuset/cpuset.cpus``.

    Attributes:

        cpu_number (int): It is used to display the number of allowed cpu.

    A small sample of the content of this file looks like::

        0,2-4,7

    Examples:
        >>> type(cpusetinfo)
        <class 'insights.parsers.cpuset_cpus.CpusetCpus'>
        >>> cpusetinfo.data
        ["0", "2", "3", "4", "7"]
        >>> cpusetinfo.cpu_number
        5
    """

    def parse_content(self, content):
        self.data = []
        self.cpu_number = 0
        values = content[0].strip().split(",")
        for value in values:
            if "-" in value:
                # Parser the case that the value is like "2-4"
                start, end = value.split("-")
                startint = int(start)
                endint = int(end)
                while startint <= endint:
                    self.data.append(str(startint))
                    startint = startint + 1
            else:
                self.data.append(value)
        self.cpu_number = len(self.data)
