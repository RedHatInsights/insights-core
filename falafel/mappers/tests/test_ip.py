from falafel.mappers import ip
from falafel.tests import context_wrap
from falafel.util import keys_in
from falafel.contrib import ipaddress

import unittest

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


class Test_IP_Addr(unittest.TestCase):
    def test_ip_addr(self):
        d = ip.IpAddr(context_wrap(IP_ADDR_TEST))

        assert len(d) == 6
        assert keys_in(["lo", "eth7", "tunl0", "tunl1", "bond1.57", "ip.tun2"], d)

        self.assertEqual(
            sorted(d.active),
            sorted(['lo', 'eth7', 'bond1.57', 'ip.tun2'])
        )

        lo = d["lo"]
        assert len(lo) == 2
        assert lo["mac"] == "00:00:00:00:00:00"
        assert lo["flags"] == ["LOOPBACK", "UP", "LOWER_UP"]
        assert lo["type"] == "loopback"
        assert lo["mac"] == "00:00:00:00:00:00"
        assert lo["mtu"] == 16436
        assert lo.addrs(4) == ["127.0.0.1"]
        assert lo.addrs(6) == ["::1"]

        eth7 = d["eth7"]
        assert len(eth7) == 0
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
        assert len(bond1Addr) == 3
        assert bond1Addr.addrs(4) == ["10.192.4.171"]
        assert bond1Addr.addrs(6) == ["fe80::211:3fff:fee2:f59e", "2001::211:3fff:fee2:f59e"]

        tun2 = d["ip.tun2"]
        assert tun2["mtu"] == 80
        assert tun2["type"] == "ipip"
        assert tun2["peer"] == "10.188.61.108"
        assert tun2["peer_ip"] == "10.192.4.203"
        assert tun2.addrs(4) == ["192.168.122.6"]

        # Tests of __cmp__
        assert eth7 != tunl0
        assert tunl0 != tunl1
        assert tunl1 == d['tunl1']

        # Tests of __iter__ and __getitem__
        for iface in d:
            self.assertIsNotNone(iface)


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

