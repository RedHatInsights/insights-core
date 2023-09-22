"""
OdCpuDmaLatency - command ``/usr/bin/od -An -t d /dev/cpu_dma_latency``
=======================================================================

This module provides the class ``OdCpuDmaLatency`` which processes
``/usr/bin/od -An -t d /dev/cpu_dma_latency`` command output.
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.od_cpu_dma_latency)
class OdCpuDmaLatency(CommandParser):
    """
    Class for parsing the output of `/usr/bin/od -An -t d /dev/cpu_dma_latency` command.

    Typical output of is::

      2000000000

    Attributes:
        force_latency(int): A integer containing the value of force_latency.

    Examples:
        >>> type(cpu_dma_latency)
        <class 'insights.parsers.od_cpu_dma_latency.OdCpuDmaLatency'>
        >>> cpu_dma_latency.force_latency
        2000000000
    """

    def parse_content(self, content):
        if content and content[0].isdigit():
            self.force_latency = int(content[0])
        else:
            raise SkipComponent('Nothing to parse.')
