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

SsTUPNA - command ``ss -tupna``
-------------------------------

ProcNsat - File ``/proc/net/netstat``
-------------------------------------
"""
from collections import defaultdict

from insights.core import CommandParser, LegacyItemAccess, Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsers import keyword_search, parse_delimited_table
from insights.specs import Specs


ACTIVE_INTERNET_CONNECTIONS = 'Active Internet connections (servers and established)'
"str: The key in Netstat data to internet connection information"
ACTIVE_UNIX_DOMAIN_SOCKETS = 'Active UNIX domain sockets (servers and established)'
"str: The key in Netstat data  UNIX domain socket information"
NETSTAT_SECTION_ID = {
    ACTIVE_INTERNET_CONNECTIONS: ['Proto', 'Recv-Q', 'Send-Q', 'Local Address', 'Foreign Address', 'State', 'User', 'Inode', 'PID/Program name', 'Timer'],
    ACTIVE_UNIX_DOMAIN_SOCKETS: ['RefCnt', 'Flags', 'Type', 'State', 'I-Node', 'PID/Program name', 'Path']
}


@parser(Specs.netstat_s)
class NetstatS(LegacyItemAccess, CommandParser):
    """
    Parses data from the ``netstat -s`` command.

    The output of the ``netstat -s`` command looks like::

        Ip:
            3405107 total packets received
            0 forwarded
            0 incoming packets discarded
            2900146 incoming packets delivered
            2886201 requests sent out
            456 outgoing packets dropped
            4 fragments received ok
            8 fragments created
        Icmp:
            114 ICMP messages received
            0 input ICMP message failed.
            ICMP input histogram:
                destination unreachable: 107
                echo requests: 4
                echo replies: 3
            261 ICMP messages sent
            0 ICMP messages failed
            ICMP output histogram:
                destination unreachable: 254
                echo request: 3
                echo replies: 4
        IcmpMsg:
                InType0: 3
                InType3: 107
                InType8: 4
                OutType0: 4
                OutType3: 254
                OutType8: 3
        Tcp:
            1648 active connections openings
            1525 passive connection openings
            105 failed connection attempts
            69 connection resets received
            139 connections established
            2886370 segments received
            2890303 segments send out
            428 segments retransmited
            0 bad segments received.
            212 resets sent
        Udp:
            4901 packets received
            107 packets to unknown port received.
            0 packet receive errors
            1793 packets sent
            0 receive buffer errors
            0 send buffer errors

    Examples:

        >>> type(stats)
        <class 'insights.parsers.netstat.NetstatS'>
        >>> sorted(stats.data.keys())  # Stored by heading, lower case
        ['icmp', 'icmpmsg', 'ip', 'ipext', 'tcp', 'tcpext', 'udp', 'udplite']
        >>> 'ip' in stats.data
        True
        >>> 'forwarded' in stats.data['ip']   # Then by keyword and value
        True
        >>> stats.data['ip']['forwarded']  # Values are strings
        '0'
        >>> stats['ip']['forwarded']  # Direct access via LegacyItemAccess
        '0'
        >>> stats['ip']['requests_sent_out']  # Spaces converted to underscores
        '2886201'
        >>> stats['tcp']['bad_segments_received']  # Dots are removed
        '0'
        >>> stats['icmp']['icmp_output_histogram']['destination_unreachable'] # Sub-table
        '254'

    """
    def parse_content(self, content):
        self.data = {}
        session = None
        first_layer = {}
        layer_key = ''
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
                        # To deal with lines that look like:
                        # '0 bad segments received.'
                        # or
                        # 'destination unreachable: 107'
                        # or
                        # 'Quick ack mode was activated 9 times'
                        if has_scd_layer:
                            first_layer[layer_key] = second_layer
                            has_scd_layer = False
                            second_layer = {}

                        # Some lines end with '.', trim that off
                        if line.endswith('.'):
                            line = line[:-1]

                        parts = line.split()

                        found_val = None
                        for val in parts:
                            if val.isdigit():
                                found_val = val
                                break
                        if found_val is not None:
                            key = '_'.join(k.lower() for k in parts if k != found_val)
                            first_layer[key] = found_val
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

        # Assign to the last session
        self.data[session] = first_layer


@parser(Specs.netstat_agn)
class NetstatAGN(CommandParser):
    """
    Parse the ``netstat -agn`` command to get interface multicast infomation.

    Sample command output::

        IPv6/IPv4 Group Memberships
        Interface       RefCnt Group
        --------------- ------ ---------------------
        lo              1      224.0.0.1
        eth0            1      224.0.0.1
        lo              3      ff02::1
        eth0            4      ff02::1
        eth0            1      ff01::1

    Examples:
        >>> type(multicast)
        <class 'insights.parsers.netstat.NetstatAGN'>
        >>> multicast.data[0]['interface']  # Access by row
        'lo'
        >>> multicast.data[0]['refcnt']  # Values are strings
        '1'
        >>> multicast.data[0]['group']  # Column names are lower case
        '224.0.0.1'
        >>> mc_ifs = multicast.group_by_iface()  # Lists by interface name
        >>> len(mc_ifs['lo'])
        2
        >>> mc_ifs['eth0'][1]['refcnt']  # Listed in order of appearance
        '4'

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
            result[entry["interface"]].append(dict((k.lower(), v) for (k, v) in entry.items() if k in ["refcnt", "group"]))
        return dict(result)

    def parse_content(self, content):
        # Skip 'IPv6/IPv6 Group Memberships' and '-----' lines.
        content = content[1:2] + content[3:]
        table = parse_delimited_table(content)
        self.data = [dict((k.lower(), v) for (k, v) in item.items()) for item in table]


