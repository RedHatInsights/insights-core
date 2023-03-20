import doctest
from insights.parsers import cpuset_cpus
from insights.tests import context_wrap


CPUSET_CPU = """
0,2-4,7
""".strip()


def test_cpuset_cpu():
    cpusetinfo = cpuset_cpus.CpusetCpus(context_wrap(CPUSET_CPU))
    assert cpusetinfo.cpu_set == ["0", "2", "3", "4", "7"]
    assert cpusetinfo.cpu_number == 5


def test_container_cpuset_cpu():
    container_cpusetinfo = cpuset_cpus.ContainerCpusetCpus(
        context_wrap(
            CPUSET_CPU,
            container_id='2869b4e2541c',
            image='registry.access.redhat.com/ubi8/nginx-120',
            engine='podman',
            path='insights_containers/2869b4e2541c/sys/fs/cgroup/cpuset/cpuset.cpus'
        )
    )
    assert container_cpusetinfo.cpu_set == ["0", "2", "3", "4", "7"]
    assert container_cpusetinfo.cpu_number == 5


def test_doc():
    env = {
        "cpusetinfo": cpuset_cpus.CpusetCpus(context_wrap(CPUSET_CPU)),
        "container_cpusetinfo": cpuset_cpus.ContainerCpusetCpus(
            context_wrap(
                CPUSET_CPU,
                container_id='2869b4e2541c',
                image='registry.access.redhat.com/ubi8/nginx-120',
                engine='podman'
            )
        )
    }
    failed_count, total = doctest.testmod(cpuset_cpus, globs=env)
    assert failed_count == 0
