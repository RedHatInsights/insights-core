"""
CpuVulns - Parsers for cpu vulnerabilities file output
======================================================

Reads the ``/sys/devices/system/cpu/vulnerabilities/*`` files and
converts file content into a dictionary in the data property.

Examples:
    >>> type(sp_v1)
    <class 'insights.parsers.cpu_vulns.CpuVulns'>
    >>> sp_v1.value
    'Mitigation: Load fences'
"""

from insights import Parser
from insights import parser
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.cpu_vulns)
class CpuVulns(Parser):
    """
    Base class for current parser

    Attributes:
        value (str): the result parsed

    Raises:
        SkipException: When file content is empty

    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Input content is empty")
        self.value = content[0]
