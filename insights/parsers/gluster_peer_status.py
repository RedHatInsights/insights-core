"""
GlusterPeerStatus - command ``gluster peer status``
===================================================
"""
from insights.core import CommandParser
from insights.core.plugins import parser
from insights.parsers import split_kv_pairs, SkipException
from insights.specs import Specs

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


@parser(Specs.gluster_peer_status)
class GlusterPeerStatus(CommandParser):
    """Parse the output of ``gluster peer status``

    Typical output of ``gluster peer status`` command is::

        Number of Peers: 1

        Hostname: versegluster1.verse.loc
        Uuid: 86c0266b-c78c-4d0c-afe7-953dec143530
        State: Peer in Cluster (Connected)

    Examples:
        >>> output.status['peers']
        1
        >>> len(output.status.get('hosts', []))
        1
        >>> output.status.get('hosts', [])[0].get('Hostname')
        'versegluster1.verse.loc'

    Attributes:
        status (dict): A dict with keys ``peers`` and ``hosts``. For example::

            {'peers': 3,
             'hosts': [
                       {'Hostname': 'foo.com', 'State': 'Peer in Cluster (Connected)', 'Uuid': '86c0266b-c78c-4d0c-afe7-953dec143530'},
                       {'Hostname': 'example.com', 'State': 'Peer in Cluster (Connected)', 'Uuid': '3b4673e3-5e95-4c02-b9bb-2823483e067b'},
                       {'Hostname': 'bar.com', 'State': 'Peer in Cluster (Disconnected)', 'Uuid': '4673e3-5e95-4c02-b9bb-2823483e067bb3'}]
            }

    """
    def _grouper(self, iterable, n, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    def parse_content(self, content):
        if not content:
            raise SkipException("No data.")

        self.status = {'peers': 0, 'hosts': []}
        self.status['peers'] = int(content[0].split(':')[-1].strip())
        for group in list(self._grouper(list(filter(lambda x: x != '', content[2:])), 3)):
            self.status['hosts'].append(split_kv_pairs(group, split_on=':'))
