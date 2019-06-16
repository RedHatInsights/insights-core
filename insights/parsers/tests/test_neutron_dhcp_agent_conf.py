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

import doctest
from insights.parsers import neutron_dhcp_agent_conf
from insights.parsers.neutron_dhcp_agent_conf import NeutronDhcpAgentIni
from insights.tests import context_wrap


DHCP_AGENT_INI = """
[DEFAULT]

ovs_integration_bridge = br-int
ovs_use_veth = false
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
ovs_vsctl_timeout = 10
resync_interval = 30
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
enable_isolated_metadata = True
force_metadata = True
enable_metadata_network = False
root_helper=sudo neutron-rootwrap /etc/neutron/rootwrap.conf
state_path=/var/lib/neutron

[AGENT]

report_interval = 30
log_agent_heartbeats = false
availability_zone = nova
""".strip()


def test_neutron_dhcp_agent_ini():
    data = NeutronDhcpAgentIni(context_wrap(DHCP_AGENT_INI))
    assert data.has_option("AGENT", "log_agent_heartbeats")
    assert data.get("DEFAULT", "force_metadata") == "True"
    assert data.getint("DEFAULT", "ovs_vsctl_timeout") == 10


def test_neutron_dhcp_agent_ini_doc():
    env = {"data": NeutronDhcpAgentIni(context_wrap(DHCP_AGENT_INI))}
    failed, total = doctest.testmod(neutron_dhcp_agent_conf, globs=env)
    assert failed == 0
