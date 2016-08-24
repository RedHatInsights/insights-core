from falafel.core.plugins import mapper
from falafel.contrib import ipaddress
from falafel.core import computed, MapperOutput
from collections import defaultdict, deque


@mapper('ip_addr')
def addr(context):
    """
    QUICK START:
    `ip addr` will return a dict that key is interface name. `addr` key is a array to store all address.
    Different type have different output. Peer ip and general interface have difference type.
    There are some examples:
    CASE 1:
    1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
        link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
        inet 127.0.0.1/8 scope host lo
        inet6 ::1/128 scope host
        valid_lft forever preferred_lft forever
    RESULT:
    "lo": {
        "qdisc": "noqueue",
        "addr": [
            "127.0.0.1",
        ],
        "addr_v6":[
            "::1",
        ]
        "state": "UNKNOWN",
        "flag": [
            "LOOPBACK",
            "UP",
            "LOWER_UP"
        ],
        "mtu": 16436,
        "mac": "00:00:00:00:00:00",
        "type": "loopback"
    }
    CASE 2:
    2: eth7: <NO-CARRIER,BROADCAST,MULTICAST,SLAVE,UP> mtu 1500 qdisc mq master bond1 state DOWN qlen 1000
        link/ether 00:11:3f:e2:f5:9f brd ff:ff:ff:ff:ff:ff link-netnsid 1
    RESULT:
    "eth7": {
        "qlen": 1000,
        "qdisc": "mq",
        "addr": [ ],
        "addr_v6": [ ],
        "state": "DOWN",
        "mtu": 1500,
        "mac": "00:11:3f:e2:f5:9f",
        "flag": [
            "NO-CARRIER",
            "BROADCAST",
            "MULTICAST",
            "SLAVE",
            "UP"
        ],
        "master": "bond1",
        "type": "ether"
    }
    CASE 3:
    3: tunl0: <NOARP> mtu 1480 qdisc noop state DOWN
        link/ipip 0.0.0.0 brd 0.0.0.0
    RESULT:
    "tunl0": {
        "qdisc": "noop",
        "addr": [ ],
        "addr_v6", [ ],
        "state": "DOWN",
        "flag": [
            "NOARP"
        ],
        "mtu": 1480,
        "mac": "0.0.0.0",
        "type": "ipip"
    }
    CASE 4:
    4: tunl1: <NOARP> mtu 1480 qdisc noop state DOWN
        link/[65534]
        inet 172.30.0.1 peer 172.30.0.2/32 scope global tun0
    RESULT:
    "tunl1": {
        "qdisc": "noop",
        "addr": [
            "172.30.0.1"
        ],
        "addr_v6": [ ],
        "state": "DOWN",
        "mtu": 1480,
        "flag": [
            "NOARP"
        ],
        "type": "[65534]"
    }
    CASE 5:
    5: bond1.57@bond1: <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP
        link/ether 00:11:3f:e2:f5:9e brd ff:ff:ff:ff:ff:ff
        inet 10.192.4.171/27 brd 10.192.4.191 scope global bond1.57
        inet6 fe80::211:3fff:fee2:f59e/64 scope link
        valid_lft forever preferred_lft forever
        inet6 2001::211:3fff:fee2:f59e/64 scope global mngtmpaddr dynamic
        valid_lft 2592000sec preferred_lft 6480000sec
    RESULT:
    "bond1.57@bond1": {
        "qdisc": "noqueue",
        "addr": [
            "10.192.4.171",
        ],
        "addr_v6":[
            "fe80::211:3fff:fee2:f59e",
            "2001::211:3fff:fee2:f59e"
        ],
        "state": "UP",
        "flag": [
            "BROADCAST",
            "MULTICAST",
            "MASTER",
            "UP",
            "LOWER_UP"
        ],
        "mtu": 1500,
        "mac": "00:11:3f:e2:f5:9e",
        "type": "ether"
    }
        CASE 6:
    6: ip.tun2: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1480 qdisc noqueue state UNKNOWN
        link/ipip 10.192.4.203 peer 10.188.61.108
        inet 192.168.112.5 peer 192.168.122.6/32 scope global ip.tun2
    RESULT:
    "ip.tun2": {
        "qdisc": "noqueue",
        "addr": [
            "192.168.112.5"
        ],
        "addr_v6":[],
        "state": "UNKNOWN",
        "peer_ip": "10.192.4.203",
        "flag": [
            "POINTOPOINT",
            "NOARP",
            "UP",
            "LOWER_UP"
        ],
        "peer": "10.188.61.108",
        "mtu": 1480,
        "type": "ipip"
    }
    """
    r = {}
    iface_name = ""
    iface_pro = {}
    iface_addr_v4 = []
    iface_addr_v6 = []
    line = 0
    if len(context.content) == 0:
        return r
    while "Message truncated" == context.content[line].strip():
        line = line + 1
    for content in [l for l in context.content[line:] if l]:
        split_content = content.strip().split()
        if len(content) > 0 and content[0] != " ":  # Parse first line
            # save previous iface info
            if iface_name != "":
                iface_pro["addr"] = iface_addr_v4
                iface_pro["addr_v6"] = iface_addr_v6
                r[iface_name] = iface_pro
                iface_name = ""
                iface_pro = {}
                iface_addr_v4 = []
                iface_addr_v6 = []
            iface_name = content.split(":")[1].strip()
            iface_pro["flag"] = split_content[2].lstrip("<").rstrip(">").split(",")
            # extract property
            for i in range(3, len(split_content), 2):
                if split_content[i] in ["mtu", "qlen"] and "X" not in split_content[i + 1]:  # must be integer
                    iface_pro[split_content[i]] = int(split_content[i + 1])
                else:
                    iface_pro[split_content[i]] = split_content[i + 1]
        elif "link" in split_content[0]:  # parse "link/ether line"
            iface_pro["type"] = split_content[0].split("/")[1]
            if "peer" in content and len(split_content) >= 3:
                iface_pro["peer_ip"] = split_content[1]
                iface_pro["peer"] = split_content[3]
            elif len(split_content) >= 2:
                iface_pro["mac"] = split_content[1]
        elif "inet" in split_content[0]:
            ipinfo = split_content[1].split("/")[0]
            if "inet6" in split_content[0]:
                iface_addr_v6.append(ipinfo)
            else:
                iface_addr_v4.append(ipinfo)
    if iface_name != "":
        iface_pro["addr"] = iface_addr_v4
        iface_pro["addr_v6"] = iface_addr_v6
        r[iface_name] = iface_pro
    return r


