"""
Netstat
=======

Shared mappers for parsing and extracting data from variations of the
```netstat``` command.
"""

from collections import defaultdict
from ..mappers import ParseException
from .. import Mapper, mapper, parse_table


ACTIVE_INTERNET_CONNECTIONS = 'Active Internet connections (servers and established)'
ACTIVE_UNIX_DOMAIN_SOCKETS = 'Active UNIX domain sockets (servers and established)'
NETSTAT_SECTION_ID = {
    ACTIVE_INTERNET_CONNECTIONS: ['Proto', 'Recv-Q', 'Send-Q', 'Local Address', 'Foreign Address', 'State', 'User', 'Inode', 'PID/Program name', 'Timer'],
    ACTIVE_UNIX_DOMAIN_SOCKETS: ['RefCnt', 'Flags', 'Type', 'State', 'I-Node', 'PID/Program name', 'Path']
}

NETSTAT_TEXT_RIGHT_ALLIGNMENT = {
    ACTIVE_INTERNET_CONNECTIONS: ['Recv-Q', 'Send-Q']
}
COMPONENT_LEN = "__component_len__"

ACTIVE_INTERNET_CONNECTIONS_LIST = ['Netid', 'State', 'Recv-Q', 'Send-Q', 'Local Address:Port', 'Peer Address:Port']


@mapper('netstat-s')
class NetstatS(Mapper):
    '''
    Parses data from the ```netstat -s``` command.

    The output of the ```netstat -s``` command looks like:

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

    Return a dictionary of nested dictionaries, and each key consist of
    lower case letters and "_". For example:

    {
        "ip": {
            "forwarded": "0",
            "fragments_received_ok": "4",
            "requests_sent_out": "2886201",
            "total_packets_received": "3405107",
            "fragments_created": "8",
            "incoming_packets_delivered": "2900146",
            "outgoing_packets_dropped": "456",
            "incoming_packets_discarded": "0"
        }
         "icmp": {
            "input_icmp_message_failed.": "0",
            "icmp_messages_failed": "0",
            "icmp_output_histogram": {
                "echo_request": "3",
                "destination_unreachable": "254",
                "echo_replies": "4"
            },
            "icmp_messages_sent": "261",
            "icmp_input_histogram": {
                "echo_requests": "4",
                "destination_unreachable": "107",
                "echo_replies": "3"
            },
            "icmp_messages_received": "114"
        }
        ......
    }
    '''
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
                            data.remove(tmp_data)
                            data.append(tmp_data[:-1])
                        for d in data:
                            if d.isdigit():
                                tmp = d
                                break
                        data.remove(tmp)
                        key, val = "_".join([k.lower() for k in data]), tmp
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


@mapper('netstat-s')
def get_netstat_s(context):
    '''
    Deprecated, use ```NetstatS``` instead.
    '''
    return NetstatS(context).data


@mapper("netstat_-agn")
class NetstatAGN(Mapper):
    """
    Parse netstat -agn to get interface multicast infomation.
    INPUT:
        IPv6/IPv4 Group Memberships
        Interface       RefCnt Group
        --------------- ------ ---------------------
        lo              1      224.0.0.1
        eth0            1      224.0.0.1
        lo              3      ff02::1
        eth0            4      ff02::1
        eth0            1      ff01::1

    OUTPUT:
    output a class named NetstatAGNDevice. The data property like this:
     [
        {"interface":"lo", "refcnt":"1", "group":"224.0.0.1"},
        {"interface":"eth0", "refcnt":"1", "group":"224.0.0.1"},
        {"interface":"lo", "refcnt":"3", "group":"ff02::1"},
        {"interface":"eth0", "refcnt":"4", "group":"ff02::1"},
        {"interface":"eth0", "refcnt":"1", "group":"ff01::1"},
     ]
    """

    def group_by_iface(self):
        """
            Group Netstat AGN data by Iface name.
            return like this:
            {
                "lo":[
                    {"refcnt":"1", "group":"224.0.0.1"},
                    {"refcnt":"1", "group":"ff02::1"}
                ]
            }

        """
        result = defaultdict(list)
        for entry in self.data:
            result[entry["interface"]].append({k.lower(): v for (k, v) in entry.iteritems() if k in ["refcnt", "group"]})
        return dict(result)

    def parse_content(self, content):
        content = content[1:2] + content[3:]
        table = parse_table(content)
        self.data = map(lambda item: {k.lower(): v for (k, v) in item.iteritems()}, table)


