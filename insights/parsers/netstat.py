"""
netstat and ss - Commands
=========================

Shared mappers for parsing and extracting data from variations of the
``netstat`` and ``ss`` commands.  Mappers contained in this module are:

NetstatS - command ``netstat -s``
---------------------------------

NetstatAGN - command ``netstat -agn``
-------------------------------------

Netstat - command ``netstat -neopa``
------------------------------------

Netstat_I - command ``netstat -i``
----------------------------------

SsTULPN - command ``ss -tulpn``
-------------------------------

"""

from collections import defaultdict
from . import ParseException, parse_delimited_table
from .. import Parser, parser, LegacyItemAccess


ACTIVE_INTERNET_CONNECTIONS = 'Active Internet connections (servers and established)'
"str: The key in Netstat data to internet connection information"
ACTIVE_UNIX_DOMAIN_SOCKETS = 'Active UNIX domain sockets (servers and established)'
"str: The key in Netstat data  UNIX domain socket information"
NETSTAT_SECTION_ID = {
    ACTIVE_INTERNET_CONNECTIONS: ['Proto', 'Recv-Q', 'Send-Q', 'Local Address', 'Foreign Address', 'State', 'User', 'Inode', 'PID/Program name', 'Timer'],
    ACTIVE_UNIX_DOMAIN_SOCKETS: ['RefCnt', 'Flags', 'Type', 'State', 'I-Node', 'PID/Program name', 'Path']
}

NETSTAT_TEXT_RIGHT_ALIGNMENT = {
    ACTIVE_INTERNET_CONNECTIONS: ['Recv-Q', 'Send-Q']
}
COMPONENT_LEN = "__component_len__"


