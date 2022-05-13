from insights.parsers.ip import IpLinkInfo
from insights.parsers.netstat import Netstat_I
from insights.util import keys_in
from insights.combiners.netstat import NetworkStats
from insights.tests import context_wrap

NETSTAT_I = """
Kernel Interface table
Iface       MTU Met    RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP TX-OVR Flg
bond0      1500   0   845265      0      0      0     1753      0      0      0 BMmRU
bond1      1500   0   842447      0      0      0     4233      0      0      0 BMmRU
eth0       1500   0   422518      0      0      0     1703      0      0      0 BMsRU
eth1       1500   0   422747      0      0      0       50      0      0      0 BMsRU
eth2       1500   0   421192      0      0      0     3674      0      0      0 BMsRU
eth3       1500   0   421255      0      0      0      559      0      0      0 BMsRU
lo        65536   0        0      0      0      0        0      0      0      0 LRU
""".strip()

IP_S_LINK = """
1: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
    link/ether 08:00:27:4a:c5:ef brd ff:ff:ff:ff:ff:ff
    RX: bytes  packets  errors  dropped overrun mcast
    1113685    2244     0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    550754     1407     0       0       0       0
2: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    RX: bytes  packets  errors  dropped overrun mcast
    884        98       0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    884        100       0       0       0       0
3: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
    link/ether 08:00:27:db:86:9e brd ff:ff:ff:ff:ff:ff
    RX: bytes  packets  errors  dropped overrun mcast
    0          6        0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    0          4        0       0       0       0
4: enp0s9: <BROADCAST,UP,MULTICAST> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
    link/ether 08:00:27:a6:bd:65 brd ff:ff:ff:ff:ff:ff
    RX: bytes  packets  errors  dropped overrun mcast
    0          8        0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    0          12        0       0       0       0
""".strip()

IP_S_LINK_2 = """
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    RX: bytes  packets  errors  dropped overrun mcast
    1736       20       0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    1736       20       0       0       0       0
2: enp0s31f6: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state DOWN mode DEFAULT group default qlen 1000
    link/ether c8:5b:76:3f:14:d5 brd ff:ff:ff:ff:ff:ff
    RX: bytes  packets  errors  dropped overrun mcast
    0          0        0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    0          0        0       0       0       0
3: wlp4s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DORMANT group default qlen 1000
    link/ether e4:a4:71:ae:70:b3 brd ff:ff:ff:ff:ff:ff
    RX: bytes  packets  errors  dropped overrun mcast
    96421231   90178    0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    7341914    51363    0       0       0       0
4: virbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DEFAULT group default qlen 1000
    link/ether 52:54:00:97:c0:bf brd ff:ff:ff:ff:ff:ff
    RX: bytes  packets  errors  dropped overrun mcast
    0          0        0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    0          0        0       0       0       0
5: virbr0-nic: <BROADCAST,MULTICAST> mtu 1500 qdisc fq_codel master virbr0 state DOWN mode DEFAULT group default qlen 1000
    link/ether 52:54:00:97:c0:bf brd ff:ff:ff:ff:ff:ff
    RX: bytes  packets  errors  dropped overrun mcast
    0          0        0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    0          0        0       0       0       0
6: tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1360 qdisc fq_codel state UNKNOWN mode DEFAULT group default qlen 100
    link/none
    RX: bytes  packets  errors  dropped overrun mcast
    14991388   21827    0       0       0       0
    TX: bytes  packets  errors  dropped carrier collsns
    1448430    22760    0       0       0       0
""".strip()

NETSTAT_I_2 = """
Kernel Interface table
Iface      MTU    RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP TX-OVR Flg
enp0s31f  1500        0      0      0 0             0      0      0      0 BMU
lo       65536       20      0      0 0            20      0      0      0 LRU
tun0      1360    21898      0      0 0         22839      0      0      0 MOPRU
virbr0    1500        0      0      0 0             0      0      0      0 BMU
wlp4s0    1500    90309      0      0 0         51481      0      0      0 BMRU
""".strip()

NETSTAT_I_NO = """
""".strip()

IP_S_LINK_NO = """
""".strip()


