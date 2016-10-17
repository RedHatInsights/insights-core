from collections import defaultdict, deque
from .. import Mapper, mapper
from ..contrib import ipaddress


class NetworkInterface(object):

    def __init__(self, d):
        self.data = d
        addresses = [unicode("/".join([a["addr"], a["mask"]])) for a in self.data["addr"]]
        self.addresses = map(ipaddress.ip_interface, addresses)

    def __len__(self):
        return len(self.addresses)

    def __cmp__(self, other):
        return cmp(self["name"], other["name"])

    def __getitem__(self, item):
        return self.data[item]

    def addrs(self, version=None):
        if version:
            return [str(a.ip) for a in self.addresses if a.version == version]
        else:
            return [str(a.ip) for a in self.addresses]


def parse_ip_addr(content):
    r = {}
    content = [l.strip() for l in content if "Message truncated" not in l]
    for line in filter(None, content):
        if line[0].isdigit():
            current = parse_interface(line)
            r[current["name"]] = current
        elif line.startswith("link"):
            parse_link(line, current)
        elif line.startswith("inet"):
            parse_inet(line, current)
    return {k: NetworkInterface(v) for k, v in r.iteritems()}


def parse_interface(line):
    split_content = line.split()
    idx, name, _ = line.split(":", 2)
    virtual = "@" in name
    if virtual:
        name, physical_name = name.split("@")
    current = {
        "index": int(idx),
        "name": name.strip(),
        "physical_name": physical_name if virtual else None,
        "virtual": virtual,
        "flags": split_content[2].strip("<>").split(","),
        "addr": []
    }
    # extract properties
    for i in range(3, len(split_content), 2):
        key, value = (split_content[i], split_content[i + 1])
        current[key] = int(value) if key in ["mtu", "qlen"] else value
    return current


def parse_link(line, d):
    split_content = line.split()
    d["type"] = split_content[0].split("/")[1]
    if "peer" in line and len(split_content) >= 3:
        d["peer_ip"] = split_content[1]
        d["peer"] = split_content[3]
    elif len(split_content) >= 2:
        d["mac"] = split_content[1]


def parse_inet(line, d):
    split_content = line.split()
    p2p = "peer" in split_content
    addr, mask = split_content[3 if p2p else 1].split("/")
    d["addr"].append({
        "addr": addr,
        "mask": mask,
        "local_addr": split_content[1] if p2p else None,
        "p2p": p2p
    })