IP_ROUTE_SHOW_TABLE_ALL_TEST_2 = """
default via 192.168.23.250 dev enp0s25
10.0.0.0/8 via 10.64.54.1 dev tun0  proto static  metric 50
10.64.54.0/23 dev tun0  proto kernel  scope link  src 10.64.54.44  metric 50
66.187.239.220 via 192.168.23.250 dev enp0s25  proto static
192.168.23.0/24 dev enp0s25  proto kernel  scope link  src 192.168.23.37
192.168.122.0/24 dev virbr0  proto kernel  scope link  src 192.168.122.1
broadcast 10.64.54.0 dev tun0  table local  proto kernel  scope link  src 10.64.54.44
local 10.64.54.44 dev tun0  table local  proto kernel  scope host  src 10.64.54.44
broadcast 10.64.55.255 dev tun0  table local  proto kernel  scope link  src 10.64.54.44
broadcast 127.0.0.0 dev lo  table local  proto kernel  scope link  src 127.0.0.1
local 127.0.0.0/8 dev lo  table local  proto kernel  scope host  src 127.0.0.1
local 127.0.0.1 dev lo  table local  proto kernel  scope host  src 127.0.0.1
broadcast 127.255.255.255 dev lo  table local  proto kernel  scope link  src 127.0.0.1
broadcast 192.168.23.0 dev enp0s25  table local  proto kernel  scope link  src 192.168.23.37
local 192.168.23.37 dev enp0s25  table local  proto kernel  scope host  src 192.168.23.37
broadcast 192.168.23.255 dev enp0s25  table local  proto kernel  scope link  src 192.168.23.37
broadcast 192.168.122.0 dev virbr0  table local  proto kernel  scope link  src 192.168.122.1
local 192.168.122.1 dev virbr0  table local  proto kernel  scope host  src 192.168.122.1
broadcast 192.168.122.255 dev virbr0  table local  proto kernel  scope link  src 192.168.122.1
unreachable ::/96 dev lo  metric 1024  error -101
unreachable ::ffff:0.0.0.0/96 dev lo  metric 1024  error -101
2001:708:40:2001:a822:baff:fec4:2428 via fe80::a96:d7ff:fe38:d757 dev enp0s25  metric 0
    cache  mtu 1492 hoplimit 255
2001:44b8:1110:f800::/64 dev enp0s25  proto kernel  metric 256  expires 6403sec mtu 1492
unreachable 2002:a00::/24 dev lo  metric 1024  error -101
unreachable 2002:7f00::/24 dev lo  metric 1024  error -101
unreachable 2002:a9fe::/32 dev lo  metric 1024  error -101
unreachable 2002:ac10::/28 dev lo  metric 1024  error -101
unreachable 2002:c0a8::/32 dev lo  metric 1024  error -101
unreachable 2002:e000::/19 dev lo  metric 1024  error -101
2404:6800:4006:802::200e via fe80::a96:d7ff:fe38:d757 dev enp0s25  metric 0
    cache  mtu 1492 hoplimit 255
2404:6800:4006:803::2003 via fe80::a96:d7ff:fe38:d757 dev enp0s25  metric 0
    cache  mtu 1492 hoplimit 255
2404:6800:4008:c00::bc via fe80::a96:d7ff:fe38:d757 dev enp0s25  metric 0
    cache  mtu 1492 hoplimit 255
2404:6800:4008:c02::bd via fe80::a96:d7ff:fe38:d757 dev enp0s25  metric 0
    cache  mtu 1492 hoplimit 255
2404:6800:4008:c06::bd via fe80::a96:d7ff:fe38:d757 dev enp0s25  metric 0
    cache  mtu 1492 hoplimit 255
2a00:1450:400e:800::2003 via fe80::a96:d7ff:fe38:d757 dev enp0s25  metric 0
    cache  mtu 1492 hoplimit 255
unreachable 3ffe:ffff::/32 dev lo  metric 1024  error -101
fe80::/64 dev enp0s25  proto kernel  metric 256  mtu 1492
default via fe80::a96:d7ff:fe38:d757 dev enp0s25  proto ra  metric 1024  expires 1568sec mtu 1492 hoplimit 255
unreachable default dev lo  table unspec  proto kernel  metric 4294967295  error -101
local ::1 dev lo  table local  proto none  metric 0
local 2001:44b8:1110:f800:56ee:75ff:fe1c:5901 dev lo  table local  proto none  metric 0
local fe80::56ee:75ff:fe1c:5901 dev lo  table local  proto none  metric 0
multicast 2001:dbc::/64 dev enp0s25
ff02::fb dev enp0s25  metric 0
    cache  mtu 1492
ff00::/8 dev enp0s25  table local  metric 256  mtu 1492
unreachable default dev lo  table unspec  proto kernel  metric 4294967295  error -101

"""

IP_ROUTE_CANNOT_DETECT_THESE_ERRORS_YET = """
/usr/sbin/ip: bad command or file name
"""

IP_ROUTE_SHOW_TABLE_ALL_TEST_BAD = """
ff00::/16
ff01::/16 dev
ff02::/16 dev enp0s25 metric
"""


