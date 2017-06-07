import unittest

from falafel.mappers.ifcfg import IfCFG
from falafel.tests import context_wrap
from falafel.util import keys_in


CONTEXT_PATH_DEVICE = "etc/sysconfig/network-scripts/ifcfg-eth0"

IFCFG_TEST_SPACE_V1 = """
DEVICE='"badName1"  '
BOOTPROTO=dhcp
IPV4_FAILURE_FATAL = no  #this is a comment
ONBOOT=yes
""".strip()

IFCFG_TEST_SPACE_V2 = """
DEVICE="\"badName2\"  "
BOOTPROTO=dhcp
IPV4_FAILURE_FATAL = no  #this is a comment
ONBOOT=yes
""".strip()

CONTEXT_PATH = "etc/sysconfig/network-scripts/ifcfg-enp0s25"

IFCFG_TEST = """
TYPE = "Ethernet"
BOOTPROTO=dhcp
IPV4_FAILURE_FATAL = no  #this is a comment
#ONBOOT=yes
NAME = enp0s25
""".strip()

IFCFG_TEST_2 = """
TYPE=Ethernet
BOOTPROTO=dhcp
DEFROUTE=yes
UUID=284549c8-0e07-41d3-a1e8-91ac9a9fca75
HWADDR=00:50:56:89:0B:B0
PEERDNS=yes
~
""".strip()

IFCFG_PATH_2 = "ssocommand/etc/sysconfig/network-scripts/ifcfg-=eno1"

IFCFG_TEST_3 = """
DEVICE=team1
DEVICETYPE=Team
ONBOOT=yes
NETMASK=255.255.252.0
IPADDR=192.168.0.1
TEAM_CONFIG='{"runner": {"name": "lacp", "active": "true", "tx_hash": ["eth", "ipv4"]}, "tx_balancer": {"name": "basic"}, "link_watch": {"name": "ethtool"}}'
""".strip()

IFCFG_PATH_3 = "etc/sysconfig/network-scripts/ifcfg-team1"

IFCFG_TEST_4 = """
DEVICE==eno2
ONBOOT=no
BOOTPROTO=none
USERCTL=no
DEVICETYPE=TeamPort
TEAM_MASTER=team1
TEAM_PORT_CONFIG='{"prio": 100}'
""".strip()

IFCFG_PATH_4 = "etc/sysconfig/network-scripts/ifcfg-=eno2"

IFCFG_TEST_5 = """
TEAM_PORT_CONFIG="{\\"prio\\": -10, \\"sticky\\": true, \\"link_watch\\": {\\"name\\": \\"ethtool\\"}}"
NAME=eth0
UUID=a4bd7fbc-3905-4ff1-a467-5b56c32572df
DEVICE=eth0
ONBOOT=yes
TEAM_MASTER=heartbeat
DEVICETYPE=TeamPort
ZONE=internal
""".strip()

IFCFG_PATH_5 = "etc/sysconfig/network-scripts/ifcfg-en0"

IFCFG_TEST_6 = """
DEVICE=bond0
IPADDR=10.11.96.172
NETMASK=255.255.252.0
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
IPV6INIT=no
BONDING_OPTS="mode=1 primary=eth1 arp_interval=1000 arp_ip_target=+10.11.96.1"


""".strip()

IFCFG_PATH_6 = "etc/sysconfig/network-scripts/ifcfg-en0"

IFCFG_TEST_NAMED_BOND_MODE = """
DEVICE=bond0
IPADDR=10.11.96.172
NETMASK=255.255.252.0
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
IPV6INIT=no
BONDING_OPTS="mode=balance-xor primary=eth1 arp_interval=1000 arp_ip_target=+10.11.96.1"
""".strip()

IFCFG_PATH_NAMED_BOND_MODE = "etc/sysconfig/network-scripts/ifcfg-en0"

IFCFG_TEST_BADLY_NAMED_BOND_MODE = """
DEVICE=bond0
IPADDR=10.11.96.172
NETMASK=255.255.252.0
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
IPV6INIT=no
BONDING_OPTS="mode=failover primary=eth1 arp_interval=1000 arp_ip_target=+10.11.96.1"
""".strip()

IFCFG_PATH_BADLY_NAMED_BOND_MODE = "etc/sysconfig/network-scripts/ifcfg-en0"


