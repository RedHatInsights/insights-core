import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import ovs_vsctl_list_bridge
from insights.parsers.ovs_vsctl_list_bridge import OVSvsctlListBridge
from insights.tests import context_wrap

OVS_VSCTL_LIST_BRIDGES_ALL = """
_uuid               : xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
auto_attach         : []
controller          : [xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx]
datapath_id         : "0000a61fd19ea54f"
datapath_type       : "enp0s9"
datapath_version    : "<unknown>"
external_ids        : {a="0"}
fail_mode           : secure
flood_vlans         : [1000]
flow_tables         : {1=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}
ipfix               : xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
mcast_snooping_enable: false
mirrors             : [xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx]
name                : br-int
netflow             : xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
other_config        : {disable-in-band="true", mac-table-size="2048"}
ports               : [xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, 0000000-0000-0000-0000-0000000000000, 1111111-1111-1111-1111-1111111111111]
protocols           : ["OpenFlow11", "OpenFlow11", "OpenFlow12", "OpenFlow13"]
rstp_enable         : true
rstp_status         : {rstp_bridge_id="8.000.a61fd19ea54f",     rstp_bridge_port_id="0000", rstp_designated_id="8.000.a61fd19ea54f", rstp_designated_port_id="0000", rstp_root_id="8.000.a61fd19ea54f", rstp_root_path_cost="0"}
sflow               : xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
status              : {"0"="1"}
stp_enable          : true

_uuid               : xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
auto_attach         : []
controller          : []
datapath_id         : "0000d29e6a8acc4c"
datapath_type       : ""
datapath_version    : "<unknown>"
external_ids        : {}
fail_mode           : []
flood_vlans         : []
flow_tables         : {}
ipfix               : []
mcast_snooping_enable: false
mirrors             : []
name                : br-tun
netflow             : []
other_config        : {}
ports               : [xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx]
protocols           : []
rstp_enable         : false
rstp_status         : {}
sflow               : []
status              : {}
stp_enable          : false
""".strip()

OVS_VSCTL_LIST_BRIDGES_FILTERED1 = """
name                : br-int
other_config        : {disable-in-band="true", mac-table-size="2048"}
name                : br-tun
other_config        : {}
""".strip()

OVS_VSCTL_LIST_BRIDGES_FILTERED2 = """
_uuid               : xxxxxxxx-xxxx-xxxx-xxxxx-xxxxxxxxxxxx
name                : br-int
netflow             : []
other_config        : {disable-in-band="true", mac-table-size="2048"}
stp_enable          : false
_uuid               : aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
name                : br-tun
netflow             : []
other_config        : {mac-table-size="4096"}
stp_enable          : true
""".strip()

EXCEPTION1 = """
""".strip()


def test_ovs_vsctl_list_bridge_documentation():
    env = {
        "bridge_lists": OVSvsctlListBridge(context_wrap(OVS_VSCTL_LIST_BRIDGES_FILTERED1)),
    }
    failed, total = doctest.testmod(ovs_vsctl_list_bridge, globs=env)
    assert failed == 0


def test_ovs_vsctl_list_bridge_all():
    data = OVSvsctlListBridge(context_wrap(OVS_VSCTL_LIST_BRIDGES_ALL))
    assert data[0]["name"] == "br-int"
    assert data[0]["external_ids"] == {"a": "0"}
    assert data[0]["flow_tables"] == {"1": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
    assert data[0].get("flood_vlans") == ["1000"]
    assert data[0]["protocols"][-1] == "OpenFlow13"
    assert data[0]["other_config"]["mac-table-size"] == "2048"
    assert data[0]["rstp_status"]["rstp_root_path_cost"] == "0"
    assert data[1]["name"] == "br-tun"
    assert data[1]["mirrors"] == []
    assert data[1]["datapath_type"] == ""
    assert data[1]["status"] == {}
    assert data[1].get("stp_enable") == "false"


def test_ovs_vsctl_list_bridge():
    data = OVSvsctlListBridge(context_wrap(OVS_VSCTL_LIST_BRIDGES_FILTERED2))
    assert data[0].get("name") == "br-int"
    assert data[0]["other_config"]["mac-table-size"] == "2048"
    assert data[1]["name"] == "br-tun"


def test_ovs_vsctl_list_bridge_exception1():
    with pytest.raises(SkipComponent) as e:
        OVSvsctlListBridge(context_wrap(EXCEPTION1))
    assert "Empty file" in str(e)