@parser('netstat-s')
class NetstatS(LegacyItemAccess, Parser):
    """
    Parses data from the ```netstat -s``` command.

    The output of the ```netstat -s``` command looks like:
        >>> content = '''
        ... Ip:
        ...     3405107 total packets received
        ...     0 forwarded
        ...     0 incoming packets discarded
        ...     2900146 incoming packets delivered
        ...     2886201 requests sent out
        ...     456 outgoing packets dropped
        ...     4 fragments received ok
        ...     8 fragments created
        ... Icmp:
        ...     114 ICMP messages received
        ...     0 input ICMP message failed.
        ...     ICMP input histogram:
        ...         destination unreachable: 107
        ...         echo requests: 4
        ...         echo replies: 3
        ...     261 ICMP messages sent
        ...     0 ICMP messages failed
        ...     ICMP output histogram:
        ...         destination unreachable: 254
        ...         echo request: 3
        ...         echo replies: 4
        ... IcmpMsg:
        ...         InType0: 3
        ...         InType3: 107
        ...         InType8: 4
        ...         OutType0: 4
        ...         OutType3: 254
        ...         OutType8: 3
        ... Tcp:
        ...     1648 active connections openings
        ...     1525 passive connection openings
        ...     105 failed connection attempts
        ...     69 connection resets received
        ...     139 connections established
        ...     2886370 segments received
        ...     2890303 segments send out
        ...     428 segments retransmited
        ...     0 bad segments received.
        ...     212 resets sent
        ... Udp:
        ...     4901 packets received
        ...     107 packets to unknown port received.
        ...     0 packet receive errors
        ...     1793 packets sent
        ...     0 receive buffer errors
        ...     0 send buffer errors
        ... '''

    Return a dictionary of nested dictionaries, and each key consist of
    lower case letters and "_". For example:

    >>> content =
    ... {
    ... "ip": {
    ...     "forwarded": "0",
    ...     "fragments_received_ok": "4",
    ...     "requests_sent_out": "2886201",
    ...     "total_packets_received": "3405107",
    ...     "fragments_created": "8",
    ...     "incoming_packets_delivered": "2900146",
    ...     "outgoing_packets_dropped": "456",
    ...     "incoming_packets_discarded": "0"
    ... }
    ...  "icmp": {
    ...     "input_icmp_message_failed.": "0",
    ...     "icmp_messages_failed": "0",
    ...     "icmp_output_histogram": {
    ...         "echo_request": "3",
    ...         "destination_unreachable": "254",
    ...         "echo_replies": "4"
    ...     },
    ...     "icmp_messages_sent": "261",
    ...     "icmp_input_histogram": {
    ...         "echo_requests": "4",
    ...         "destination_unreachable": "107",
    ...         "echo_replies": "3"
    ...     },
    ...     "icmp_messages_received": "114"
    ... }
    ... ......
    ... }
    """
    def parse_content(self, content):
        self.data = {}
        session = None
        first_layer = {}
        second_layer = {}
        has_scd_layer = False

        # There maybe some error metadata, such as:
        # 'cannot open /proc/net/snmp: No such file or directory'
        # or  '/bin/sh: /bin/netstat: No such file or directory'
        if len(content) == 1:
            raise ParseException("Corrupt netstat -s file: {0}".format(content[0]))

        # The right metadata(content) will start with "Ip". Some metadata may start
        # with 'error' or 'ERROR' and the rest of lines are right datas.For example:
        # ~~~~~~~
        # error parsing /proc/net/netstat: No such file or directory
        # Ip:
        #   515 total packets received
        #   5 with invalid addresses
        #   0 forwarded
        # .....
        # ~~~~~~~~
        # In this situation, 'error...' line will be ignored.
        for line in content:
            if session:
                if line.startswith("  "):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key = key.strip().replace(" ", "_").lower()
                        # For example:
                        # ~~~~~~~
                        # ICMP input histogram:
                        #        echo requests: 309
                        # ...
                        # ~~~~~~~
                        # There need second layer dict
                        if val == "" and not has_scd_layer:
                            has_scd_layer = True
                            layer_key = key
                        else:
                            if has_scd_layer:
                                second_layer[key] = val.strip().lower()
                            else:
                                first_layer[key] = val.strip().lower()
                    else:
                        # To deal with lines look like:
                        # 0 bad segments received.
                        if has_scd_layer:
                            first_layer[layer_key] = second_layer
                            has_scd_layer = False
                            second_layer = {}
                        data = line.split()

                        # Some line's end has a '.', it'll be removed
                        tmp_data = data[-1]
                        if tmp_data[-1] == ".":
                            data[-1] = tmp_data[:-1]
                        for d in data:
                            if d.isdigit():
                                val = d
                                break
                        else:
                            # Line contained no number, ignore
                            continue
                        data.remove(val)
                        key = "_".join([k.lower() for k in data])
                        first_layer[key] = val
                else:
                    if has_scd_layer:
                        first_layer[layer_key] = second_layer
                        has_scd_layer = False
                        second_layer = {}
                    self.data[session] = first_layer
                    first_layer = {}
                    session = None
            if not session:
                session = line.split(":")[0].lower()
                if session.startswith('error'):
                    session = None

        # Assign to the last seesion
        self.data[session] = first_layer