class Test_ip_route(unittest.TestCase):
    def test_ip_route(self):
        context = context_wrap(IP_ROUTE_SHOW_TABLE_ALL_TEST)
        d = ip.RouteDevices(context)

        self.assertEqual(len(d.data), 5)
        assert d["30.142.34.0/26"][0].dev == "bond0.300"
        assert d["30.142.64.0/26"][0].dev == "bond0.400"
        assert d["169.254.0.0/16"][0].dev == "bond0"
        assert d.ifaces(None) is None
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

    def test_ip_route_2(self):
        context = context_wrap(IP_ROUTE_SHOW_TABLE_ALL_TEST_2)
        context.path = "sos_commands/networking/ip_route_show_all"
        tbl = ip.RouteDevices(context)

        assert len(tbl.data) == 18

        # Ignored route types:
        assert 'broadcast' not in tbl
        assert 'local' not in tbl
        assert 'unreachable' not in tbl
        assert 'throw' not in tbl
        assert 'prohibit' not in tbl
        assert 'blackhole' not in tbl
        assert 'nat' not in tbl

        # Standard route types:
        assert 'default' in tbl

        # Assert existence of the standard route attributes for all route
        # objects, even though the attribute itself may be None
        for prefix in tbl.data.keys():
            for route in tbl[prefix]:
                for attr in ['via', 'dev', 'type', 'netmask', 'prefix', 'table']:
                    assert hasattr(route, attr)

        # Route object checks
        # 10.0.0.0/8 via 10.64.54.1 dev tun0  proto static  metric 50
        assert '10.0.0.0/8' in tbl
        r1 = tbl['10.0.0.0/8']
        assert len(r1) == 1
        r1a = r1[0]
        assert hasattr(r1a, 'prefix')
        assert r1a.prefix == '10.0.0.0/8'
        assert hasattr(r1a, 'via')
        assert r1a.via == '10.64.54.1'
        assert hasattr(r1a, 'dev')
        assert r1a.dev == 'tun0'
        assert hasattr(r1a, 'proto')
        assert r1a.proto == 'static'
        assert hasattr(r1a, 'metric')
        assert r1a.metric == '50'
        # a bit of a hack to make sure we test the __repr__ function of
        # the Route object:
        self.assertEqual(
            r1a.__repr__(),
            "{'via': '10.64.54.1', 'proto': 'static', 'metric': '50', " +
            "'prefix': '10.0.0.0/8', 'dev': 'tun0', 'netmask': 8, " +
            "'table': None, 'type': None}"
        )

        # 10.64.54.0/23 dev tun0  proto kernel  scope link  src 10.64.54.44  metric 50
        assert '10.64.54.0/23' in tbl
        r2 = tbl['10.64.54.0/23']
        assert len(r2) == 1
        r2a = r2[0]
        assert hasattr(r2a, 'prefix')
        assert r2a.prefix == '10.64.54.0/23'
        assert hasattr(r2a, 'via')
        assert r2a.via is None
        assert hasattr(r2a, 'dev')
        assert r2a.dev == 'tun0'
        assert hasattr(r2a, 'proto')
        assert r2a.proto == 'kernel'
        assert hasattr(r2a, 'scope')
        assert r2a.scope == 'link'
        assert hasattr(r2a, 'src')
        assert r2a.src == '10.64.54.44'
        assert hasattr(r2a, 'metric')
        assert r2a.metric == '50'

        # 2001:708:40:2001:a822:baff:fec4:2428 via fe80::a96:d7ff:fe38:d757 dev enp0s25  metric 0
        #     cache  mtu 1492 hoplimit 255
        assert '2001:708:40:2001:a822:baff:fec4:2428' in tbl
        r3 = tbl['2001:708:40:2001:a822:baff:fec4:2428']
        assert len(r3) == 1
        r3a = r3[0]
        assert hasattr(r3a, 'prefix')
        assert r3a.prefix == '2001:708:40:2001:a822:baff:fec4:2428'
        assert hasattr(r3a, 'via')
        assert r3a.via == 'fe80::a96:d7ff:fe38:d757'
        assert hasattr(r3a, 'dev')
        assert r3a.dev == 'enp0s25'
        assert hasattr(r3a, 'metric')
        assert r3a.metric == '0'
        assert hasattr(r3a, 'cache')
        assert r3a.cache
        assert hasattr(r3a, 'mtu')
        assert r3a.mtu == '1492'
        assert hasattr(r3a, 'hoplimit')
        assert r3a.hoplimit == '255'

        # by_prefix checks
        prefixes = tbl.by_prefix
        for prefix, route in prefixes.iteritems():
            self.assertIn(route[0], tbl.by_device[route[0].dev])

        # by_device checks
        devices = tbl.by_device
        assert 'tun0' in devices
        assert 'enp0s25' in devices
        assert 'virbr0' in devices
        assert len(devices) == 3
        assert len(devices['enp0s25']) == 16
        # Should be in order of reading, so find them in order by name
        assert devices['enp0s25'][0] == tbl['2001:44b8:1110:f800::/64'][0]
        assert devices['enp0s25'][1] == tbl['fe80::/64'][0]
        assert devices['enp0s25'][2] == tbl['2001:708:40:2001:a822:baff:fec4:2428'][0]
        # Default routes accumulate in the same order?
        assert devices['enp0s25'][3] == tbl['default'][0]
        assert devices['enp0s25'][4] == tbl['default'][1]
        assert devices['enp0s25'][5] == tbl['2404:6800:4008:c02::bd'][0]
        assert devices['enp0s25'][6] == tbl['2a00:1450:400e:800::2003'][0]
        assert devices['enp0s25'][7] == tbl['66.187.239.220'][0]
        assert devices['enp0s25'][8] == tbl['2404:6800:4006:803::2003'][0]
        assert devices['enp0s25'][9] == tbl['192.168.23.0/24'][0]
        assert devices['enp0s25'][10] == tbl['2404:6800:4006:802::200e'][0]
        assert devices['enp0s25'][11] == tbl['2404:6800:4008:c00::bc'][0]
        assert devices['enp0s25'][12] == tbl['2404:6800:4008:c06::bd'][0]
        assert devices['enp0s25'][13] == tbl['2001:dbc::/64'][0]
        assert devices['enp0s25'][14] == tbl['ff02::fb'][0]
        assert devices['enp0s25'][15] == tbl['ff00::/8'][0]

        # by_type checks
        types = tbl.by_type
        self.assertEqual(types.keys(), ['None', 'multicast'])
        self.assertEqual(len(types['None']), 18)
        for entry in types['None']:
            self.assertIn(entry, tbl[entry.prefix])

        # by_table checks
        tables = tbl.by_table
        self.assertEqual(tables.keys(), ['None', 'local'])
        self.assertEqual(len(tables['None']), 18)
        # Something tells me that out of
        self.assertEqual(len(tables['local']), 1)
        local = tables['local'][0]
        self.assertIsNone(local.via)
        self.assertEqual(local.metric, '256')
        self.assertEqual(local.prefix, 'ff00::/8')
        self.assertEqual(local.dev, 'enp0s25')
        self.assertEqual(local.mtu, '1492')
        self.assertEqual(local.netmask, 8)
        self.assertEqual(local.table, 'local')
        self.assertIsNone(local.type)

    def test_bad_ip_routes(self):
        context = context_wrap(IP_ROUTE_SHOW_TABLE_ALL_TEST_BAD)
        context.path = "sos_commands/networking/ip_route_show_all"
        tbl = ip.RouteDevices(context)

        # As long as the line has a CIDR-net or address, the Route object is
        # instantiated but most of its fields are None
        assert len(tbl.data) == 3

        self.assertIn('ff00::/16', tbl)
        r0a = tbl['ff00::/16'][0]
        for attr in ['via', 'dev', 'type', 'table']:
            self.assertTrue(hasattr(r0a, attr))
            self.assertIsNone(getattr(r0a, attr))
        self.assertTrue(hasattr(r0a, 'prefix'))
        self.assertEqual(r0a.prefix, 'ff00::/16')
        self.assertTrue(hasattr(r0a, 'netmask'))
        self.assertEqual(r0a.netmask, 16)

        self.assertIn('ff01::/16', tbl)
        r1a = tbl['ff01::/16'][0]
        for attr in ['via', 'dev', 'type', 'table']:
            self.assertTrue(hasattr(r1a, attr))
            self.assertIsNone(getattr(r1a, attr))
        self.assertTrue(hasattr(r1a, 'prefix'))
        self.assertEqual(r1a.prefix, 'ff01::/16')
        self.assertTrue(hasattr(r1a, 'netmask'))
        self.assertEqual(r1a.netmask, 16)

        self.assertIn('ff02::/16', tbl)
        r2a = tbl['ff02::/16'][0]
        for attr in ['via', 'type', 'table']:
            self.assertTrue(hasattr(r2a, attr))
            self.assertIsNone(getattr(r2a, attr))
        self.assertTrue(hasattr(r2a, 'prefix'))
        self.assertEqual(r2a.prefix, 'ff02::/16')
        self.assertTrue(hasattr(r2a, 'netmask'))
        self.assertEqual(r2a.netmask, 16)
        self.assertTrue(hasattr(r2a, 'dev'))
        self.assertEqual(r2a.dev, 'enp0s25')
        self.assertFalse(hasattr(r2a, 'metric'))

        # Also a good chance to test the failure to find an interface for a
        # routed address, since we don't have a default route defined.
        self.assertIsNone(tbl.ifaces('192.168.0.1'))


