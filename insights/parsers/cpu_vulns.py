"""
CpuVulnsSpectreV2 - file ``/sys/devices/system/cpu/vulnerabilities/spectre_v2``
===============================================================================
Module for parsing the output of file ``/sys/devices/system/cpu/vulnerabilities/spectre_v2``.

"""

from __future__ import division
from insights import Parser
from insights import parser
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.cpu_vulns)
class CpuVulnsSpectreV2(Parser):
    """
    Class for parsing file ``/sys/devices/system/cpu/vulnerabilities/spectre_v2``

    Typical output of file ``/sys/devices/system/cpu/vulnerabilities/spectre_v2`` looks like::

        Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling

    Examples:
        >>> type(obj)
        <class 'insights.parsers.cpu_vulns.CpuVulnsSpectreV2'>
        >>> obj.value
        'Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling'

    Raises:
        SkipException: When input content is empty

    Attributes:
        value (str): the result parsed of '/sys/devices/system/cpu/vulnerabilities/spectre_v2'

    """

    def parse_content(self, content):
        EMPTY = "Input content is empty"

        if not content:
            raise SkipException(EMPTY)

        self.value = content[0]
