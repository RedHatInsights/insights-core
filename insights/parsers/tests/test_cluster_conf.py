from insights.parsers.cluster_conf import ClusterConf
from insights.tests import context_wrap

CLUSTER_CONF_INFO = """
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
        <fencedevice agent="fence_imm" ipaddr="192.0.2.1" login="opmgr" name="fence1" passwd="***"/>
        <fencedevice agent="fence_imm" ipaddr="192.0.2.2" login="opmgr" name="fence2" passwd="***"/>
    </fencedevices>
   <rm>
    <resources>
       <lvm name="lvm" vg_name="shared_vg" lv_name="ha-lv"/>
       <fs name="FS" device="/dev/shared_vg/ha-lv" force_fsck="0" force_unmount="1" fsid="64050" fstype="ext4" mountpoint="/mnt" options="" self_fence="0"/>
    </resources>
   </rm>
</cluster>
"""


def test_cluster_conf():
    conf = ClusterConf(context_wrap(CLUSTER_CONF_INFO))
    assert any('clusternode' in line for line in conf.lines)
