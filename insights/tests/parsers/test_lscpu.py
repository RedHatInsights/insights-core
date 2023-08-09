import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import lscpu
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

# RHEL 9 output
LSCPU_3 = """
Architecture:            x86_64
  CPU op-mode(s):        32-bit, 64-bit
  Address sizes:         40 bits physical, 48 bits virtual
  Byte Order:            Little Endian
CPU(s):                  2
  On-line CPU(s) list:   0,1
Vendor ID:               GenuineIntel
  BIOS Vendor ID:        QEMU
  Model name:            Intel Core Processor (Haswell, no TSX, IBRS)
    BIOS Model name:     pc-q35-5.2
    CPU family:          6
    Model:               60
    Thread(s) per core:  1
    Core(s) per socket:  1
    Socket(s):           2
    Stepping:            1
    BogoMIPS:            3599.99
    Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss syscall nx pdpe1gb rdtscp lm co
                         nstant_tsc rep_good nopl xtopology cpuid tsc_known_freq pni pclmulqdq vmx ssse3 fma cx16 pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt
                          tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm abm cpuid_fault invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow
                         vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid xsaveopt arat umip md_clear arch_capabilities
Virtualization features:
  Virtualization:        VT-x
  Hypervisor vendor:     KVM
  Virtualization type:   full
Caches (sum of all):
  L1d:                   64 KiB (2 instances)
  L1i:                   64 KiB (2 instances)
  L2:                    8 MiB (2 instances)
  L3:                    32 MiB (2 instances)
NUMA:
  NUMA node(s):          1
  NUMA node0 CPU(s):     0,1
Vulnerabilities:
  Itlb multihit:         Not affected
  L1tf:                  Mitigation; PTE Inversion; VMX flush not necessary, SMT disabled
  Mds:                   Mitigation; Clear CPU buffers; SMT Host state unknown
  Meltdown:              Mitigation; PTI
  Spec store bypass:     Mitigation; Speculative Store Bypass disabled via prctl and seccomp
  Spectre v1:            Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:            Mitigation; Full generic retpoline, IBPB conditional, IBRS_FW, STIBP disabled, RSB filling
  Srbds:                 Unknown: Dependent on hypervisor status
  Tsx async abort:       Not affected
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

    output = lscpu.LsCPU(context_wrap(LSCPU_3))
    assert output.info['Architecture'] == 'x86_64'
    assert output.info['CPUs'] == '2'
    assert output.info['On-line CPUs list'] == '0,1'
    assert output.info['Cores per socket'] == '1'
    assert output.info['Sockets'] == '2'


def test_lscpu_blank_output():
    with pytest.raises(SkipComponent) as e:
        lscpu.LsCPU(context_wrap(BLANK))
    assert "No data." in str(e)


def test_documentation():
    failed_count, tests = doctest.testmod(
        lscpu,
        globs={'output': lscpu.LsCPU(context_wrap(LSCPU_1))}
    )
    assert failed_count == 0
