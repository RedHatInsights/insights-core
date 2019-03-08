from insights.parsers import SkipException
from insights.parsers import ovs_vsctl_list_bridge
from insights.parsers.ovs_vsctl_list_bridge import OVSvsctlListBridge
from insights.tests import context_wrap
import doctest
import pytest


OVS_VSCTL_LIST_BRIDGE = """
name                : br-int
other_config        : {disable-in-band="true", mac-table-size="2048"}
name                : br-tun
other_config        : {}
""".strip()

EXCEPTION1 = """
""".strip()

EXCEPTION2 = """
name                : br-int
other_config        :
""".strip()


def test_ovs_vsctl_list_bridge_documentation():
    env = {
        "data": OVSvsctlListBridge(context_wrap(OVS_VSCTL_LIST_BRIDGE)),
    }
    failed, total = doctest.testmod(ovs_vsctl_list_bridge, globs=env)
    assert failed == 0


def test_ovs_vsctl_list_bridge():
    data = OVSvsctlListBridge(context_wrap(OVS_VSCTL_LIST_BRIDGE))
    assert data[0]["name"] == "br-int"
    assert data[0]["other_config"]["mac-table-size"] == "2048"
    assert data[1]["name"] == "br-tun"


def test_ovs_vsctl_list_bridge_exception1():
    with pytest.raises(SkipException) as e:
        OVSvsctlListBridge(context_wrap(EXCEPTION1))
    assert "Empty file" in str(e)


def test_ovs_vsctl_list_bridge_exception2():
    with pytest.raises(SkipException) as e:
        OVSvsctlListBridge(context_wrap(EXCEPTION2))
    assert "Value not present for the key other_config" in str(e)
