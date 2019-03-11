from insights.parsers import ParseException, SkipException
from insights.parsers import ovs_bridge_mac_table_entry_count
from insights.parsers.ovs_bridge_mac_table_entry_count import OVSappctlFdbShowBridgeCount
from insights.tests import context_wrap
import doctest
import pytest


BRIDGE_NAME_MAC_COUNT = """
{"br-int": 6, "br-int1": 21, "br-tun": 1, "br0": 0}
""".strip()

EXCEPTION1 = """
""".strip()

EXCEPTION2 = """
br-int:"1"
""".strip()


def test_ovs_bridge_mac_table_entry_count_documentation():
    env = {
        "data": OVSappctlFdbShowBridgeCount(context_wrap(BRIDGE_NAME_MAC_COUNT)),
    }
    failed, total = doctest.testmod(ovs_bridge_mac_table_entry_count, globs=env)
    assert failed == 0


def test_ovs_bridge_mac_table_entry_count():
    data = OVSappctlFdbShowBridgeCount(context_wrap(BRIDGE_NAME_MAC_COUNT))
    assert data["br-int1"] == 21
    assert ("bridge0" in data) is False
    assert int(data.get("br-tun")) == 1


def test_ovs_bridge_mac_table_entry_count_exception1():
    with pytest.raises(SkipException) as e:
        OVSappctlFdbShowBridgeCount(context_wrap(EXCEPTION1))
    assert "Empty file" in str(e)


def test_ovs_bridge_mac_table_entry_count_exception2():
    with pytest.raises(ParseException) as e:
        OVSappctlFdbShowBridgeCount(context_wrap(EXCEPTION2))
    assert "Incorrect content: 'br-int:\"1\"'" in str(e)
