from insights.parsers import init_process_cgroup
from insights.tests import context_wrap


CGROUP_HOST = """
11:hugetlb:/
10:memory:/
9:devices:/
8:pids:/
7:perf_event:/
6:net_prio,net_cls:/
5:blkio:/
4:freezer:/
3:cpuacct,cpu:/
2:cpuset:/
1:name=systemd:/
""".strip()


CGROUP_CONTAINER = """
11:hugetlb:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
10:memory:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
9:devices:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
8:pids:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
7:perf_event:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
6:net_prio,net_cls:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
5:blkio:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
4:freezer:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
3:cpuacct,cpu:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
2:cpuset:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
1:name=systemd:/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope
""".strip()


def test_init_process_cgroup():
    result = init_process_cgroup.InitProcessCgroup(context_wrap(CGROUP_HOST))
    assert result.data["memory"] == ["10", "/"]
    assert result.is_container is False

    result = init_process_cgroup.InitProcessCgroup(context_wrap(CGROUP_CONTAINER))
    assert result.data["memory"] == ["10", "/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope"]
    assert result.is_container is True
