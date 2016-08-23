from falafel.mappers.cpuinfo import CpuInfo
from falafel.tests import context_wrap

CPUINFO = """
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
address sizes   : 40 bits physical, 48 bits virtual

""".strip()


def test_cpuinfo():
    cpu_info = CpuInfo.parse_context(context_wrap(CPUINFO))
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
        "cache_sizes": "20480 KB"
    }


def test_empty_cpuinfo():
    cpu_info = CpuInfo.parse_context(context_wrap(""))
    assert cpu_info.cpu_count is None