def test_ip_data_Link():
    link_info = IpLinkInfo(context_wrap(IP_S_LINK))
    if_list = link_info.active

    assert len(if_list) == 4
    assert keys_in(["lo", "enp0s3", "enp0s8", "enp0s9"], if_list)

    assert sorted(link_info.active) == sorted(['lo', 'enp0s3', 'enp0s8', 'enp0s9'])

    lo = link_info["lo"]
    assert lo["mac"] == "00:00:00:00:00:00"
    assert lo["flags"] == ["LOOPBACK", "UP", "LOWER_UP"]
    assert lo["type"] == "loopback"
    assert lo["mtu"] == 65536
    assert lo["rx_packets"] == 98
    assert lo["tx_packets"] == 100
    assert lo["index"] == 2

    enp0s3 = link_info["enp0s3"]
    assert enp0s3["mac"] == "08:00:27:4a:c5:ef"
    assert enp0s3["flags"] == ["BROADCAST", "MULTICAST", "UP", "LOWER_UP"]
    assert enp0s3["type"] == "ether"
    assert enp0s3["mtu"] == 1500
    assert enp0s3["rx_packets"] == 2244
    assert enp0s3["tx_packets"] == 1407
    assert enp0s3["index"] == 1


def test_get_netstat_i():
    netstat = Netstat_I(context_wrap(NETSTAT_I))
    nstat = NetworkStats(netstat, None)
    result = nstat.group_by_iface
    assert len(result) == 7
    assert result["bond0"] == {
        "MTU": "1500", "Met": "0", "RX-OK": "845265", "RX-ERR": "0",
        "RX-DRP": "0", "RX-OVR": "0", "TX-OK": "1753", "TX-ERR": "0",
        "TX-DRP": "0", "TX-OVR": "0", "Flg": "BMmRU"
    }
    assert result["eth0"] == {
        "MTU": "1500", "Met": "0", "RX-OK": "422518", "RX-ERR": "0",
        "RX-DRP": "0", "RX-OVR": "0", "TX-OK": "1703", "TX-ERR": "0",
        "TX-DRP": "0", "TX-OVR": "0", "Flg": "BMsRU"
    }


def test_combined():
    context = context_wrap(NETSTAT_I)
    nstat = Netstat_I(context)
    networkstats = NetworkStats(nstat, None)
    assert networkstats.data[0]["Iface"] == "bond0"
    result = networkstats.group_by_iface
    assert len(result) == 7
    assert result["bond0"] == {
        "MTU": "1500", "Met": "0", "RX-OK": "845265", "RX-ERR": "0",
        "RX-DRP": "0", "RX-OVR": "0", "TX-OK": "1753", "TX-ERR": "0",
        "TX-DRP": "0", "TX-OVR": "0", "Flg": "BMmRU"
    }

    context = context_wrap(IP_S_LINK)
    linkinfo = IpLinkInfo(context)
    networkstats = NetworkStats(None, linkinfo)
    result = networkstats.group_by_iface
    # the order of this structure is a cpython implementation detail
    # assert networkstats.data[0]["Iface"] == "lo"
    assert len(result) == 4
    assert result["lo"] == {
        'RX-OK': 98, 'TX-OK': 100, 'MTU': 65536, 'RX-ERR': 0,
        'TX-DRP': 0, 'TX-ERR': 0, 'RX-DRP': 0, 'RX-OVR': 0, 'Flg': 'LRU'
    }
    assert result["enp0s8"] == {
        'RX-OK': 6, 'TX-DRP': 0, 'TX-OK': 4, 'MTU': 1500,
        'RX-ERR': 0, 'TX-ERR': 0, 'RX-DRP': 0, 'RX-OVR': 0, 'Flg': 'BMRU'
    }

    context = context_wrap(NETSTAT_I_2)
    nstat = Netstat_I(context)
    networkstats = NetworkStats(nstat, None)
    result = networkstats.group_by_iface
    assert len(result) == 5

    context = context_wrap(IP_S_LINK_NO)
    linkinfo = IpLinkInfo(context)
    networkstats = NetworkStats(None, linkinfo)
    result = networkstats.group_by_iface
    assert len(result) == 0

    context = context_wrap(IP_S_LINK_2)
    linkinfo = IpLinkInfo(context)
    networkstats = NetworkStats(None, linkinfo)
    result = networkstats.group_by_iface
    assert len(result) == 6
