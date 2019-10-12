"""
CpuVulns - files ``/sys/devices/system/cpu/vulnerabilities/*``
==============================================================

Parser to parse the output of files ``/sys/devices/system/cpu/vulnerabilities/*``
"""

from insights import Parser
from insights import parser
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.cpu_vulns)
class CpuVulns(Parser):
    """
    Base class to parse ``/sys/devices/system/cpu/vulnerabilities/*`` files,
    the file content will be stored in a string.

    Sample output for files:
        ``/sys/devices/system/cpu/vulnerabilities/spectre_v1``::
            Mitigation: Load fences

        ``/sys/devices/system/cpu/vulnerabilities/spectre_v2``::
            Vulnerable: Retpoline without IBPB

        ``/sys/devices/system/cpu/vulnerabilities/meltdown``::
            Mitigation: PTI

        ``/sys/devices/system/cpu/vulnerabilities/spec_store_bypass``::
            Mitigation: Speculative Store Bypass disabled

    Examples:
        >>> type(sp_v1)
        <class 'insights.parsers.cpu_vulns.CpuVulns'>
        >>> type(sp_v1) == type(sp_v2) == type(md) == type(ssb)
        True
        >>> sp_v1.value
        'Mitigation: Load fences'
        >>> sp_v2.value
        'Vulnerable: Retpoline without IBPB'
        >>> md.value
        'Mitigation: PTI'
        >>> ssb.value
        'Mitigation: Speculative Store Bypass disabled'

    Attributes:
        value (str): The result parsed

    Raises:
        SkipException: When file content is empty

    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Input content is empty")
        self.value = content[0]
