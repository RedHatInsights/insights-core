"""
Parsers for ``ip`` command outputs
==================================

This module provides the following parsers:

IpAddr - command ``ip addr``
----------------------------

RouteDevices - command ``ip route show table all``
--------------------------------------------------

IpNeighParser - command ``ip neigh show nud all``
-------------------------------------------------

IpLinkInfo - command ``ip -d -s link``
--------------------------------------
"""

from __future__ import print_function

import six
from collections import defaultdict, deque
from .. import parser, CommandParser
from ..contrib import ipaddress
from insights.specs import Specs


class NetworkInterface(object):
    def __init__(self, d):
        self.data = d
        addresses = [u"/".join([a["addr"], a["mask"]]) for a in self.data["addr"]]
        self.addresses = list(map(ipaddress.ip_interface, addresses))

    def __len__(self):
        return len(self.addresses)

    def __lt__(self, other):
        return self["name"] < other["name"]

    def __eq__(self, other):
        return self["name"] == other["name"]

    def __getitem__(self, item):
        return self.data[item]

    def addrs(self, version=None):
        if version:
            return [str(a.ip) for a in self.addresses if a.version == version]
        else:
            return [str(a.ip) for a in self.addresses]


def parse_ip_addr(content):
    r = {}
    current = {}
    if_details = {}
    rx_next_line = False
    tx_next_line = False
    content = [l.strip() for l in content if "Message truncated" not in l]
    for line in filter(None, content):
        if rx_next_line and current:
            parse_rx_stats(line, current)
            rx_next_line = False
        if tx_next_line and current:
            parse_tx_stats(line, current)
            tx_next_line = False
        elif line[0].isdigit() and "state" in line:
            current = parse_interface(line)
            r[current["name"]] = current
        elif line.startswith("link"):
            parse_link(line, current)
        elif 'vxlan' in line:
            split_content = line.split()
            current['vxlan'] = split_content
        elif 'openvswitch' in line:
            split_content = line.split()
            current['openvswitch'] = split_content
        elif 'geneve' in line:
            split_content = line.split()
            current['geneve'] = split_content
        elif line.startswith("inet"):
            parse_inet(line, current)
        elif line.startswith("RX") and current and "rx_bytes" not in current:
            rx_next_line = True
        elif line.startswith("TX") and current and "tx_bytes" not in current:
            tx_next_line = True
        elif line.startswith("vf "):
            current['vf_enabled'] = True
    for k, v in r.items():
        if_details[k] = NetworkInterface(v)
    return if_details


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
        "addr": [],
        "vf_enabled": False
    }
    # extract properties
    for i in range(4, len(split_content), 2):
        key, value = (split_content[i - 1], split_content[i])
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
        if "promiscuity" in split_content:
            d["promiscuity"] = split_content[
                split_content.index('promiscuity') + 1]


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


def parse_rx_stats(line, d):
    split_content = line.split()
    d["rx_bytes"] = int(split_content[0])
    d["rx_packets"] = int(split_content[1])
    d["rx_errors"] = int(split_content[2])
    d["rx_dropped"] = int(split_content[3])
    d["rx_overrun"] = int(split_content[4])
    d["rx_mcast"] = int(split_content[5])


def parse_tx_stats(line, d):
    split_content = line.split()
    d["tx_bytes"] = int(split_content[0])
    d["tx_packets"] = int(split_content[1])
    d["tx_errors"] = int(split_content[2])
    d["tx_dropped"] = int(split_content[3])
    d["tx_carrier"] = int(split_content[4])
    d["tx_collsns"] = int(split_content[5])


@parser(Specs.ip_addr)
class IpAddr(CommandParser):
    """
    This parser reads the output of ``ip addr`` into a dict whose key is
    the interface name.  The information about this interface`addr` key is a array to store all address.
    Different type have different output. Peer ip and general interface have difference type.

    Example output::

        1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
            link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
            inet 127.0.0.1/8 scope host lo
            inet6 ::1/128 scope host
            valid_lft forever preferred_lft forever

    Resultant data structure::

        {
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

    Examples:

        >>> for iface in shared[IpAddr]:
        ...     print 'Interface:', iface['name']
        ...     print 'State:', iface['state']
        ...     print 'Addresses:', ', '.join(a['addr'] for a in iface['addr'])
        ...
        Interface: lo
        State: UNKNOWN
        Addresses: 127.0.0.1, ::1
        Interface: eth7
        State: DOWN
        Addresses:
        Interface: tunl1
        State: DOWN
        Addresses: 172.30.0.1
        Interface: bond1.57
        State: UP
        Addresses:10.192.4.171, fe80::211:3fff:fee2:f59e, 2001::211:3fff:fee2:f59e
        Interface: ip.tun2
        State: UNKNOWN
        Addresses: 192.168.122.6

    """

    def parse_content(self, content):
        self.data = parse_ip_addr(content)

    def __iter__(self):
        """
        (iterable): Iterate through the list of available interfaces (in no order)
        """
        return iter(self.data.values())

    def __len__(self):
        """
        (int): number of interfaces configured.
        """
        return len(self.data)

    def __getitem__(self, item):
        """
        Parameters:
            item (str): Interface name
        Returns:
            (dict): Dictionary of the named interface
        """
        return self.data[item]

    def __contains__(self, item):
        """
        Is the given interface name configured?
        """
        return item in self.data

    @property
    def active(self):
        """
        (list): List of interfaces with 'UP' set in their flags.
        """
        return [i["name"] for i in self if "UP" in i["flags"]]


