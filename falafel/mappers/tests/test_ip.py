import unittest

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
6: ip.tun2: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu XXX80 qdisc noqueue state UNKNOWN
    link/ipip 10.192.4.203 peer 10.188.61.108
    inet 192.168.112.5 peer 192.168.122.6/32 scope global ip.tun2
""".strip()


class TestIPAddr(unittest.TestCase):
    def test_ip_addr(self):
        d = ip.addr(context_wrap(IP_ADDR_TEST))

        self.assertEqual(len(d), 6)
        self.assertTrue(keys_in(["lo", "eth7", "tunl0", "tunl1", "bond1.57@bond1", "ip.tun2"], d))

        lo = d["lo"]
        self.assertEqual(lo["mac"], "00:00:00:00:00:00")
        self.assertEqual(len(lo["flag"]), 3)
        self.assertItemsEqual(["LOOPBACK", "UP", "LOWER_UP"], lo["flag"])
        self.assertEqual("loopback", lo["type"])
        self.assertEqual(lo["mac"], "00:00:00:00:00:00")
        self.assertEqual(lo["mtu"], 16436)
        self.assertEqual(1, len(lo["addr"]))
        self.assertItemsEqual(["127.0.0.1"], lo["addr"])
        self.assertItemsEqual(["::1"], lo["addr_v6"])

        eth7 = d["eth7"]
        self.assertEqual(eth7["mac"], "00:11:3f:e2:f5:9f")
        self.assertItemsEqual(["NO-CARRIER", "BROADCAST", "MULTICAST", "SLAVE", "UP"], eth7["flag"])
        self.assertEqual(eth7["master"], "bond1")
        self.assertEqual(eth7["qlen"], 1000)
        self.assertEqual(eth7["mtu"], 1500)
        self.assertEqual(len(eth7["addr"]), 0)

        tunl0 = d["tunl0"]
        self.assertEqual(tunl0["type"], "ipip")

        tunl1 = d["tunl1"]
        self.assertEqual(tunl1["type"], "[65534]")
        self.assertItemsEqual(["172.30.0.1"], tunl1["addr"])

        bond1Addr = d["bond1.57@bond1"]["addr"]
        self.assertEqual(len(bond1Addr), 1)
        self.assertItemsEqual(["10.192.4.171"], bond1Addr)
        self.assertItemsEqual(["fe80::211:3fff:fee2:f59e", "2001::211:3fff:fee2:f59e"], d["bond1.57@bond1"]["addr_v6"])

        tun2 = d["ip.tun2"]
        self.assertEqual(tun2["mtu"], "XXX80")
        self.assertEqual(tun2["type"], "ipip")
        self.assertEqual(tun2["peer"], "10.188.61.108")
        self.assertEqual(tun2["peer_ip"], "10.192.4.203")
        self.assertItemsEqual(["192.168.112.5"], tun2["addr"])