@parser("netstat_-agn")
class NetstatAGN(Parser):
    """
    Parse netstat -agn to get interface multicast infomation.

    INPUT:
        >>> content= '''
        ... IPv6/IPv4 Group Memberships
        ... Interface       RefCnt Group
        ... --------------- ------ ---------------------
        ... lo              1      224.0.0.1
        ... eth0            1      224.0.0.1
        ... lo              3      ff02::1
        ... eth0            4      ff02::1
        ... eth0            1      ff01::1
        ... '''

    OUTPUT a class named NetstatAGNDevice. The data property like this:
        >>> content= '''
        ... [
        ...    {"interface":"lo", "refcnt":"1", "group":"224.0.0.1"},
        ...    {"interface":"eth0", "refcnt":"1", "group":"224.0.0.1"},
        ...    {"interface":"lo", "refcnt":"3", "group":"ff02::1"},
        ...    {"interface":"eth0", "refcnt":"4", "group":"ff02::1"},
        ...    {"interface":"eth0", "refcnt":"1", "group":"ff01::1"},
        ... ]
        ... '''
    """

    def group_by_iface(self):
        """
        Group Netstat AGN data by Iface name, return like this:
            >>> content= '''
            ... {
            ...     "lo":[
            ...         {"refcnt":"1", "group":"224.0.0.1"},
            ...         {"refcnt":"1", "group":"ff02::1"}
            ...     ]
            ... }
            ... '''
        """
        result = defaultdict(list)
        for entry in self.data:
            result[entry["interface"]].append(dict((k.lower(), v) for (k, v) in entry.iteritems() if k in ["refcnt", "group"]))
        return dict(result)

    def parse_content(self, content):
        # Skip 'IPv6/IPv6 Group Memberships' and '-----' lines.
        content = content[1:2] + content[3:]
        table = parse_delimited_table(content)
        self.data = map(lambda item: dict((k.lower(), v) for (k, v) in item.iteritems()), table)


class NetstatSection(object):

    def __init__(self, name):
        self.name = name.strip()
        assert self.name in NETSTAT_SECTION_ID
        self.meta = NETSTAT_SECTION_ID[self.name]
        self.data = {}
        for m in self.meta:
            self.data[m] = []
        self.datalist = []
        self.lines = []

    def add_meta_data(self, line):
        data = []
        meta = {}

        for m in NETSTAT_SECTION_ID[self.name]:
            if m not in line:
                raise ParseException("Did not find '{h}' heading in header".format(h=m))
            meta[line.index(m)] = m
            data.append([])

        self.indexes = sorted(meta.keys())
        self.data = data
        self.meta = meta

    def add_data(self, line):
        self.lines.append(line)
        indexes = self.indexes

        i = 1
        from_index = 0
        while i < len(indexes):
            self.data[i - 1].append(line[from_index: indexes[i]].strip())
            from_index = indexes[i]
            i += 1
        self.data[i - 1].append(line[indexes[i - 1]:])

        self.datalist.append(dict((m, d) for m, d in zip(
            NETSTAT_SECTION_ID[self.name], [r[-1] for r in self.data]
        )))
        # For convenience, unpack 'PID/Program name' into 'PID' and 'Program name'
        # This field must exist because of NETSTAT_SECTION_ID and the
        # exception in add_meta_data
        pidprogram = self.datalist[-1]['PID/Program name']
        if '/' in pidprogram:
            pid, program = pidprogram.split('/')
            self.datalist[-1]['PID'] = pid
            self.datalist[-1]['Program name'] = program
        # For convenience, unpack 'Local Address' into 'Local IP' and 'Port'
        if 'Local Address' in self.datalist[-1]:
            local_addr = self.datalist[-1]['Local Address']
            if ':' not in local_addr:
                raise ParseException('Local Address is expected to have a colon separating address and port')
            # Remember, IPv6 addresses have colons in them.  The port
            # is the last part.
            parts = local_addr.split(':')
            self.datalist[-1]['Local IP'] = ':'.join(parts[:-1])
            self.datalist[-1]['Port'] = parts[-1]
        # Unix socket information doesn't have Local Address.

    def _merge_data_index(self):
        merged_data = {}
        component_len = {}
        for i, index in enumerate(self.indexes):
            m = self.meta[index]
            merged_data[m] = self.data[i]
            component_len[m] = self.indexes[i + 1] - self.indexes[i] if i != len(self.indexes) - 1 else None

        self.data = merged_data
        self.data[COMPONENT_LEN] = component_len

        del self.indexes
        del self.meta
        return self.data


