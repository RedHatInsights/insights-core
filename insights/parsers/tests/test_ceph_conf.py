import doctest

from insights.parsers import ceph_conf
from insights.tests import context_wrap


CEPH_CONF = '''
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
'''


def test_ceph_conf():
    conf = ceph_conf.CephConf(context_wrap(CEPH_CONF))
    assert list(conf.sections()) == ['global',
                                     'osd',
                                     'mon.controller1-az2',
                                     'client.radosgw.gateway']
    assert conf.has_option('osd', 'osd_journal_size') is True
    assert conf.getboolean('client.radosgw.gateway', 'rgw_swift_account_in_url') is True
    assert conf.get('client.radosgw.gateway', 'rgw_swift_account_in_url') == 'true'
    assert conf.get('client.radosgw.gateway', 'user') == 'apache'
    assert conf.get('client.radosgw.gateway', 'log_file') == '/var/log/ceph/radosgw.log'


def test_ceph_conf_documentation():
    failed_count, tests = doctest.testmod(
        ceph_conf,
        globs={'conf': ceph_conf.CephConf(context_wrap(CEPH_CONF))}
    )
    assert failed_count == 0
