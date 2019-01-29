from insights.parsers.ifcfg import IfCFG
from insights.tests import context_wrap
from insights.util import keys_in


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

IFCFG_TEST_MASTER = """
DEVICE="eth0"
BOOTPROTO=dhcp
MASTER="bond0"
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
BONDING_OPTS="mode=balance-xor primary=eth1 arp_interval=1000 arp_ip_target=+10.11.96.1 downdelay =0"
""".strip()

IFCFG_TEST_RAW_MASTER_VALUE = """
DEVICE="eth2"
IPADDR=10.11.96.172
NETMASK=255.255.252.0
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
IPV6INIT=no
MASTER="bond0"
""".strip()

IFCFG_TEST_RAW_TEAM_MASTER_VALUE = """
TYPE=Ethernet
DEVICE="eth1"
BOOTPROTO=none
ONBOOT=yes
TEAM_MASTER="team0"
MTU=9000
""".strip()

IFCFG_TEST_RAW_BONDING_VALUE = """
DEVICE="bond0"
IPADDR=10.11.96.172
NETMASK=255.255.252.0
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
IPV6INIT=no
BONDING_OPTS="mode=balance-xor primary=eth1 arp_interval=1000 arp_ip_target=+10.11.96.1 downdelay =0"
""".strip()

IFCFG_CONFIG_STR_ERROR = """
DEVICE=bond0
IPADDR=10.11.96.172
NETMASK=255.255.252.0
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
IPV6INIT=no
BONDING_OPTS="mode=balance-xor primary = eth1 arp_interval= 1000 arp_ip_target=+10.11.96.1 downdelay =0"
""".strip()

IFCFG_PATH_NAMED_BOND_MODE = "etc/sysconfig/network-scripts/ifcfg-en0"

IFCFG_PATH_ETH1 = "etc/sysconfig/network-scripts/ifcfg-eth1"

IFCFG_PATH_ETH2 = "etc/sysconfig/network-scripts/ifcfg-eth2"

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

IFCFG_BLANK_LINE = """

DEVICE==eno2

ONBOOT=no
BOOTPROTO=none
USERCTL=no
DEVICETYPE=TeamPort
TEAM_MASTER=team1
TEAM_PORT_CONFIG='{"prio": 100}'
"""

IFCFG_PATH_BLANK_LINE = "etc/sysconfig/network-scripts/ifcfg-=eno2"


def test_ifcfg_space_v1():
    context = context_wrap(IFCFG_TEST_SPACE_V1)
    context.path = CONTEXT_PATH_DEVICE

    r = IfCFG(context)
    assert keys_in(["DEVICE", "iface", "ONBOOT", "BOOTPROTO",
                    "IPV4_FAILURE_FATAL"], r)
    assert r["DEVICE"] == '\'"badName1"  \''


def test_ifcfg_space_v2():
    context = context_wrap(IFCFG_TEST_SPACE_V2)
    context.path = CONTEXT_PATH_DEVICE

    r = IfCFG(context)
    assert keys_in(["DEVICE", "iface", "ONBOOT", "BOOTPROTO",
                    "IPV4_FAILURE_FATAL"], r)
    assert r["DEVICE"] == '\"\"badName2\"  \"'


def test_ifcfg_master():
    context = context_wrap(IFCFG_TEST_MASTER)
    context.path = CONTEXT_PATH_DEVICE

    r = IfCFG(context)
    assert keys_in(["DEVICE", "iface", "ONBOOT", "BOOTPROTO",
                    "MASTER"], r)
    assert r["MASTER"] == 'bond0'


def test_ifcfg():
    context = context_wrap(IFCFG_TEST)
    context.path = CONTEXT_PATH

    r = IfCFG(context)
    assert keys_in(["iface", "TYPE", "BOOTPROTO",
                    "IPV4_FAILURE_FATAL", "NAME"], r)
    assert not keys_in(["ONBOOT"], r)
    assert r["TYPE"] == "Ethernet"
    assert r["BOOTPROTO"] == "dhcp"
    assert r["IPV4_FAILURE_FATAL"] == "no"
    assert r["NAME"] == "enp0s25"
    assert r["iface"] == "enp0s25"
    assert r.ifname == r['iface']
    assert r.bonding_mode is None