@parser("netstat")
class Netstat(Parser):
    """
    Parsing netstat command content and return

    For the input content:
        >>> content = '''
        ... Active Internet connections (servers and established)
        ... Proto Recv-Q Send-Q Local Address           Foreign Address         State       User       Inode      PID/Program name     Timer
        ... tcp        0      0 0.0.0.0:5672            0.0.0.0:*               LISTEN      996        19422      1279/qpidd           off (0.00/0/0)
        ... tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      184        20380      2007/mongod          off (0.00/0/0)
        ... tcp        0      0 127.0.0.1:53644         0.0.0.0:*               LISTEN      995        1154674    12387/Passenger Rac  off (0.00/0/0)
        ... tcp        0      0 0.0.0.0:5646            0.0.0.0:*               LISTEN      991        20182      1272/qdrouterd       off (0.00/0/0)
        ... Active UNIX domain sockets (servers and established)
        ... Proto RefCnt Flags       Type       State         I-Node   PID/Program name     Path
        ... unix  2      [ ]         DGRAM                    11776    1/systemd            /run/systemd/shutdownd
        ... unix  2      [ ACC ]     STREAM     LISTENING     535      1/systemd            /run/lvm/lvmetad.socket
        ... unix  2      [ ACC ]     STREAM     LISTENING     16411    738/NetworkManager   /var/run/NetworkManager/private
        ... '''

    The following attributes are all keyed on the header as it appears
    complete in the input - e.g. active connections are stored by the key
    'Active Internet connections (servers and established)'.  For convenience,
    these two keys are stored in this module under the constant names:

        * ACTIVE_INTERNET_CONNECTIONS
        * ACTIVE_UNIX_DOMAIN_SOCKETS

    Access to the data in this class is using the following attributes:

    Attributes:
        data(dict): Keyed as above, each item is a dictionary of lists,
            corresponding to a column and row lookup from the table data.
            For example, the first line's State is ['State'][0]
        datalist(dict): Keyed as above, each item is a list of dictionaries
            corresponding to a row and column lookup from the table.
            For example, the first line's State is [0]['State']
        lines(dict): Keyed as above, each item is a list of the original
            line of data from the input, in the same order that the data
            appears in the ``datalist`` attribute's list.

    The keys in the ``data`` dictionary and each element of the ``datalist``
    lists are the same as the headers in the table (e.g. ``Proto``,
    ``Recv-Q``, etc for 'Active Internet connections (servers and
    established)' and ``Proto``, ``RefCnt``, ``Flags``, etc. for 'Active UNIX
    domain sockets (servers and established)').  The ``datalist`` row
    dictionaries also have the following keys:

    * ``Local IP`` - (for internet connections) the address portion of the
      'Local Address' field.
    * ``Port`` - (for internet connections) the port portion of the 'Local
      Address' field.
    * ``PID`` - the process ID from the 'PID/Program name' field.
    * ``Program name`` - the process ID from the 'PID/Program name' field.

    Examples:
        >>> from insights.mappers import netstat
        >>> ns = netstat.Netstat(context_wrap(content))
        >>> ns.data[netstat.ACTIVE_INTERNET_CONNECTIONS]['Local Address'][1]
        '127.0.0.1:27017'  # access by column then row
        >>> ns.lines[netstat.ACTIVE_INTERNET_CONNECTIONS][1]  # original line
        'tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      184        20380      2007/mongod          off (0.00/0/0)'
        >>> nsdl = ns.datalist[netstat.ACTIVE_INTERNET_CONNECTIONS]
        >>> nsdl[1]['Local Address']  # access by row then column
        '127.0.0.1:27017'
        >>> nsdl[1]['PID']  # convenience split of 'PID/Program name' column
        '2007'  # - note string
        >>> nsdl[1]['Port']  # convenience split of 'Local address' column
        '27017'
    """

    def parse_content(self, content):
        if not content:
            raise ParseException("Input content is empty")

        if len(content) < 3:
            raise ParseException("Input content is not empty but there is no useful parsed data")

        sections = []
        cur_section = None
        is_meta_data = False
        for line in content:
            if line in NETSTAT_SECTION_ID:

                # this is a new section
                cur_section = NetstatSection(line)
                sections.append(cur_section)
                is_meta_data = True
                continue

            if cur_section:
                if is_meta_data:
                    cur_section.add_meta_data(line)
                    is_meta_data = False
                else:
                    cur_section.add_data(line)

        if not sections:
            raise ParseException("Found no section headers in content")

        self.data = dict((s.name, s._merge_data_index()) for s in sections)
        self.lines = dict((s.name, s.lines) for s in sections)
        self.datalist = dict((s.name, s.datalist) for s in sections)

    @property
    def running_processes(self):
        """
        List all the running processes given in the netstat output.

        Returns:
            set: set of process names (with spaces, as given in netstat output)
        """

        # Is it possible to have a machine that has no active connections?
        if ACTIVE_INTERNET_CONNECTIONS not in self.data:
            return set()
        return set(
            pg.split('/', 1)[1].strip()
            for pg in self.data[ACTIVE_INTERNET_CONNECTIONS]['PID/Program name']
            if '/' in pg
        )

    @property
    def listening_pid(self):
        """
            Find PIDs of all LISTEN processes

            Returns:
                dict: If any are found, they are returned in a dictionary
                following the format::

                    {'pid': ("addr": ip_address, 'port': port, 'name': process_name)}
        """
        pids = {}
        # Is it possible to have a machine that has no active connections?
        if ACTIVE_INTERNET_CONNECTIONS not in self.datalist:
            return pids
        connlist = self.datalist[ACTIVE_INTERNET_CONNECTIONS]
        for line in connlist:
            if line['State'] != 'LISTEN':
                continue
            if not (':' in line['Local Address'] and '/' in line['PID/Program name']):
                continue
            addr, port = line['Local Address'].strip().split(":", 1)
            pid, name = line['PID/Program name'].strip().split('/', 1)
            pids[pid] = {'addr': addr, 'port': port, 'name': name}
        return pids

    def get_original_line(self, section_id, index):
        """
        Get the original netstat line that is stripped white spaces
        """
        if section_id not in self.data:
            return
        return self.lines[section_id][index]

    def rows_by(self, section_id, search_dict):
        """
        Find all the rows in datalist where the data is the same as the search
        dictionary.  This operates as a kind of free-form search utility
        function - for example::

            ns.rows_by(
                netstat.ACTIVE_INTERNET_CONNECTIONS,
                {'State': 'LISTEN', 'Port': '5672'}
            )

        Would list all rows where the socket state was LISTEN and the local
        port was '5672'.

        Returns:

            list: A list of rows in the same dictionaries given in the
            ``datalist`` property, with an extra key '``raw line``' set to
            the original line of input that produced this row.
        """
        results = []
        if search_dict == {}:
            return results
        for line, row in enumerate(self.datalist[section_id]):
            if all([key in row and row[key] == value for key, value in search_dict.iteritems()]):
                copy = dict(row)
                copy['raw line'] = self.lines[section_id][line]
                results.append(copy)
        return results


