from insights.parsers.neutron_sriov_agent import NeutronSriovAgent
from insights.tests import context_wrap

NEUTRON_SRIOV_AGENT_CONF = """
[DEFAULT]
debug = false
verbose = false

[sriov_nic]
physical_device_mappings=datacentre:enp2s0f6

[agent]
polling_interval=2

[securitygroup]
firewall_driver=noop
report_interval = 60

[keystone_authtoken]
"""


def test_neutron_sriov_agent():
    n_sriov_agent = NeutronSriovAgent(context_wrap(NEUTRON_SRIOV_AGENT_CONF))
    assert n_sriov_agent is not None
    assert list(n_sriov_agent.sections()) == [
        'sriov_nic', 'agent', 'securitygroup', 'keystone_authtoken']
    assert n_sriov_agent.defaults() == {
        'debug': 'false',
        'verbose': 'false'}
    assert n_sriov_agent.get('sriov_nic', 'physical_device_mappings') == 'datacentre:enp2s0f6'
    assert n_sriov_agent.has_option('securitygroup', 'firewall_driver')
    assert not n_sriov_agent.has_option('yabba', 'dabba_do')
    assert n_sriov_agent.get('DEFAULT', 'debug') == 'false'
