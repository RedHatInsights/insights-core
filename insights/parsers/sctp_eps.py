"""
SCTPEps - file ``/proc/net/sctp/eps ``
======================================

This provides detail information about SCTP endpoints.
Which includes Endpoints, Socket, Socket type, Socket State,
hash bucket, bind port, UID, socket inodes, Local IP
address.

Typical content of ``eps`` file is::
    ENDPT            SOCK             STY SST HBKT LPORT   UID INODE     LADDRS
    ffff88017e0a0200 ffff880299f7fa00 2   10  29   11165   200 299689357 10.0.0.102 10.0.0.70 
    ffff880612e81c00 ffff8803c28a1b00 2   10  30   11166   200 273361203 10.0.0.102 10.0.0.70 
    ffff88061fba9800 ffff88061f8a3180 2   10  31   11167   200 273361145 10.0.0.102 10.0.0.70 
    ffff88031e6f1a00 ffff88031dbdb180 2   10  32   11168   200 273365974 10.0.0.102 10.0.0.70

Output data is stored in the dictionary format

Examples:
    >>> type(sctp_info)
    <class 'insights.parsers.sctp_eps.SCTPEps'>
"""

from insights import Parser, parser, get_active_lines
from insights.specs import Specs
from insights.parsers import SkipException, ParseException


@parser(Specs.sctp_eps)
class SCTPEps(Parser):
    """
    This parser parses the content of ``/proc/net/sctp/eps`` file.
    Currently we need "Bind Port" and "Local address"
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
        exp_column = sorted(COLUMN_IDX.keys())
        for line in content:
            row = {}
            line = line.strip()
            line = line.split()
            if ("LPORT" in line):
                if len(line) == len(exp_column):
                    columns = line
                else:
                    raise ParseException("Unrecognised Column Name".format(b=raws))
            else:
                for idx, val in enumerate(columns):
                    key = COLUMN_IDX[val]
                    row[key]=line[idx]
                self.data.append(row)

