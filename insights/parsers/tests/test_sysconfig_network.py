from insights.parsers.sysconfig import NetworkSysconfig
from insights.tests import context_wrap

NETWORK_SYSCONFIG = """
NETWORKING=yes
HOSTNAME=rhel7-box
GATEWAY=172.31.0.1
NM_BOND_VLAN_ENABLED=no
""".strip()


def test_sysconfig_network():
    result = NetworkSysconfig(context_wrap(NETWORK_SYSCONFIG))
    assert result["GATEWAY"] == '172.31.0.1'
    assert result.get("NETWORKING") == 'yes'
    assert result['NM_BOND_VLAN_ENABLED'] == 'no'