class NetstatSection(object):

    def __init__(self, name):
        self.name = name.strip()
        assert self.name in NETSTAT_SECTION_ID
        self.meta = NETSTAT_SECTION_ID[self.name]
        self.data = defaultdict(list)
        for m in self.meta:
            self.data[m] = []
        self.data = dict(self.data)

    def add_meta_data(self, line):
        data = []
        meta = {}

        for m in NETSTAT_SECTION_ID[self.name]:
            meta[line.index(m)] = m
            data.append([])

        self.indexes = sorted(meta.keys())
        self.data = data
        self.meta = meta

    def add_data(self, line):
        indexes = self.indexes

        i = 1
        from_index = 0
        while i < len(indexes):
            value = line[from_index: indexes[i]].strip()
            if not value:
                value = None

            self.data[i - 1].append(value)
            from_index = indexes[i]
            i += 1

        self.data[i - 1].append(line[indexes[i - 1]:])

    def _merge_data_index(self):
        merged_data = {}
        component_len = {}
        i = 0
        while i < len(self.indexes):
            index = self.indexes[i]
            m = self.meta[index]
            merged_data[m] = self.data[i]
            component_len[m] = self.indexes[i + 1] - self.indexes[i] if i != len(self.indexes) - 1 else None
            i += 1

        self.data = merged_data
        self.data[COMPONENT_LEN] = component_len

        del self.indexes
        del self.meta
        return self.data


@mapper("netstat")
class Netstat(Mapper):
    """
    Parsing netstat command content and return

    Examples:
        {
            'Active Internet connections (servers and established)': {
                'Proto': ['tcp', 'tcp', 'tcp', 'tcp'],
                'Recv-Q': ['0', '0', '0', '0'],
                ..
                'PID/Program name': ['1279/qpidd', '2007/mongod', '2387/Passenger Rac', '1272/qdrouterd']
            },

            'Active UNIX domain sockets (servers and established)': {
                'Proto': ['unix', 'unix', 'unix'],
                'RefCnt': ['2', '2', '2'],
                ...
                'PID/Program name': ['1/systemd', '1/systemd', '738/NetworkManager']
            }
        }
    For the input content:
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
    """

    def parse_content(self, content):
        if not content:
            raise ParseException("Input content is empty")

        if len(content) < 3:
            raise ParseException("Input content is not empty but there is no useful parsed data")

        sections = []
        cur_section = None
        is_meta_data = False
        num_active_lines = 0
        for line in content:
            num_active_lines += 1
            if line in NETSTAT_SECTION_ID:

                # this is a new section
                cur_section = NetstatSection(line)
                sections.append(cur_section)
                is_meta_data = True
                continue

            if is_meta_data:
                cur_section.add_meta_data(line)
                is_meta_data = False
            else:
                cur_section.add_data(line)

        if not sections:
            if num_active_lines < 1:
                raise ParseException("Input content is empty")
            else:
                raise ParseException("Input content is not empty but there is no useful parsed data")

        self.data = {s.name: s._merge_data_index() for s in sections}

    @property
    def running_processes(self):

        process_names = set()

        if ACTIVE_INTERNET_CONNECTIONS in self.data:
            for pg in self.data[ACTIVE_INTERNET_CONNECTIONS]['PID/Program name']:
                try:
                    if not pg:
                        continue

                    pid, name = pg.split("/", 1)
                    process_names.add(name.strip())
                except Exception:
                    pass

        return process_names

    @property
    def listening_pid(self):
        """
            Find PIDs of all LISTEN processes

            Returns:
                dict: If any are found, they are returned in a dictionary following the format:
                    [
                     {'pid': ("addr": 'ip_address', 'port', 'process_name')},
                     {'pid': ('ip_address', 'port', 'process_name)}
                    ]
        """
        pids = {}
        connections = self.data.get(ACTIVE_INTERNET_CONNECTIONS, {})
        for i, s in enumerate(connections.get('State', [])):
            try:
                if s.strip() == 'LISTEN':
                    addr, port = connections['Local Address'][i].strip().split(":", 1)
                    pid, name = connections['PID/Program name'][i].strip().split("/", 1)
                    pids[pid] = {"addr": addr, "port": port, "name": name}

            except Exception:
                # sometimes netstat provide "-" for empty value, so the parser will throw exception for those fields
                # just ignore it
                pass

        if pids:
            return pids

    def get_original_line(self, section_id, index):
        """
        Get the original netstat line that is stripped white spaces
        """
        if section_id not in self.data:
            return

        data = self.data[section_id]
        component_len = data[COMPONENT_LEN]

        line = ""
        for component_label in NETSTAT_SECTION_ID[section_id]:
            len = component_len[component_label]

            str = data[component_label][index] if data[component_label][index] else ""
            if len:
                if component_label in NETSTAT_TEXT_RIGHT_ALLIGNMENT[section_id]:
                    line += str.rjust(len - 1) + ' '
                else:
                    line += str.ljust(len)
            else:
                line += str

        return line.strip()


