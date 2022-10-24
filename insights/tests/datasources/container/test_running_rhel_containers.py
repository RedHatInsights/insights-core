import pytest

from insights.tests import context_wrap
from insights.specs.datasources.container import running_rhel_containers
from insights.core.dr import SkipComponent
from insights.core.context import HostContext
from insights.parsers.podman_list import PodmanListContainers
from insights.parsers.docker_list import DockerListContainers
from insights.tests.parsers.test_podman_list import PODMAN_LIST_CONTAINERS
from insights.tests.parsers.test_docker_list import DOCKER_LIST_CONTAINERS

FEDORA = """
Fedora release 23 (Twenty Three)
""".strip()

REDHAT_RELEASE8 = """
Red Hat Enterprise Linux release 8.2 (Ootpa)
""".strip()

REDHAT_RELEASE7 = """
Red Hat Enterprise Linux release 7.3
""".strip()


class FakeContext(object):
    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
        tmp_cmd = cmd.strip().split()
        if '03e2861336a7' in tmp_cmd:
            return [REDHAT_RELEASE7, ]
        if '95516ea08b56' in tmp_cmd:
            return [FEDORA, ]

        raise Exception()


class FakeContextNoRHEL(object):
    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
        return [FEDORA, ]


def test_get_running_rhel_containers():
    p_ctn = PodmanListContainers(context_wrap(PODMAN_LIST_CONTAINERS))
    d_ctn = DockerListContainers(context_wrap(DOCKER_LIST_CONTAINERS))
    assert p_ctn is not None
    assert d_ctn is not None
    ctx = FakeContext()

    broker = {
        PodmanListContainers: p_ctn,
        DockerListContainers: d_ctn,
        HostContext: ctx}

    ret = running_rhel_containers(broker)
    assert len(ret) == 2
    assert ('rhel7_httpd', 'podman', '03e2861336a7') in ret
    assert ('rhel7_httpd', 'docker', '03e2861336a7') in ret


def test_get_running_rhel_containers_empty():
    p_ctn = PodmanListContainers(context_wrap(PODMAN_LIST_CONTAINERS))
    d_ctn = DockerListContainers(context_wrap(DOCKER_LIST_CONTAINERS))
    assert p_ctn is not None
    assert d_ctn is not None
    ctx = FakeContextNoRHEL()

    broker = {
        PodmanListContainers: p_ctn,
        DockerListContainers: d_ctn,
        HostContext: ctx}


    with pytest.raises(SkipComponent):
        ret = running_rhel_containers(broker)
        assert len(ret) == 0
