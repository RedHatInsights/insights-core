"""
Parsers for cpu vulnerabilities file output
===========================================

This module provides the following parser:

CpuVulns - ``/sys/devices/system/cpu/vulnerabilities/*``
"""

from __future__ import division
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
