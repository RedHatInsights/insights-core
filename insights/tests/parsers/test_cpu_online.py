import doctest
from insights.parsers import cpu_online
from insights.tests import context_wrap


CPU_ONLINE = """
0,2-4,7
""".strip()


def test_container_cpu_online():
    container_cpu_online_info = cpu_online.ContainerCpuOnline(
        context_wrap(
            CPU_ONLINE,
            container_id='2869b4e2541c',
            image='registry.access.redhat.com/ubi8/nginx-120',
            engine='podman',
            path='insights_containers/2869b4e2541c/sys/fs/cgroup/cpuset/cpuset.cpus'
        )
    )
    assert container_cpu_online_info.cpu_online_set == ["0", "2", "3", "4", "7"]
    assert container_cpu_online_info.cpu_online_number == 5


def test_doc():
    env = {
        "container_cpu_online_info": cpu_online.ContainerCpuOnline(
            context_wrap(
                CPU_ONLINE,
                container_id='2869b4e2541c',
                image='registry.access.redhat.com/ubi8/nginx-120',
                engine='podman'
            )
        )
    }
    failed_count, total = doctest.testmod(cpu_online, globs=env)
    assert failed_count == 0