class NetstatSection(object):

    def __init__(self, name):
        self.name = name.strip()
        if self.name not in NETSTAT_SECTION_ID:
            raise ParseException("The name '{name}' isn't a valid name.".format(name=self.name))

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
            pid, program = pidprogram.split('/', 1)
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
        for i, index in enumerate(self.indexes):
            m = self.meta[index]
            merged_data[m] = self.data[i]

        self.data = merged_data

        del self.indexes
        del self.meta
        return self.data


@parser(Specs.netstat)
class Netstat(CommandParser):
    """
    Parsing the ``/bin/netstat -neopa`` command output.

    Example output::

        Active Internet connections (servers and established)
        Proto Recv-Q Send-Q Local Address           Foreign Address         State       User       Inode      PID/Program name     Timer
        tcp        0      0 0.0.0.0:5672            0.0.0.0:*               LISTEN      996        19422      1279/qpidd           off (0.00/0/0)
        tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      184        20380      2007/mongod          off (0.00/0/0)
        tcp        0      0 127.0.0.1:53644         0.0.0.0:*               LISTEN      995        1154674    12387/Passenger Rac  off (0.00/0/0)
        tcp        0      0 0.0.0.0:5646            0.0.0.0:*               LISTEN      991        20182      1272/qdrouterd       off (0.00/0/0)
        Active UNIX domain sockets (servers and established)
        Proto RefCnt Flags       Type       State         I-Node   PID/Program name     Path
        unix  2      [ ]         DGRAM                    11776    1/systemd            /run/systemd/shutdownd
        unix  2      [ ACC ]     STREAM     LISTENING     535      1/systemd            /run/lvm/lvmetad.socket
        unix  2      [ ACC ]     STREAM     LISTENING     16411    738/NetworkManager   /var/run/NetworkManager/private

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
        >>> type(ns)
        <class 'insights.parsers.netstat.Netstat'>
        >>> sorted(ns.data.keys())  # Both tables stored in dictionary by name
        ['Active Internet connections (servers and established)', 'Active UNIX domain sockets (servers and established)']
        >>> intcons = 'Active Internet connections (servers and established)'
        >>> sorted(ns.data[intcons].keys())  # Data stored by column:
        ['Foreign Address', 'Inode', 'Local Address', 'PID/Program name', 'Proto', 'Recv-Q', 'Send-Q', 'State', 'Timer', 'User']
        >>> ns.data[intcons]['Local Address'][1]  # ... and then by row
        '127.0.0.1:27017'
        >>> ns.datalist[intcons][1]['Local Address']  # Data in a list by row then column
        '127.0.0.1:27017'
        >>> ns.lines[intcons][1]  # The raw line
        'tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      184        20380      2007/mongod          off (0.00/0/0)'
        >>> ns.get_original_line(intcons, 1)  # Alternative way of getting line
        'tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      184        20380      2007/mongod          off (0.00/0/0)'
        >>> 'qpidd' in ns.running_processes  # All running processes on internet ports
        True
        >>> 'systemd' in ns.running_processes  # Does not look at UNIX sockets
        False
        >>> pids = ns.listening_pid  # All PIDs listening on internet ports, with info
        >>> sorted(pids.keys())  # Note: keys are strings
        ['12387', '1272', '1279', '2007']
        >>> pids['12387']['addr']
        '127.0.0.1'
        >>> pids['12387']['port']
        '53644'
        >>> pids['12387']['name']
        'Passenger Rac'
        >>> datagrams = ns.search(Type='DGRAM')  # List of data row dictionaries
        >>> len(datagrams)
        1
        >>> datagrams[0]['RefCnt']
        'unix  2'
        >>> datagrams[0]['Flags']
        '[ ]'
        >>> datagrams[0]['Type']
        'DGRAM'
        >>> datagrams[0]['State']
        ''
        >>> datagrams[0]['I-Node']
        '11776'
        >>> datagrams[0]['PID/Program name']
        '1/systemd'
        >>> datagrams[0]['Path']
        '/run/systemd/shutdownd'
    """

    def parse_content(self, content):
        if not content:
            raise ParseException("Input content is empty")

        if len(content) < 3:
            raise ParseException("Input content is not empty but there is no useful parsed data.")

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
        List all the running processes given in the Active Internet
        Connections part of the netstat output.

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

    def search(self, **kwargs):
        """
        Search for rows in the data matching keywords in the search.

        This method searches both the active internet connections and
        active UNIX domain sockets.  If you only want to search one, specify
        the name via the ``search_list`` keyword, e.g.::

            from insights.parsers import Netstat, ACTIVE_UNIX_DOMAIN_SOCKETS
            conns.search(search_list=[ACTIVE_UNIX_DOMAIN_SOCKETS], State='LISTEN')

        The ``search_list`` can be either a list, or a string, containing
        one of the named constants defined in this module.  If
        ``search_list`` is not given, both the active internet connections
        and active UNIX domain sockets are searched, in that order.

        The results of the search are compiled into one list.  This allows
        you to search for all listening processes, whether for internet
        connections or UNIX sockets, by e.g.::

            conns.search(State__contains='LISTEN')

        This method uses the :py:func:`insights.parsers.keyword_search`
        function - see its documentation for a complete description of its
        keyword recognition capabilities.
        """
        if 'search_list' in kwargs:
            search_list = []
            if isinstance(kwargs['search_list'], list):
                # Compile a list from matching strings
                search_list = [
                    l
                    for l in kwargs['search_list']
                    if l in NETSTAT_SECTION_ID
                ]
            elif isinstance(kwargs['search_list'], str) and kwargs['search_list'] in NETSTAT_SECTION_ID:
                # Just use this string
                search_list = [kwargs['search_list']]
            del kwargs['search_list']
        else:
            search_list = [ACTIVE_INTERNET_CONNECTIONS, ACTIVE_UNIX_DOMAIN_SOCKETS]
        if not search_list:
            # No valid search list?  No items.
            return []

        found = []
        for l in search_list:
            found.extend(keyword_search(self.datalist[l], **kwargs))
        return found


