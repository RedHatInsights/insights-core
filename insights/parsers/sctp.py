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
    <class 'insights.parsers.sctp.SCTPEps'>
    >>> sorted(sctp_info.sctp_ports) == sorted(['11165', '11166'])
    True
    >>> sorted(sctp_info.sctp_local_ips) == sorted(['10.0.0.102', '10.0.0.70', '172.31.1.2'])
    True
    >>> sorted(sctp_info.search(local_port="11165")) == sorted([{'endpoints': 'ffff88017e0a0200', 'socket': 'ffff880299f7fa00', 'sk_type': '2', 'sk_state': '10', 'hash_bkt': '29', 'local_port': '11165', 'uid': '200', 'inode': '299689357', 'local_addr': ['10.0.0.102', '10.0.0.70']}])
    True
    >>> len(sctp_info.search(local_port="11165")) == 1
    True
    >>> len(sctp_info.search(endpoints="ffff88017e0a0200")) == 1
    True
    >>> sctp_info.sctp_eps_ips
    {'ffff88017e0a0200': ['10.0.0.102', '10.0.0.70'], 'ffff880612e81c00': ['10.0.0.102', '10.0.0.70', '172.31.1.2']}
"""

from insights import Parser, parser
from insights.parsers import SkipException, ParseException
from . import keyword_search
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
        self._sctp_ports = []
        self._sctp_local_ips = set([])
        self._sctp_eps_ips = {}
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
                    if val == "ENDPT":
                        # Save endpoint
                        _eps = line[idx]
                        self._sctp_eps_ips[_eps] = []
                    if val == "LADDRS":
                        # Append multihomed ip address
                        key = COLUMN_IDX[val]
                        row[key] = []
                        while (idx != len(line)):
                            ip_addr = line[idx]
                            row[key].append(ip_addr)
                            self._sctp_local_ips.add(ip_addr)
                            self._sctp_eps_ips[_eps].append(ip_addr)
                            idx = idx + 1
                    else:
                        key = COLUMN_IDX[val]
                        row[key] = line[idx]
                        if key == 'local_port':
                            self._sctp_ports.append(line[idx])
                self.data.append(row)

    @property
    def sctp_ports(self):
        """
        (list): This function returns a list of SCTP ports if SCTP
                endpoints are created, else `[]`.
        """
        return self._sctp_ports

    @property
    def sctp_local_ips(self):
        """
        (list): This function returns a list of all local ip addresses
                if SCTP endpoints are created, else `[]`.
        """
        return list(self._sctp_local_ips)

    @property
    def sctp_eps_ips(self):
        """
        (dict): This function returns a dict of all endpoints and corresponding
                local ip addresses used by SCTP endpoints if SCTP endpoints are
                created, else `{}`.
        """
        return self._sctp_eps_ips

    def search(self, **args):
        """
        (list): This function return a list of all endpoints when args search matches,
                when args search do not match then it returns `[]`.
        """
        return keyword_search(self.data, **args)
