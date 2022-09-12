"""
OdCpuDmaLatency - command ``/usr/bin/od -An -t d /dev/cpu_dma_latency``
=======================================================================

This module provides the class ``OdCpuDmaLatency`` which processes
``/usr/bin/od -An -t d /dev/cpu_dma_latency`` command output.
"""
from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException


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
            raise SkipException('Nothing to parse.')