class Route(object):
    def __init__(self, data):
        for k, v in data.items():
            setattr(self, k, v)

    def __repr__(self):
        return self.__dict__.__repr__()


@parser(Specs.ip_route_show_table_all)
class RouteDevices(CommandParser):
    """
    This parser reads the output of the command ``ip route show table all``
    and provides access to the routing table.

    Each object in these properties is stored as a Route object, which has
    as properties the various parts of the route line.  Route objects will
    always include these properties (all defaulting to None):

    * ``type`` - the type of route (e.g. 'throw')
    * ``dev`` - the device routed through (e.g. 'eth0')
    * ``via`` - the external address routed through, or None if direct
    * ``netmask`` - the CIDR notation of the network as a string (e.g. '24')
    * ``table`` - the routing table, or None if not given.

    Destinations given as **broadcast**, **throw**, **unreachable**,
    **prohibit**, **blackhole** and **nat** are discarded.

    Destinations given as **unicast**, **multicast** and **local** are considered.

    Properties::

        by_device (dict): routes by device (e.g. 'eth0').
        by_type (dict): routes by table type (e.g. 'throw', default = 'None').
        by_table (dict): routes by table (e.g. 'mgmt', default = 'None').

    Sample routing table::

        default via 192.168.1.254 dev enp0s25
        10.0.0.0/8 via 10.64.54.1 dev tun0  proto static  metric 50
        10.64.54.0/23 dev tun0  proto kernel  scope link  src 10.64.54.44  metric 50
        66.187.239.220 via 192.168.23.250 dev enp0s25  proto static
        192.168.0.0/24 dev enp0s25  proto kernel  scope link  src 192.168.1.37
        192.168.122.0/24 dev virbr0  proto kernel  scope link  src 192.168.122.1

    Examples:

        >>> routes = shared[RouteDevices]
        >>> 'default' in routes
        True
        >>> '10.64.54.0/23' in routes
        False
        >>> len(routes['10.64.54.0/23']) # Multiple routes possible, esp. for default
        1
        >>> tunnel = routes['10.64.54.0/23'][0]
        >>> tunnel.dev
        'tun0'
        >>> tunnel.proto
        'kernel'
        >>> len(routes.by_device['tun0'])
        2
        >>> routes.by_device['tun0'][1] == tunnel
        True

    """
    SAVED_TYPES = set(["unicast", "multicast", 'local'])

    # Why have types we ignore?
    IGNORE_TYPES = set(["broadcast",
                        "throw",
                        "unreachable",
                        "prohibit",
                        "blackhole",
                        "nat"])

    @property
    def by_prefix(self):
        """
        (Route): The dictionary of routes by prefix  (e.g. '192.168.0.0/24').
        """
        return self.routes.get('by_prefix', {})

    @property
    def defaults(self):
        """
        (list): The list of default routes.
        """
        return self.routes.get('by_prefix', {}).get('default', [])

    def __contains__(self, prefix):
        """
        (bool): Is there a route with the given prefix?
        """
        return prefix in self.data

    def __getitem__(self, prefix):
        """
        (Route): Retrieve the given prefix - same as the ``by_prefix`` dict.
        """
        return self.data.get(prefix, None)

    def parse_content(self, content):
        """
        Read the routing table and construct the routes and data properties.
        """
        self.data = defaultdict(list)
        prev_line = ''
        for line in content:
            # Seems to not get blank lines here...
            # Leading spaces indicate a line continued from the previous
            if line.startswith('    '):
                prev_line += line
            else:
                if prev_line:
                    self.parse_line(prev_line)
                prev_line = line
        # Grab last line
        self.parse_line(prev_line)

        # Reprocess these into routes by prefix, device, type and table.
        self.routes = defaultdict(lambda: defaultdict(list))
        all_routes = [r for routes in self.data.values() for r in routes]
        # For some reason, if we try to construct the by_prefix property
        # as a defaultdict(list) here we break the tests.  Leaving it as is...
        self.routes['by_prefix'] = self.data
        self.by_device = defaultdict(list)
        self.by_type = defaultdict(list)
        self.by_table = defaultdict(list)
        for route in all_routes:
            table_type = route.type if route.type else 'None'
            dev = route.dev if route.dev else 'None'
            table = route.table if route.table else 'None'
            self.by_device[dev].append(route)
            self.by_type[table_type].append(route)
            self.by_table[table].append(route)
        # self.routes = {k: dict(v) for k, v in self.routes.items()}

    def parse_line(self, line):
        parts = deque(line.split(None))
        route = self.parse_route(parts)
        if route and (route.prefix != 'default' or not route.table):
            self.data[route.prefix].append(route)

    def parse_route(self, parts):
        required_parts = ['via', 'dev', 'type', 'netmask', 'prefix', 'table']
        route = dict((part, None) for part in required_parts)
        table_type = None
        if parts[0] in self.IGNORE_TYPES:
            return None
        if parts[0] in self.SAVED_TYPES:
            table_type = parts.popleft()
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
            if len(parts) > 1 and parts[0] == key:
                k, v = parts.popleft(), parts.popleft()
                route[k] = v

    def parse_node_spec(self, parts, route):
        while parts:
            if parts[0] == 'cache':
                route['cache'] = True
                parts.popleft()
                continue
            if len(parts) == 1:
                return
            k, v = parts.popleft(), parts.popleft()
            route[k] = v

    def ifaces(self, ip):
        """
        Given an IP address, choose the best iface name to return.  If
        there are multiple routes that match, then the one with the most
        specific netmask will be returned.  There may be multiple interfaces
        that serve this route so it returns a list.  If there are default
        routes, then these are used if a route is not found.  If no default
        routes are found, then return ``None``.

        Returns:
            (list): Device names that serve this network, or None if not found.

        Examples:

            >>> ip_table = shared[RouteDevices]
            >>> iface = ip_table.ifaces(YOUR_IP_ADDRESS_STRING)
        """
        if ip is None:
            return
        routes = self.by_type.get('None', [])
        addr = ipaddress.ip_address(six.u(ip))
        # Iterate through by descending netmask, so first found is most precise
        for route in sorted(routes, key=lambda r: r.netmask, reverse=True):
            if route.prefix == "default":
                continue
            net = ipaddress.ip_network(six.u(route.prefix))
            # Only test containment if this is the same verison of IP address.
            if addr.version != net.version:
                continue
            if addr not in net:
                continue
            return [r.dev for r in self.by_prefix[route.prefix] if r.dev]

        if self.defaults:
            return [self.defaults[0].dev]

        return None


