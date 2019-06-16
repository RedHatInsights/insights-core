#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.parsers.neutron_conf import NeutronConf
from insights.tests import context_wrap

NEUTRON_CONF = """
[DEFAULT]
# debug = False
debug = False
# verbose = True
verbose = False
core_plugin =neutron.plugins.openvswitch.ovs_neutron_plugin.OVSNeutronPluginV2

[quotas]
default_quota = -1
quota_network = 10
[agent]
report_interval = 60

[keystone_authtoken]
auth_host = ost-controller-lb-del.om-l.dsn.inet
auth_port = 35357
[database]
connection = mysql://neutron:dSNneutron01@ost-mysql.om-l.dsn.inet/neutron?ssl_ca=/etc/pki/CA/certs/ca.crt
[service_providers]
service_provider = LOADBALANCER:Haproxy:neutron.services.loadbalancer.drivers.haproxy.plugin_driver.HaproxyOnHostPluginDriver:default
"""


def test_neutron_conf():
    nconf = NeutronConf(context_wrap(NEUTRON_CONF))
    assert nconf is not None
    assert list(nconf.sections()) == ['quotas', 'agent', 'keystone_authtoken', 'database', 'service_providers']
    assert nconf.defaults() == {
        'debug': 'False',
        'verbose': 'False',
        'core_plugin': 'neutron.plugins.openvswitch.ovs_neutron_plugin.OVSNeutronPluginV2'}
    assert nconf.get('quotas', 'quota_network') == '10'
    assert nconf.has_option('database', 'connection')
    assert not nconf.has_option('yabba', 'dabba_do')
    assert nconf.get('DEFAULT', 'debug') == 'False'
