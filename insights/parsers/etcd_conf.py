"""
EtcdConf - file ``/etc/etcd/etcd.conf``
=======================================

The EtcdConf class parses the file ``/etc/etcd/etcd.conf``. The
etcd.conf is in the standard 'ini' format and is read by the base
parser class `IniConfigFile`.

Typical contents of the file look like::

    [member]
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
    [auth]
    ETCD_AUTH_TOKEN=simple

Examples:

    >>> conf.get('auth', 'ETCD_AUTH_TOKEN') == 'simple'
    True

    >>> conf.has_option('member', 'ETCD_NAME')
    True
"""


from .. import IniConfigFile, parser, add_filter
from insights.specs import Specs

add_filter(Specs.etcd_conf, ["["])


@parser(Specs.etcd_conf)
class EtcdConf(IniConfigFile):
    """Class for etcd.conf file content."""
    pass
