import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import etcd_conf
from insights.parsers.etcd_conf import EtcdConf
from insights.tests import context_wrap

ETCD_CONF = """

[member]
ETCD_NAME=f05-h19-000-1029p.rdu2.scalelab.redhat.com
ETCD_LISTEN_PEER_URLS=https://10.1.40.235:2380
ETCD_DATA_DIR=/var/lib/etcd/
#ETCD_WAL_DIR=
ETCD_SNAPSHOT_COUNT=10000
ETCD_HEARTBEAT_INTERVAL=500

[auth]
ETCD_AUTH_TOKEN=simple

""".strip()


def test_etcd_conf_empty():
    with pytest.raises(SkipComponent):
        assert etcd_conf.EtcdConf(context_wrap('')) is None


def test_etcd_conf():
    conf = EtcdConf(context_wrap(ETCD_CONF))
    assert conf.has_option('member', 'ETCD_HEARTBEAT_INTERVAL') is True


def test_etcd_conf_documentation():
    failed_count, tests = doctest.testmod(
        etcd_conf,
        globs={'conf': EtcdConf(context_wrap(ETCD_CONF))}
    )
    assert failed_count == 0