@parser("netstat-i")
class Netstat_I(Parser):
    """
    Parse netstat -i to get interface traffic info such as "TX-OK" and "RX-OK".

    INPUT:
        >>> content = '''
        ... Kernel Interface table
        ... Iface       MTU Met    RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP TX-OVR Flg
        ... bond0      1500   0   845265      0      0      0     1753      0      0      0 BMmRU
        ... bond1      1500   0   842447      0      0      0     4233      0      0      0 BMmRU
        ... eth0       1500   0   422518      0      0      0     1703      0      0      0 BMsRU
        ... eth1       1500   0   422747      0      0      0       50      0      0      0 BMsRU
        ... eth2       1500   0   421192      0      0      0     3674      0      0      0 BMsRU
        ... eth3       1500   0   421255      0      0      0      559      0      0      0 BMsRU
        ... lo        65536   0        0      0      0      0        0      0      0      0 LRU
        ... '''

    Group Netstat_I data by Iface name, output like:
        >>> content = '''
        ... {
        ...     "bond0": {
        ...         "MTU": "1500", "Met": "0", "RX-OK": "845265", "RX-ERR": "0",
        ...         "RX-DRP": "0", "RX-OVR": "0", "TX-OK": "1753", "TX-ERR": "0",
        ...         "TX-DPR": "0", "TX-OVR": "0", "Flg": "BMmRU"},
        ...     },
        ...     "eth0": {
        ...         "MTU": "1500", "Met": "0", "RX-OK": "422518", "RX-ERR": "0",
        ...         "RX-DRP": "0", "RX-OVR": "0", "TX-OK": "1703", "TX-ERR": "0",
        ...         "TX-DPR": "0", "TX-OVR": "0", "Flg": "BMmRU"}
        ...     }
        ... }
        ... '''
    """

    @property
    def group_by_iface(self):
        return self._group_by_iface

    def parse_content(self, content):
        self._group_by_iface = {}
        # heading_ignore is first line we _don't_ want to ignore...
        table = parse_delimited_table(content, heading_ignore=['Iface'])
        self.data = map(lambda item:
                        dict((k, v) for (k, v) in item.iteritems()), table)
        for entry in self.data:
            self._group_by_iface[entry["Iface"]] = \
                dict((k, v) for (k, v) in entry.iteritems() if k != 'Iface')
        return


