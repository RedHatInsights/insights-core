import doctest
from insights.tests import context_wrap
from insights.parsers import swift_conf

proxy_server_conf = """
[DEFAULT]
bind_port = 8080
bind_ip = 172.20.15.20
workers = 0
user = swift
log_name = proxy-server
log_facility = LOG_LOCAL1
log_level = INFO
log_headers = False
log_address = /dev/log
[pipeline:main]
pipeline = catch_errors healthcheck proxy-logging cache ratelimit bulk tempurl formpost authtoken keystone staticweb versioned_writes ceilometer proxy-logging proxy-server
[app:proxy-server]
use = egg:swift#proxy
set log_name = proxy-server
set log_facility = LOG_LOCAL1
set log_level = INFO
set log_address = /dev/log
log_handoffs = true
allow_account_management = true
account_autocreate = true
node_timeout = 60
[filter:catch_errors]
use = egg:swift#catch_errors
[filter:bulk]
use = egg:swift#bulk
max_containers_per_extraction = 10000
max_failed_extractions = 1000
max_deletes_per_request = 10000
yield_frequency = 60
[filter:tempurl]
use = egg:swift#tempurl
[filter:formpost]
use = egg:swift#formpost
[filter:authtoken]
log_name = swift
signing_dir = /var/cache/swift
paste.filter_factory = keystonemiddleware.auth_token:filter_factory
auth_uri = http://172.20.3.28:5000/v2.0
auth_url = http://172.20.4.106:35357
auth_plugin = password
project_domain_id = default
user_domain_id = default
project_name = service
username = swift
delay_auth_decision = 1
cache = swift.cache
include_service_catalog = false
[filter:keystone]
use = egg:swift#keystoneauth
operator_roles = admin, swiftoperator, ResellerAdmin
reseller_prefix = AUTH_
[filter:staticweb]
use = egg:swift#staticweb
url_base = https://10.75.13.138:13808
[filter:versioned_writes]
use = egg:swift#versioned_writes
allow_versioned_writes = true
[filter:ceilometer]
paste.filter_factory = ceilometermiddleware.swift:filter_factory
url = rabbit://guest:J8F22AqWpXqCJyv3mQKeRQszG@172.20.3.20:5672,guest:J8F22AqWpXqCJyv3mQKeRQszG@172.20.3.31:5672,guest:J8F22AqWpXqCJyv3mQKeRQszG@172.20.3.22:5672//
url_test =
"""

object_expirer = """
[DEFAULT]
[object-expirer]
# auto_create_account_prefix = .
auto_create_account_prefix = .
process=0
concurrency=1
recon_cache_path=/var/cache/swift
interval=300
reclaim_age=604800
report_interval=300
processes=0
expiring_objects_account_name=expiring_objects
[pipeline:main]
pipeline = catch_errors cache proxy-server
[app:proxy-server]
use = egg:swift#proxy
[filter:cache]
use = egg:swift#memcache
memcache_servers = 172.16.64.60:11211
[filter:catch_errors]
use = egg:swift#catch_errors
"""

SWIFT_CONF = """
[swift-hash]
# random unique strings that can never change (DO NOT LOSE)
# Use only printable chars (python -c "import string; print(string.printable)")
swift_hash_path_prefix = changeme
swift_hash_path_suffix = changeme

[storage-policy:0]
name = gold
policy_type = replication
default = yes

[storage-policy:1]
name = silver
policy_type = replication

[storage-policy:2]
name = ec42
policy_type = erasure_coding
ec_type = liberasurecode_rs_vand
ec_num_data_fragments = 4
ec_num_parity_fragments = 2
"""


def test_proxy_server_conf():
    result = swift_conf.SwiftProxyServerConf(context_wrap(proxy_server_conf))
    assert 'filter:ceilometer' in result
    assert 'filter:staticweb' in result
    assert result.items('filter:ceilometer').get('url_test') == ''
    assert result.getint('DEFAULT', 'bind_port') == 8080


def test_object_expirer_conf():
    result = swift_conf.SwiftObjectExpirerConf(context_wrap(object_expirer))
    assert 'filter:cache' in result
    assert 'object-expirer' in result
    assert result.get('filter:cache', 'memcache_servers') == '172.16.64.60:11211'
    assert result.getint('object-expirer', 'report_interval') == 300


def test_swift_conf():
    conf = swift_conf.SwiftConf(context_wrap(SWIFT_CONF))
    assert 'swift-hash' in conf.sections()
    assert conf.has_option('storage-policy:2', 'policy_type') is True
    assert conf.get('storage-policy:2', 'policy_type') == 'erasure_coding'
    assert conf.get('storage-policy:2', 'ec_type') == 'liberasurecode_rs_vand'


def test_swift_conf_documentation():
    failed_count, tests = doctest.testmod(
        swift_conf,
        globs={'swift_conf': swift_conf.SwiftConf(context_wrap(SWIFT_CONF)),
               'object_expirer_conf': swift_conf.SwiftObjectExpirerConf(context_wrap(object_expirer)),
               'proxy_server_conf': swift_conf.SwiftProxyServerConf(context_wrap(proxy_server_conf))}
    )
    assert failed_count == 0
