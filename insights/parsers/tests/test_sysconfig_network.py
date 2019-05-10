import doctest
from insights.parsers.sysconfig_network import NetSysconfig
from insights.parsers import sysconfig_network
from insights.tests import context_wrap

NETWORK_SYSCONFIG = """
NETWORKING=yes
HOSTNAME=rhel7-box
GATEWAY=172.31.0.1
NM_BOND_VLAN_ENABLED=no
""".strip()


def test_sysconfig_network():
    result = NetSysconfig(context_wrap(NETWORK_SYSCONFIG))
    assert result["GATEWAY"] == '172.31.0.1'
    assert result.get("NETWORKING") == 'yes'
    assert result['NM_BOND_VLAN_ENABLED'] == 'no'


def test_sysconfig_network_doc_examples():
    env = {
        'net_syscfg': NetSysconfig(context_wrap(NETWORK_SYSCONFIG)),
    }
    failed, total = doctest.testmod(sysconfig_network, globs=env)
    assert failed == 0
