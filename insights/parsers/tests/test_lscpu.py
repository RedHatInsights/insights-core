import doctest
import pytest
from insights.parsers import lscpu, SkipException
from insights.tests import context_wrap


LSCPU_1 = """
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
""".strip()

LSCPU_2 = """
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                2
On-line CPU(s) list:   0
Off-line CPU(s) list:  1
Thread(s) per core:    1
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
NUMA node0 CPU(s):     0
""".strip()

BLANK = """
""".strip()

BAD_LSCPU = """
Architecture:          x86_64
CPU op-mode(s) =        32-bit, 64-bit
""".strip()


def test_lscpu_output():
    output = lscpu.LsCPU(context_wrap(LSCPU_1))
    assert output.info['Architecture'] == 'x86_64'
    assert len(output.info) == 22
    assert output.info['CPUs'] == '2'
    assert output.info['Threads per core'] == '2'
    assert output.info['Cores per socket'] == '1'
    assert output.info['Sockets'] == '1'

    output = lscpu.LsCPU(context_wrap(LSCPU_2))
    assert output.info['Architecture'] == 'x86_64'
    assert output.info['CPUs'] == '2'
    assert output.info['On-line CPUs list'] == '0'
    assert output.info['Off-line CPUs list'] == '1'
    assert output.info['Cores per socket'] == '1'
    assert output.info['Sockets'] == '1'


def test_lscpu_blank_output():
    with pytest.raises(SkipException) as e:
        lscpu.LsCPU(context_wrap(BLANK))
    assert "No data." in str(e)


def test_documentation():
    failed_count, tests = doctest.testmod(
        lscpu,
        globs={'output': lscpu.LsCPU(context_wrap(LSCPU_1))}
    )
    assert failed_count == 0