@mapper("netstat-i")
class Netstat_I(Mapper):
    """
    Parse netstat -i to get interface traffic info
    such as "TX-OK" and "RX-OK".

    INPUT:
        Kernel Interface table
        Iface       MTU Met    RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP TX-OVR Flg
        bond0      1500   0   845265      0      0      0     1753      0      0      0 BMmRU
        bond1      1500   0   842447      0      0      0     4233      0      0      0 BMmRU
        eth0       1500   0   422518      0      0      0     1703      0      0      0 BMsRU
        eth1       1500   0   422747      0      0      0       50      0      0      0 BMsRU
        eth2       1500   0   421192      0      0      0     3674      0      0      0 BMsRU
        eth3       1500   0   421255      0      0      0      559      0      0      0 BMsRU
        lo        65536   0        0      0      0      0        0      0      0      0 LRU

    OUTPUT:
        Group Netstat_I data by Iface name.
        return like this:
        {
            "bond0": {
                "MTU": "1500", "Met": "0", "RX-OK": "845265", "RX-ERR": "0",
                "RX-DRP": "0", "RX-OVR": "0", "TX-OK": "1753", "TX-ERR": "0",
                "TX-DPR": "0", "TX-OVR": "0", "Flg": "BMmRU"},
            },
            "eth0": {
                "MTU": "1500", "Met": "0", "RX-OK": "422518", "RX-ERR": "0",
                "RX-DRP": "0", "RX-OVR": "0", "TX-OK": "1703", "TX-ERR": "0",
                "TX-DPR": "0", "TX-OVR": "0", "Flg": "BMmRU"}
            }
        }
    """

    @property
    def group_by_iface(self):
        return self._group_by_iface

    def parse_content(self, content):
        self._group_by_iface = {}
        table = parse_table(content[1:])
        self.data = map(lambda item:
                        {k: v for (k, v) in item.iteritems()}, table)
        for entry in self.data:
            self._group_by_iface[entry["Iface"]] = \
                {k: v for (k, v) in entry.iteritems() if k != 'Iface'}
        return


class SsSection(NetstatSection):

    def __init__(self):
        self.meta = ACTIVE_INTERNET_CONNECTIONS_LIST
        self.data = defaultdict(list)
        for m in self.meta:
            self.data[m] = []
        self.data = dict(self.data)

    def add_meta_data(self, line):
        data = []
        meta = {}

        for m in self.meta:
            meta[line.index(m)] = m
            data.append([])
        meta[line.index(m) + len(m) + 2] = 'Process_info'
        data.append([])
        self.indexes = sorted(meta.keys())
        self.data = data
        self.meta = meta

    def _merge_data_index(self):
        merged_data = {}
        i = 0
        while i < len(self.indexes):
            index = self.indexes[i]
            m = self.meta[index]
            merged_data[m] = self.data[i]
            i += 1

        self.data = merged_data
        del self.indexes
        del self.meta
        return self.data


@mapper("ss")
class SsTULPN(Mapper):
    """
    INPUT:
        COMMAND> ss -tulpn

        Netid  State      Recv-Q Send-Q     Local Address:Port       Peer Address:Port
        tcp    LISTEN     0      10                    :::5671                 :::*      users:(("qpidd",10973,27))
        tcp    LISTEN     0      50                     *:5646                  *:*      users:(("qdrouterd",10991,6))
        tcp    UNCONN     0      0                    ::1:323                  :::*      users:(("chronyd",848,5))
        tcp    LISTEN     0      100                   :::8443                 :::*      users:(("java",11066,46))

    OUTPUT:
        return like this:
        {
            'Netid': ['tcp', 'tcp', 'tcp', 'tcp'],
            'State': ['LISTEN', 'LISTEN', 'UNCONN', 'LISTEN'],
            ...
            'Peer Address:Port': ['users:(("qpidd",10973,27))', 'users:(("qdrouterd",10991,6))', 'users:(("chronyd",848,5))', 'users:(("java",11066,46))']
        }
    """

    @property
    def listening_port(self):
        return self._listening_port

    def parse_content(self, content):
        self._listening_port = {}
        is_meta_data = False
        cur_section = SsSection()

        for line in content:
            if is_meta_data:
                cur_section.add_data(line)
                continue
            if "Netid" in line:
                cur_section.add_meta_data(line)
                is_meta_data = True
        self.data = cur_section._merge_data_index()
        for i, s in enumerate(self.data.get('State', [])):
            try:
                if s.strip() == 'LISTEN':
                    port = self.data['Local Address:Port'][i].strip().split(":")[-1]
                    if self.data['Local Address:Port'][i].strip().split(port)[0] != ':::':
                        addr = self.data['Local Address:Port'][i].strip().split(":")[0]
                    else:
                        addr = '::'
                    self._listening_port[port] = {"addr": addr, "port": port}

            except Exception:
                pass

        if self._listening_port:
            return self._listening_port

    def col(self, name):
        return [v.strip() for v in self.data[name]]
