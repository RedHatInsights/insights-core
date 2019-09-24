"""
CpuVulnsBranch - combiner for cpu vulnerabilities:
==================================================

cpu vulnerabilities includes:
    * CpuVulnsBranch - file /sys/devices/system/cpu/vulnerabilities/*

Examples:
    >>> type(cvb)
    <class 'insights.combiners.cpu_vulns_branch.CpuVulnsBranch'>
    >>> list(cvb.keys())
    ['meltdown', 'spectre_v1']

"""

from insights.core.plugins import combiner
from insights.parsers.cpu_vulns import CpuVulns
from insights.parsers import SkipComponent


@combiner(CpuVulns)
class CpuVulnsBranch(dict):
    """
    This combiner provides an interface to CPU vulnerabilities parsers.
    """

    def __init__(self, cpu_vulns):
        for cv in cpu_vulns:
            self.update({cv.path: cv.value}) if cv.path else None
        if len(self) == 0:
            raise SkipComponent('Not available data')
