from insights.parsers.cpuinfo import CpuInfo
from insights.tests import context_wrap

CPUINFO = """
COMMAND> cat /proc/cpuinfo
processor       : 0
vendor_id       : GenuineIntel
cpu family      : 6
model           : 45
model name      : Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz
stepping        : 2
microcode       : 1808
cpu MHz         : 2900.000
cache size      : 20480 KB
physical id     : 0
siblings        : 1
core id         : 0
cpu cores       : 1
flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch epb intel_pt tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm mpx rdseed adx smap clflushopt xsaveopt xsavec xgetbv1 dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp
address sizes   : 40 bits physical, 48 bits virtual

processor       : 1
vendor_id       : GenuineIntel
cpu family      : 6
model           : 45
model name      : Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz
stepping        : 2
microcode       : 1808
cpu MHz         : 2900.000
cache size      : 20480 KB
physical id     : 2
siblings        : 1
core id         : 0
cpu cores       : 1
flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch epb intel_pt tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm mpx rdseed adx smap clflushopt xsaveopt xsavec xgetbv1 dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp
address sizes   : 40 bits physical, 48 bits virtual

""".strip()

ONE_SOCKET_CPUINFO = """
processor	: 0
vendor_id	: GenuineIntel
cpu family	: 6
model		: 60
model name	: Intel(R) Core(TM) i7-4800MQ CPU @ 2.70GHz
stepping	: 3
microcode	: 0x1c
cpu MHz		: 3154.042
cache size	: 6144 KB
physical id	: 0
siblings	: 8
core id		: 0
cpu cores	: 4
apicid		: 0
initial apicid	: 0
fpu		: yes
fpu_exception	: yes
cpuid level	: 13
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid xsaveopt
bogomips	: 5388.09
clflush size	: 64
cache_alignment	: 64
address sizes	: 39 bits physical, 48 bits virtual
power management:

processor	: 1
vendor_id	: GenuineIntel
cpu family	: 6
model		: 60
model name	: Intel(R) Core(TM) i7-4800MQ CPU @ 2.70GHz
stepping	: 3
microcode	: 0x1c
cpu MHz		: 3160.371
cache size	: 6144 KB
physical id	: 0
siblings	: 8
core id		: 0
cpu cores	: 4
apicid		: 1
initial apicid	: 1
fpu		: yes
fpu_exception	: yes
cpuid level	: 13
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid xsaveopt
bogomips	: 5388.09
clflush size	: 64
cache_alignment	: 64
address sizes	: 39 bits physical, 48 bits virtual
power management:

processor	: 2
vendor_id	: GenuineIntel
cpu family	: 6
model		: 60
model name	: Intel(R) Core(TM) i7-4800MQ CPU @ 2.70GHz
stepping	: 3
microcode	: 0x1c
cpu MHz		: 3149.929
cache size	: 6144 KB
physical id	: 0
siblings	: 8
core id		: 1
cpu cores	: 4
apicid		: 2
initial apicid	: 2
fpu		: yes
fpu_exception	: yes
cpuid level	: 13
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid xsaveopt
bogomips	: 5388.09
clflush size	: 64
cache_alignment	: 64
address sizes	: 39 bits physical, 48 bits virtual
power management:

processor	: 3
vendor_id	: GenuineIntel
cpu family	: 6
model		: 60
model name	: Intel(R) Core(TM) i7-4800MQ CPU @ 2.70GHz
stepping	: 3
microcode	: 0x1c
cpu MHz		: 3149.929
cache size	: 6144 KB
physical id	: 0
siblings	: 8
core id		: 1
cpu cores	: 4
apicid		: 3
initial apicid	: 3
fpu		: yes
fpu_exception	: yes
cpuid level	: 13
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid xsaveopt
bogomips	: 5388.09
clflush size	: 64
cache_alignment	: 64
address sizes	: 39 bits physical, 48 bits virtual
power management:

processor	: 4
vendor_id	: GenuineIntel
cpu family	: 6
model		: 60
model name	: Intel(R) Core(TM) i7-4800MQ CPU @ 2.70GHz
stepping	: 3
microcode	: 0x1c
cpu MHz		: 3153.937
cache size	: 6144 KB
physical id	: 0
siblings	: 8
core id		: 2
cpu cores	: 4
apicid		: 4
initial apicid	: 4
fpu		: yes
fpu_exception	: yes
cpuid level	: 13
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid xsaveopt
bogomips	: 5388.09
clflush size	: 64
cache_alignment	: 64
address sizes	: 39 bits physical, 48 bits virtual
power management:

processor	: 5
vendor_id	: GenuineIntel
cpu family	: 6
model		: 60
model name	: Intel(R) Core(TM) i7-4800MQ CPU @ 2.70GHz
stepping	: 3
microcode	: 0x1c
cpu MHz		: 3160.371
cache size	: 6144 KB
physical id	: 0
siblings	: 8
core id		: 2
cpu cores	: 4
apicid		: 5
initial apicid	: 5
fpu		: yes
fpu_exception	: yes
cpuid level	: 13
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid xsaveopt
bogomips	: 5388.09
clflush size	: 64
cache_alignment	: 64
address sizes	: 39 bits physical, 48 bits virtual
power management:

processor	: 6
vendor_id	: GenuineIntel
cpu family	: 6
model		: 60
model name	: Intel(R) Core(TM) i7-4800MQ CPU @ 2.70GHz
stepping	: 3
microcode	: 0x1c
cpu MHz		: 3154.042
cache size	: 6144 KB
physical id	: 0
siblings	: 8
core id		: 3
cpu cores	: 4
apicid		: 6
initial apicid	: 6
fpu		: yes
fpu_exception	: yes
cpuid level	: 13
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid xsaveopt
bogomips	: 5388.09
clflush size	: 64
cache_alignment	: 64
address sizes	: 39 bits physical, 48 bits virtual
power management:

processor	: 7
vendor_id	: GenuineIntel
cpu family	: 6
model		: 60
model name	: Intel(R) Core(TM) i7-4800MQ CPU @ 2.70GHz
stepping	: 3
microcode	: 0x1c
cpu MHz		: 3133.687
cache size	: 6144 KB
physical id	: 0
siblings	: 8
core id		: 3
cpu cores	: 4
apicid		: 7
initial apicid	: 7
fpu		: yes
fpu_exception	: yes
cpuid level	: 13
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm ida arat epb pln pts dtherm tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid xsaveopt
bogomips	: 5388.09
clflush size	: 64
cache_alignment	: 64
address sizes	: 39 bits physical, 48 bits virtual
power management:

"""