@parser(Specs.netstat_i)
class Netstat_I(CommandParser):
    """
    Parse the ``netstat -i`` command output  to get interface traffic info
    such as "TX-OK" and "RX-OK".

    The output of `netstat -i` looks like::

        Kernel Interface table
        Iface       MTU Met    RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP TX-OVR Flg
        bond0      1500   0   845265      0      0      0     1753      0      0      0 BMmRU
        bond1      1500   0   842447      0      0      0     4233      0      0      0 BMmRU
        eth0       1500   0   422518      0      0      0     1703      0      0      0 BMsRU
        eth1       1500   0   422747      0      0      0       50      0      0      0 BMsRU
        eth2       1500   0   421192      0      0      0     3674      0      0      0 BMsRU
        eth3       1500   0   421255      0      0      0      559      0      0      0 BMsRU
        lo        65536   0        0      0      0      0        0      0      0      0 LRU

    Examples:
        >>> type(traf)
        <class 'insights.parsers.netstat.Netstat_I'>
        >>> traf.data[0]['Iface']  # A list of the interfaces and stats.
        'bond0'
        >>> 'bond0' in traf.group_by_iface  # A dictionary keyed on interface.
        True
        >>> 'enp0s25' in traf.group_by_iface
        False
        >>> 'MTU' in traf.group_by_iface['bond0']
        True
        >>> traf.group_by_iface['bond0']['MTU']  # as string
        '1500'
        >>> traf.group_by_iface['bond0']['RX-OK']
        '845265'
    """

    @property
    def group_by_iface(self):
        return self._group_by_iface

    def parse_content(self, content):
        self._group_by_iface = {}
        # heading_ignore is first line we _don't_ want to ignore...
        table = parse_delimited_table(content, heading_ignore=['Iface'])
        self.data = [dict((k, v) for (k, v) in item.items()) for item in table]
        for entry in self.data:
            self._group_by_iface[entry["Iface"]] = \
                dict((k, v) for (k, v) in entry.items() if k != 'Iface')
        return


