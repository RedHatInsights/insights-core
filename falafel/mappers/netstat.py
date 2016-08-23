from falafel.core.plugins import mapper
from falafel.util import parse_table
from collections import defaultdict
from falafel.core import MapperOutput, computed
from falafel.mappers import get_active_lines
import re


class NetstatParserException(Exception):
    pass


@mapper('netstat-s')
def get_netstat_s(context):
    '''
    Return a dict nested dicts, and each key consist of lower case letters and
    "_". For example:

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
    info = dict()
    session = None
    first_layer = dict()
    second_layer = dict()
    has_scd_layer = False

    # There maybe some error metadata, such as:
    # 'cannot open /proc/net/snmp: No such file or directory'
    # or  '/bin/sh: /bin/netstat: No such file or directory'
    # In this situation, return {} directly.
    if 'cannot open' in context.content[0] or 'bin' in context.content[0]:
        return info

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
    # In this situation, 'error...' line will be ignore.
    for line in context.content:
        if session:
            if line.startswith("  "):
                if ":" in line:
                    key, val = line.split(":")
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
                        second_layer = dict()
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
                    second_layer = dict()
                info[session] = first_layer
                first_layer = dict()
                session = None
        if not session:
            session = line.split(":")[0].lower()
            if session.startswith('error'):
                session = None

    # Assign to the last seesion
    info[session] = first_layer
    return info


class NetstatAGNDevice(MapperOutput):
    def groupByIface(self):
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
        return result


@mapper("netstat_-agn")
def get_netstat_agn(context):
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
    content = context.content[1:2] + context.content[3:]
    table = parse_table(content)
    result = map(lambda item: {k.lower(): v for (k, v) in item.iteritems()}, table)
    return NetstatAGNDevice(result)

ACTIVE_INTERNET_CONNECTIONS = 'Active Internet connections (servers and established)'
ACTIVE_UNIX_DOMAIN_SOCKETS = 'Active UNIX domain sockets (servers and established)'
NETSTAT_SECTION_ID = {
    ACTIVE_INTERNET_CONNECTIONS: ['Proto', 'Recv-Q', 'Send-Q', 'Local Address', 'Foreign Address', 'State', 'User', 'Inode', 'PID/Program name', 'Timer'],
    ACTIVE_UNIX_DOMAIN_SOCKETS: ['RefCnt', 'Flags', 'Type', 'State', 'I-Node', 'PID/Program name', 'Path']
}

HTTPD_REGEX = re.compile(r'/httpd($|\s+)')


class NetstatSection:

    def __init__(self, name):
        self.name = name.strip()
        if self.name not in NETSTAT_SECTION_ID:
            raise NetstatParserException("Unknown netstat section : " + name)
        self.meta = NETSTAT_SECTION_ID[self.name]
        self.data = defaultdict(list)
        for m in self.meta:
            self.data[m] = []

    def addMetaData(self, line):
        try:
            data = []

            meta = {}

            for m in NETSTAT_SECTION_ID[self.name]:
                meta[line.index(m)] = m
                data.append([])

            self.indexes = sorted(meta.keys())
            self.data = data
            self.meta = meta

        except Exception, e:
            raise NetstatParserException("Cannot parse meta data: " + line, e)

    def addData(self, line):
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


@mapper("netstat")
class Netstat(MapperOutput):

    @staticmethod
    def parse_content(content):
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

        sections = []
        cur_section = None
        is_meta_data = False
        num_active_lines = 0
        for line in get_active_lines(content):
            num_active_lines += 1
            if line in NETSTAT_SECTION_ID:

                # this is a new section
                cur_section = NetstatSection(line)
                sections.append(cur_section)
                is_meta_data = True
                continue

            if is_meta_data:
                cur_section.addMetaData(line)
                is_meta_data = False
            else:
                cur_section.addData(line)

        if not sections:
            if num_active_lines < 1:
                raise NetstatParserException("Input content is empty")
            else:
                raise NetstatParserException("Input content is not empty but there is no useful parsed data")

        section_map = {}
        for s in sections:
            s._merge_data_index()
            section_map[s.name] = s.data

        return section_map

    @computed
    def is_httpd_running(self):
        if ACTIVE_INTERNET_CONNECTIONS in self.data:
            for pid in self.data[ACTIVE_INTERNET_CONNECTIONS]['PID/Program name']:
                if HTTPD_REGEX.search(pid):
                    return True
