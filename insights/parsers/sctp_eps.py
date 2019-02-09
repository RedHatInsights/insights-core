"""
SCTPEps - file ``/proc/net/sctp/eps``
=====================================

This provides detail information about SCTP endpoints.
Which includes Endpoints, Socket, Socket type, Socket State,
hash bucket, bind port, UID, socket inodes, Local IP
address.

Typical content of ``eps`` file is::

    ENDPT            SOCK             STY SST HBKT LPORT   UID INODE     LADDRS
    ffff88017e0a0200 ffff880300f7fa00 2   10  29   11165   200 299689357 10.0.0.102 10.0.0.70
    ffff880612e81c00 ffff8803c28a1b00 2   10  30   11166   200 273361203 10.0.0.102 10.0.0.70 172.31.1.2

Output data is stored in the dictionary format

Examples:
    >>> type(sctp_info)
    <class 'insights.parsers.sctp_eps.SCTPEps'>
    >>> sorted(sctp_info.get_ports()) == sorted(['11165', '11166'])
    True
    >>> sorted(sctp_info.get_local_ips()) == sorted(['10.0.0.102', '10.0.0.70', '172.31.1.2'])
    True
"""

from insights import Parser, parser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.sctp_eps)
class SCTPEps(Parser):
    """
    This parser parses the content of ``/proc/net/sctp/eps`` file.
    And returns a list of dictionaries. The dictionary contains details
    of individual SCTP endpoint"
    """

    def parse_content(self, content):
        if (not content) or (not self.file_path):
            raise SkipException("No Contents")

        COLUMN_IDX = {
            'ENDPT': 'endpoints',
            'SOCK': 'socket',
            'STY': 'sk_type',
            'SST': 'sk_state',
            'HBKT': 'hash_bkt',
            'LPORT': 'local_port',
            'UID': 'uid',
            'INODE': 'inode',
            'LADDRS': 'local_addr'
        }

        self.data = []
        exp_column = COLUMN_IDX.keys()
        for line in content:
            row = {}
            line = line.strip()
            line = line.split()
            if ("LPORT" in line):
                if len(line) == len(exp_column):
                    columns = line
                else:
                    raise ParseException("Contents are not compatible to this parser".format(row))
            else:
                for idx, val in enumerate(columns):
                    if val == "LADDRS":
                        key = COLUMN_IDX[val]
                        row[key] = []
                        while (idx != len(line)):
                            row[key].append(line[idx])
                            idx = idx + 1
                    else:
                        key = COLUMN_IDX[val]
                        row[key] = line[idx]
                self.data.append(row)

    def get_ports(self):
        """
        (list): This function returns a list of SCTP ports if SCTP
                endpoints are created, else `[]`.
        """
        sctp_ports = []
        for eps in self.data:
            sctp_ports.append(eps['local_port'])
        return sctp_ports

    def get_local_ips(self):
        """
        (list): This function returns a list of all local ip addresses
                if SCTP endpoints are created, else `[]`.
        """
        sctp_ips = set([])
        for eps in self.data:
            sctp_ips = set.union(sctp_ips, set(eps['local_addr']))
        return list(sctp_ips)

    def get_eps_ips(self):
        """
        (dict): This function returns a dict of all endpoints and corresponding
                local ip addresses used by SCTP endpoints if SCTP endpoints are
                created, else `None`.
        """
        sctp_eps = {}
        for eps in self.data:
            sctp_eps[eps['endpoints']] = eps['local_addr']
        return sctp_eps
