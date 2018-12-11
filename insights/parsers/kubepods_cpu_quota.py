"""
KubepodsCpuQuota - file ``/sys/fs/cgroup/cpu/kubepods.slice/kubepods-burstable.slice/*.slice/cpu.cfs_quota_us``
===============================================================================================================

This parser reads the content of ``/sys/fs/cgroup/cpu/kubepods.slice/kubepods-burstable.slice/*.slice/cpu.cfs_quota_us``.
"""

from insights import Parser, parser, LegacyItemAccess
from insights.specs import Specs
from ..parsers import ParseException


@parser(Specs.kubepods_cpu_quota)
class KubepodsCpuQuota(LegacyItemAccess, Parser):
    """
    Class ``KubepodsCpuQuota`` parses the content of the ``/sys/fs/cgroup/cpu/kubepods.slice/kubepods-burstable.slice/*.slice/cpu.cfs_quota_us``.

    Attributes:
        cpu_quota (int): It is used to show the value of cpu_quota for a perticular .

    A typical sample of the content of this file looks like::

        -1

    Examples:
        >>> type(kubepods_cpu_quota)
        <class 'insights.parsers.kubepods_cpu_quota.KubepodsCpuQuota'>
        >>> kubepods_cpu_quota.cpu_quota
        -1
    """

    def parse_content(self, content):
        if len(content) != 1:
            raise ParseException("Error: ", content[0] if content else 'empty file')
        self.cpu_quota = int(content[0].strip())
