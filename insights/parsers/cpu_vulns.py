"""
Parsers for file ``/sys/devices/system/cpu/vulnerabilities/*`` outputs
======================================================================

This module provides the following parsers:

CpuVulnsMeltdown - file ``/sys/devices/system/cpu/vulnerabilities/meltdown``
----------------------------------------------------------------------------

CpuVulnsSpectreV1 - file ``/sys/devices/system/cpu/vulnerabilities/spectre_v1``
-------------------------------------------------------------------------------

CpuVulnsSpectreV2 - file ``/sys/devices/system/cpu/vulnerabilities/spectre_v2``
-------------------------------------------------------------------------------

CpuVulnsSpecStoreBypass - file ``/sys/devices/system/cpu/vulnerabilities/spec_store_bypass``
--------------------------------------------------------------------------------------------

CpuVulnsSmt - file ``/sys/devices/system/cpu/vulnerabilities/l1tf``
-------------------------------------------------------------------

CpuVulnsMds - file ``/sys/devices/system/cpu/vulnerabilities/mds``
------------------------------------------------------------------

"""

from __future__ import division
from insights import Parser
from insights import parser
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.cpu_vulns)
class CpuVulns(Parser):
    """
    Class for parsing file ``/sys/devices/system/cpu/vulnerabilities/*``

    Attributes:
        value (str): the result parsed of `/sys/devices/system/cpu/vulnerabilities/*`

    Raises:
        SkipException: When the name of file parsed is not expected or content is empty

    """

    def __init__(self, *args, **kwargs):
        super(CpuVulns, self).__init__(*args, **kwargs)
        input_name = args[0].metadata['input_name']
        if self.file_name != input_name:
            raise SkipException("Not expected file: {0}".format(self.file_name))

    def parse_content(self, content):
        if not content:
            raise SkipException("Input content is empty")
        self.value = content[0]


@parser(Specs.cpu_vulns)
class CpuVulnsMeltdown(CpuVulns):
    """
    Class for parsing file ``/sys/devices/system/cpu/vulnerabilities/meltdown``

    Typical output of file ``/sys/devices/system/cpu/vulnerabilities/meltdown`` looks like::

        Mitigation: PTI

    Examples:
        >>> type(md)
        <class 'insights.parsers.cpu_vulns.CpuVulnsMeltdown'>
        >>> md.value
        'Mitigation: PTI'

    Raises:
        SkipException: When file name is not 'meltdown' or file content is empty

    Attributes:
        value (str): the result parsed of '/sys/devices/system/cpu/vulnerabilities/meltdown'

    """
    pass


@parser(Specs.cpu_vulns)
class CpuVulnsSpectreV1(CpuVulns):
    """
    Class for parsing file ``/sys/devices/system/cpu/vulnerabilities/spectre_v1``

    Typical output of file ``/sys/devices/system/cpu/vulnerabilities/spectre_v1`` looks like::

        Mitigation: Load fences

    Examples:
        >>> type(sp_v1)
        <class 'insights.parsers.cpu_vulns.CpuVulnsSpectreV1'>
        >>> sp_v1.value
        'Mitigation: Load fences'

    Raises:
        SkipException: When file name is not 'spectre_v1' or file content is empty

    Attributes:
        value (str): the result parsed of '/sys/devices/system/cpu/vulnerabilities/spectre_v1'

    """
    pass


@parser(Specs.cpu_vulns)
class CpuVulnsSpectreV2(CpuVulns):
    """
    Class for parsing file ``/sys/devices/system/cpu/vulnerabilities/spectre_v2``

    Typical output of file ``/sys/devices/system/cpu/vulnerabilities/spectre_v2`` looks like::

        Vulnerable: Retpoline without IBPB

    Examples:
        >>> type(sp_v2)
        <class 'insights.parsers.cpu_vulns.CpuVulnsSpectreV2'>
        >>> sp_v2.value
        'Vulnerable: Retpoline without IBPB'

    Raises:
        SkipException: When file name is not 'spectre_v2' or file content is empty

    Attributes:
        value (str): the result parsed of '/sys/devices/system/cpu/vulnerabilities/spectre_v2'

    """
    pass


@parser(Specs.cpu_vulns)
class CpuVulnsSpecStoreBypass(CpuVulns):
    """
    Class for parsing file ``/sys/devices/system/cpu/vulnerabilities/spec_store_bypass``

    Typical output of file ``/sys/devices/system/cpu/vulnerabilities/spec_store_bypass`` looks like::

        Mitigation: Speculative Store Bypass disabled

    Examples:
        >>> type(ssb)
        <class 'insights.parsers.cpu_vulns.CpuVulnsSpecStoreBypass'>
        >>> ssb.value
        'Mitigation: Speculative Store Bypass disabled'

    Raises:
        SkipException: When file name is not 'spec_store_bypass' or file content is empty

    Attributes:
        value (str): the result parsed of '/sys/devices/system/cpu/vulnerabilities/spec_store_bypass'

    """
    pass


@parser(Specs.cpu_vulns)
class CpuVulnsSmt(CpuVulns):
    """
    Class for parsing file ``/sys/devices/system/cpu/vulnerabilities/l1tf``

    Typical output of file ``/sys/devices/system/cpu/vulnerabilities/l1tf`` looks like::

        Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable

    Examples:
        >>> type(smt)
        <class 'insights.parsers.cpu_vulns.CpuVulnsSmt'>
        >>> smt.value
        'Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable'

    Raises:
        SkipException: When file name is not 'l1tf' or file content is empty

    Attributes:
        value (str): the result parsed of '/sys/devices/system/cpu/vulnerabilities/l1tf'

    """
    pass


@parser(Specs.cpu_vulns)
class CpuVulnsMds(CpuVulns):
    """
    Class for parsing file ``/sys/devices/system/cpu/vulnerabilities/mds``

    Typical output of file ``/sys/devices/system/cpu/vulnerabilities/mds`` looks like::

        Vulnerable: Clear CPU buffers attempted, no microcode; SMT vulnerable

    Examples:
        >>> type(mds)
        <class 'insights.parsers.cpu_vulns.CpuVulnsMds'>
        >>> mds.value
        'Vulnerable: Clear CPU buffers attempted, no microcode; SMT vulnerable'

    Raises:
        SkipException: When file name is not 'mds' or file content is empty

    Attributes:
        value (str): the result parsed of '/sys/devices/system/cpu/vulnerabilities/mds'

    """
    pass
