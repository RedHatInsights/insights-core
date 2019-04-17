from insights.parsers.pcs_config import PCSConfig
from insights.parsers import pcs_config
from insights.tests import context_wrap
import doctest

NORMAL_PCS_CONFIG = """
Cluster Name: cluster-1
Corosync Nodes:
 node-1 node-2
Pacemaker Nodes:
 node-1 node-2

Resources:
 Clone: clone-1
  Meta Attrs: interleave=true ordered=true
  Resource: res-1 (class=ocf provider=pacemaker type=controld)
   Operations: start interval=0s timeout=90 (dlm-start-interval-0s)
               stop interval=0s timeout=100 (dlm-stop-interval-0s)
               monitor interval=30s on-fail=fence (dlm-monitor-interval-30s)
 Clone: clone-2
  Meta Attrs: interleave=true ordered=true
  Resource: res-2 (class=ocf provider=pacemaker type=controld)
   Operations: start interval=0s timeout=90 (dlm-start-interval-0s)
               stop interval=0s timeout=100 (dlm-stop-interval-0s)
               monitor interval=30s on-fail=fence (dlm-monitor-interval-30s)
 Group: grp-1
  Resource: res-1 (class=ocf provider=heartbeat type=IPaddr2)
   Attributes: ip=10.0.0.1 cidr_netmask=32
   Operations: monitor interval=120s (ip_monitor-interval-120s)
               start interval=0s timeout=20s (ip_-start-interval-0s)
               stop interval=0s timeout=20s (ip_-stop-interval-0s)
  Resource: res-2 (class=ocf provider=heartbeat type=Filesystem)
   Attributes: device=/dev/lv_exzpr directory= fstype=xfs run_fsck=yes fast_stop=yes
   Operations: start interval=0s timeout=60 (fs_exzpr-start-interval-0s)
               stop interval=0s timeout=60 (fs_exzpr-stop-interval-0s)
               monitor interval=30s timeout=60 (fs_exzpr-monitor-interval-30s)

Stonith Devices:
Fencing Levels:

Location Constraints:
  Resource: fence-1
    Disabled on: res-mgt (score:-INFINITY) (id:location-fence-1--INFINITY)
  Resource: res-1
    Enabled on: res-mcast (score:INFINITY) (role: Started) (id:cli-prefer-res)
Ordering Constraints:
  start clone-1 then start clone-x (kind:Mandatory) (id:clone-mandatory)
  start clone-2 then start clone-y (kind:Mandatory) (id:clone-mandatory)
Colocation Constraints:
  clone-1 with clone-x (score:INFINITY) (id:clone-INFINITY)
  clone-2 with clone-x (score:INFINITY) (id:clone-INFINITY)

Resources Defaults:
 resource-stickiness: 100
 migration-threshold: 3
Operations Defaults:
 No defaults set

Cluster Properties:
 cluster-infrastructure: corosync
 cluster-name: cluster-1
 dc-version: 1.1.13-10.el7_2.4-44eb2dd
 have-watchdog: false
 no-quorum-policy: ignore
 stonith-enable: true
 stonith-enabled: false
""".strip()


def test_pcs_config_basic():
    pcs = PCSConfig(context_wrap(NORMAL_PCS_CONFIG))
    assert pcs.get("Cluster Name") == "cluster-1"
    assert pcs.get("Corosync Nodes") == ["node-1", "node-2"]
    assert pcs.get("Pacemaker Nodes") == ["node-1", "node-2"]
    assert pcs.get("Unknown Key") is None


def test_pcs_config_normal():
    pcs = PCSConfig(context_wrap(NORMAL_PCS_CONFIG))
    assert "cluster-infrastructure: corosync" in pcs.get("Cluster Properties")
    assert "stonith-enabled: false" in pcs.get("Cluster Properties")
    assert pcs.get("Resources Defaults") == ["resource-stickiness: 100", "migration-threshold: 3"]
    assert "cluster-infrastructure" in pcs.cluster_properties
    assert "have-watchdog" in pcs.cluster_properties
    assert pcs.cluster_properties.get("have-watchdog") == "false"


def test_pcs_config_documentation():
    env = {
        'pcs_config': PCSConfig(context_wrap(NORMAL_PCS_CONFIG)),
    }
    failed, total = doctest.testmod(pcs_config, globs=env)
    assert failed == 0