@parser("ss")
class SsTULPN(Parser):
    """
    This class parse the input as a table with header:
        "Netid  State  Recv-Q  Send-Q  Local-Address-Port Peer-Address-Port  Process"

    Sample input data looks like:
        COMMAND> ss -tulpn

        Netid  State      Recv-Q Send-Q Local Address:Port               Peer Address:Port
        udp    UNCONN     0      0         *:55898                 *:*
        udp    UNCONN     0      0      127.0.0.1:904                   *:*                   users:(("rpc.statd",pid=29559,fd=7))
        udp    UNCONN     0      0         *:111                   *:*                   users:(("rpcbind",pid=953,fd=9))
        udp    UNCONN     0      0        :::37968                :::12345                    users:(("rpc.statd",pid=29559,fd=10))

    This class parse the input as a table with header:
        "Netid  State  Recv-Q  Send-Q  Local-Address-Port Peer-Address-Port  Process"

    Examples:

        >>> ss = shared[SsTULPN]
        >>> ss.data[0]
        {'Netid': 'udp',
         'Peer-Address-Port': '*:*',
         'Send-Q': '0',
         'Local-Address-Port': '*:55898',
         'State': 'UNCONN',
         'Recv-Q': '0'}
        >>> ss.get_service("rpcbind")
        [{'Netid': 'udp',
          'Process': 'users:(("rpcbind",pid=953,fd=9))',
          'Peer-Address-Port': '*:*',
          'Send-Q': '0', 'Local-Address-Port': '*:111',
          'State': 'UNCONN',
          'Recv-Q': '0'}]
        >>> ss.get_port("55898")
        [{'Netid': 'udp',
         'Peer-Address-Port': '*:*',
         'Send-Q': '0',
         'Local-Address-Port': '*:55898',
         'State': 'UNCONN',
         'Recv-Q': '0'}]
    """

    def parse_content(self, content):
        SSTULPN_TABLE_HEADER = ["Netid  State  Recv-Q  Send-Q  Local-Address-Port Peer-Address-Port  Process"]
        self.data = parse_delimited_table(SSTULPN_TABLE_HEADER + content[1:])

    def get_service(self, service):
        return [l for l in self.data if l.get("Process", None) and service in l["Process"]]

    def get_localport(self, port):
        return [l for l in self.data if l.get("Local-Address-Port") and
                port in l["Local-Address-Port"]]

    def get_peerport(self, port):
        return [l for l in self.data if l.get("Peer-Address-Port") and
                port in l["Peer-Address-Port"]]

    def get_port(self, port):
        return self.get_localport(port) + self.get_peerport(port)
