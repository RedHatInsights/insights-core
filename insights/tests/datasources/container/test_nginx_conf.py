import pytest

from mock.mock import patch, PropertyMock

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent, ContentException
from insights.core.spec_factory import ContainerCommandProvider
from insights.specs.datasources.container.nginx_conf import LocalSpecs, nginx_conf

CONTAINER_CMD = '%s exec -e "PATH=$PATH" %s sh -c "command -v find && find /etc/ /opt/ *.conf"'

find_list = [
    '/etc/nginx/nginx.conf',
    '/etc/nginx/nginx.conf.d/ss-nginx.conf',
    '/opt/rh-nginx/nginx.conf',
    '/opt/rh-nginx/nginx.conf.d/ss-nginx.conf',
]

find_list_ng = [
    '/etc/rd-nginx/nginx.conf',
    '/etc/rd-nginx/nginx.conf.d/ss-nginx.conf',
    '/opt/nginx/nginx.conf',
    '/opt/nginx/nginx.conf.d/ss-nginx.conf',
]

# with spec keep_rc, cmd CalledProcessError would be kept as self._content
find_cmd_exec_error = [
    'Error: runc: exec failed: unable to start container process: exec: '
    + '"find": executable file not found in $PATH: OCI runtime attempted to'
    + 'invoke a command that was not found'
]

find_result_empty = ContentException(
    "Empty after cleaning: insights_containers/03e2861336a6/insights_commands/find_.etc_.opt_-name_.conf"
)


@patch("insights.core.spec_factory.CommandOutputProvider.validate", return_value=None)
@patch("insights.core.spec_factory.CommandOutputProvider.load", return_value=None)
@patch(
    "insights.core.spec_factory.CommandOutputProvider.content",
    new_callable=PropertyMock,
    return_value=find_list,
)
def test_nginx_conf(validate, load, find_l):
    find_nginx_confs = [
        ContainerCommandProvider(CONTAINER_CMD % ("podman", "03e2861336a7"), None, 'rhel8_nginx'),
        ContainerCommandProvider(CONTAINER_CMD % ("docker", "03e2861336a8"), None, 'rhel7_nginx'),
    ]
    broker = {LocalSpecs.container_find_etc_opt_conf: find_nginx_confs, HostContext: None}

    ret = nginx_conf(broker)
    assert len(ret) == 8
    assert ('rhel8_nginx', 'podman', '03e2861336a7', '/etc/nginx/nginx.conf') in ret
    assert (
        'rhel7_nginx',
        'docker',
        '03e2861336a8',
        '/opt/rh-nginx/nginx.conf.d/ss-nginx.conf',
    ) in ret


@patch("insights.core.spec_factory.CommandOutputProvider.validate", return_value=None)
@patch("insights.core.spec_factory.CommandOutputProvider.load", return_value=None)
@patch(
    "insights.core.spec_factory.CommandOutputProvider.content",
    new_callable=PropertyMock,
    return_value=find_list_ng,
)
def test_nginx_conf_empty(validate, load, find_l):
    find_nginx_confs_ng = [
        ContainerCommandProvider(CONTAINER_CMD % ("podman", "03e2861336a7"), None, 'rhel8_nginx'),
        ContainerCommandProvider(CONTAINER_CMD % ("docker", "03e2861336a8"), None, 'rhel7_nginx'),
    ]
    broker = {LocalSpecs.container_find_etc_opt_conf: find_nginx_confs_ng, HostContext: None}

    with pytest.raises(SkipComponent):
        ret = nginx_conf(broker)
        assert len(ret) == 0


@patch("insights.core.spec_factory.CommandOutputProvider.validate", return_value=None)
@patch("insights.core.spec_factory.CommandOutputProvider.load", return_value=None)
@patch(
    "insights.core.spec_factory.CommandOutputProvider.content",
    new_callable=PropertyMock,
    side_effect=[find_cmd_exec_error, find_result_empty, find_list_ng, find_list],
)
def test_nginx_conf_on_cmd_error(validate, load, find_l):
    find_nginx_confs = [
        ContainerCommandProvider(CONTAINER_CMD % ("podman", "03e2861336a5"), None, 'rhel8_nginx'),
        ContainerCommandProvider(CONTAINER_CMD % ("docker", "03e2861336a6"), None, 'rhel7_nginx'),
        ContainerCommandProvider(CONTAINER_CMD % ("podman", "03e2861336a7"), None, 'rhel8_nginx'),
        ContainerCommandProvider(CONTAINER_CMD % ("docker", "03e2861336a8"), None, 'rhel7_nginx'),
    ]
    broker = {LocalSpecs.container_find_etc_opt_conf: find_nginx_confs, HostContext: None}

    ret = nginx_conf(broker)
    assert len(ret) == 4
    assert ('rhel8_nginx', 'podman', '03e2861336a5', '/etc/nginx/nginx.conf') not in ret
    assert (
        'rhel7_nginx',
        'docker',
        '03e2861336a6',
        '/opt/rh-nginx/nginx.conf.d/ss-nginx.conf',
    ) not in ret
    assert ('rhel8_nginx', 'podman', '03e2861336a7', '/etc/nginx/nginx.conf') not in ret
    assert (
        'rhel7_nginx',
        'docker',
        '03e2861336a8',
        '/opt/rh-nginx/nginx.conf.d/ss-nginx.conf',
    ) in ret
