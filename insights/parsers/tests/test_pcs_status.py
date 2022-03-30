from insights.parsers.pcs_status import PCSStatus
from insights.tests import context_wrap

CLUSTER_NORMAL = """
Cluster name: openstack
Last updated: Fri Oct 14 15:45:32 2016
Last change: Thu Oct 13 20:02:27 2016
Stack: corosync
Current DC: myhost15 (1) - partition with quorum
Version: 1.1.12-a14efad
3 Nodes configured
143 Resources configured


Online: [ myhost15 myhost16 myhost17 ]

Full list of resources:

 stonith-ipmilan-10.24.221.172	(stonith:fence_ipmilan):	Started myhost15
 stonith-ipmilan-10.24.221.171	(stonith:fence_ipmilan):	Started myhost16
 stonith-ipmilan-10.24.221.173	(stonith:fence_ipmilan):	Started myhost15
 ip-ceilometer-pub-10.50.218.121	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-neutron-pub-10.50.218.129	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-ceilometer-prv-10.24.82.127	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-ceilometer-adm-10.24.82.126	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-horizon-pub-10.50.218.126	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-horizon-adm-10.24.82.137	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-amqp-pub-10.24.82.145	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-loadbalancer-pub-10.50.218.128	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-neutron-adm-10.24.82.141	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-neutron-prv-10.24.82.142	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-horizon-prv-10.24.82.138	(ocf::heartbeat:IPaddr2):	Started myhost16
 Clone Set: memcached-clone [memcached]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: haproxy-clone [haproxy]
     Started: [ myhost15 myhost16 myhost17 ]
 ip-galera-pub-10.24.82.130	(ocf::heartbeat:IPaddr2):	Started myhost15
 Master/Slave Set: galera-master [galera]
     Masters: [ myhost15 myhost16 myhost17 ]
 Clone Set: rabbitmq-server-clone [rabbitmq-server]
     Started: [ myhost15 myhost16 myhost17 ]
 ip-keystone-pub-10.50.218.127	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-keystone-adm-10.24.82.139	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-keystone-prv-10.24.82.140	(ocf::heartbeat:IPaddr2):	Started myhost15
 Clone Set: keystone-clone [keystone]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: fs-varlibglanceimages-clone [fs-varlibglanceimages]
     Started: [ myhost15 myhost16 myhost17 ]
 ip-glance-pub-10.50.218.123	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-glance-prv-10.24.82.132	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-glance-adm-10.24.82.131	(ocf::heartbeat:IPaddr2):	Started myhost16
 Clone Set: glance-registry-clone [glance-registry]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: glance-api-clone [glance-api]
     Started: [ myhost15 myhost16 myhost17 ]
 ip-nova-pub-10.50.218.130	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-nova-adm-10.24.82.143	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-nova-prv-10.24.82.144	(ocf::heartbeat:IPaddr2):	Started myhost15
 Clone Set: openstack-nova-novncproxy-clone [openstack-nova-novncproxy]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: openstack-nova-consoleauth-clone [openstack-nova-consoleauth]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: openstack-nova-conductor-clone [openstack-nova-conductor]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: openstack-nova-api-clone [openstack-nova-api]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: openstack-nova-scheduler-clone [openstack-nova-scheduler]
     Started: [ myhost15 myhost16 myhost17 ]
 ip-cinder-pub-10.50.218.122	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-cinder-prv-10.24.82.129	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-cinder-adm-10.24.82.128	(ocf::heartbeat:IPaddr2):	Started myhost16
 Clone Set: cinder-api-clone [cinder-api]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: cinder-scheduler-clone [cinder-scheduler]
     Started: [ myhost15 myhost16 myhost17 ]
 cinder-volume	(systemd:openstack-cinder-volume):	Started myhost15
 ip-heat-pub-10.50.218.124	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-heat-prv-10.24.82.134	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-heat-adm-10.24.82.133	(ocf::heartbeat:IPaddr2):	Started myhost15
 ip-heat_cfn-pub-10.50.218.125	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-heat_cfn-prv-10.24.82.136	(ocf::heartbeat:IPaddr2):	Started myhost16
 ip-heat_cfn-adm-10.24.82.135	(ocf::heartbeat:IPaddr2):	Started myhost16
 Clone Set: neutron-server-clone [neutron-server]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: neutron-scale-clone [neutron-scale] (unique)
     neutron-scale:0	(ocf::neutron:NeutronScale):	Started myhost17
     neutron-scale:1	(ocf::neutron:NeutronScale):	Started myhost16
     neutron-scale:2	(ocf::neutron:NeutronScale):	Started myhost15
 Clone Set: neutron-ovs-cleanup-clone [neutron-ovs-cleanup]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: neutron-netns-cleanup-clone [neutron-netns-cleanup]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: neutron-openvswitch-agent-clone [neutron-openvswitch-agent]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: neutron-dhcp-agent-clone [neutron-dhcp-agent]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: neutron-l3-agent-clone [neutron-l3-agent]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: neutron-metadata-agent-clone [neutron-metadata-agent]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: heat-api-clone [heat-api]
     Started: [ myhost15 myhost16 myhost17 ]
 Resource Group: heat
     openstack-heat-engine	(systemd:openstack-heat-engine):	Started myhost15
 Clone Set: heat-api-cfn-clone [heat-api-cfn]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: heat-api-cloudwatch-clone [heat-api-cloudwatch]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: horizon-clone [horizon]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: mongod-clone [mongod]
     Started: [ myhost15 myhost16 myhost17 ]
 openstack-ceilometer-central	(systemd:openstack-ceilometer-central):	Started myhost16
 Clone Set: openstack-ceilometer-api-clone [openstack-ceilometer-api]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: openstack-ceilometer-alarm-evaluator-clone [openstack-ceilometer-alarm-evaluator]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: openstack-ceilometer-collector-clone [openstack-ceilometer-collector]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: openstack-ceilometer-notification-clone [openstack-ceilometer-notification]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: openstack-ceilometer-alarm-notifier-clone [openstack-ceilometer-alarm-notifier]
     Started: [ myhost15 myhost16 myhost17 ]
 Clone Set: ceilometer-delay-clone [ceilometer-delay]
     Started: [ myhost15 myhost16 myhost17 ]
 openstack-nova-compute-vc13cl42	(systemd:openstack-nova-compute-vc13cl42):	Started myhost15
 openstack-manila-api	(systemd:openstack-manila-api):	Started myhost16
 openstack-manila-scheduler	(systemd:openstack-manila-scheduler):	Started myhost16
 openstack-manila-share	(systemd:openstack-manila-share):	Started myhost16
 ip-manila-10.50.218.150	(ocf::heartbeat:IPaddr2):	Started myhost16

PCSD Status:
  myhost15: Online
  myhost17: Online
  myhost16: Online

Daemon Status:
  corosync: active/enabled
  pacemaker: active/enabled
  pcsd: active/enabled
""".strip()

