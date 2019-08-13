"""
LsCPU - command ``lscpu``
=========================

This module provides the information about the CPU architecture using the output of the command ``lscpu``.
"""
from insights.core import CommandParser
from insights.core.plugins import parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.lscpu)
class LsCPU(CommandParser):
    """Parse the output of ``/usr/bin/lscpu``. It uses the ``CommandParser`` as the
    base class. The ``parse_content`` method also converts plural keys for
    better accessibility.

    Ex: "CPU(s)" is converted to "CPUs"

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

        >>> output.info['Architecture']
        'x86_64'
        >>> len(output.info)
        22
        >>> output.info['CPUs']
        '2'
        >>> output.info['Threads per core']
        '2'
        >>> output.info['Cores per socket']
        '1'
        >>> output.info['Sockets']
        '1'

    """
    def parse_content(self, content):
        if not content:
            raise SkipException("No data.")
        self.info = {}
        split_on = ":"
        for line in content:
            k, v = line.split(split_on, 1)
            self.info[k.replace("(s)", "s").strip()] = v.strip()
