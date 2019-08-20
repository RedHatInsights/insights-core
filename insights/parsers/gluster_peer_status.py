"""
GlusterPeerStatus - command ``gluster peer status``
===================================================
"""
import re

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.parsers import ParseException, SkipException
from insights.specs import Specs
from insights.parsers import split_kv_pairs

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

    Returns:
        A dict with keys ``peers`` and ``hosts`` where ``peers`` indicate
        total number of hosts(int) and ``hosts`` is a list of dictionaries having
        host detail.
    """
    def grouper(self, iterable, n, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    def parse_content(self, content):
        if not content:
            raise SkipException("No data.")
        peers_pattern = re.compile(r"Number of Peers: (\d*)")
        self.status = {'peers': 0, 'hosts': []}
        if peers_pattern.search(content[0]):
            self.status['peers'] = int(peers_pattern.search(content[0]).groups()[-1])

            for group in list(self.grouper(list(filter(lambda x: x != '', content[2:])), 3)):
                self.status['hosts'].append(split_kv_pairs(group, split_on=':'))
        else:
            raise ParseException('Unable to parse the output.')