CLUSTER_NODES_AND_RESOURCES = """
Cluster name: tripleo_cluster
Last updated: Tue May  2 03:08:03 2017          Last change: Tue May  2 01:54:35 2017 by root via crm_resource on overcloud-controller-0
Stack: corosync
Current DC: overcloud-controller-0 (version 1.1.13-10.el7_2.2-44eb2dd) - partition with quorum
3 nodes and 112 resources configured

Online: [ overcloud-controller-0 overcloud-controller-1 overcloud-controller-2 ]

Full list of resources:

 ip-172.20.20.10        (ocf::heartbeat:IPaddr2):       Started overcloud-controller-0
 Clone Set: haproxy-clone [haproxy]
     Started: [ overcloud-controller-0 overcloud-controller-1 overcloud-controller-2 ]
 ip-10.67.16.160        (ocf::heartbeat:IPaddr2):       Started overcloud-controller-2
 ip-172.40.40.10        (ocf::heartbeat:IPaddr2):       Started overcloud-controller-0
 ip-172.50.50.10        (ocf::heartbeat:IPaddr2):       Started overcloud-controller-1
 ip-192.0.2.31  (ocf::heartbeat:IPaddr2):       Started overcloud-controller-0
 ip-172.20.20.11        (ocf::heartbeat:IPaddr2):       Started overcloud-controller-2
 Master/Slave Set: redis-master [redis]
     Masters: [ overcloud-controller-0 ]
     Slaves: [ overcloud-controller-1 overcloud-controller-2 ]
 Master/Slave Set: galera-master [galera]
     Masters: [ overcloud-controller-0 overcloud-controller-1 overcloud-controller-2 ]
 Clone Set: mongod-clone [mongod]
     Started: [ overcloud-controller-0 overcloud-controller-1 overcloud-controller-2 ]
 Clone Set: rabbitmq-clone [rabbitmq]
     Started: [ overcloud-controller-0 overcloud-controller-1 overcloud-controller-2 ]
 Clone Set: memcached-clone [memcached]
     Started: [ overcloud-controller-0 overcloud-controller-1 overcloud-controller-2 ]
 Clone Set: openstack-nova-scheduler-clone [openstack-nova-scheduler]
     Started: [ overcloud-controller-0 overcloud-controller-1 overcloud-controller-2 ]
 Clone Set: neutron-l3-agent-clone [neutron-l3-agent]
     Started: [ overcloud-controller-0 overcloud-controller-1 overcloud-controller-2 ]

PCSD Status:
  overcloud-controller-0: Online
  overcloud-controller-1: Online
  overcloud-controller-2: Online

Daemon Status:
  corosync: active/enabled
  pacemaker: active/enabled
  pcsd: active/enabled
"""

