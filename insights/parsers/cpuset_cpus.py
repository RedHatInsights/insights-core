#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
CpuSetCpus - File ``/sys/fs/cgroup/cpuset/cpuset.cpus``
=======================================================

This parser reads the content of ``/sys/fs/cgroup/cpuset/cpuset.cpus``.
This file shows the default cgroup cpuset.cpu of system. The format
of the content is string including comma.
"""

from .. import parser, CommandParser
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
        >>> cpusetinfo.cpuset
        ["0", "2", "3", "4", "7"]
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
