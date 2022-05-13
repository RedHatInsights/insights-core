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


CGROUP_CONTAINER_1 = """
12:freezer:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
11:pids:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
10:cpuset:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
9:memory:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
8:devices:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
7:blkio:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
6:cpu,cpuacct:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
5:rdma:/
4:net_cls,net_prio:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
3:perf_event:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
2:hugetlb:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
1:name=systemd:/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope
""".strip()


def test_init_process_cgroup():
    result = init_process_cgroup.InitProcessCgroup(context_wrap(CGROUP_HOST))
    assert result.data["memory"] == ["10", "/"]
    assert result.is_container is False

    result = init_process_cgroup.InitProcessCgroup(context_wrap(CGROUP_CONTAINER))
    assert result.data["memory"] == ["10", "/system.slice/docker-55b2b88feeb4fc56bb9384e55100a8581271ca7a22399c6ec52784a35dba933b.scope"]
    assert result.is_container is True

    result = init_process_cgroup.InitProcessCgroup(context_wrap(CGROUP_CONTAINER_1))
    assert result.data["memory"] == ["9", "/machine.slice/libpod-af097fa761cd92daf9ac2e18b6d59959b1212e12621a0951223f9f55d99b452c.scope"]
    assert result.is_container is True
