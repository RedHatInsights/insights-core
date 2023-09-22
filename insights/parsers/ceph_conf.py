"""
CephConf - file ``/etc/ceph/ceph.conf``
=======================================
"""
from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

add_filter(Specs.ceph_conf, ["["])


@parser(Specs.ceph_conf)
class CephConf(IniConfigFile):
    """
    The CephConf class parses the file ``/etc/ceph/ceph.conf``. The
    ceph.conf is in the standard 'ini' format and is read by the base
    parser class `IniConfigFile`.

    Sample ``/etc/ceph/ceph.conf`` file::

        [global]
        osd_pool_default_pgp_num = 128
        auth_service_required = cephx
        mon_initial_members = controller1-az1,controller1-az2,controller1-az3
        fsid = a4c3-11e8-99c5-5254003f2830-ea8796d6
        cluster_network = 10.xx.xx.xx/23
        auth_supported = cephx
        auth_cluster_required = cephx
        mon_host = 10.xx.xx.xx,xx.xx.xx.xx,10.xx.xx.xx
        auth_client_required = cephx
        osd_pool_default_size = 3
        osd_pool_default_pg_num = 128
        ms_bind_ipv6 = false
        public_network = 10.xx.xx.xx/23

        [osd]
        osd_journal_size = 81920

        [mon.controller1-az2]
        public_addr = 10.xx.xx.xx

        [client.radosgw.gateway]
        user = apache
        rgw_frontends = civetweb port=10.xx.xx.xx:8080
        log_file = /var/log/ceph/radosgw.log
        host = controller1-az2
        keyring = /etc/ceph/ceph.client.radosgw.gateway.keyring
        rgw_keystone_implicit_tenants = true
        rgw_keystone_token_cache_size = 500
        rgw_keystone_url = http://10.xx.xx.xx:35357
        rgw_s3_auth_use_keystone = true
        rgw_keystone_admin_467fE = Xqzta6dYhPHGHGEFaGnctoken
        rgw_keystone_accepted_roles = admin,_member_,Member
        rgw_swift_account_in_url = true


    Examples:
        >>> type(conf)
        <class 'insights.parsers.ceph_conf.CephConf'>
        >>> sorted(conf.sections())
        ['client.radosgw.gateway', 'global', 'mon.controller1-az2', 'osd']
        >>> conf.has_option('osd', 'osd_journal_size')
        True
        >>> conf.getboolean('client.radosgw.gateway', 'rgw_swift_account_in_url')
        True
        >>> conf.get('client.radosgw.gateway', 'rgw_swift_account_in_url') == 'true'
        True
        >>> conf.get('client.radosgw.gateway', 'user') == 'apache'
        True
        >>> conf.get('client.radosgw.gateway', 'log_file') == '/var/log/ceph/radosgw.log'
        True
    """
    pass