IPV4_NEIGH_CONTEXT = """
172.17.42.10 dev lo lladdr 00:00:00:00:00:00 PERMANENT
172.17.42.11 dev lo lladdr 00:00:00:00:00:01 NOARP
172.17.42.12 dev lo lladdr 00:00:00:00:00:02 REACHABLE
172.17.42.13 dev lo lladdr 00:00:00:00:00:03 STALE
172.17.42.14 dev lo lladdr 00:00:00:00:00:04 DELAY
172.17.42.15 dev lo lladdr 00:00:00:00:00:05 FAILED
172.17.0.18 FAILED
172.17.0.19 dev docker0  FAILED
"""


class TestIpv4Neigh(unittest.TestCase):
    def test_ipv4_neigh(self):
        result = ip.Ipv4Neigh(context_wrap(IPV4_NEIGH_CONTEXT))
        self.assertIn('172.17.0.18', result)
        self.assertEqual(len(result.data), 8)

        # Test all unreachability detection states
        self.assertEqual(result["172.17.42.10"], {
            "dev": "lo", "lladdr": "00:00:00:00:00:00", "nud": "PERMANENT",
            'addr': ipaddress.ip_address(u'172.17.42.10')
        })
        self.assertEqual(result["172.17.42.11"], {
            "dev": "lo", "lladdr": "00:00:00:00:00:01", "nud": "NOARP",
            'addr': ipaddress.ip_address(u'172.17.42.11')
        })
        self.assertEqual(result["172.17.42.12"], {
            "dev": "lo", "lladdr": "00:00:00:00:00:02", "nud": "REACHABLE",
            'addr': ipaddress.ip_address(u'172.17.42.12')
        })
        self.assertEqual(result["172.17.42.13"], {
            "dev": "lo", "lladdr": "00:00:00:00:00:03", "nud": "STALE",
            'addr': ipaddress.ip_address(u'172.17.42.13')
        })
        self.assertEqual(result["172.17.42.14"], {
            "dev": "lo", "lladdr": "00:00:00:00:00:04", "nud": "DELAY",
            'addr': ipaddress.ip_address(u'172.17.42.14')
        })
        self.assertEqual(result["172.17.42.15"], {
            "dev": "lo", "lladdr": "00:00:00:00:00:05", "nud": "FAILED",
            'addr': ipaddress.ip_address(u'172.17.42.15')
        })
        self.assertEqual(result["172.17.0.18"], {
            "nud": "FAILED", 'addr': ipaddress.ip_address(u'172.17.0.18')
        })
        self.assertEqual(result["172.17.0.19"], {
            "dev": "docker0", "nud": "FAILED",
            'addr': ipaddress.ip_address(u'172.17.0.19')
        })


