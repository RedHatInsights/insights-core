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
KubepodsCpuQuota - CPU quota for each Kubernetes pod
====================================================

This parser reads the content of ``/sys/fs/cgroup/cpu/kubepods.slice/kubepods-burstable.slice/*.slice/cpu.cfs_quota_us``.
"""

from insights import Parser, parser
from insights.specs import Specs
from ..parsers import ParseException


@parser(Specs.kubepods_cpu_quota)
class KubepodsCpuQuota(Parser):
    """
    Class ``KubepodsCpuQuota`` parses the content of the ``/sys/fs/cgroup/cpu/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod*.slice/cpu.cfs_quota_us``.

    Attributes:
        cpu_quota (int): It is used to show the value of cpu quota for a particular pod in a Kubernetes cluster or an OpenShift cluster.

    A typical sample of the content of this file looks like::

        -1

    Examples:
        >>> type(kubepods_cpu_quota)
        <class 'insights.parsers.kubepods_cpu_quota.KubepodsCpuQuota'>
        >>> kubepods_cpu_quota.cpu_quota
        -1
    """

    def parse_content(self, content):
        if len(content) != 1 or not content[0].strip('-').isdigit():
            raise ParseException("Error: ", content if content else 'empty file')
        self.cpu_quota = int(content[0].strip())
