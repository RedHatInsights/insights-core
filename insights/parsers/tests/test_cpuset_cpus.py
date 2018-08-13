from insights.parsers import cpuset_cpus
from insights.tests import context_wrap


CPUSET_CPU = """
0,2-4,7
""".strip()


def test_init_process_cgroup():
    cpusetinfo = cpuset_cpus.CpusetCpus(context_wrap(CPUSET_CPU))
    assert cpusetinfo.cpu_set == ["0", "2", "3", "4", "7"]
    assert cpusetinfo.cpu_number == 5