BAD_NEIGH_CONTEXT = """
/usr/sbin/ip: bad command or file name
172.17.0
172.17.0.19
172.17.42.1 dev
172.17.42.2 dev lo
172.17.42.2 dev lo lladdr
"""


class TestBadNeigh(unittest.TestCase):
    def test_bad_neigh(self):
        result = ip.Ipv4Neigh(context_wrap(BAD_NEIGH_CONTEXT))
        self.assertEqual(len(result.data), 0)
        # Check unparsed_lines?
        self.assertEqual(len(result.unparsed_lines), 6)


IPV6_NEIGH_CONTEXT = """
ff02::16 dev vlinuxbr lladdr 33:33:00:00:00:16 NOARP
ff02::1:ffea:2c00 dev tun0 lladdr 33:33:ff:ea:2c:00 NOARP
"""


class TestIpv6Neigh(unittest.TestCase):
    def test_ipv6_neigh(self):
        result = ip.Ipv6Neigh(context_wrap(IPV6_NEIGH_CONTEXT))
        self.assertEqual(len(result.data), 2)
        self.assertEqual(len(result["ff02::16"]), 4)
        self.assertEqual(len(result["ff02::1:ffea:2c00"]), 4)
        self.assertEqual(result["ff02::16"], {
            "dev": "vlinuxbr", "nud": "NOARP", "lladdr": "33:33:00:00:00:16",
            'addr': ipaddress.ip_address(u'ff02::16')
        })
        self.assertEqual(result["ff02::1:ffea:2c00"], {
            "dev": "tun0", "nud": "NOARP", "lladdr": "33:33:ff:ea:2c:00",
            'addr': ipaddress.ip_address(u'ff02::1:ffea:2c00')
        })
