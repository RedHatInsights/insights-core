from insights.tests import context_wrap
from insights.parsers.swift_conf import SwiftProxyServerConf

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


def test_proxy_server_conf():
    result = SwiftProxyServerConf(context_wrap(proxy_server_conf))
    assert 'filter:ceilometer' in result
    assert 'filter:staticweb' in result
    assert result.items('filter:ceilometer').get('url_test') == ''
    assert result.getint('DEFAULT', 'bind_port') == 8080