class IpNeighParser(CommandParser):
    """
    This parser takes the output of ``ip neigh show nud all`` results for
    ARP and NDISC cache entries and reads them into a dictionary of results
    keyed on the name of the IP address.  Each item is a dictionary of the
    properties of that address record in the ARP table.  Fields usually
    include:

    * ``dev`` - the device the address was seen on
    * ``lladdr`` - the link level (MAC) address associated with the IP
    * ``nud`` - the Neighbour Unreachability Detection result, which is one
      of the following values:

      * **permanent** - the neighbour is permanently valid
      * **noarp** - the neighbour is valid and does not need revalidation
      * **reachable** - the neighbour is valid until its lifetime expires
      * **stale** - the neighour has not been seen in a while and its
        lifetime has expired, but it may still be valid
      * **failed** - the neighbour resolution has failed

    This class deals with both IPv4 and IPv6 records, and is subclassed to
    the two related parsers.

    Sample (IPv4) input data::

        172.17.0.19 dev docker0  FAILED
        172.17.42.1 dev lo lladdr 00:00:00:00:00:00 NOARP

    Examples:

        >>> neighb4 = shared[Ipv4Neigh]
        >>> '192.168.0.1' in neighb4
        False
        >>> '172.17.0.19' in neighb4
        True
        >>> neighb4['172.17.0.19']['dev']
        'docker0'
        >>> neighb4['172.17.42.1']['lladdr']
        '00:00:00:00:00:00'
    """

    VALID_NUD_STATES = {
        'PERMANENT': 0,
        'NOARP': 1,
        'REACHABLE': 2,
        'STALE': 3,
        'DELAY': 4,
        'FAILED': 5,
        'INCOMPLETE': 6,
    }

    def parse_content(self, content):
        """
        Parse the lines if the ``ip neighbor`` output.  Each line is split up
        into words on spaces, and must meet the following criteria:

        * there must be at least two words on the line
        * the first word must be a valid IP (v4 or v6) address
        * the last word must be a valid Neighbour Unreachability Detection state
        * the remaining words must be in pairs - these are then combined into
          key-value pairs for a dictionary.

        Each line is then stored in a dictionary by the address (as a string).
        The address as parsed by the ``ipaddress`` module is stored in the
        ``addr`` item in the dictionary, for convenience.
        """
        self.data = {}
        self.unparsed_lines = []
        for line in filter(None, content):
            split_result = line.split()
            # Need at least IP address, something, and reachability
            if len(split_result) < 2:
                self.unparsed_lines.append({
                    'line': line,
                    'reason': "not enough words"
                })
                continue
            # Total words needs to be even: beginning + 2*keyvals + ending
            if len(split_result) % 2 == 1:
                self.unparsed_lines.append({
                    'line': line,
                    'reason': "odd number of words"
                })
                continue
            # Don't parse this line if the first thing isn't an
            # IP address
            try:
                addr = ipaddress.ip_address(six.u(split_result[0]))
            except ValueError:
                self.unparsed_lines.append({
                    'line': line,
                    'reason': "can't convert address '" + split_result[0] + "'"
                })
                continue
            # Don't parse this line if the last item doesn't seem to be a
            # neighbour unreachability state
            if split_result[-1] not in self.VALID_NUD_STATES:
                self.unparsed_lines.append({
                    'line': line,
                    'reason': split_result[-1] + " is not a valid state"
                })
                continue

            # OK, good to go, split everything in the middle up
            key_value_content = split_result[1:-1]
            if len(key_value_content) >= 2:
                entry = dict((k, v) for k, v in zip(key_value_content[0::2],
                                                    key_value_content[1::2]))
            else:
                entry = {}
            entry["nud"] = split_result[-1]
            entry['addr'] = addr  # save the object
            self.data[split_result[0]] = entry

    def __contains__(self, item):
        """
        (bool): Is there neighbour information for the given address?
        """
        return item in self.data

    def __getitem__(self, item):
        """
        (dict): Get the neighbour information for the given address.
        """
        return self.data[item]


