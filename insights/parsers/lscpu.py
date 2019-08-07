"""
LsCPU - command ``lscpu``
=========================

This module provides the information about the CPU architecture using the output of the command ``lscpu``.
"""
from insights.parsers import SkipException, split_kv_pairs
from insights.specs import Specs
from .. import CommandParser, parser, LegacyItemAccess


@parser(Specs.lscpu)
class LsCPU(CommandParser, LegacyItemAccess):
    """Parse the output of ``lscpu``.

    Typical output of ``lscpu`` command is::

        Architecture:          x86_64
        CPU op-mode(s):        32-bit, 64-bit
        Byte Order:            Little Endian
        CPU(s):                2
        On-line CPU(s) list:   0,1
        Thread(s) per core:    2
        Core(s) per socket:    1
        Socket(s):             1
        NUMA node(s):          1
        Vendor ID:             GenuineIntel
        CPU family:            6
        Model:                 60
        Model name:            Intel Core Processor (Haswell, no TSX)
        Stepping:              1
        CPU MHz:               2793.530
        BogoMIPS:              5587.06
        Hypervisor vendor:     KVM
        Virtualization type:   full
        L1d cache:             32K
        L1i cache:             32K
        L2 cache:              4096K
        NUMA node0 CPU(s):     0,1

    Examples:

        >>> output.data['Architecture']
        'x86_64'
        >>> len(output.data)
        22
        >>> output.data['CPUs']
        '2'
        >>> output.data['Threads per core']
        '2'
        >>> output.data['Cores per socket']
        '1'
        >>> output.data['Sockets']
        '1'
    """
    def parse_content(self, content):
        if not content:
            raise SkipException("No data.")
        self.data = {}
        _content = split_kv_pairs(content, split_on=":")

        # Cleanup
        for i in _content:
            if "(s)" in i:
                self.data[i.replace("(s)", "s")] = _content[i]
            else:
                self.data[i] = _content[i]
