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