@parser(Specs.ipv4_neigh)
class Ipv4Neigh(IpNeighParser):
    """
    Class to parse ``ip -4 neigh show nud all`` command output.
    """
    pass


@parser(Specs.ipv6_neigh)
class Ipv6Neigh(IpNeighParser):
    """
    Class to parse ``ip -6 neigh show nud all`` command output.
    """
    pass


@parser(Specs.ip_neigh_show)
class IpNeighShow(IpNeighParser):
    """
    Class to parse ``ip neigh show`` or ``ip -s -s neigh show`` command output.
    """
    pass


@parser(Specs.ip_s_link)
class IpLinkInfo(IpAddr):
    """
    This parser parses the output of ``ip -s link`` command, which shows the
    data link layer stats of network devices, like packets received, packets
    dropped, link state, mtu.

    Example output::

        1: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
                    link/ether 08:00:27:4a:c5:ef brd ff:ff:ff:ff:ff:ff
                    RX: bytes  packets  errors  dropped overrun mcast
                    1113685    2244     0       0       0       0
                    TX: bytes  packets  errors  dropped carrier collsns
                    550754     1407     0       0       0       0


    Resultant output::

        {
            "index": 1,
            "physical_name": null,
            "name": "enp0s3",
            "flags": [
                "BROADCAST",
                "MULTICAST",
                "UP",
                "LOWER_UP"
            ],
            "addr":[]
            "mtu": 1500,
            "qdisc": "pfifo_fast",
            "state": "UP",
            "mode": "DEFAULT",
            "qlen": 1000,
            "mac": "08:00:27:4a:c5:ef",
            "brd": "ff:ff:ff:ff:ff:ff",
            "rx_bytes": 1113685,
            "rx_packets": 2244,
            "rx_errors": 0,
            "rx_dropped": 0,
            "rx_overrun": 0,
            "rx_mcast": 0,
            "tx_bytes": 550754,
            "tx_packets": 1407,
            "tx_errors": 0,
            "tx_dropped": 0,
            "tx_carrier": 0,
            "tx_collsns": 0
        }

    Examples:

        >>> type(ip_link)
        <class 'insights.parsers.ip.IpLinkInfo'>
        >>> for iface in ip_link:
        ...     print 'Interface:', iface['name']
        ...     print 'State:', iface['state']
        ...     print 'RX packets:', iface['rx_packets']
        ...     print 'RX dropped:', iface['rx_dropped']
        ...     print 'TX packets:', iface['tx_packets']
        ...     print 'TX dropped:', iface['tx_dropped']
        ...
        Interface: lo
        State: UNKNOWN
        RX packets: 98
        RX dropped: 0
        TX packets: 10
        TX dropped: 0
        Interface: enp0s3
        State: UP
        RX packets: 2244
        RX dropped: 0
        TX packets: 1407
        TX dropped: 0
        Interface: enp0s8
        State: UP
        RX packets: 1
        RX dropped: 0
        TX packets: 4
        TX dropped: 0
        Interface: enp0s9
        State: UP
        RX packets: 8
        RX dropped: 0
        TX packets: 12
        TX dropped: 0
    """
    pass
