import pytest

from mock.mock import patch, PropertyMock

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import ContainerCommandProvider
from insights.specs.datasources.container.nginx_conf import LocalSpecs, nginx_conf


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


@patch("insights.core.spec_factory.CommandOutputProvider.validate", return_value=None)
@patch("insights.core.spec_factory.CommandOutputProvider.load", return_value=None)
@patch("insights.core.spec_factory.CommandOutputProvider.content",
        new_callable=PropertyMock, return_value=find_list)
def test_nginx_conf(validate, load, find_l):
    find_nginx_confs = [
        ContainerCommandProvider(
            'podman exec 03e2861336a7 find /etc/ /opt/ *.conf',
            None, 'rhel8_nginx'),
        ContainerCommandProvider(
            'docker exec 03e2861336a8 find /etc/ /opt/ *.conf',
            None, 'rhel7_nginx'),
    ]
    broker = {
        LocalSpecs.container_find_etc_opt_conf: find_nginx_confs,
        HostContext: None}

    ret = nginx_conf(broker)
    assert len(ret) == 8
    assert ('rhel8_nginx', 'podman', '03e2861336a7', '/etc/nginx/nginx.conf') in ret
    assert ('rhel7_nginx', 'docker', '03e2861336a8', '/opt/rh-nginx/nginx.conf.d/ss-nginx.conf') in ret


@patch("insights.core.spec_factory.CommandOutputProvider.validate", return_value=None)
@patch("insights.core.spec_factory.CommandOutputProvider.load", return_value=None)
@patch("insights.core.spec_factory.CommandOutputProvider.content",
        new_callable=PropertyMock, return_value=find_list_ng)
def test_nginx_conf_empty(validate, load, find_l):
    find_nginx_confs_ng = [
        ContainerCommandProvider(
            'podman exec 03e2861336a7 find /etc/ /opt/ *.conf',
            None, 'rhel8_nginx'),
        ContainerCommandProvider(
            'docker exec 03e2861336a8 find /etc/ /opt/ *.conf',
            None, 'rhel7_nginx'),
    ]
    broker = {
        LocalSpecs.container_find_etc_opt_conf: find_nginx_confs_ng,
        HostContext: None}

    with pytest.raises(SkipComponent):
        ret = nginx_conf(broker)
        assert len(ret) == 0
