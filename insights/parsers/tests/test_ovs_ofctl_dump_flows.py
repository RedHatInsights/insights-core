from insights.parsers import SkipException
from insights.parsers import ovs_ofctl_dump_flows
from insights.parsers.ovs_ofctl_dump_flows import OVSofctlDumpFlows
from insights.tests import context_wrap
import doctest
import pytest


OVS_FLOW_DUMPS = """
cookie=0x0, duration=8.528s, table=0, n_packets=0, n_bytes=0, idle_timeout=60, priority=65535,arp,in_port="s1-eth2",vlan_tci=0x0000,dl_src=62:ee:31:2b:35:7c,dl_dst=a2:72:e7:06:75:2e,arp_spa=10.0.0.2,arp_tpa=10.0.0.3,arp_op=2 actions=output:"s1-eth3"
cookie=0x0, duration=4.617s, table=0, n_packets=0, n_bytes=0, idle_timeout=60, priority=65535,arp,in_port="s1-eth1",vlan_tci=0x0000,dl_src=d6:fc:9c:e7:a2:f9,dl_dst=a2:72:e7:06:75:2e,arp_spa=10.0.0.1,arp_tpa=10.0.0.3,arp_op=2 actions=output:"s1-eth3"
cookie=0x0, duration=3.439s, table=0, n_packets=0, n_bytes=0, idle_timeout=60, priority=65535,arp,in_port="s1-eth2",vlan_tci=0x0000,dl_src=62:ee:31:2b:35:7c,dl_dst=a2:72:e7:06:75:2e,arp_spa=10.0.0.2,arp_tpa=10.0.0.3,arp_op=1 actions=output:"s1-eth3"
cookie=0x0, duration=3.424s, table=0, n_packets=0, n_bytes=0, idle_timeout=60, priority=65535,arp,in_port="s1-eth3",vlan_tci=0x0000,dl_src=a2:72:e7:06:75:2e,dl_dst=62:ee:31:2b:35:7c,arp_spa=10.0.0.3,arp_tpa=10.0.0.2,arp_op=2 actions=output:"s1-eth2"
cookie=0x0, duration=8.519s, table=0, n_packets=1, n_bytes=98, idle_timeout=60, priority=65535,icmp,in_port="s1-eth3",vlan_tci=0x0000,dl_src=a2:72:e7:06:75:2e,dl_dst=62:ee:31:2b:35:7c,nw_src=10.0.0.3,nw_dst=10.0.0.2,nw_tos=0,icmp_type=8,icmp_code=0 actions=output:"s1-eth2"
cookie=0x0, duration=8.511s, table=0, n_packets=1, n_bytes=98, idle_timeout=60, priority=65535,icmp,in_port="s1-eth2",vlan_tci=0x0000,dl_src=62:ee:31:2b:35:7c,dl_dst=a2:72:e7:06:75:2e,nw_src=10.0.0.2,nw_dst=10.0.0.3,nw_tos=0,icmp_type=0,icmp_code=0 actions=output:"s1-eth3"
cookie=0x0, duration=4.607s, table=0, n_packets=2, n_bytes=196, idle_timeout=60, priority=65535,icmp,in_port="s1-eth3",vlan_tci=0x0000,dl_src=a2:72:e7:06:75:2e,dl_dst=d6:fc:9c:e7:a2:f9,nw_src=10.0.0.3,nw_dst=10.0.0.1,nw_tos=0,icmp_type=8,icmp_code=0 actions=output:"s1-eth1"
cookie=0x0, duration=4.602s, table=0, n_packets=2, n_bytes=196, idle_timeout=60, priority=65535,icmp,in_port="s1-eth1",vlan_tci=0x0000,dl_src=d6:fc:9c:e7:a2:f9,dl_dst=a2:72:e7:06:75:2e,nw_src=10.0.0.1,nw_dst=10.0.0.3,nw_tos=0,icmp_type=0,icmp_code=0 actions=output:"s1-eth3"
""".strip()


PATH_BR0 = "insights_commands/ovs-ofctl_dump-flows_br0".strip()


def test_ovs_appctl_fdb_show_bridge():
    data = OVSofctlDumpFlows(context_wrap(OVS_FLOW_DUMPS, path=PATH_BR0))
