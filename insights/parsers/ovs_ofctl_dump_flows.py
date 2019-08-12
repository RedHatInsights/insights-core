"""
OVSofctlDumpFlows - command ``/usr/bin/ovs-ofctl dump-flows <bridge-name>``
===========================================================================

This module provides class ``OVSofctlDumpFlows`` to parse the
output of command ``/usr/bin/ovs-ofctl dump-flows <bridge-name>``.
"""


from insights import CommandParser, parser
from insights.parsers import SkipException, split_kv_pairs
from insights.specs import Specs


@parser(Specs.ovs_ofctl_dump_flows)
class OVSofctlDumpFlows(CommandParser):
    """
        This class provides processing for the output of the command
        ``/usr/bin/ovs-ofctl dump-flows <bridge-name>``.


        Sample command output::

            cookie=0x0, duration=8.528s, table=0, n_packets=0, n_bytes=0, idle_timeout=60, priority=65535,arp,in_port="s1-eth2",vlan_tci=0x0000,dl_src=62:ee:31:2b:35:7c,dl_dst=a2:72:e7:06:75:2e,arp_spa=10.0.0.2,arp_tpa=10.0.0.3,arp_op=2 actions=output:"s1-eth3"
            cookie=0x0, duration=4.617s, table=0, n_packets=0, n_bytes=0, idle_timeout=60, priority=65535,arp,in_port="s1-eth1",vlan_tci=0x0000,dl_src=d6:fc:9c:e7:a2:f9,dl_dst=a2:72:e7:06:75:2e,arp_spa=10.0.0.1,arp_tpa=10.0.0.3,arp_op=2 actions=output:"s1-eth3"


        Sample parsed output::

            [
                    { 'cookie': '0x0', 'duration': '8.528s', 'table': '0', 'n_packets': '0', 'n_bytes': '0', 'idle_timeout': '60', 'priority': '65535', 'arp,in_port': 's1-eth2', 'vlan_tci': '0x0000', 'dl_src': '62:ee:31:2b:35:7c', 'dl_dst': 'a2:72:e7:06:75:2e', 'arp_spa': '10.0.0.2', 'arp_tpa': '10.0.0.3', 'arp_op': '2' 'actions=output':'s1-eth3'},
                    { 'cookie': '0x0', 'duration': '4.617s', 'table': '0', 'n_packets': '0', 'n_bytes': '0', 'idle_timeout': '60', 'priority': '65535', 'arp,in_port': 's1-eth1', 'vlan_tci': '0x0000', 'dl_src': 'd6:fc:9c:e7:a2:f9', 'dl_dst': 'a2:72:e7:06:75:2e', 'arp_spa': '10.0.0.1', 'arp_tpa': '10.0.0.3', 'arp_op': '2' 'actions=output':'s1-eth3'}
            ]

        Examples:
            >>> ovs_obj.bridge_name
            'br0'
            >>> len(ovs_obj.flow_dumps)
            2
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty Content!")

        self._bridges = []

        # Extract the bridge name
        try:
            self._bridge_name = self.file_path.split("ovs-ofctl_dump-flows_")[1]
        except:
            raise SkipException("Invalid Path!")

        for line in content:
            line = line.split(',')
            flow_list = split_kv_pairs(line, split_on='=')
            if flow_list:
                self._bridges.append(flow_list)
        if not self._bridges:
            raise SkipException("Invalid Content!")

    @property
    def bridge_name(self):
        """
        (str): It will return bridge interface name on success else returns
        `None` on failure.
        """
        return self._bridge_name

    @property
    def flow_dumps(self):
        """
        (list): It will return list of flows added under bridge else returns
        empty list `[]` on failure.
        """
        return self._bridges
