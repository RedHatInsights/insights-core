"""
cpuset_cpus - File ``/sys/fs/cgroup/cpuset/cpuset.cpus``
========================================================

This parser reads the content of ``/sys/fs/cgroup/cpuset/cpuset.cpus``.
This file shows the default cgroup cpuset.cpu of system. The format
of the content is string including comma.
"""

from insights.core import CommandParser, ContainerParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.cpuset_cpus)
class CpusetCpus(CommandParser):
    """
    Class ``CpusetCpus`` parses the content of the ``/sys/fs/cgroup/cpuset/cpuset.cpus``.

    Attributes:
        cpu_set (list): It is used to show the list of allowed cpu.

        cpu_number (int): It is used to display the number of allowed cpu.

    A small sample of the content of this file looks like::

        0,2-4,7

    Examples:
        >>> type(cpusetinfo)
        <class 'insights.parsers.cpuset_cpus.CpusetCpus'>
        >>> cpusetinfo.cpu_set
        ['0', '2', '3', '4', '7']
        >>> cpusetinfo.cpu_number
        5
    """

    def parse_content(self, content):
        self.cpu_set = []
        self.cpu_number = 0
        values = content[0].strip().split(",")
        for value in values:
            if "-" in value:
                # Parse the value like "2-4"
                start, end = value.split("-")
                self.cpu_set.extend([str(i) for i in range(int(start), int(end) + 1)])
            else:
                self.cpu_set.append(value)
        self.cpu_number = len(self.cpu_set)


@parser(Specs.container_cpuset_cpus)
class ContainerCpusetCpus(ContainerParser, CpusetCpus):
    """
    Class ``ContainerCpusetCpus`` parses the content of the ``/sys/fs/cgroup/cpuset/cpuset.cpus`` from containers.

    Attributes:
        cpu_set (list): It is used to show the list of allowed cpu.

        cpu_number (int): It is used to display the number of allowed cpu.

    A small sample of the content of this file looks like::

        0,2-4,7

    Examples:
        >>> type(container_cpusetinfo)
        <class 'insights.parsers.cpuset_cpus.ContainerCpusetCpus'>
        >>> container_cpusetinfo.container_id
        '2869b4e2541c'
        >>> container_cpusetinfo.image
        'registry.access.redhat.com/ubi8/nginx-120'
        >>> container_cpusetinfo.cpu_set
        ['0', '2', '3', '4', '7']
        >>> container_cpusetinfo.cpu_number
        5
    """
    pass