class TestIfcfg(unittest.TestCase):
    def test_ifcfg_space_v1(self):
        context = context_wrap(IFCFG_TEST_SPACE_V1)
        context.path = CONTEXT_PATH_DEVICE

        r = IfCFG(context)
        self.assertTrue(keys_in(["DEVICE", "iface", "ONBOOT", "BOOTPROTO",
                                 "IPV4_FAILURE_FATAL"], r))
        self.assertEqual(r["DEVICE"], '\'"badName1"  \'')

    def test_ifcfg_space_v2(self):
        context = context_wrap(IFCFG_TEST_SPACE_V2)
        context.path = CONTEXT_PATH_DEVICE

        r = IfCFG(context)
        self.assertTrue(keys_in(["DEVICE", "iface", "ONBOOT", "BOOTPROTO",
                                 "IPV4_FAILURE_FATAL"], r))
        self.assertEqual(r["DEVICE"], '\"\"badName2\"  \"')

    def test_ifcfg(self):
        context = context_wrap(IFCFG_TEST)
        context.path = CONTEXT_PATH

        r = IfCFG(context)
        self.assertTrue(keys_in(["iface", "TYPE", "BOOTPROTO",
                                 "IPV4_FAILURE_FATAL", "NAME"], r))
        self.assertFalse(keys_in(["ONBOOT"], r))
        self.assertEqual(r["TYPE"], "Ethernet")
        self.assertEqual(r["BOOTPROTO"], "dhcp")
        self.assertEqual(r["IPV4_FAILURE_FATAL"], "no")
        self.assertEqual(r["NAME"], "enp0s25")
        self.assertEqual(r["iface"], "enp0s25")
        self.assertEqual(r.ifname, r['iface'])
        self.assertIsNone(r.bonding_mode)

    def test_ifcfg_2(self):
        context = context_wrap(IFCFG_TEST_2)
        context.path = IFCFG_PATH_2

        r = IfCFG(context)
        self.assertTrue(len(r.data) == 7)
        self.assertEqual(r["iface"], "=eno1")
        self.assertEqual(r["TYPE"], "Ethernet")
        self.assertEqual(r["BOOTPROTO"], "dhcp")
        self.assertEqual(r["DEFROUTE"], "yes")
        self.assertEqual(r["UUID"], "284549c8-0e07-41d3-a1e8-91ac9a9fca75")
        self.assertEqual(r["HWADDR"], "00:50:56:89:0B:B0")
        self.assertEqual(r["PEERDNS"], "yes")

    def test_ifcfg_3(self):
        context = context_wrap(IFCFG_TEST_3)
        context.path = IFCFG_PATH_3

        r = IfCFG(context)

        self.assertTrue(len(r.data) == 7)
        self.assertEqual(r["DEVICE"], "team1")
        self.assertEqual(r["DEVICETYPE"], "Team")
        self.assertEqual(r["ONBOOT"], "yes")
        self.assertEqual(r["NETMASK"], "255.255.252.0")
        self.assertEqual(r["IPADDR"], "192.168.0.1")
        self.assertEqual(r["TEAM_CONFIG"]["runner"]["name"], "lacp")
        self.assertEqual(r["TEAM_CONFIG"]["runner"]["active"], "true")
        self.assertEqual(r["TEAM_CONFIG"]["tx_balancer"]["name"], "basic")
        self.assertEqual(r["TEAM_CONFIG"]["link_watch"]["name"], "ethtool")

    def test_ifcfg_4(self):
        context = context_wrap(IFCFG_TEST_4)
        context.path = IFCFG_PATH_4

        r = IfCFG(context)

        self.assertEqual(r["TEAM_PORT_CONFIG"]["prio"], 100)
        self.assertEqual(r["iface"], "=eno2")
        self.assertEqual(r["DEVICE"], "=eno2")

    def test_ifcfg_5(self):
        context = context_wrap(IFCFG_TEST_5)
        context.path = IFCFG_PATH_5

        r = IfCFG(context)

        self.assertEqual(r["TEAM_PORT_CONFIG"]["prio"], -10)

    def test_ifcfg_6(self):
        context = context_wrap(IFCFG_TEST_6)
        context.path = IFCFG_PATH_6

        r = IfCFG(context)

        self.assertEqual(r["BONDING_OPTS"]["mode"], "1")
        self.assertEqual(r["BONDING_OPTS"]["arp_ip_target"], "+10.11.96.1")
        self.assertEqual(r.bonding_mode, 1)

    def test_ifcfg_named_bond_mode(self):
        context = context_wrap(IFCFG_TEST_NAMED_BOND_MODE)
        context.path = IFCFG_PATH_NAMED_BOND_MODE

        r = IfCFG(context)

        self.assertEqual(r.bonding_mode, 2)

    def test_ifcfg_badly_named_bond_mode(self):
        context = context_wrap(IFCFG_TEST_BADLY_NAMED_BOND_MODE)
        context.path = IFCFG_PATH_BADLY_NAMED_BOND_MODE

        r = IfCFG(context)

        self.assertIsNone(r.bonding_mode)
