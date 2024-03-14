"""
cpu_online - File ``/sys/devices/system/cpu/online``
====================================================

This parser reads the content of ``/sys/devices/system/cpu/online``.
This file shows the number of online cpu. The format of the content
is string including comma.
"""

from insights.core import ContainerParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.container_cpu_online)
class ContainerCpuOnline(ContainerParser):
    """
    Class ``ContainerCpuOnline`` parses the content of the ``/sys/devices/system/cpu/online`` from containers.

    Attributes:
        cpu_online_set (list): It is used to show the list of online cpu.

        cpu_online_number (int): It is used to display the number of online cpu.

    A small sample of the content of this file looks like::

        0,2-4,7

    Examples:
        >>> type(container_cpu_online_info)
        <class 'insights.parsers.cpu_online.ContainerCpuOnline'>
        >>> container_cpu_online_info.container_id
        '2869b4e2541c'
        >>> container_cpu_online_info.image
        'registry.access.redhat.com/ubi8/nginx-120'
        >>> container_cpu_online_info.cpu_online_set
        ['0', '2', '3', '4', '7']
        >>> container_cpu_online_info.cpu_online_number
        5
    """
    def parse_content(self, content):
        self.cpu_online_set = []
        self.cpu_online_number = 0
        values = content[0].strip().split(",")
        for value in values:
            if "-" in value:
                # Parse the value like "2-4"
                start, end = value.split("-")
                self.cpu_online_set.extend([str(i) for i in range(int(start), int(end) + 1)])
            else:
                self.cpu_online_set.append(value)
        self.cpu_online_number = len(self.cpu_online_set)