ARM_CPUINFO = """
processor       : 0
model name      : ARMv7 Processor rev 5 (v7l)
BogoMIPS        : 38.40
Features        : half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae evtstrm
CPU implementer : 0x41
CPU architecture: 7
CPU variant     : 0x0
CPU part        : 0xc07
CPU revision    : 5

processor       : 1
model name      : ARMv7 Processor rev 5 (v7l)
BogoMIPS        : 38.40
Features        : half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae evtstrm
CPU implementer : 0x41
CPU architecture: 7
CPU variant     : 0x0
CPU part        : 0xc07
CPU revision    : 5

processor       : 2
model name      : ARMv7 Processor rev 5 (v7l)
BogoMIPS        : 38.40
Features        : half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae evtstrm
CPU implementer : 0x41
CPU architecture: 7
CPU variant     : 0x0
CPU part        : 0xc07
CPU revision    : 5

processor       : 3
model name      : ARMv7 Processor rev 5 (v7l)
BogoMIPS        : 38.40
Features        : half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae evtstrm
CPU implementer : 0x41
CPU architecture: 7
CPU variant     : 0x0
CPU part        : 0xc07
CPU revision    : 5

Hardware        : BCM2709
Revision        : a01041
"""


POWER_CPUINFO = """
processor	: 0
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 1
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 2
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 3
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 4
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 5
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 6
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 7
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 8
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 9
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 10
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 11
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 12
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 13
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 14
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 15
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 16
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 17
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 18
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 19
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 20
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 21
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 22
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 23
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 24
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 25
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 26
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

processor	: 27
cpu		: POWER7 (architected), altivec supported
clock		: 3612.000000MHz
revision	: 2.0 (pvr 004a 0200)

timebase	: 512000000
platform	: pSeries
model		: IBM,8231-E2D
machine		: CHRP IBM,8231-E2D
"""


def test_cpuinfo():
    cpu_info = CpuInfo(context_wrap(CPUINFO))
    assert cpu_info.cpu_count == 2
    assert cpu_info.socket_count == 2
    assert cpu_info.vendor == "GenuineIntel"
    assert cpu_info.model_name == "Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz"
    assert cpu_info.get_processor_by_index(0) == {
        "cpus": "0",
        "sockets": "0",
        "vendors": "GenuineIntel",
        "models": "Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz",
        "model_ids": "45",
        "families": "6",
        "clockspeeds": "2900.000",
        "cache_sizes": "20480 KB",
        "cpu_cores": "1",
        "flags": "fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch epb intel_pt tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm mpx rdseed adx smap clflushopt xsaveopt xsavec xgetbv1 dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp",
        "stepping": "2",
    }
    assert cpu_info.cpu_speed == "2900.000"
    assert cpu_info.cache_size == "20480 KB"
    assert cpu_info.model_number == "45"
    assert "mmx" in cpu_info.flags
    assert "avx512f" not in cpu_info.flags
    for i, cpu in enumerate(cpu_info):
        assert cpu['cpus'] == str(i)


def test_one_socket_cpuinfo():
    cpu_info = CpuInfo(context_wrap(ONE_SOCKET_CPUINFO))
    assert cpu_info.cpu_count == 8
    assert cpu_info.socket_count == 1
    assert cpu_info.core_total == 32


def test_empty_cpuinfo():
    cpu_info = CpuInfo(context_wrap(""))
    assert cpu_info.cpu_count == 0


def test_arm_cpuinfo():
    cpu_info = CpuInfo(context_wrap(ARM_CPUINFO))
    assert cpu_info.cpu_count == 4
    assert cpu_info.socket_count == 0
    for i, cpu in enumerate(cpu_info):
        assert cpu["models"] == "ARMv7 Processor rev 5 (v7l)"
        assert cpu["features"] == "half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae evtstrm"
        assert cpu["cpu_implementer"] == "0x41"
        assert cpu["cpu_architecture"] == "7"
        assert cpu["cpu_variant"] == "0x0"
        assert cpu["cpu_part"] == "0xc07"
        assert cpu["cpu_revision"] == "5"


def test_power_cpuinfo():
    cpu_info = CpuInfo(context_wrap(POWER_CPUINFO))
    assert cpu_info.cpu_count == 28
    assert cpu_info.socket_count == 0
    for i, cpu in enumerate(cpu_info):
        assert cpu["cpu"] == "POWER7 (architected), altivec supported"
        assert cpu["revision"] == "2.0 (pvr 004a 0200)"
