"""
SockStats - file ``/proc/net/sockstat``
=======================================
The ``TcpIpStats`` class implements the parsing of ``/proc/net/sockstat``
file, which contains TCP/IP stats of individual layer.
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.sockstat)
class SockStats(Parser, dict):
    """
    Parser for ``/proc/net/sockstat`` file.

    Sample input is provided in the *Examples*.

    Sample content::

        sockets: used 3037
        TCP: inuse 1365 orphan 17 tw 2030 alloc 2788 mem 4109
        UDP: inuse 6 mem 3
        UDPLITE: inuse 0
        RAW: inuse 0
        FRAG: inuse 0 memory 0

    Examples:

        >>> type(sock_obj)
        <class 'insights.parsers.sockstat.SockStats'>
        >>> sock_obj.seg_details('tcp')['mem']
        '4109'
        >>> sock_obj.seg_element_details('tcp', 'mem')
        4109
        >>> sock_obj.seg_element_details('frag', 'inuse')
        0
        >>> sock_obj.get('sockets')
        {'used': '3037'}
        >>> sock_obj.get('sockets').get('used')
        '3037'
        >>> sock_obj.seg_element_details('tcp', 'abc') is None
        True


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
        SkipComponent: When contents are empty
    """

    def parse_content(self, content):

        if not content:
            raise SkipComponent("No Contents")

        for line in content:
            line_split = line.split(':')
            nt_seg = line_split[0].lower()
            self[nt_seg] = {}
            val_lst = line_split[1].strip().split()
            key = True
            # Convert string to dictionary
            for idx in val_lst:
                if key:
                    key_idx = idx.lower()
                    self[nt_seg][key_idx] = None
                    key = False
                else:
                    self[nt_seg][key_idx] = idx
                    key = True

    @property
    def sock_stats(self):
        """
        Returns (dict): On On success, it will return detailed memory consumption
        done by all TCP/IP layer in single data, on failure it will return ``None``
        """
        return self

    def seg_details(self, seg):
        """
        Returns (dict): On success, it will return detailed memory consumption
        done by each segment(TCP/IP layer), on failure it will return ``None``.
        """
        return self.get(seg, None)

    def seg_element_details(self, seg, elem):
        """
        Returns (int): On success, it will return memory consumption done by each
        element of the segment(TCP/IP layer), on failure it will return ``None``.
        """

        if seg and elem and elem in self.get(seg, {}):
            return int(self.get(seg, {}).get(elem))
        return None
