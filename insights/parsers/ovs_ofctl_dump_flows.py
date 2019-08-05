"""
OVSofctlDumpFlows - command ``/usr/bin/ovs-ofctl dump-flows <bridge-name>``
===========================================================================

This module provides class ``OVSofctlDumpFlows`` to parse the
output of command ``/usr/bin/ovs-ofctl dump-flows <bridge-name>``.

"""

from insights import CommandParser, LegacyItemAccess, parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.ovs_ofctl_dump_flows)
class OVSofctlDumpFlows(CommandParser, LegacyItemAccess):
    """
        This class provides processing for the output of the command
        ``/usr/bin/ovs-ofctl dump-flows <bridge-name>``.


        Sample command output::

            cookie=0x0, duration=8.528s, table=0, n_packets=0, n_bytes=0, idle_timeout=60, priority=65535,arp,in_port="s1-eth2",vlan_tci=0x0000,dl_src=62:ee:31:2b:35:7c,dl_dst=a2:72:e7:06:75:2e,arp_spa=10.0.0.2,arp_tpa=10.0.0.3,arp_op=2 actions=output:"s1-eth3"
            cookie=0x0, duration=4.617s, table=0, n_packets=0, n_bytes=0, idle_timeout=60, priority=65535,arp,in_port="s1-eth1",vlan_tci=0x0000,dl_src=d6:fc:9c:e7:a2:f9,dl_dst=a2:72:e7:06:75:2e,arp_spa=10.0.0.1,arp_tpa=10.0.0.3,arp_op=2 actions=output:"s1-eth3"


        Sample parsed output::

            {
                'br0': [
                    { 'cookie': '0x0', 'duration': '8.528s', 'table': '0', 'n_packets': '0', 'n_bytes': '0', 'idle_timeout': '60', 'priority': '65535', 'arp,in_port': 's1-eth2', 'vlan_tci': '0x0000', 'dl_src': '62:ee:31:2b:35:7c', 'dl_dst': 'a2:72:e7:06:75:2e', 'arp_spa': '10.0.0.2', 'arp_tpa': '10.0.0.3', 'arp_op': '2' 'actions=output':'s1-eth3'},
                    { 'cookie': '0x0', 'duration': '4.617s', 'table': '0', 'n_packets': '0', 'n_bytes': '0', 'idle_timeout': '60', 'priority': '65535', 'arp,in_port': 's1-eth1', 'vlan_tci': '0x0000', 'dl_src': 'd6:fc:9c:e7:a2:f9', 'dl_dst': 'a2:72:e7:06:75:2e', 'arp_spa': '10.0.0.1', 'arp_tpa': '10.0.0.3', 'arp_op': '2' 'actions=output':'s1-eth3'}
                ]
            }

        Attributes:
            data (dict): A dictionary where each element contains the bridge-name
                         as key and list of dictionary elements having flow dumps.

        Raises:
            SkipException: When the file is empty or data is not present for a bridge.

        Examples:
            >>> len(data["br0"])
            2
    """
    
    def parse_content(self, content):
        if len(content) == 0:
            raise SkipException("Empty Content!")

        self.data = {}

        # Extract the bridge name
        bridge_name = self.file_path.split("ovs-ofctl_dump-flows_*")[-1]

        for line in content:
            import pdb; pdb.set_trace()
