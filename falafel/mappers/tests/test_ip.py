from falafel.mappers import ip
from falafel.tests import context_wrap
from falafel.util import keys_in

IP_ADDR_TEST = """
Message truncated
Message truncated
Message truncated
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host
    valid_lft forever preferred_lft forever
2: eth7: <NO-CARRIER,BROADCAST,MULTICAST,SLAVE,UP> mtu 1500 qdisc mq master bond1 state DOWN qlen 1000
    link/ether 00:11:3f:e2:f5:9f brd ff:ff:ff:ff:ff:ff link-netnsid 1
3: tunl0: <NOARP> mtu 1480 qdisc noop state DOWN
    link/ipip 0.0.0.0 brd 0.0.0.0
4: tunl1: <NOARP> mtu 1480 qdisc noop state DOWN
    link/[65534]
    inet 172.30.0.1 peer 172.30.0.2/32 scope global tun0
5: bond1.57@bond1: <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP
    link/ether 00:11:3f:e2:f5:9e brd ff:ff:ff:ff:ff:ff
    inet 10.192.4.171/27 brd 10.192.4.191 scope global bond1.57
    inet6 fe80::211:3fff:fee2:f59e/64 scope link
    valid_lft forever preferred_lft forever
    inet6 2001::211:3fff:fee2:f59e/64 scope global mngtmpaddr dynamic
    valid_lft 2592000sec preferred_lft 6480000sec
6: ip.tun2: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 80 qdisc noqueue state UNKNOWN
    link/ipip 10.192.4.203 peer 10.188.61.108
    inet 192.168.112.5 peer 192.168.122.6/32 scope global ip.tun2
""".strip()


def test_ip_addr():
    d = ip.IpAddr(context_wrap(IP_ADDR_TEST))

    assert len(d) == 6
    assert keys_in(["lo", "eth7", "tunl0", "tunl1", "bond1.57", "ip.tun2"], d)

    lo = d["lo"]
    assert lo["mac"] == "00:00:00:00:00:00"
    assert lo["flags"] == ["LOOPBACK", "UP", "LOWER_UP"]
    assert lo["type"] == "loopback"
    assert lo["mac"] == "00:00:00:00:00:00"
    assert lo["mtu"] == 16436
    assert lo.addrs(4) == ["127.0.0.1"]
    assert lo.addrs(6) == ["::1"]

    eth7 = d["eth7"]
    assert eth7["mac"] == "00:11:3f:e2:f5:9f"
    assert eth7["flags"] == ["NO-CARRIER", "BROADCAST", "MULTICAST", "SLAVE", "UP"]
    assert eth7["master"] == "bond1"
    assert eth7["qlen"] == 1000
    assert eth7["mtu"] == 1500
    assert len(eth7["addr"]) == 0

    tunl0 = d["tunl0"]
    assert tunl0["type"] == "ipip"

    tunl1 = d["tunl1"]
    assert tunl1["type"] == "[65534]"
    assert tunl1.addrs() == ["172.30.0.2"]  # P2P links use the remote IP

    bond1Addr = d["bond1.57"]
    assert bond1Addr.addrs(4) == ["10.192.4.171"]
    assert bond1Addr.addrs(6) == ["fe80::211:3fff:fee2:f59e", "2001::211:3fff:fee2:f59e"]

    tun2 = d["ip.tun2"]
    assert tun2["mtu"] == 80
    assert tun2["type"] == "ipip"
    assert tun2["peer"] == "10.188.61.108"
    assert tun2["peer_ip"] == "10.192.4.203"
    assert tun2.addrs(4) == ["192.168.122.6"]


IP_ROUTE_SHOW_TABLE_ALL_TEST = """
throw 30.142.64.0/26  table red_mgmt
default via 30.142.64.1 dev bond0.400  table red_mgmt
throw 30.142.34.0/26  table red_storage
default via 30.142.34.1 dev bond0.300  table red_storage
30.0.0.0/8 dev notExist proto kernel scope link src 30.0.0.1
30.142.34.0/26 dev bond0.300  proto kernel  scope link  src 30.142.34.5
30.142.64.0/26 dev bond0.400  proto kernel  scope link  src 30.142.64.9
169.254.0.0/16 dev bond0  scope link  metric 1012
169.254.0.0/16 dev bond0.300  scope link  metric 1013
169.254.0.0/16 dev bond0.400  scope link  metric 1014
169.254.0.0/16 dev bond0.700  scope link  metric 1015
default via 30.142.64.1 dev bond0.400
broadcast 127.255.255.255 dev lo  table local  proto kernel  scope link  src 127.0.0.1
local 30.142.64.9 dev bond0.400  table local  proto kernel  scope host  src 30.142.64.9
""".strip()


class Test_ip_route():
    def test_ip_route(self):
        context = context_wrap(IP_ROUTE_SHOW_TABLE_ALL_TEST)
        d = ip.RouteDevices(context)

        assert len(d.data) == 5
        assert d["30.142.34.0/26"][0].dev == "bond0.300"
        assert d["30.142.64.0/26"][0].dev == "bond0.400"
        assert d["169.254.0.0/16"][0].dev == "bond0"
        assert d.ifaces("30.142.34.1")[0] == "bond0.300"
        assert d.ifaces("30.142.64.1")[0] == "bond0.400"
        assert d.ifaces("169.254.0.1")[0] == "bond0"
        assert d.ifaces("30.0.0.1")[0] == "notExist"
        assert d.ifaces("192.168.0.1")[0] == "bond0.400"
        assert len(d.data["default"]) == 1
        assert getattr(d.by_device['bond0.300'][0], 'src') == '30.142.34.5'
        assert getattr(d.by_prefix['default'][0], 'via') == '30.142.64.1'
        assert getattr(d.by_prefix['30.142.34.0/26'][0], 'scope') == 'link'
        assert getattr(d.by_table['None'][1], 'proto') == 'kernel'
        assert getattr(d.by_type['None'][3], 'netmask') == 8


IPV4_NEIGH_CONTEXT = """
172.17.0.19 dev docker0  FAILED
172.17.42.1 dev lo lladdr 00:00:00:00:00:00 NOARP
"""


def test_ip_neigh():
    result = ip.get_ipv4_neigh(context_wrap(IPV4_NEIGH_CONTEXT))
    assert len(result) == 2
    assert len(result["172.17.0.19"])
    assert len(result["172.17.42.1"])
    assert result["172.17.0.19"] == [{"dev": "docker0", "nud": "FAILED"}]
    assert result["172.17.42.1"] == [{"dev": "lo", "nud": "NOARP", "lladdr": "00:00:00:00:00:00"}]
