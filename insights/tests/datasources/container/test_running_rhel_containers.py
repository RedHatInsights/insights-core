import pytest

from mock.mock import patch

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.parsers.docker_list import DockerListContainers
from insights.parsers.podman_list import PodmanListContainers
from insights.specs.datasources.container import running_rhel_containers
from insights.tests import context_wrap

PODMAN_LIST_CONTAINERS_2_UP = """
CONTAINER ID                                                       IMAGE         COMMAND                                            CREATED             STATUS                      PORTS                  NAMES               SIZE
03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216   rhel7_httpd   "/usr/sbin/httpd -DFOREGROUND"                     45 seconds ago      Up 37 seconds               0.0.0.0:8080->80/tcp   angry_saha          796 B (virtual 669.2 MB)
05516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102   bd8638c869ea  "/bin/sh -c 'yum install -y vsftpd-2.2.2-6.el6'"   18 hours ago        Up 18 hours ago                                    tender_rosalind     4.751 MB (virtual 200.4 MB)
""".strip()

DOCKER_LIST_CONTAINERS_1_UP = """
CONTAINER ID                                                       IMAGE         COMMAND                                            CREATED             STATUS                      PORTS                  NAMES               SIZE
d3e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216   rhel7_httpd   "/usr/sbin/httpd -DFOREGROUND"                     45 seconds ago      Up 37 seconds               0.0.0.0:8080->80/tcp   angry_saha          796 B (virtual 669.2 MB)
d5516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102   bd8638c869ea  "/bin/sh -c 'yum install -y vsftpd-2.2.2-6.el6'"   18 hours ago        Exited (137) 18 hours ago                          tender_rosalind     4.751 MB (virtual 200.4 MB)
""".strip()

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


@patch("insights.core.context.HostContext.shell_out", return_value=[REDHAT_RELEASE7, ])
def test_get_running_rhel_containers_both_ok(fso):
    p_ctn = PodmanListContainers(context_wrap(PODMAN_LIST_CONTAINERS_2_UP))
    d_ctn = DockerListContainers(context_wrap(DOCKER_LIST_CONTAINERS_1_UP))
    assert p_ctn is not None
    assert d_ctn is not None

    broker = {
        PodmanListContainers: p_ctn,
        DockerListContainers: d_ctn,
        HostContext: HostContext()}

    ret = running_rhel_containers(broker)
    assert len(ret) == 3
    assert ('rhel7_httpd', 'podman', '03e2861336a7') in ret
    assert ('bd8638c869ea', 'podman', '05516ea08b56') in ret
    assert ('rhel7_httpd', 'docker', 'd3e2861336a7') in ret
    # the stopped container is not collected


@patch("insights.core.context.HostContext.shell_out", side_effect=fake_shell_out)
def test_get_running_rhel_containers_podman_only(fso):
    p_ctn = PodmanListContainers(context_wrap(PODMAN_LIST_CONTAINERS_2_UP))
    d_ctn = DockerListContainers(context_wrap(DOCKER_LIST_CONTAINERS_1_UP))
    assert p_ctn is not None
    assert d_ctn is not None

    broker = {
        PodmanListContainers: p_ctn,
        DockerListContainers: d_ctn,
        HostContext: HostContext()}

    ret = running_rhel_containers(broker)
    assert len(ret) == 2
    assert ('rhel7_httpd', 'podman', '03e2861336a7') in ret
    assert ('bd8638c869ea', 'podman', '05516ea08b56') in ret
    # docker container is from Fedora image, not collected


@patch("insights.core.context.HostContext.shell_out", return_value=[REDHAT_RELEASE7, ])
def test_get_running_rhel_containers_skip_dup(fso):
    p_ctn = PodmanListContainers(context_wrap(PODMAN_LIST_CONTAINERS_2_UP))
    # use the 'podman list' result as input for docker
    d_ctn = DockerListContainers(context_wrap(PODMAN_LIST_CONTAINERS_2_UP))
    assert p_ctn is not None
    assert d_ctn is not None

    broker = {
        PodmanListContainers: p_ctn,
        DockerListContainers: d_ctn,
        HostContext: HostContext()}

    ret = running_rhel_containers(broker)
    assert len(ret) == 2
    assert ('rhel7_httpd', 'podman', '03e2861336a7') in ret
    assert ('bd8638c869ea', 'podman', '05516ea08b56') in ret
    # duplicated container is removed from docker, not collected


@patch("insights.core.context.HostContext.shell_out", return_value=[FEDORA, ])
def test_get_running_rhel_containers_empty(fso):
    p_ctn = PodmanListContainers(context_wrap(PODMAN_LIST_CONTAINERS_2_UP))
    d_ctn = DockerListContainers(context_wrap(DOCKER_LIST_CONTAINERS_1_UP))
    assert p_ctn is not None
    assert d_ctn is not None

    broker = {
        PodmanListContainers: p_ctn,
        DockerListContainers: d_ctn,
        HostContext: HostContext()}

    with pytest.raises(SkipComponent):
        ret = running_rhel_containers(broker)
        assert len(ret) == 0