def test_ifcfg_2():
    context = context_wrap(IFCFG_TEST_2)
    context.path = IFCFG_PATH_2

    r = IfCFG(context)
    assert len(r.data) == 7
    assert r["iface"] == "=eno1"
    assert r["TYPE"] == "Ethernet"
    assert r["BOOTPROTO"] == "dhcp"
    assert r["DEFROUTE"] == "yes"
    assert r["UUID"] == "284549c8-0e07-41d3-a1e8-91ac9a9fca75"
    assert r["HWADDR"] == "00:50:56:89:0B:B0"
    assert r["PEERDNS"] == "yes"


def test_ifcfg_3():
    context = context_wrap(IFCFG_TEST_3)
    context.path = IFCFG_PATH_3

    r = IfCFG(context)

    assert len(r.data) == 8
    assert r["DEVICE"] == "team1"
    assert r["DEVICETYPE"] == "Team"
    assert r["ONBOOT"] == "yes"
    assert r["NETMASK"] == "255.255.252.0"
    assert r["IPADDR"] == "192.168.0.1"
    assert r["TEAM_CONFIG"]["runner"]["name"] == "lacp"
    assert r["TEAM_CONFIG"]["runner"]["active"] == "true"
    assert r["TEAM_CONFIG"]["tx_balancer"]["name"] == "basic"
    assert r["TEAM_CONFIG"]["link_watch"]["name"] == "ethtool"


def test_ifcfg_4():
    context = context_wrap(IFCFG_TEST_4)
    context.path = IFCFG_PATH_4

    r = IfCFG(context)

    assert r["TEAM_PORT_CONFIG"]["prio"] == 100
    assert r["iface"] == "=eno2"
    assert r["DEVICE"] == "=eno2"


def test_ifcfg_5():
    context = context_wrap(IFCFG_TEST_5)
    context.path = IFCFG_PATH_5

    r = IfCFG(context)

    assert r["TEAM_PORT_CONFIG"]["prio"] == -10


def test_ifcfg_6():
    context = context_wrap(IFCFG_TEST_6)
    context.path = IFCFG_PATH_6

    r = IfCFG(context)

    assert r["BONDING_OPTS"]["mode"] == "1"
    assert r["BONDING_OPTS"]["arp_ip_target"] == "+10.11.96.1"
    assert r.bonding_mode == 1


def test_ifcfg_named_bond_mode():
    context = context_wrap(IFCFG_TEST_NAMED_BOND_MODE)
    context.path = IFCFG_PATH_NAMED_BOND_MODE

    r = IfCFG(context)

    assert r.bonding_mode == 2


def test_ifcfg_badly_named_bond_mode():
    context = context_wrap(IFCFG_TEST_BADLY_NAMED_BOND_MODE)
    context.path = IFCFG_PATH_BADLY_NAMED_BOND_MODE

    r = IfCFG(context)

    assert r.bonding_mode is None


def test_ifcfg_bonding_opts():
    context = context_wrap(IFCFG_TEST_NAMED_BOND_MODE)
    context.path = IFCFG_PATH_NAMED_BOND_MODE

    r = IfCFG(context)

    assert r["BONDING_OPTS"]["mode"] == "balance-xor"
    assert r["BONDING_OPTS"]["arp_ip_target"] == "+10.11.96.1"
    assert r["BONDING_OPTS"]["downdelay"] == "0"
    assert r.has_empty_line is False
    assert r.bonding_mode == 2


def test_ifcfg_blankline():
    context = context_wrap(IFCFG_BLANK_LINE)
    context.path = IFCFG_PATH_BLANK_LINE
    r = IfCFG(context)
    assert r.has_empty_line is True


def test_ifcfg_raw_bonding_master_value():
    context = context_wrap(IFCFG_TEST_RAW_MASTER_VALUE)
    context.path = IFCFG_PATH_ETH2

    r = IfCFG(context)

    assert r["raw_device_value"] == '"eth2"'
    assert r["raw_master_value"] == '"bond0"'


def test_ifcfg_raw_bonding_value():
    context = context_wrap(IFCFG_TEST_RAW_BONDING_VALUE)
    context.path = IFCFG_PATH_NAMED_BOND_MODE

    r = IfCFG(context)

    assert r["raw_device_value"] == '"bond0"'
    assert r["raw_bonding_value"] == '"mode=balance-xor primary=eth1 arp_interval=1000 arp_ip_target=+10.11.96.1 downdelay =0"'


def test_ifcfg_raw_team_master_value():
    context = context_wrap(IFCFG_TEST_RAW_TEAM_MASTER_VALUE)
    context.path = IFCFG_PATH_ETH1

    r = IfCFG(context)

    assert r["raw_device_value"] == '"eth1"'
    assert r["raw_team_value"] == '"team0"'