CLUSTER_OUTPUT_PACEMAKER_VERSION2 = """
Cluster name: cluster1
Cluster Summary:
  * Stack: corosync
  * Current DC: host2 (2) (version 2.1.0-8.el8-7c3f660707) - partition with quorum
  * Last updated: Wed Feb 23 15:35:41 2022
  * Last change:  Fri Feb 11 09:09:23 2022 by root via cibadmin on host2
  * 2 nodes configured
  * 6 resource instances configured

Node List:
  * Online: [ host1 (1) host2 (2) ]

Full List of Resources:
  * Resource Group: TEST-HA-DB:
    * TEST-HA-IP (ocf::heartbeat:IPaddr2):    Started host2
    * TEST-HA-VG (ocf::heartbeat:LVM-activate):   Started host2
    * TEST-HA-FS (ocf::heartbeat:Filesystem):     Started host2
    * TEST-HA-BKP-FS (ocf::heartbeat:Filesystem):     Started host2
    * TEST-HA-DB-START   (systemd:postgresql-12):     Started host2
  * vmfence (stonith:fence_vmware_soap):     Started host1

Migration Summary:

Failed Fencing Actions:
  * reboot of r40 failed: delegate=, client=pacemaker-fenced.160287, origin=r11, completed='2022-03-06 23:27:35 +08:00'
  * reboot of r40 failed: delegate=, client=pacemaker-fenced.160287, origin=r11, completed='2022-03-06 23:26:13 +08:00'
  * reboot of r40 failed: delegate=, client=pacemaker-fenced.160287, origin=r11, completed='2022-03-06 23:19:10 +08:00'
  * reboot of r40 failed: delegate=, client=stonith_admin.630429, origin=r11, completed='2022-03-06 23:17:19 +08:00'
  * reboot of r40 failed: delegate=, client=pacemaker-controld.2976, origin=r11, completed='2022-02-27 23:49:15 +08:00'
  * reboot of r40 failed: delegate=, client=pacemaker-controld.2901, origin=r11, completed='2022-02-27 00:05:59 +08:00'

Fencing History:
  * reboot of r40 successful: delegate=r11, client=pacemaker-controld.160291, origin=r11, completed='2022-03-13 23:26:20 +08:00'
  * reboot of r40 successful: delegate=r11, client=pacemaker-controld.160291, origin=r11, completed='2022-03-13 23:08:10 +08:00'
  * reboot of r40 successful: delegate=r11, client=pacemaker-controld.160291, origin=r11, completed='2022-03-13 23:00:05 +08:00'
  * reboot of r40 successful: delegate=r11, client=stonith_admin.1155499, origin=r40, completed='2022-03-06 23:34:03 +08:00'
  * reboot of r40 successful: delegate=r11, client=pacemaker-controld.160291, origin=r11, completed='2022-03-06 23:34:03 +08:00'

Tickets:

PCSD Status:
  host1: Online host2: Online

Daemon Status:
  corosync: active/disabled
  pacemaker: active/enabled
  pcsd: active/enabled
"""

CLUSTER_OUTPUT_PACEMAKER_VERSION_1 = """
Cluster name: test0304
Stack: corosync
Current DC: test-host1 (1) (version 1.1.23-1.el7_9.1-9acf116022) - partition with quorum
Last updated: Thu Feb 17 16:43:01 2022
Last change: Thu Feb 17 16:31:17 2022 by root via cibadmin on test-host1

2 nodes configured
1 resource instance configured

Online: [ test-host1 (1) test-host2 (2) ]

Full list of resources:

 clusterfence	(stonith:fence_aws):	Stopped

Node Attributes:
* Node test-host1 (1):
* Node test-host2 (2):

Migration Summary:
* Node test-host1 (1):
   clusterfence: migration-threshold=1000000 fail-count=1000000 last-failure='Thu Feb 17 16:35:17 2022'
* Node test-host2 (2):
   clusterfence: migration-threshold=1000000 fail-count=1000000 last-failure='Thu Feb 17 16:39:17 2022'

Failed Resource Actions:
* clusterfence_start_0 on test-host1 'unknown error' (1): call=78, status=Timed Out, exitreason='',
    last-rc-change='Thu Feb 17 16:31:17 2022', queued=0ms, exec=240006ms
* clusterfence_start_0 on test-host2 'unknown error' (1): call=24, status=Timed Out, exitreason='',
    last-rc-change='Thu Feb 17 16:35:17 2022', queued=0ms, exec=240005ms

Failed Fencing Actions:
* reboot of test-HOST2 failed: delegate=, client=stonith_admin.26944, origin=test-host1,
    completed='Thu Feb 17 16:40:23 2022'
* reboot of test-host2 failed: delegate=, client=stonith_admin.26937, origin=test-host1,
    completed='Thu Feb 17 16:40:19 2022'

Fencing History:

PCSD Status:
  test-host2: Online  test-host1: Online


Daemon Status:
  corosync: active/disabled
  pacemaker: active/disabled
  pcsd: active/enabled
"""

