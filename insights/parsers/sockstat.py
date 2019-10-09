"""
SockStats - file ``/proc/net/sockstat``
=======================================
The ``TcpIpStats`` class implements the parsing of ``/proc/net/snmp``
file, which contains TCP/IP stats of individual layer.
"""


from .. import Parser, parser, LegacyItemAccess
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.sockstat)
class SockStats(Parser, LegacyItemAccess):
    """
    Parser for ``/proc/net/sockstat`` file.

    Sample input is provided in the *Examples*.

    Examples:

        >>> type(sock_obj)
        <class 'insights.parsers.sockstat.SockStats'>
        >>> sock_obj.seg_details('tcp')['mem']
        '4109'
        >>> sock_obj.seg_element_details('tcp', 'mem')
        4109
        >>> sock_obj.seg_element_details('frag', 'inuse')
        0


    Resultant Data::


        {
            'sockets':
                    {
                        'used': '3037'
                    },
            'tcp':
                 {
                     'inuse': '1365',
                     'orphan': '17',
                     'tw': '2030',
                     'alloc': '2788',
                     'mem': '4109'
                 },
            'udp':
                 {
                     'inuse': '6',
                     'mem': '3'
                 },
            'udplite':
                     {
                        'inuse': '0'
                     },
            'raw':
                 {
                    'inuse': '0'
                 }
            'frag':
                  {
                    'inuse': '0',
                    'memory': '0'
                  }
        }

    Raises:
        SkipException: When contents are empty
    """

    def parse_content(self, content):
        self.sock_stats = {}

        if not content:
            raise SkipException("No Contents")

        for line in content:
            line_split = line.split(":")
            nt_seg = line_split[0].lower()
            self.sock_stats[nt_seg] = {}
            val_lst = line_split[1].strip().split(' ')
            key = True
            # Convert string to dictionary
            for idx in val_lst:
                if key:
                    key_idx = idx.lower()
                    self.sock_stats[nt_seg][key_idx] = None
                    key = False
                else:
                    self.sock_stats[nt_seg][key_idx] = idx
                    key = True

    def seg_details(self, seg):
        """
        Returns (dict): On success, it will return detailed memory consumption
        done by each segment(TCP/IP layer), on failure it will return None
        """
        return self.sock_stats.get(seg, None)

    def seg_element_details(self, seg, elem):
        """
        Returns (int): On success, it will return memory consumption done by each
        element of the segment(TCP/IP layer), on failure it will return None.
        """
        if seg and elem and self.sock_stats:
            if seg in self.sock_stats and\
                    elem in self.sock_stats[seg]:
                return int(self.sock_stats[seg][elem])