@parser(Specs.ss)
class SsTULPN(CommandParser):
    """
    Parse the output of the ``/usr/sbin/ss -tulpn`` command.

    This class parse the input as a table with header:
        "Netid  State  Recv-Q  Send-Q  Local-Address-Port Peer-Address-Port  Process"

    Sample input data looks like::

        Netid  State      Recv-Q Send-Q Local Address:Port               Peer Address:Port
        udp    UNCONN     0      0                  *:55898                 *:*
        udp    UNCONN     0      0          127.0.0.1:904                   *:*                   users:(("rpc.statd",pid=29559,fd=7))
        udp    UNCONN     0      0                  *:111                   *:*                   users:(("rpcbind",pid=953,fd=9))
        udp    UNCONN     0      0                 :::37968                :::12345               users:(("rpc.statd",pid=29559,fd=10))
        tcp    LISTEN     0      128                *:111                   *:*                   users:(("rpcbind",pid=1139,fd=5),("systemd",pid=1,fd=41))

    Examples:

        >>> type(ss)
        <class 'insights.parsers.netstat.SsTULPN'>
        >>> sorted(ss.data[1].keys())  # Rows stored by column headings
        ['Local-Address-Port', 'Netid', 'Peer-Address-Port', 'Process', 'Recv-Q', 'Send-Q', 'State']
        >>> ss.data[0]['Local-Address-Port']
        '*:55898'
        >>> ss.data[0]['State']
        'UNCONN'
        >>> rpcbind = ss.get_service("rpcbind")  # All connections opened by rpcbind
        >>> len(rpcbind)
        2
        >>> rpcbind[0]['State']
        'UNCONN'
        >>> rpcbind[1]['State']
        'LISTEN'
        >>> rpcbind[0]['Process']
        'users:(("rpcbind",pid=953,fd=9))'
        >>> rpcbind[1]['Process']
        'users:(("rpcbind",pid=1139,fd=5),("systemd",pid=1,fd=41))'
        >>> using_55898 = ss.get_port("55898")  # Both local and peer port searched
        >>> len(using_55898)
        1
        >>> 'Process' in using_55898  # Not in dictionary if field not found
        False
        >>> rpcbind == ss.get_localport('111')  # Only local port or address searched
        True
    """

    def parse_content(self, content):
        # Use headings without spaces and colons
        SSTULPN_TABLE_HEADER = ["Netid  State  Recv-Q  Send-Q  Local-Address-Port Peer-Address-Port  Process"]
        content = [line for line in content if (('UNCONN' in line) or ('LISTEN' in line))]
        self.data = parse_delimited_table(SSTULPN_TABLE_HEADER + content)

    def get_service(self, service):
        return [l for l in self.data if l.get("Process", None) and service in l["Process"]]

    def get_localport(self, port):
        list_conn = []
        for line in self.data:
            local_port = line.get('Local-Address-Port')
            if local_port and ':*' not in local_port and\
                    int(port) == int(local_port.split(':')[-1]):
                list_conn.append(line)
        return list_conn

    def get_peerport(self, port):
        list_conn = []
        for line in self.data:
            peer_port = line.get('Peer-Address-Port')
            if peer_port and ':*' not in peer_port and\
                    int(port) == int(peer_port.split(':')[-1]):
                list_conn.append(line)
        return list_conn

    def get_port(self, port):
        return self.get_localport(port) + self.get_peerport(port)


