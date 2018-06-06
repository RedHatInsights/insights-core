from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.ovs_vsctl_show)
class OVSvsctlshow(CommandParser):
    """
    Input example:
    ====================
    aa3f16d3-9534-4b74-8e9e-8b0ce94038c5
    Bridge br-ctlplane
        Port "eth0"
            Interface "eth0"
        Port br-ctlplane
            Interface br-ctlplane
                type: internal
        Port phy-br-ctlplane
            Interface phy-br-ctlplane
                type: patch
                options: {peer=int-br-ctlplane}
    Bridge br-int
        fail_mode: secure
        Port br-int
            Interface br-int
                type: internal
        Port int-br-ctlplane
            Interface int-br-ctlplane
            type: patch
            options: {peer=phy-br-ctlplane}
        Port "tap293d29ec-d1"
            tag: 1
            Interface "tap293d29ec-d1"
                type: internal
    ovs_version: "2.3.2"

   Parse result:
   ===============================
    {
        "uuid": "aa3f16d3-9534-4b74-8e9e-8b0ce94038c5"
        "bridges": {
            "br-ctlplane": {
                "ports": [
                    {
                        "interface": "eth0",
                        "port": "eth0"
                    },
                    {
                        "interface": "br-ctlplane",
                        "port": "br-ctlplane",
                        "type": "internal"
                    },
                    {
                        "interface": "phy-br-ctlplane",
                        "options": {
                            "peer": "int-br-ctlplane"
                        },
                        "port": "phy-br-ctlplane",
                        "type": "patch"
                    }
                ]
            },
            "br-int": {
                "fail_mode": "secure",
                "ports": [
                    {
                        "interface": "br-int",
                        "port": "br-int",
                        "type": "internal"
                    },
                    {
                        "interface": "int-br-ctlplane",
                        "options": {
                            "peer": "phy-br-ctlplane"
                        },
                        "port": "int-br-ctlplane",
                        "type": "patch"
                    },
                    {
                        "interface": "tap293d29ec-d1",
                        "port": "tap293d29ec-d1",
                        "tag": "1",
                        "type": "internal"
                    }
                ]
            }
        },
        "ovs_version": "2.3.2",
    }
    """

    def parse_content(self, content):
        if len(content) < 3:
            return
        version_line = content[-1]
        self.data = {"uuid": content[0], "bridges": {}, "ovs_version": version_line.split('"')[1]}
        bridge_dict = {}
        port_dict = {}
        for line in content[1:-1]:
            line = line.strip()
            prefix, _, value = line.partition(" ")
            if prefix == "Bridge":
                bridge_dict = {"ports": []}
                self.data["bridges"][value] = bridge_dict
            elif prefix == "fail_mode:":
                bridge_dict["fail_mode"] = value
            elif prefix == "Port":
                port_dict = {"port": value.replace('"', "")}
                bridge_dict["ports"].append(port_dict)
            elif prefix == "tag:":
                port_dict["tag"] = value
            elif prefix == "Interface":
                port_dict["interface"] = value.replace('"', "")
            elif prefix == "type:":
                port_dict["type"] = value
            elif prefix == "options:":
                options_items = value[1:-1].split(", ")
                port_dict["options"] = dict(
                    (item.split("=")[0], item.split("=")[1].replace('"', ""))
                    for item in options_items
                )

    def get_ovs_version(self):
        return self.data.get("ovs_version")

    def get_bridge(self, bridge_name):
        return self.data["bridges"].get(bridge_name, None)
