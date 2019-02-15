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
        self._sctp_local_ports = []
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
                            self._sctp_local_ports.append(line[idx])
                self.data.append(row)

    @property
    def sctp_local_ports(self):
        """
        (list): This function returns a list of SCTP ports if SCTP
                endpoints are created, else `[]`.
        """
        return self._sctp_local_ports

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

    Typical contents of ``/proc/net/sctp/eps`` file are::

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

    def parse_content(self, content):
        if (not content) or (not self.file_path):
            raise SkipException("No Contents")

        ASC_COLUMN_IDX = {
            'ASSOC': 'asc_struct',
            'SOCK': 'socket',
            'STY': 'sk_type',
            'SST': 'sk_state',
            'ST': 'asc_state',
            'HBKT': 'hash_bkt',
            'ASSOC-ID': 'asc_id',
            'TX_QUEUE': 'tx_que',
            'RX_QUEUE': 'rx_que',
            'UID': 'uid',
            'INODE': 'inode',
            'LPORT': 'local_port',
            'RPORT': 'remote_port',
            'LADDRS': 'local_addr',
            'RADDRS': 'remote_addr',
            'HBINT': 'hrtbt_intrvl',
            'INS': 'max_instream',
            'OUTS': 'max_outstream',
            'MAXRT': 'max_retrans_atmpt',
            'T1X': 'init_chunks_send',
            'T2X': 'shutdown_chunks_send',
            'RTXC': 'data_chunks_retrans',
            '<->': 'relation'
        }

        self.data = []
        exp_column = ASC_COLUMN_IDX.keys()
        self._sctp_local_ports = set([])
        self._sctp_remote_ports = set([])
        self._sctp_local_ips = set([])
        self._sctp_remote_ips = set([])
        self._sctp_eps_ips = {}

        def remove_ip_addr(ip_list, line):
            for ip_addr in ip_list:
                if ip_addr in line:
                    line.remove(ip_addr)
            return line

        for line in content:
            row = {}
            remote = False
            line = line.strip()
            line = line.split()
            if ("LPORT" in line):
                # Making sure that the columns supported by parser are not depricated.
                if len(line) == len(exp_column):
                    columns = line
                    # Remove column names which create inconsistency in the number of columns and
                    # number of data items in the row.
                    for key, val in enumerate(['LADDRS', '<->', 'RADDRS']):
                        columns.remove(val)
                else:
                    raise ParseException("Contents are not compatible to this parser".format(row))
            else:
                row['remote_addr'] = []
                row['local_addr'] = []
                for idx, val in enumerate(line):
                    if val == '<->':
                        # Remote ip addresses starts here.
                        remote = True
                    # Get IPv4 or IPv6 Ip addrs
                    if '.' in val or ':' in val:
                        if remote:
                            row['remote_addr'].append(val)
                            self._sctp_remote_ips.add(val)
                        else:
                            row['local_addr'].append(val)
                            self._sctp_local_ips.add(val)

                # Remove inconsistent entries from the row
                line = remove_ip_addr(self._sctp_local_ips, line)
                line = remove_ip_addr(self._sctp_remote_ips, line)
                line.remove('<->')
                for idx, val in enumerate(columns):
                    key = ASC_COLUMN_IDX[val]
                    row[key] = line[idx]
                    if key == 'local_port':
                        self._sctp_local_ports.add(line[idx])
                    if key == 'remote_port':
                        self._sctp_remote_ports.add(line[idx])
                self.data.append(row)

    @property
    def sctp_local_ports(self):
        """
        (list): This function returns a list of SCTP local peer ports
                if SCTP endpoints are created, else `[]`.
        """
        return list(self._sctp_local_ports)

    @property
    def sctp_remote_ports(self):
        """
        (list): This function returns a list of SCTP remote peer ports
                if SCTP endpoints are created, else `[]`.
        """
        return list(self._sctp_remote_ports)

    @property
    def sctp_local_ips(self):
        """
        (list): This function returns a list of all local peer's ip addresses
                if SCTP endpoints are created, else `[]`.
        """
        return list(self._sctp_local_ips)

    @property
    def sctp_remote_ips(self):
        """
        (list): This function returns a list of all remote peer's ip addresses
                if SCTP endpoints are created, else `[]`.
        """
        return list(self._sctp_remote_ips)

    def search(self, **args):
        """
        (list): This function return a list of all SCTP associations when args search matches,
                when args search do not match then it returns `[]`.
        """
        return keyword_search(self.data, **args)
