from insights.tests import context_wrap
from insights.parsers.swift_conf import SwiftProxyServerConf
from insights.parsers.swift_conf import SwiftObjectExpirerConf

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


def test_proxy_server_conf():
    result = SwiftProxyServerConf(context_wrap(proxy_server_conf))
    assert 'filter:ceilometer' in result
    assert 'filter:staticweb' in result
    assert result.items('filter:ceilometer').get('url_test') == ''
    assert result.getint('DEFAULT', 'bind_port') == 8080


def test_object_expirer_conf():
    result = SwiftObjectExpirerConf(context_wrap(object_expirer))
    assert 'filter:cache' in result
    assert 'object-expirer' in result
    assert result.get('filter:cache', 'memcache_servers') == '172.16.64.60:11211'
    assert result.getint('object-expirer', 'report_interval') == 300