@mapper('ip_addr')
class IpAddr(Mapper):
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
        "index": 1,
        "physical_name": null,
        "qdisc": "noqueue",
        "name": "lo",
        "state": "UNKNOWN",
        "virtual": false,
        "mtu": 16436,
        "mac": "00:00:00:00:00:00",
        "flags": [
            "LOOPBACK",
            "UP",
            "LOWER_UP"
        ],
        "type": "loopback",
        "addr": [
            {
                "local_addr": null,
                "mask": "8",
                "p2p": false,
                "addr": "127.0.0.1"
            },
            {
                "local_addr": null,
                "mask": "128",
                "p2p": false,
                "addr": "::1"
            }
        ]
    }
    CASE 2:
    2: eth7: <NO-CARRIER,BROADCAST,MULTICAST,SLAVE,UP> mtu 1500 qdisc mq master bond1 state DOWN qlen 1000
        link/ether 00:11:3f:e2:f5:9f brd ff:ff:ff:ff:ff:ff link-netnsid 1
    RESULT:
    "eth7": {
        "index": 2,
        "physical_name": null,
        "qdisc": "mq",
        "name": "eth7",
        "state": "DOWN",
        "qlen": 1000,
        "virtual": false,
        "mtu": 1500,
        "mac": "00:11:3f:e2:f5:9f",
        "flags": [
            "NO-CARRIER",
            "BROADCAST",
            "MULTICAST",
            "SLAVE",
            "UP"
        ],
        "master": "bond1",
        "type": "ether",
        "addr": []
    }
    CASE 3:
    3: tunl0: <NOARP> mtu 1480 qdisc noop state DOWN
        link/ipip 0.0.0.0 brd 0.0.0.0
    RESULT:
    "tunl0": {
        "index": 3,
        "physical_name": null,
        "qdisc": "noop",
        "name": "tunl0",
        "state": "DOWN",
        "virtual": false,
        "mtu": 1480,
        "mac": "0.0.0.0",
        "flags": [
            "NOARP"
        ],
        "type": "ipip",
        "addr": []
    }
    CASE 4:
    4: tunl1: <NOARP> mtu 1480 qdisc noop state DOWN
        link/[65534]
        inet 172.30.0.1 peer 172.30.0.2/32 scope global tun0
    RESULT:
    "tunl1": {
        "index": 4,
        "physical_name": null,
        "qdisc": "noop",
        "name": "tunl1",
        "virtual": false,
        "mtu": 1480,
        "state": "DOWN",
        "flags": [
            "NOARP"
        ],
        "type": "[65534]",
        "addr": [
            {
                "local_addr": "172.30.0.1",
                "mask": "32",
                "p2p": true,
                "addr": "172.30.0.2"
            }
        ]
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
    "bond1.57": {
        "index": 5,
        "physical_name": "bond1",
        "qdisc": "noqueue",
        "name": "bond1.57",
        "state": "UP",
        "virtual": true,
        "mtu": 1500,
        "mac": "00:11:3f:e2:f5:9e",
        "flags": [
            "BROADCAST",
            "MULTICAST",
            "MASTER",
            "UP",
            "LOWER_UP"
        ],
        "type": "ether",
        "addr": [
            {
                "local_addr": null,
                "mask": "27",
                "p2p": false,
                "addr": "10.192.4.171"
            },
            {
                "local_addr": null,
                "mask": "64",
                "p2p": false,
                "addr": "fe80::211:3fff:fee2:f59e"
            },
            {
                "local_addr": null,
                "mask": "64",
                "p2p": false,
                "addr": "2001::211:3fff:fee2:f59e"
            }
        ]
    }
    CASE 6:
    6: ip.tun2: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1480 qdisc noqueue state UNKNOWN
        link/ipip 10.192.4.203 peer 10.188.61.108
        inet 192.168.112.5 peer 192.168.122.6/32 scope global ip.tun2
    RESULT:
    "ip.tun2": {
        "index": 6,
        "physical_name": null,
        "qdisc": "noqueue",
        "name": "ip.tun2",
        "virtual": false,
        "mtu": 1480,
        "state": "UNKNOWN",
        "flags": [
            "POINTOPOINT",
            "NOARP",
            "UP",
            "LOWER_UP"
        ],
        "peer": "10.188.61.108",
        "peer_ip": "10.192.4.203",
        "type": "ipip",
        "addr": [
            {
                "local_addr": "192.168.112.5",
                "mask": "32",
                "p2p": true,
                "addr": "192.168.122.6"
            }
        ]
    }
    """

    def parse_content(self, content):
        self.data = parse_ip_addr(content)

    def __iter__(self):
        return iter(self.data.values())

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    @property
    def active(self):
        return [i["name"] for i in self if "UP" in i["flags"]]


class Route(object):
    def __init__(self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)

    def __repr__(self):
        return self.data.__repr__()


@mapper("ip_route_show_table_all")
class RouteDevices(Mapper):

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

    @property
    def by_prefix(self):
        return self.routes.get('by_prefix', {})

    @property
    def by_device(self):
        return self.routes.get('by_device', {})

    @property
    def by_type(self):
        return self.routes.get('by_type', {})

    @property
    def by_table(self):
        return self.routes.get('by_table', {})

    @property
    def defaults(self):
        return self.routes.get('by_prefix', {}).get('default', [])

    def __getitem__(self, prefix):
        return self.data[prefix]

    def parse_content(self, content):
        self.data = defaultdict(list)
        for line in filter(None, [l.strip() for l in content]):
            route = self.parse_line(line)
            if route and (route.prefix != 'default' or not route.table):
                self.data[route.prefix].append(route)
        self.routes = defaultdict(lambda: defaultdict(list))
        all_routes = [r for routes in self.data.values() for r in routes]
        for route in all_routes:
            table_type = route.type if route.type else 'None'
            dev = route.dev if route.dev else 'None'
            table = route.table if route.table else 'None'
            self.routes['by_prefix'] = self.data
            self.routes['by_device'][dev].append(route)
            self.routes['by_type'][table_type].append(route)
            self.routes['by_table'][table].append(route)

    def parse_line(self, line):
        parts = deque(filter(None, line.split()))
        route = self.parse_route(parts)
        if route:
            return route

    def parse_route(self, parts):
        route = {}
        table_type = None
        if parts[0] in self.TYPES:
            table_type = parts.popleft()
            if table_type in self.IGNORE_TYPES:
                return None
        route['type'] = table_type
        prefix = parts.popleft()
        route['netmask'] = 255
        if '/' in prefix:
            route['netmask'] = int(prefix.split('/')[1])
        route['prefix'] = prefix
        self.parse_info_spec(parts, route)
        self.parse_node_spec(parts, route)
        return Route(route)

    def parse_info_spec(self, parts, route):
        keys = ['via', 'dev']
        for k in keys:
            route[k] = None

        if not parts:
            return
        for key in keys:
            if parts and parts[0] == key:
                k, v = parts.popleft(), parts.popleft()
                route[k] = v

    def parse_node_spec(self, parts, route):
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
        if ip is None:
            return
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
                max_netmask = route.netmask  # Longest Prefix Match
        if ifaces:
            return ifaces

        if self.defaults:
            return [self.defaults[0].dev]

        return None


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
