"""
SCTP Socket State Parser
========================

Parsers provided by this module include:

SCTPEps - file ``/proc/net/sctp/eps``
-------------------------------------

SCTPAsc - file ``/proc/net/sctp/assocs``
----------------------------------------
"""

from insights import Parser, parser
from insights.parsers import SkipException, ParseException
from . import keyword_search
from insights.specs import Specs


@parser(Specs.sctp_eps)
class SCTPEps(Parser):
    """
    This parser parses the content of ``/proc/net/sctp/eps`` file.
    It returns a list of dictionaries. The dictionary contains detail
    information of individual SCTP endpoint, which includes Endpoints, Socket,
    Socket type, Socket State, hash bucket, bind port, UID, socket inodes,
    Local IP address.

    Typical contents of ``/proc/net/sctp/eps`` file are::

        ENDPT            SOCK             STY SST HBKT LPORT   UID INODE     LADDRS
        ffff88017e0a0200 ffff880300f7fa00 2   10  29   11165   200 299689357 10.0.0.102 10.0.0.70
        ffff880612e81c00 ffff8803c28a1b00 2   10  30   11166   200 273361203 10.0.0.102 10.0.0.70 172.31.1.2

    Output data is stored in the list of dictionaries

    Examples:
        >>> type(sctp_info)
        <class 'insights.parsers.sctp.SCTPEps'>
        >>> sorted(sctp_info.sctp_local_ports) == sorted(['11165', '11166'])
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

    COLUMN_IDX = [
        'endpoints',
        'socket',
        'sk_type',
        'sk_state',
        'hash_bkt',
        'local_port',
        'uid',
        'inode',
        'local_addr'
    ]

    def parse_content(self, content):
        if (not content) or (not self.file_path):
            raise SkipException("No Contents")

        line = content[0].strip().split()
        keys_cnt = len(self.COLUMN_IDX)
        if "LPORT" not in line or len(line) != keys_cnt:
            raise ParseException("Contents are not compatible to this parser".format(line))

        self.data = []
        for line in content[1:]:
            line = line.strip().split(None, keys_cnt - 1)
            line[-1] = line[-1].split()
            self.data.append(dict(zip(self.COLUMN_IDX, line)))

        self._sctp_local_ports = set()
        self._sctp_local_ips = set()
        self._sctp_eps_ips = {}
        for line in self.data:
            self._sctp_local_ports.add(line['local_port'])
            local_addr = line['local_addr']
            self._sctp_local_ips.update(local_addr)
            if line['endpoints'] not in self._sctp_eps_ips:
                self._sctp_eps_ips[line['endpoints']] = []
            self._sctp_eps_ips[line['endpoints']].extend(local_addr)

    @property
    def sctp_local_ports(self):
        """
        (list): This function returns a list of SCTP ports if SCTP
                endpoints are created, else `[]`.
        """
        return sorted(self._sctp_local_ports)

    @property
    def sctp_local_ips(self):
        """
        (list): This function returns a list of all local ip addresses
                if SCTP endpoints are created, else `[]`.
        """
        return sorted(self._sctp_local_ips)

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


@parser(Specs.sctp_asc)
class SCTPAsc(Parser):
    """
    This parser parses the content of ``/proc/net/sctp/assocs`` file.
    And returns a list of dictionaries. The dictionary contains details
    of individual SCTP endpoint, which includes Association Struct, Socket,
    Socket type, Socket State, Association state, hash bucket, association id,
    tx queue, rx queue, uid, inode, local port, remote port, 'local addr,
    remote addr, heartbeat interval, max in-stream, max out-stream, max
    retransmission attempt, number of init chunks send, number of shutdown
    chunks send, data chunks retransmitted'

    Typical contents of ``/proc/net/sctp/assocs`` file are::

        ASSOC     SOCK   STY SST ST HBKT ASSOC-ID TX_QUEUE RX_QUEUE UID INODE LPORT RPORT LADDRS <-> RADDRS HBINT INS OUTS MAXRT T1X T2X RTXC
        ffff88045ac7e000 ffff88062077aa00 2   1   4  1205  963        0        0     200 273361167 11567 11166  10.0.0.102 10.0.0.70 <-> *10.0.0.109 10.0.0.77      1000     2     2   10    0    0        0
        ffff88061fbf2000 ffff88060ff92500 2   1   4  1460  942        0        0     200 273360669 11566 11167  10.0.0.102 10.0.0.70 <-> *10.0.0.109 10.0.0.77      1000     2     2   10    0    0        0

    Output data is stored in the list of dictionaries

    Examples:
        >>> type(sctp_asc)
        <class 'insights.parsers.sctp.SCTPAsc'>
        >>> sorted(sctp_asc.sctp_local_ports) == sorted(['11567','11566'])
        True
        >>> sorted(sctp_asc.sctp_remote_ports) == sorted(['11166','11167'])
        True
        >>> sorted(sctp_asc.sctp_local_ips) == sorted(['10.0.0.102', '10.0.0.70'])
        True
        >>> sorted(sctp_asc.sctp_remote_ips) == sorted(['*10.0.0.109', '10.0.0.77'])
        True
        >>> sorted(sctp_asc.search(local_port='11566')) == sorted([{'init_chunks_send': '0', 'uid': '200', 'shutdown_chunks_send': '0', 'max_outstream': '2', 'tx_que': '0', 'inode': '273360669', 'hrtbt_intrvl': '1000', 'sk_type': '2', 'remote_addr': ['*10.0.0.109', '10.0.0.77'], 'data_chunks_retrans': '0', 'local_addr': ['10.0.0.102', '10.0.0.70'], 'asc_id': '942', 'max_instream': '2', 'remote_port': '11167', 'asc_state': '4', 'max_retrans_atmpt': '10', 'sk_state': '1', 'socket': 'ffff88060ff92500', 'asc_struct': 'ffff88061fbf2000', 'local_port': '11566', 'hash_bkt': '1460', 'rx_que': '0'}])
        True
    """
    COLUMN_IDX = [
        'asc_struct',
        'socket',
        'sk_type',
        'sk_state',
        'asc_state',
        'hash_bkt',
        'asc_id',
        'tx_que',
        'rx_que',
        'uid',
        'inode',
        'local_port',
        'remote_port',
        'local_addr',
        'remote_addr',
        'hrtbt_intrvl',
        'max_instream',
        'max_outstream',
        'max_retrans_atmpt',
        'init_chunks_send',
        'shutdown_chunks_send',
        'data_chunks_retrans',
        'relation',   # should be ignore
    ]

    def parse_content(self, content):
        if (not content) or (not self.file_path):
            raise SkipException("No Contents")

        line = content[0].strip().split()
        keys_cnt = len(self.COLUMN_IDX)
        if "LPORT" not in line or len(line) != keys_cnt:
            raise ParseException("Contents are not compatible to this parser".format(line))

        self.data = []
        laddr_idx = line.index('LADDRS')
        raddr_ridx = len(line) - line.index('RADDRS')
        for line in content[1:]:
            line_1 = line.strip().split(None, laddr_idx)
            line_end = line_1.pop()
            idx = line_end.index('<->')
            laddrs = line_end[:idx].strip().split()
            line_end = line_end[idx + 3:].strip().rsplit(None, raddr_ridx - 1)
            raddrs = line_end.pop(0).split()
            line_1.append(laddrs)
            line_1.append(raddrs)
            line_1.extend(line_end)
            self.data.append(dict(zip(self.COLUMN_IDX[:-1], line_1)))

        self._sctp_local_ports = set()
        self._sctp_remote_ports = set()
        self._sctp_local_ips = set()
        self._sctp_remote_ips = set()
        for line in self.data:
            self._sctp_local_ports.add(line['local_port'])
            self._sctp_remote_ports.add(line['remote_port'])
            self._sctp_local_ips.update(line['local_addr'])
            self._sctp_remote_ips.update(line['remote_addr'])

    @property
    def sctp_local_ports(self):
        """
        (list): This function returns a list of SCTP local peer ports
                if SCTP endpoints are created, else `[]`.
        """
        return sorted(self._sctp_local_ports)

    @property
    def sctp_remote_ports(self):
        """
        (list): This function returns a list of SCTP remote peer ports
                if SCTP endpoints are created, else `[]`.
        """
        return sorted(self._sctp_remote_ports)

    @property
    def sctp_local_ips(self):
        """
        (list): This function returns a list of all local peer's ip addresses
                if SCTP endpoints are created, else `[]`.
        """
        return sorted(self._sctp_local_ips)

    @property
    def sctp_remote_ips(self):
        """
        (list): This function returns a list of all remote peer's ip addresses
                if SCTP endpoints are created, else `[]`.
        """
        return sorted(self._sctp_remote_ips)

    def search(self, **args):
        """
        (list): This function return a list of all SCTP associations when args search matches,
                when args search do not match then it returns `[]`.
        """
        return keyword_search(self.data, **args)
