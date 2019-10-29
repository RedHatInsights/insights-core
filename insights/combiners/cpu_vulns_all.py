"""
CpuVulnsAll - files ``/sys/devices/system/cpu/vulnerabilities/*``
=================================================================

This combiner provides an interface to CPU vulnerabilities parsers for files
``/sys/devices/system/cpu/vulnerabilities/*``
"""

from insights.core.plugins import combiner
from insights.parsers.cpu_vulns import CpuVulns
from insights.parsers import SkipComponent


@combiner(CpuVulns)
class CpuVulnsAll(dict):
    """
    Class to capsulate the parsers of cpu_vulns, which includes all files in
    ``/sys/devices/system/cpu/vulnerabilities/*``. Files information will be
    stored in a list of dictionaries, each dictionary is for one file, the
    dictionary key is the file name, dictionary value is the file content.

    Sample output for files:
        ``/sys/devices/system/cpu/vulnerabilities/spectre_v1``::
            Mitigation: Load fences
         ``/sys/devices/system/cpu/vulnerabilities/meltdown``::
            Mitigation: PTI

    Examples:
        >>> type(cvb)
        <class 'insights.combiners.cpu_vulns_all.CpuVulnsAll'>
        >>> list(cvb.keys())
        ['meltdown', 'spectre_v1']

    Raises:
        SkipComponent: Not available data

    """

    def __init__(self, cpu_vulns):
        for cv in cpu_vulns:
            self.update({cv.file_name: cv.value}) if cv.file_name else None
        if len(self) == 0:
            raise SkipComponent('Not available data')