class Route(MapperOutput):
    def __init__(self, data, path=None):
        super(Route, self).__init__(data, path)
        for k, v in self.data.iteritems():
            self._add_to_computed(k, v)

    def __repr__(self):
        return self.data.__repr__()


class Routes(MapperOutput):

    TYPES = set(["unicast",
                 "local",
                 "broadcast",
                 "multicast",
                 "throw",
                 "unreachable",
                 "prohibit",
                 "blackhole",
                 "nat"])

    IGNORE_TYPES = set(["broadcast",
                        "throw",
                        "local",
                        "unreachable",
                        "prohibit",
                        "blackhole",
                        "nat"])

    def __init__(self, data, path=None):
        all_routes = [route for routes in data.values() for route in routes]
        routes = defaultdict(lambda: defaultdict(list))
        for route in all_routes:
            table_type = route.type if route.type else 'None'
            dev = route.dev if route.dev else 'None'
            table = route.table if route.table else 'None'
            routes['by_prefix'] = data
            routes['by_device'][dev].append(route)
            routes['by_type'][table_type].append(route)
            routes['by_table'][table].append(route)
        self.routes = routes
        super(Routes, self).__init__(data, path)

    @computed
    def by_prefix(self):
        return self.routes.get('by_prefix', {})

    @computed
    def by_device(self):
        return self.routes.get('by_device', {})

    @computed
    def by_type(self):
        return self.routes.get('by_type', {})

    @computed
    def by_table(self):
        return self.routes.get('by_table', {})

    @computed
    def defaults(self):
        return self.routes.get('by_prefix', {}).get('default', [])

    @classmethod
    def parse_content(cls, content):
        routes = defaultdict(list)
        for line in filter(None, [l.strip() for l in content]):
            route = cls.parse_line(line)
            if route and (route.prefix != 'default' or not route.table):
                routes[route.prefix].append(route)
        return routes
            
    @classmethod
    def parse_line(cls, line):
        parts = deque(filter(None, line.split()))
        route = cls.parse_route(parts)
        if route:
            return route

    @classmethod
    def parse_route(cls, parts):
        route = {}
        table_type = None
        if parts[0] in cls.TYPES:
            table_type = parts.popleft()
            if table_type in cls.IGNORE_TYPES:
                return None
        route['type'] = table_type
        prefix = parts.popleft()
        route['netmask'] = 255
        if '/' in prefix:
            route['netmask'] = int(prefix.split('/')[1])
        route['prefix'] = prefix
        cls.parse_info_spec(parts, route)
        cls.parse_node_spec(parts, route)
        return Route(route)

    @classmethod
    def parse_info_spec(cls, parts, route):
        keys = ['via', 'dev']
        for k in keys:
            route[k] = None

        if not parts:
            return
        for key in keys:
            if parts and parts[0] == key:
                k, v = parts.popleft(), parts.popleft()
                route[k] = v

    @classmethod
    def parse_node_spec(cls, parts, route):
        keys = ['tos', 'table', 'proto', 'scope', 'metric', 'src', 'error']
        for k in keys:
            route[k] = None
        if not parts:
            return
        for key in keys:
            if parts and parts[0] == key:
                k, v = parts.popleft(), parts.popleft()
                route[k] = v

    def ifaces(self, ip):
        """
        Given an IP address, choose the best iface name to return.  If there
        are multiple routes that match, then the one with the most specific
        netmask will be returned.

        Example:
        ip_table = shared.get(get_ip_route)
        iface = ip_table.get_iface_by_ip(YOUR_IP_ADDRESS_STRING)
        """
        routes = self.by_type.get('None', [])
        max_netmask = 0
        ifaces = None
        addr = ipaddress.ip_address(unicode(ip))
        for route in routes:
            if route.prefix == "default":
                continue
            net = ipaddress.ip_network(unicode(route.prefix))
            if addr not in net:
                continue
            if route.netmask > max_netmask:
                ifaces = [r.dev for r in self.by_prefix[route.prefix] if r.dev]
                max_netmask = route.netmask # Longest Prefix Match
        if ifaces:
            return ifaces

        if self.defaults:
            return [self.defaults[0].dev]

        return None


@mapper("ip_route_show_table_all")
class RouteDevices(Routes):
    pass


@mapper("ip_route_show_table_all")
def route_devices(context):
    return RouteDevices.parse_context(context)


@mapper("ipv4_neigh")
def get_ipv4_neigh(context):
    """
    Return ip -4 neigh show nud all result.
    INPUT:
    172.17.0.19 dev docker0  FAILED
    172.17.42.1 dev lo lladdr 00:00:00:00:00:00 NOARP

    OUTPUT:
    {
        "172.17.0.19": [{"dev":"docker0","nud":"FAILED"}]
        "172.17.0.27": [{"dev":"lo", "nud":"NOARP", "lladdr":"00:00:00:00:00:00" }]
    }
    """

    result = defaultdict(list)
    for line in filter(None, context.content):
        split_result = line.split()
        key_value_content = split_result[1:-1]
        if len(key_value_content) >= 2:
            entry = {k: v for k, v in zip(key_value_content[0::2], key_value_content[1::2])}
        else:
            entry = {}
        entry["nud"] = split_result[-1]
        result[split_result[0]].append(entry)
    return result
