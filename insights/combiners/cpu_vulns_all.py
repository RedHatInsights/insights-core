"""
CpuVulnsAll - combiner for cpu vulnerabilities:
===============================================

cpu vulnerabilities includes:
    * CpuVulnsAll - file /sys/devices/system/cpu/vulnerabilities/*

Examples:
    >>> type(cvb)
    <class 'insights.combiners.cpu_vulns_all.CpuVulnsAll'>
    >>> list(cvb.keys())
    ['meltdown', 'spectre_v1']

Raises:
    SkipComponent: Not available data

"""

from insights.core.plugins import combiner
from insights.parsers.cpu_vulns import CpuVulns
from insights.parsers import SkipComponent


@combiner(CpuVulns)
class CpuVulnsAll(dict):
    """
    This combiner provides an interface to CPU vulnerabilities parsers.
    """

    def __init__(self, cpu_vulns):
        for cv in cpu_vulns:
            self.update({cv.file_name: cv.value}) if cv.file_name else None
        if len(self) == 0:
            raise SkipComponent('Not available data')