@parser(Specs.ss)
class SsTUPNA(SsTULPN):
    """
    Parse the output of the ``/usr/sbin/ss -tupna`` command.

    This class parse the input as a table with header:
        "Netid  State  Recv-Q  Send-Q  Local-Address-Port Peer-Address-Port  Process"

    Sample input data looks like::

        Netid State      Recv-Q Send-Q    Local Address:Port    Peer Address:Port
        tcp   UNCONN     0      0                     *:68                 *:*      users:(("dhclient",1171,6))
        tcp   LISTEN     0      100           127.0.0.1:25                 *:*      users:(("master",1326,13))
        tcp   ESTAB      0      0         192.168.0.106:22     192.168.0.101:59232  users:(("sshd",11427,3))
        tcp   ESTAB      0      0         192.168.0.106:739    192.168.0.105:2049
        tcp   LISTEN     0      128                  :::111               :::*      users:(("rpcbind",483,11))

    Examples:

        >>> type(ssa)
        <class 'insights.parsers.netstat.SsTUPNA'>
        >>> sorted(ssa.data[2].items())
        [('Local-Address-Port', '192.168.0.106:22'), ('Netid', 'tcp'), ('Peer-Address-Port', '192.168.0.101:59232'), ('Process', 'users:(("sshd",11427,3))'), ('Recv-Q', '0'), ('Send-Q', '0'), ('State', 'ESTAB')]
        >>> sorted(ssa.get_service("sshd")[0].items())  # All connections opened by rpcbind
        [('Local-Address-Port', '192.168.0.106:22'), ('Netid', 'tcp'), ('Peer-Address-Port', '192.168.0.101:59232'), ('Process', 'users:(("sshd",11427,3))'), ('Recv-Q', '0'), ('Send-Q', '0'), ('State', 'ESTAB')]
        >>> sorted(ssa.get_port("2049")[0].items())  # Both local and peer port searched
        [('Local-Address-Port', '192.168.0.106:739'), ('Netid', 'tcp'), ('Peer-Address-Port', '192.168.0.105:2049'), ('Recv-Q', '0'), ('Send-Q', '0'), ('State', 'ESTAB')]
        >>> sorted(ssa.get_localport("739")[0].items())  # local port searched
        [('Local-Address-Port', '192.168.0.106:739'), ('Netid', 'tcp'), ('Peer-Address-Port', '192.168.0.105:2049'), ('Recv-Q', '0'), ('Send-Q', '0'), ('State', 'ESTAB')]
        >>> sorted(ssa.get_peerport("59232")[0].items())  # peer port searched
        [('Local-Address-Port', '192.168.0.106:22'), ('Netid', 'tcp'), ('Peer-Address-Port', '192.168.0.101:59232'), ('Process', 'users:(("sshd",11427,3))'), ('Recv-Q', '0'), ('Send-Q', '0'), ('State', 'ESTAB')]
    """

    def parse_content(self, content):
        # Use headings without spaces and colons
        SSTUPNA_TABLE_HEADER = ["Netid  State  Recv-Q  Send-Q  Local-Address-Port Peer-Address-Port  Process"]
        self.data = parse_delimited_table(SSTUPNA_TABLE_HEADER + content[1:])


