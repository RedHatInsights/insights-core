import pytest
from mock.mock import patch

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

REDHAT_RELEASE7 = """
Red Hat Enterprise Linux release 7.3
""".strip()


def fake_shell_out(cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
    tmp_cmd = cmd.strip().split()
    if 'podman' in tmp_cmd[0]:
        return [REDHAT_RELEASE7, ]
    if 'docker' in tmp_cmd[0]:
        return [FEDORA, ]
    raise Exception()


@patch("insights.core.context.HostContext.shell_out", side_effect=fake_shell_out)
def test_get_running_rhel_containers(fso):
    p_ctn = PodmanListContainers(context_wrap(PODMAN_LIST_CONTAINERS))
    d_ctn = DockerListContainers(context_wrap(DOCKER_LIST_CONTAINERS))
    assert p_ctn is not None
    assert d_ctn is not None

    broker = {
        PodmanListContainers: p_ctn,
        DockerListContainers: d_ctn,
        HostContext: HostContext()}

    ret = running_rhel_containers(broker)
    assert len(ret) == 1
    assert ('rhel7_httpd', 'podman', '03e2861336a7') in ret
    assert ('rhel7_httpd', 'docker', '03e2861336a7') not in ret


@patch("insights.core.context.HostContext.shell_out", return_value=[FEDORA, ])
def test_get_running_rhel_containers_empty(fso):
    p_ctn = PodmanListContainers(context_wrap(PODMAN_LIST_CONTAINERS))
    d_ctn = DockerListContainers(context_wrap(DOCKER_LIST_CONTAINERS))
    assert p_ctn is not None
    assert d_ctn is not None

    broker = {
        PodmanListContainers: p_ctn,
        DockerListContainers: d_ctn,
        HostContext: HostContext()}

    with pytest.raises(SkipComponent):
        ret = running_rhel_containers(broker)
        assert len(ret) == 0