CLUSTER_NOT_RUNNING = """
Error: cluster is not currently running on this node
"""

CLUSTER_WARNINGS = """
WARNING: We don't know where, but something awful is going to happen
WARNING: This is another made-up warning, please supply real ones
"""

CLUSTER_UNCLEANNODE = """
Node control-2: UNCLEAN (online)
Online: [ control-0 control-1 ]
RemoteOnline: [ compute-0 compute-1 compute-2 compute-3 compute-4 compute-5 compute-6 compute-7 ]

PCSD Status:
  control-0: Online
  control-1: Online
  control-2: Online
"""


def test_pcs_status():
    pcs = PCSStatus(context_wrap(CLUSTER_NORMAL))
    assert pcs.nodes == ['myhost15', 'myhost17', 'myhost16']
    assert pcs.get('Stack') == 'corosync'
    assert pcs.get('Cluster name') == 'openstack'
    assert pcs.get('Current DC') == 'myhost15 (1) - partition with quorum'
    assert pcs.get("Nodes configured") == "3"
    assert pcs.get("Resources configured") == "143"
    assert pcs.get("Online") == "[ myhost15 myhost16 myhost17 ]"
    assert pcs.get('Nonexistent key') is None


def test_pcs_nodes_and_resources():
    pcs = PCSStatus(context_wrap(CLUSTER_NODES_AND_RESOURCES))
    assert pcs.nodes == ['overcloud-controller-0', 'overcloud-controller-1', 'overcloud-controller-2']
    # 3 nodes and 112 resources configured
    assert pcs.data['Nodes configured'] == '3'
    assert pcs.data['Resources configured'] == '112'
    assert pcs.data['Daemon Status'] == [
        'corosync: active/enabled',
        'pacemaker: active/enabled',
        'pcsd: active/enabled',
    ]


def test_pcs_output1():
    pcs = PCSStatus(context_wrap(CLUSTER_OUTPUT_PACEMAKER_VERSION2))
    assert pcs.get('Current DC') == 'host2 (2) (version 2.1.0-8.el8-7c3f660707) - partition with quorum'
    assert pcs.get('Cluster name') == 'cluster1'
    assert pcs.nodes == ['host1', 'host2']
    assert pcs['Nodes configured'] == '2'
    assert pcs['Resources configured'] == '6'
    assert len(pcs['Full list of resources']) == 7
    assert 'Tickets' in pcs
    assert not pcs['Tickets']
    assert len(pcs['Failed Fencing Actions']) == 6
    assert len(pcs['Fencing History']) == 5
    assert 'Migration Summary' in pcs
    assert not pcs['Migration Summary']
    assert len(pcs['Node List']) == 1


def test_pcs_output2():
    pcs = PCSStatus(context_wrap(CLUSTER_OUTPUT_PACEMAKER_VERSION_1))
    assert pcs['Nodes configured'] == '2'
    assert pcs['Resources configured'] == '1'
    assert len(pcs['Full list of resources']) == 1
    assert 'clusterfence	(stonith:fence_aws):	Stopped' in pcs['Full list of resources']
    assert 'Failed Actions' in pcs
    assert len(pcs['Failed Actions']) == 4
    assert "* clusterfence_start_0 on test-host1 'unknown error' (1): call=78, status=Timed Out, exitreason=''," in pcs.data['Failed Actions']
    assert 'Migration Summary' in pcs
    assert len(pcs['Migration Summary']) == 4
    assert "clusterfence: migration-threshold=1000000 fail-count=1000000 last-failure='Thu Feb 17 16:35:17 2022'" in pcs.data['Migration Summary']
    assert len(pcs['Node Attributes']) == 2
    assert '* Node test-host1 (1):' in pcs['Node Attributes']


def test_cluster_not_running():
    pcs = PCSStatus(context_wrap(CLUSTER_NOT_RUNNING))
    assert pcs.nodes == []


def test_cluster_warning():
    pcs = PCSStatus(context_wrap(CLUSTER_WARNINGS))
    assert pcs.nodes == []
    assert pcs.data['WARNING'] == [
        "WARNING: We don't know where, but something awful is going to happen",
        "WARNING: This is another made-up warning, please supply real ones"
    ]


def test_pcs_uncleannode():
    pcs = PCSStatus(context_wrap(CLUSTER_UNCLEANNODE))
    assert pcs.nodes == ['control-0', 'control-1', 'control-2']
    assert pcs.bad_nodes == [{'status': 'UNCLEAN (online)', 'name': 'control-2'}]