@parser(Specs.proc_netstat)
class ProcNsat(Parser):
    """
    Parse the content of the ``/proc/net/netstat`` file

    Sample input data looks like::

        TcpExt: SyncookiesSent SyncookiesRecv SyncookiesFailed EmbryonicRsts PruneCalled RcvPruned OfoPruned OutOfWindowIcmps LockDroppedIcmps ArpFilter TW TWRecycled TWKilled PAWSPassive PAWSActive PAWSEstab DelayedACKs DelayedACKLocked DelayedACKLost ListenOverflows ListenDrops TCPPrequeued TCPDirectCopyFromBacklog TCPDirectCopyFromPrequeue TCPPrequeueDropped TCPHPHits TCPHPHitsToUser TCPPureAcks TCPHPAcks TCPRenoRecovery TCPSackRecovery TCPSACKReneging TCPFACKReorder TCPSACKReorder TCPRenoReorder TCPTSReorder TCPFullUndo TCPPartialUndo TCPDSACKUndo TCPLossUndo TCPLostRetransmit TCPRenoFailures TCPSackFailures TCPLossFailures TCPFastRetrans TCPForwardRetrans TCPSlowStartRetrans TCPTimeouts TCPLossProbes TCPLossProbeRecovery TCPRenoRecoveryFail TCPSackRecoveryFail TCPSchedulerFailed TCPRcvCollapsed TCPDSACKOldSent TCPDSACKOfoSent TCPDSACKRecv TCPDSACKOfoRecv TCPAbortOnData TCPAbortOnClose TCPAbortOnMemory TCPAbortOnTimeout TCPAbortOnLinger TCPAbortFailed TCPMemoryPressures TCPSACKDiscard TCPDSACKIgnoredOld TCPDSACKIgnoredNoUndo TCPSpuriousRTOs TCPMD5NotFound TCPMD5Unexpected TCPSackShifted TCPSackMerged TCPSackShiftFallback TCPBacklogDrop PFMemallocDrop TCPMinTTLDrop TCPDeferAcceptDrop IPReversePathFilter TCPTimeWaitOverflow TCPReqQFullDoCookies TCPReqQFullDrop TCPRetransFail TCPRcvCoalesce TCPOFOQueue TCPOFODrop TCPOFOMerge TCPChallengeACK TCPSYNChallenge TCPFastOpenActive TCPFastOpenActiveFail TCPFastOpenPassive TCPFastOpenPassiveFail TCPFastOpenListenOverflow TCPFastOpenCookieReqd TCPSpuriousRtxHostQueues BusyPollRxPackets TCPAutoCorking TCPFromZeroWindowAdv TCPToZeroWindowAdv TCPWantZeroWindowAdv TCPSynRetrans TCPOrigDataSent TCPHystartTrainDetect TCPHystartTrainCwnd TCPHystartDelayDetect TCPHystartDelayCwnd TCPACKSkippedSynRecv TCPACKSkippedPAWS TCPACKSkippedSeq TCPACKSkippedFinWait2 TCPACKSkippedTimeWait TCPACKSkippedChallenge TCPWqueueTooBig
        TcpExt: 10 20 30 40 0 0 0 0 0 0 8387793 2486 0 0 0 3 27599330 35876 309756 0 0 84351589 9652226708 54271044841 0 10507706759 112982361 177521295 3326559442 0 26212 0 36 33090 0 14345 959 8841 425 833 399 0 160 2 633809 11063 7056 233144 1060065 640242 0 228 54 0 310709 0 820887 112 900268 31664 0 232144 0 0 0 261 1048 808390 9 0 0 120433 244126 450077 0 0 0 5625 0 0 0 0 0 6772744900 19251701 0 0 465 463 0 0 0 0 0 0 1172 0 623074473 51282 51282 142025 465090 8484708872 836920 18212118 88 4344 0 0 5 4 3 2 1
        IpExt: InNoRoutes InTruncatedPkts InMcastPkts OutMcastPkts InBcastPkts OutBcastPkts InOctets OutOctets InMcastOctets OutMcastOctets InBcastOctets OutBcastOctets InCsumErrors InNoECTPkts InECT1Pkts InECT0Pkts InCEPkts ReasmOverlaps
        IpExt: 100 200 300 400 500 0 10468977960762 8092447661930 432 0 3062938 0 0 12512350267 400 300 200 100

    Examples:

        >>> type(pnstat)
        <class 'insights.parsers.netstat.ProcNsat'>
        >>> len(pnstat.data) == 132
        True
        >>> pnstat.get_stats('ReasmOverlaps')
        100
        >>> pnstat.get_stats('EmbryonicRsts')
        40
    """

    def parse_content(self, content):
        self.data = {}
        if not content:
            raise SkipComponent("No Contents")
        tcp_hdr = content[0].split()[1:]
        tcp_hdr_len = len(tcp_hdr)
        tcp_stat = content[1].split()[1:]
        tcp_stat_len = len(tcp_stat)
        ip_hdr = content[2].split()[1:]
        ip_hdr_len = len(ip_hdr)
        ip_stat = content[3].split()[1:]
        ip_stat_len = len(ip_stat)
        if (tcp_hdr_len != tcp_stat_len) or (ip_hdr_len != ip_stat_len):
            raise ParseException("Invalid Contents")
        if tcp_hdr and tcp_stat:
            self.data = dict(zip(tcp_hdr, tcp_stat))
        if ip_hdr and ip_stat:
            self.data.update(dict(zip(ip_hdr, ip_stat)))

    def get_stats(self, key_stats):
        """
        (int): The parser method will return the integer stats of the key if key is present in
               TcpExt or IpExt else it will return `None`.
        """
        if key_stats in self.data:
            return int(self.data.get(key_stats))
