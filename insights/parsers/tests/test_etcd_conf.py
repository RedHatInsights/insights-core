import pytest
import doctest
from insights.parsers.etcd_conf import EtcdConf
from insights.tests import context_wrap
from insights.parsers import ParseException, SkipException
from insights.tests import context_wrap
from insights.parsers import etcd_conf
ETCD_CONF_1 = """
ETCD_NAME=f05-h19-000-1029p.rdu2.scalelab.redhat.com
ETCD_LISTEN_PEER_URLS=https://10.1.40.235:2380
ETCD_DATA_DIR=/var/lib/etcd/
#ETCD_WAL_DIR=
#ETCD_SNAPSHOT_COUNT=10000
ETCD_HEARTBEAT_INTERVAL=500
ETCD_ELECTION_TIMEOUT=2500
ETCD_LISTEN_CLIENT_URLS=https://10.1.40.235:2379
#ETCD_MAX_SNAPSHOTS=5
#ETCD_MAX_WALS=5
#ETCD_CORS=


#[cluster]
ETCD_INITIAL_ADVERTISE_PEER_URLS=https://10.1.40.235:2380
ETCD_INITIAL_CLUSTER=f05-h19-000-1029p.rdu2.scalelab.redhat.com=https://10.1.40.235:2380
ETCD_INITIAL_CLUSTER_STATE=new
ETCD_INITIAL_CLUSTER_TOKEN=etcd-cluster-1
#ETCD_DISCOVERY=
#ETCD_DISCOVERY_SRV=
#ETCD_DISCOVERY_FALLBACK=proxy
#ETCD_DISCOVERY_PROXY=
ETCD_ADVERTISE_CLIENT_URLS=https://10.1.40.235:2379
#ETCD_STRICT_RECONFIG_CHECK=false
#ETCD_AUTO_COMPACTION_RETENTION=0
#ETCD_ENABLE_V2=true
ETCD_QUOTA_BACKEND_BYTES=8589934592

#[proxy]
#ETCD_PROXY=off
#ETCD_PROXY_FAILURE_WAIT=5000
#ETCD_PROXY_REFRESH_INTERVAL=30000
#ETCD_PROXY_DIAL_TIMEOUT=1000
#ETCD_PROXY_WRITE_TIMEOUT=5000
#ETCD_PROXY_READ_TIMEOUT=0

#[security]
ETCD_TRUSTED_CA_FILE=/etc/etcd/ca.crt
ETCD_CLIENT_CERT_AUTH=true
ETCD_CERT_FILE=/etc/etcd/server.crt
ETCD_KEY_FILE=/etc/etcd/server.key
#ETCD_AUTO_TLS=false
ETCD_PEER_TRUSTED_CA_FILE=/etc/etcd/ca.crt
ETCD_PEER_CLIENT_CERT_AUTH=true
ETCD_PEER_CERT_FILE=/etc/etcd/peer.crt
ETCD_PEER_KEY_FILE=/etc/etcd/peer.key
#ETCD_PEER_AUTO_TLS=false

#[logging]
ETCD_DEBUG=False

#[profiling]
#ETCD_ENABLE_PPROF=false
#ETCD_METRICS=basic
#
#[auth]
#ETCD_AUTH_TOKEN=simple

""".strip()

BLANK_SAMPLE = """
""".strip()


ETCD_CONF_PATH = "etc/etcd/etcd.conf"


def test_constructor():
    context = context_wrap(ETCD_CONF_1, ETCD_CONF_PATH)
    result = EtcdConf(context)

# Active lines are the ones that don't start with HASH.
def test_active_lines_unparsed():
    context = context_wrap(ETCD_CONF_1, ETCD_CONF_PATH)
    result = EtcdConf(context)
    test_active_lines = []
    for line in ETCD_CONF_1.split("\n"):
        if not line.strip().startswith("#"):
            if line.strip():
                test_active_lines.append(line)
    assert test_active_lines == result.active_lines_unparsed

#Key-value pair split, based on "="
def build_active_settings_expected():
    active_settings = {}
    for line in ETCD_CONF_1.split("\n"):
        if not line.strip().startswith("#"):
            if line.strip():
                try:
                    key, value = line.split("=", 1)
                    key, value = key.strip(), value.strip()
                except:
                    pass
                else:
                    active_settings[key] = value
    return active_settings

def test_active_settings():
    context = context_wrap(ETCD_CONF_1, ETCD_CONF_PATH)
    result = EtcdConf(context)
    active_settings = build_active_settings_expected()
    assert active_settings == result.active_settings

def test_get_active_setting_value():
    context = context_wrap(ETCD_CONF_1, ETCD_CONF_PATH)
    result = EtcdConf(context)
    active_settings = build_active_settings_expected()
    for key, value in active_settings.items():
        assert result.get_active_setting_value(key) == value

def test_etcd_blank_input():
    with pytest.raises(SkipException) as sc:
        result= EtcdConf(context_wrap(BLANK_SAMPLE))
    assert "Content is empty." in str(sc.value)

def test_doc():
    env = {
            'EtcdConf': EtcdConf,
            'result': EtcdConf(context_wrap(ETCD_CONF_1, path='/etc/etcd/etcd.conf')),
    }
    failed, total = doctest.testmod(etcd_conf, globs=env)
    assert failed == 0