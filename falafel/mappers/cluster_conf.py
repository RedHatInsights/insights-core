from falafel.core.plugins import mapper
import xml.etree.ElementTree as ET


@mapper('cluster.conf')
def get_cluster_conf(context):
    """
    Return node, fence, fencedevices and resources infomation.The json structure accord the xml struct.
    Here is example:

        <cluster name="mycluster" config_version="3">
            <clusternodes>
                <clusternode name="node-01.example.com" nodeid="1">
                    <fence>
                        <method name="APC">
                            <device name="apc" port="1"/>
                        </method>
                        <method name="SAN">
                            <device name="sanswitch1" port="12" action="on"/>
                            <device name="sanswitch2" port="12" action="on"/>
                        </method>
                    </fence>
                </clusternode>
                <clusternode name="node-02.example.com" nodeid="2">
                    <fence>
                        <method name="APC">
                            <device name="apc" port="2"/>
                        </method>
                        <method name="SAN">
                            <device name="sanswitch1" port="12"/>
                        </method>
                    </fence>
                </clusternode>
            </clusternodes>
        <cman expected_votes="3"/>
        <fencedevices>
            <fencedevice agent="fence_imm" ipaddr="139.223.41.219" login="opmgr" name="fence1" passwd="***"/>
            <fencedevice agent="fence_imm" ipaddr="139.223.41.229" login="opmgr" name="fence2" passwd="***"/>
        </fencedevices>
        <rm>
            <resources>
                <lvm name="lvm" vg_name="shared_vg" lv_name="ha-lv"/>
                <fs name="FS" device="/dev/shared_vg/ha-lv" force_fsck="0" force_unmount="1" fsid="64050" fstype="ext4" mountpoint="/mnt" options="" self_fence="0"/>
            </resources>
        </rm>
    </cluster>

    OUTPUT like this:
        {
            "fencedevices": [
                {
                    "passwd": "***",
                    "login": "opmgr",
                    "ipaddr": "139.223.41.219",
                    "name": "fence1",
                    "agent": "fence_imm"
                },
                {
                    "passwd": "***",
                    "login": "opmgr",
                    "ipaddr": "139.223.41.229",
                    "name": "fence2",
                    "agent": "fence_imm"
                }
            ],
            "nodes": [
                {
                    "fences": [
                        {
                            "device": [
                                {
                                    "name": "apc",
                                    "port": "1"
                                }
                            ],
                            "meth_name": "APC"
                        },
                        {
                            "device": [
                                {
                                    "action": "on",
                                    "name": "sanswitch1",
                                    "port": "12"
                                },
                                {
                                    "action": "on",
                                    "name": "sanswitch2",
                                    "port": "12"
                                }
                            ],
                            "meth_name": "SAN"
                        }
                    ],
                    "name": "node-01.example.com",
                    "nodeid": "1"
                },
                {
                    "fences": [
                        {
                            "device": [
                                {
                                    "name": "apc",
                                    "port": "2"
                                }
                            ],
                            "meth_name": "APC"
                        },
                        {
                            "device": [
                                {
                                    "name": "sanswitch1",
                                    "port": "12"
                                }
                            ],
                            "meth_name": "SAN"
                        }
                    ],
                    "name": "node-02.example.com",
                    "nodeid": "2"
                }
            ],
            "resources": {
                "lvm": {
                    "name": "lvm",
                    "vg_name": "shared_vg",
                    "lv_name": "ha-lv"
                },
                "fs": {
                    "self_fence": "0",
                    "name": "FS",
                    "force_unmount": "1",
                    "fstype": "ext4",
                    "device": "/dev/shared_vg/ha-lv",
                    "mountpoint": "/mnt",
                    "options": "",
                    "fsid": "64050",
                    "force_fsck": "0"
                }
            }
        }
    """
    cluster_xml = ET.fromstringlist(context.content)
    result = {"nodes": []}
    for node in cluster_xml.iter('clusternode'):
        attr = node.attrib
        attr["fences"] = []
        for fence in node.iter('fence'):
            # There are only one fence in one node part
            for method in fence.iter("method"):
                attr["fences"].append({
                    "meth_name": method.attrib["name"],
                    "device": [device.attrib for device in method.iter("device")]
                })
        result["nodes"].append(attr)
    result["fencedevices"] = []
    result["fencedevices"] += [fencedevice.attrib for fencedevice in cluster_xml.findall(".//fencedevices//")]

    result["resources"] = {}
    result["resources"].update({key: value for key, value in [(sub.tag, sub.attrib) for sub in cluster_xml.findall("./rm/resources//")]})
    return result
