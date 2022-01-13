"""
EtcdConf - file ``/etc/etcd/etcd.conf``
=======================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.core.filters import add_filter
from insights.specs import Specs

add_filter(Specs.etcd_conf, ["["])


@parser(Specs.etcd_conf)
class EtcdConf(IniConfigFile):
    """
    The EtcdConf class parses the file ``/etc/etcd/etcd.conf``. The
    etcd.conf is in the standard 'ini' format and is read by the base
    parser class `IniConfigFile`.

    Typical contents of the file look like::

        [member]
        ETCD_NAME=f05-h19-000-1029p.rdu2.scalelab.redhat.com
        ETCD_LISTEN_PEER_URLS=https://10.1.40.235:2380
        ETCD_DATA_DIR=/var/lib/etcd/
        ETCD_HEARTBEAT_INTERVAL=500
        ETCD_ELECTION_TIMEOUT=2500
        ETCD_LISTEN_CLIENT_URLS=https://10.1.40.235:2379

        [auth]
        ETCD_AUTH_TOKEN=simple

    Examples:
        >>> type(conf)
        <class 'insights.parsers.etcd_conf.EtcdConf'>
        >>> conf.get('auth', 'ETCD_AUTH_TOKEN') == 'simple'
        True
        >>> conf.has_option('member', 'ETCD_NAME')
        True
    """
    pass
