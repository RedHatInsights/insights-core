import pytest
import re

from insights.tests import context_wrap
from insights.parsers import ethtool, ParseException
from insights.util import keys_in

import doctest


TEST_ETHTOOL_A_DOCS = '''
Pause parameters for eth0:
Autonegotiate:  on
RX:             on
TX:             on
RX negotiated:  off
TX negotiated:  off
'''

SUCCESS_ETHTOOL_A = """
Pause parameters for enp0s25:
Autonegotiate : on
RX:             off
TX:             off
RX negotiated:  off
TX negotiated:  off
""".strip()

SUCCESS_ETHTOOL_A_PATH = """
sos_commands/networking/ethtool_-a_enp0s25
""".strip()

FAIL_ETHTOOL_A = """
Cannot get device pause settings: Operation not supported
Pause parameters for __wlp3s0:
""".strip()

FAIL_ETHTOOL_A_PATH = """
sos_commands/networking/ethtool_-a___wlp3s0
""".strip()

FAIL_ETHTOOL_A_1 = """
ethtool: bad command line argument(s)
For more information run ethtool -h
""".strip()
FAIL_ETHTOOL_A_PATH_1 = """
sos_commands/networking/ethtool_-a_bond0.1384@bond0
""".strip()

FAIL_ETHTOOL_A_2 = """
ethtool version 6
Usage:
ethtool DEVNAME Display standard information about device
    ethtool -s|--change DEVNAME
""".strip()
FAIL_ETHTOOL_A_PATH_2 = """
sos_commands/networking/ethtool_-a_g_bond2
""".strip()

SUCCESS_ETHTOOL_A_BLANK_LINE = """
Pause parameters for enp0s25:

Autonegotiate : on
RX:             off
TX:             off
RX negotiated:  off
TX negotiated:  off
""".strip()


def test_ethtool_a():
    context = context_wrap(SUCCESS_ETHTOOL_A, path=SUCCESS_ETHTOOL_A_PATH)
    result = ethtool.Pause(context)
    assert result.ifname == "enp0s25"
    assert result.autonegotiate
    assert not result.rx
    assert not result.tx
    assert not result.rx_negotiated
    assert not result.tx_negotiated


def test_ethtool_a_1():
    context = context_wrap(FAIL_ETHTOOL_A, path=FAIL_ETHTOOL_A_PATH)
    result = ethtool.Pause(context)
    assert result.ifname == "__wlp3s0"
    assert not result.autonegotiate


def test_ethtool_a_2():
    context = context_wrap(FAIL_ETHTOOL_A_1, path=FAIL_ETHTOOL_A_PATH_1)
    result = ethtool.Pause(context)
    assert result.ifname == "bond0.1384@bond0"


def test_ethtool_a_3():
    context = context_wrap(FAIL_ETHTOOL_A_2, path=FAIL_ETHTOOL_A_PATH_2)
    result = ethtool.Pause(context)
    assert result.ifname == "g_bond2"


def test_ethtool_a_blank_line():
    context = context_wrap(SUCCESS_ETHTOOL_A_BLANK_LINE, path=SUCCESS_ETHTOOL_A_PATH)
    result = ethtool.Pause(context)
    assert result.ifname == "enp0s25"


TEST_ETHTOOL_C_DOCS = '''
Coalesce parameters for eth0:
Adaptive RX: off  TX: off
stats-block-usecs: 0
sample-interval: 0
pkt-rate-low: 0
pkt-rate-high: 0

rx-usecs: 20
rx-frames: 5
rx-usecs-irq: 0
rx-frames-irq: 5

tx-usecs: 72
tx-frames: 53
tx-usecs-irq: 0
tx-frames-irq: 5

rx-usecs-low: 0
rx-frame-low: 0
tx-usecs-low: 0
tx-frame-low: 0

rx-usecs-high: 0
rx-frame-high: 0
tx-usecs-high: 0
tx-frame-high: 0
'''

TEST_ETHTOOL_C = """
Coalesce parameters for eth2:
Adaptive RX: off  TX: off
pkt-rate-high: 10

tx-usecs-irq: 0
tx-frame-low: 25

tx-usecs-high: 0
tx-frame-high: 0

""".strip()

TEST_ETHTOOL_C_PATH = "sos_commands/networking/ethtool_-c_eth2"

TEST_ETHTOOL_C_CANNOT_GET = """
Cannot get device coalesce settings: Operation not supported
Coalesce parameters for usb0:
""".strip()

TEST_ETHTOOL_C_BAD_ARGS = """
ethtool: bad command line argument(s)
For more information run ethtool -h
"""

TEST_ETHTOOL_C_SHORT = """
Coalesce parameters for eth2:
""".strip()


def test_get_ethtool_c():
    context = context_wrap(TEST_ETHTOOL_C)
    context.path = TEST_ETHTOOL_C_PATH
    result = ethtool.CoalescingInfo(context)
    assert keys_in(["adaptive-rx", "adaptive-tx", "pkt-rate-high",
                    "tx-usecs-irq", "tx-frame-low", "tx-usecs-high", "tx-frame-high"], result.data)
    assert result.ifname == "eth2"
    assert not result.adaptive_rx
    assert not result.adaptive_tx
    assert result.pkt_rate_high == 10
    assert result.tx_usecs_irq == 0
    assert result.tx_frame_low == 25
    assert result.tx_usecs_high == 0
    assert result.tx_frame_high == 0


def test_get_ethtool_c_cannot_get():
    context = context_wrap(TEST_ETHTOOL_C_CANNOT_GET)
    context.path = 'sos_commands/networking/ethtool_-c_usb0'
    result = ethtool.CoalescingInfo(context)
    assert result.ifname == 'usb0'


def test_get_ethtool_c_bad_args():
    context = context_wrap(TEST_ETHTOOL_C_BAD_ARGS, path='sos_commands/networking/ethtool_-c_eth0')
    result = ethtool.CoalescingInfo(context)
    assert result.ifname == 'eth0'


def test_get_ethtool_c_short():
    context = context_wrap(TEST_ETHTOOL_C_SHORT, path=TEST_ETHTOOL_C_PATH)
    with pytest.raises(ParseException) as exc:
        ethtool.CoalescingInfo(context)
    assert 'Command output missing value data' in str(exc)


TEST_ETHTOOL_G_DOCS = '''
Ring parameters for eth0:
Pre-set maximums:
RX:             2047
RX Mini:        0
RX Jumbo:       0
TX:             511
Current hardware settings:
RX:             200
RX Mini:        0
RX Jumbo:       0
TX:             511
'''

TEST_ETHTOOL_G = """
Ring parameters for eth2:
Pre-set maximums:
RX:     2047
RX Mini:    0
RX Jumbo:   0
TX:     511

Current hardware settings:
RX:     200
RX Mini:    0
RX Jumbo:   0
TX:     511


""".strip()

TEST_ETHTOOL_G_PATH = """
sos_commands/networking/ethtool_-g_eth2
""".strip()

TEST_ETHTOOL_G_1 = """
Cannot get device ring settings: No such device
Ring parameters for bond0.102@bond0:

"""

TEST_ETHTOOL_G_PATH_1 = """
sos-command/neworking/ethtool_-g_bond2.102@bond2
"""

TEST_ETHTOOL_G_2 = """
ethtool: bad command line argument(s)
For more information run ethtool -h
"""

TEST_ETHTOOL_G_PATH_2 = """
sos_commands/networkking/ethtool_-g_eth2
"""


def test_ethtool_g():
    context = context_wrap(TEST_ETHTOOL_G)
    context.path = TEST_ETHTOOL_G_PATH
    result = ethtool.Ring(context)
    assert keys_in(["max", "current"], result.data)

    assert result.ifname == "eth2"
    assert result.data['max'].rx == 2047
    assert result.data['max'].rx_mini == 0
    assert result.data['max'].rx_jumbo == 0
    assert result.data['max'].tx == 511
    assert result.max.rx == 2047
    assert result.max.rx_mini == 0
    assert result.max.rx_jumbo == 0
    assert result.max.tx == 511
    assert result.current.rx == 200
    assert result.current.rx_mini == 0
    assert result.current.rx_jumbo == 0
    assert result.current.tx == 511


def test_ethtool_g_1():
    context = context_wrap(TEST_ETHTOOL_G_1)
    context.path = TEST_ETHTOOL_G_PATH_1
    result = ethtool.Ring(context)
    assert result.ifname == "bond0.102@bond0"


def test_ethtool_g_2():
    context = context_wrap(TEST_ETHTOOL_G_2, path=TEST_ETHTOOL_G_PATH_2)
    result = ethtool.Ring(context)
    assert result.ifname == "eth2"


TEST_ETHTOOL_I_DOCS = '''
driver: bonding
version: 3.6.0
firmware-version: 2
bus-info:
supports-statistics: no
supports-test: no
supports-eeprom-access: no
supports-register-dump: no
supports-priv-flags: no
'''

TEST_ETHTOOL_I_GOOD = """
driver: virtio_net
version: 1.0.0
firmware-version:
bus-info: 0000:00:03.0
supports-statistics: no
supports-test: no
supports-eeprom-access: no
supports-register-dump: no
supports-priv-flags: no
"""

TEST_ETHTOOL_I_MISSING_KEYS = """
driver: virtio_net
firmware-version:
bus-info: 0000:00:03.0
supports-statistics: no
supports-test: no
supports-eeprom-access: no
supports-register-dump: no
supports-priv-flags: no
something without a colon here is ignored
"""


def test_good():
    context = context_wrap(TEST_ETHTOOL_I_GOOD)
    parsed = ethtool.Driver(context)
    assert parsed.version == "1.0.0"
    assert parsed.driver == 'virtio_net'
    assert parsed.firmware_version is None
    assert parsed.bus_info == '0000:00:03.0'
    assert not parsed.supports_statistics
    assert not parsed.supports_test
    assert not parsed.supports_eeprom_access
    assert not parsed.supports_register_dump
    assert not parsed.supports_priv_flags


def test_missing_version():
    context = context_wrap(TEST_ETHTOOL_I_MISSING_KEYS)
    parsed = ethtool.Driver(context)
    assert parsed.version is None


def test_missing_value():
    context = context_wrap(TEST_ETHTOOL_I_GOOD)
    parsed = ethtool.Driver(context)
    assert parsed.firmware_version is None


def test_iface():
    context = context_wrap(TEST_ETHTOOL_I_GOOD, path="sbin/ethtool_-i_eth0")
    parsed = ethtool.Driver(context)
    assert parsed.ifname == "eth0"


def test_no_iface():
    context = context_wrap(TEST_ETHTOOL_I_GOOD, path="foo/bar/baz/oopsie")
    parsed = ethtool.Driver(context)
    assert parsed.ifname is None


ETHTOOL_K_STANDARD = """
Features for bond0:
rx-checksumming: off [fixed]
tx-checksumming: on
    tx-checksum-ipv4: off [fixed]
    tx-checksum-unneeded: on [fixed]
    tx-checksum-ip-generic: off [fixed]
    tx-checksum-ipv6: off [fixed]
    tx-checksum-fcoe-crc: off [fixed]
    tx-checksum-sctp: off [fixed]
scatter-gather: on
    tx-scatter-gather: on [fixed]
    tx-scatter-gather-fraglist: off [fixed]
tcp-segmentation-offload: on
    tx-tcp-segmentation: on [fixed]
    tx-tcp-ecn-segmentation: on [fixed]
    tx-tcp6-segmentation: on [fixed]
udp-fragmentation-offload: off [fixed]
generic-segmentation-offload: off [requested on]
generic-receive-offload: on
large-receive-offload: on
rx-vlan-offload: on
tx-vlan-offload: on
ntuple-filters: off
receive-hashing: off
highdma: on [fixed]
rx-vlan-filter: on [fixed]
vlan-challenged: off [fixed]
tx-lockless: on [fixed]
netns-local: off [fixed]
tx-gso-robust: off [fixed]
tx-fcoe-segmentation: off [fixed]
tx-gre-segmentation: on [fixed]
tx-udp_tnl-segmentation: on [fixed]
fcoe-mtu: off [fixed]
loopback: off [fixed]
"""

ETHTOOL_K_BAD_ARGS = """
ethtool: bad command line argument(s)
For more information run ethtool -h
""".strip()

ETHTOOL_K_CANNOT_GET = """
Cannot get stats strings information: Operation not supported
""".strip()

ETHTOOL_K_MISSING_COLON = """
Features for bond0:
rx-checksumming off [fixed]
tx-checksumming on
"""


def test_Features_good():
    # Test picking up interface from header line rather than path
    features = ethtool.Features(
        context_wrap(ETHTOOL_K_STANDARD, path='sos_commands/networking/ethtool_-k_bond0'))
    assert features.ifname == 'bond0'
    assert features.iface == 'bond0'

    assert not features.is_on('rx-checksumming')
    assert features.is_on('tx-checksumming')

    assert features.is_fixed('rx-checksumming')
    assert not features.is_fixed('tx-checksumming')


def test_Features_bad_args():
    # Even if content is bad, interface should be available from path
    features = ethtool.Features(
        context_wrap(ETHTOOL_K_BAD_ARGS, path="sbin/ethtool_-k_bond0"))
    assert features.ifname == 'bond0'
    assert features.iface == 'bond0'
    assert features.data == {}


def test_Features_cannot_get():
    features = ethtool.Features(
        context_wrap(ETHTOOL_K_CANNOT_GET, path="sbin/ethtool_-k_eth1"))
    assert features.ifname == 'eth1'
    assert features.iface == 'eth1'

    assert features.data == {}


def test_Features_missing_colon():
    features = ethtool.Features(
        context_wrap(ETHTOOL_K_MISSING_COLON, path="sbin/ethtool_-k_bond0"))
    assert features.ifname == 'bond0'
    assert features.data == {}


TEST_ETHTOOL_S_DOCS = '''
NIC statistics:
     rx_octets: 808488730
     rx_fragments: 0
     rx_ucast_packets: 1510830
     rx_mcast_packets: 678653
     rx_bcast_packets: 9921
     rx_fcs_errors: 0
     rx_align_errors: 0
     rx_xon_pause_rcvd: 0
     rx_xoff_pause_rcvd: 0
     rx_mac_ctrl_rcvd: 0
     rx_xoff_entered: 0
     rx_frame_too_long_errors: 0
     rx_jabbers: 0
'''

SUCCEED_ETHTOOL_S = '''
NIC statistics:
    rx_packets: 912398
    tx_packets: 965449
    rx_bytes: 96506134
    tx_bytes: 190360255
    rx_broadcast: 4246
    tx_broadcast: 4248
    rx_multicast: 18
    tx_multicast: 20
    multicast: 18
    collisions: 0
    rx_crc_errors: 0
    rx_no_buffer_count: 0
    rx_missed_errors: 0
    tx_aborted_errors: 0
    tx_carrier_errors: 0
    tx_window_errors: 0
    tx_abort_late_coll: 0
    tx_deferred_ok: 0
    tx_single_coll_ok: 0
    tx_multi_coll_ok: 0
    tx_timeout_count: 0
    rx_long_length_errors: 0
    rx_short_length_errors: 0
    rx_align_errors: 0
    tx_tcp_seg_good: 0
    tx_tcp_seg_failed: 0
    rx_flow_control_xon: 0
    rx_flow_control_xoff: 0
    tx_flow_control_xon: 0
    tx_flow_control_xoff: 0
    rx_long_byte_count: 96506134
    tx_dma_out_of_sync: 0
    tx_smbus: 0
    rx_smbus: 0
    dropped_smbus: 0
    os2bmc_rx_by_bmc: 0
    os2bmc_tx_by_bmc: 0
    os2bmc_tx_by_host: 0
    os2bmc_rx_by_host: 0
    tx_hwtstamp_timeouts: 0
    rx_hwtstamp_cleared: 0
    rx_errors: 0
    tx_errors: 0
    tx_dropped: 0
    rx_length_errors: 0
    rx_over_errors: 0
    rx_frame_errors: 0
    rx_fifo_errors: 0
    tx_fifo_errors: 0
    tx_heartbeat_errors: 0
    tx_queue_0_packets: 613
    tx_queue_0_bytes: 240342
    tx_queue_0_restart: 0
    tx_queue_1_packets: 935473
    tx_queue_1_bytes: 181899495
    tx_queue_1_restart: 0
    tx_queue_2_packets: 6
    tx_queue_2_bytes: 412
    tx_queue_2_restart: 0
    tx_queue_3_packets: 29357
    tx_queue_3_bytes: 4358198
    tx_queue_3_restart: 0
    rx_queue_0_packets: 912398
    rx_queue_0_bytes: 92856542
    rx_queue_0_drops: 0
    rx_queue_0_csum_err: 0
    rx_queue_0_alloc_failed: 0
    rx_queue_1_packets: 0
    rx_queue_1_bytes: 0
    rx_queue_1_drops: 0
    rx_queue_1_csum_err: 0
    rx_queue_1_alloc_failed: 0
    rx_queue_2_packets: 0
    rx_queue_2_bytes: 0
    rx_queue_2_drops: 0
    rx_queue_2_csum_err: 0
    rx_queue_2_alloc_failed: 0
    rx_queue_3_packets: 0
    rx_queue_3_bytes: 0
    rx_queue_3_drops: 0
    rx_queue_3_csum_err: 0
    rx_queue_3_alloc_failed: 0
'''

ETHTOOL_S_eth0_1 = """NIC statistics:
    rxq0: rx_pkts: 5000000
    rxq0: rx_drops_no_frags: 5000
    rxq1: rx_pkts: 5000000
    rxq1: rx_drops_no_frags: 5000
"""

FAILED_ETHTOOL_S_ONE = "no stats avilable "

FAILED_ETHTOOL_S_TWO = "Cannot get stats strings information: Operation not supported"

FAILED_ETHTOOL_S_THREE = """NIC statistics:
Nothing to see here
"""


def test_ethtool_S():
    ethtool_S_info = ethtool.Statistics(context_wrap(SUCCEED_ETHTOOL_S))
    ret = {}
    for line in SUCCEED_ETHTOOL_S.split('\n')[2:-1]:
        key, value = line.split(':')
        ret[key.strip()] = int(value.strip()) if value else None
    eth_data = dict(ethtool_S_info.data)
    assert eth_data == ret

    # Test search functionality
    assert ethtool_S_info.search(r'rx_queue_3') == {
        'rx_queue_3_packets': 0,
        'rx_queue_3_bytes': 0,
        'rx_queue_3_drops': 0,
        'rx_queue_3_csum_err': 0,
        'rx_queue_3_alloc_failed': 0,
    }
    assert ethtool_S_info.search(r'RX_QUEUE_3', flags=re.IGNORECASE) == {
        'rx_queue_3_packets': 0,
        'rx_queue_3_bytes': 0,
        'rx_queue_3_drops': 0,
        'rx_queue_3_csum_err': 0,
        'rx_queue_3_alloc_failed': 0,
    }


def test_ethtool_S_subinterface():
    ethtool_S_info = ethtool.Statistics(context_wrap(ETHTOOL_S_eth0_1))
    assert sorted(ethtool_S_info.data.keys()) == sorted([
        'rxq0: rx_pkts', 'rxq0: rx_drops_no_frags',
        'rxq1: rx_pkts', 'rxq1: rx_drops_no_frags'
    ])
    assert ethtool_S_info.data['rxq0: rx_pkts'] == 5000000


def test_ethtool_S_f():
    ethtool_S_info_f1 = ethtool.Statistics(context_wrap(FAILED_ETHTOOL_S_ONE))
    assert not ethtool_S_info_f1.ifname
    ethtool_S_info_f2 = ethtool.Statistics(context_wrap(FAILED_ETHTOOL_S_TWO))
    assert not ethtool_S_info_f2.ifname
    ethtool_S_info_f2 = ethtool.Statistics(context_wrap(FAILED_ETHTOOL_S_THREE))
    assert not ethtool_S_info_f2.ifname


TEST_ETHTOOL_TIMESTAMP = '''
Time stamping parameters for eno1:

Capabilities:
    hardware-transmit     (SOF_TIMESTAMPING_TX_HARDWARE)
    software-transmit     (SOF_TIMESTAMPING_TX_SOFTWARE)
    hardware-receive      (SOF_TIMESTAMPING_RX_HARDWARE)
    software-receive      (SOF_TIMESTAMPING_RX_SOFTWARE)
    software-system-clock (SOF_TIMESTAMPING_SOFTWARE)
    hardware-raw-clock    (SOF_TIMESTAMPING_RAW_HARDWARE)
PTP Hardware Clock: 0
Hardware Transmit Timestamp Modes:
    off                   (HWTSTAMP_TX_OFF)
    on                    (HWTSTAMP_TX_ON)
Hardware Receive Filter Modes:
    none                  (HWTSTAMP_FILTER_NONE)
    all                   (HWTSTAMP_FILTER_ALL)
'''

TEST_ETHTOOL_TIMESTAMP_AB = '''
Time stamping parameters for eno1:

Capabilities:
    hardware-transmit     (SOF_TIMESTAMPING_TX_HARDWARE
    software-transmit     (SOF_TIMESTAMPING_TX_SOFTWARE)
    hardware-receive      (SOF_TIMESTAMPING_RX_HARDWARE)
    software-receive      (SOF_TIMESTAMPING_RX_SOFTWARE)
    software-system-clock (SOF_TIMESTAMPING_SOFTWARE)
    hardware-raw-clock    (SOF_TIMESTAMPING_RAW_HARDWARE)
PTP Hardware Clock: 0
Hardware Transmit Timestamp Modes:
    off                   (HWTSTAMP_TX_OFF)
    on                    (HWTSTAMP_TX_ON)
Hardware Receive Filter Modes:
    none                  (HWTSTAMP_FILTER_NONE)
    all                   (HWTSTAMP_FILTER_ALL)
'''


def test_ethtool_timestamp():
    timestamp = ethtool.TimeStamp(context_wrap(TEST_ETHTOOL_TIMESTAMP, path="sbin/ethtool_-T_eno1"))
    assert timestamp.ifname == 'eno1'
    assert timestamp.data['Capabilities']['hardware-transmit'] == 'SOF_TIMESTAMPING_TX_HARDWARE'
    assert timestamp.data['Capabilities']['hardware-raw-clock'] == 'SOF_TIMESTAMPING_RAW_HARDWARE'
    assert timestamp.data['PTP Hardware Clock'] == '0'
    assert timestamp.data['Hardware Transmit Timestamp Modes']['off'] == 'HWTSTAMP_TX_OFF'
    assert timestamp.data['Hardware Receive Filter Modes']['all'] == 'HWTSTAMP_FILTER_ALL'
    with pytest.raises(ParseException) as pe:
        ethtool.TimeStamp(context_wrap(TEST_ETHTOOL_TIMESTAMP_AB, path="sbin/ethtool_-T_eno1"))
        assert 'bad line:' in str(pe)


TEST_EXTRACT_FROM_PATH_1 = """
    ethtool_-a_eth0
""".strip()
TEST_EXTRACT_FROM_PATH_2 = """
    ethtool_-a_bond0.104_bond0
""".strip()
TEST_EXTRACT_FROM_PATH_3 = """
    ethtool_-a___tmp199222
""".strip()
TEST_EXTRACT_FROM_PATH_4 = """
    ethtool_-a_macvtap_bond0
""".strip()
TEST_EXTRACT_FROM_PATH_5 = """
    ethtool_-a_p3p2.2002-fcoe_p3p2
""".strip()
TEST_EXTRACT_FROM_PATH_PARAM = """
    ethtool_-a
""".strip()


def test_extract_from_path_1():
    test_data = [
        (TEST_EXTRACT_FROM_PATH_1, "eth0"),
        (TEST_EXTRACT_FROM_PATH_2, "bond0.104@bond0"),
        (TEST_EXTRACT_FROM_PATH_3, "__tmp199222"),
        (TEST_EXTRACT_FROM_PATH_4, "macvtap@bond0"),
        (TEST_EXTRACT_FROM_PATH_5, "p3p2.2002-fcoe@p3p2"),
    ]
    for input_, value in test_data:
        ifname = ethtool.extract_iface_name_from_path(input_, TEST_EXTRACT_FROM_PATH_PARAM)
        assert ifname == value


TEST_ETHTOOL_DOCS = '''
        Settings for eth0:
                Supported ports: [ TP MII ]
                Supported link modes:   10baseT/Half 10baseT/Full
                                       100baseT/Half 100baseT/Full
                Supported pause frame use: No
                Supports auto-negotiation: Yes
                Advertised link modes:  10baseT/Half 10baseT/Full
                                        100baseT/Half 100baseT/Full
                Advertised pause frame use: Symmetric
                Advertised auto-negotiation: Yes
                Link partner advertised link modes:  10baseT/Half 10baseT/Full
                                                     100baseT/Half 100baseT/Full
                Link partner advertised pause frame use: Symmetric
                Link partner advertised auto-negotiation: No
                Speed: 100Mb/s
                Duplex: Full
                Port: MII
                PHYAD: 32
                Transceiver: internal
                Auto-negotiation: on
        Cannot get wake-on-lan settings: Operation not permitted
                Current message level: 0x00000007 (7)
                                       drv probe link
        Cannot get link status: Operation not permitted
'''

ETHTOOL_INFO = """
Cannot get wake-on-lan settings: Operation not permitted
Cannot get link status: Operation not permitted
Settings for eth1:
    Supported ports: [ TP MII ]
    Supported link modes: 10baseT/Half 10baseT/Full
                          100baseT/Half 100baseT/Full
                          1000baseT/Full
    Supported pause frame use: Symmetric
    Supports auto-negotiation: Yes
    Advertised link modes: 10baseT/Half 10baseT/Full
                           100baseT/Half 100baseT/Full
                           1000baseT/Full
    Advertised pause frame use: Symmetric
    Advertised auto-negotiation: Yes
    Speed: 1000Mb/s
    Duplex: Full
    Port: Twisted Pair
    PHYAD: 1
    Transceiver: internal
    Auto-negotiation: on
    MDI-X: off (auto)
    Supports Wake-on: pumbg
    Wake-on: d
    Current message level: 0x00000007 (7)
                           drv probe link
    Link detected: yes
""".strip()

ETHTOOL_INFO_TEST = """
Settings for eth1:
    Supported pause frame use: Symmetric

    Supports auto-negotiation: Yes
""".strip()


def test_ethtool():
    ethtool_info = ethtool.Ethtool(context_wrap(ETHTOOL_INFO, path="ethtool_eth1"))
    assert ethtool_info.ifname == "eth1"
    assert ethtool_info.link_detected
    assert ethtool_info.speed == ['1000Mb/s']
    assert ethtool_info.supported_link_modes == [
        '10baseT/Half', '10baseT/Full',
        '100baseT/Half', '100baseT/Full',
        '1000baseT/Full'
    ]
    assert ethtool_info.advertised_link_modes == [
        '10baseT/Half', '10baseT/Full',
        '100baseT/Half', '100baseT/Full',
        '1000baseT/Full'
    ]
    assert ethtool_info.supported_ports == ['TP', 'MII']


def test_ethtool_corner_cases():
    ethtool_info = ethtool.Ethtool(context_wrap(ETHTOOL_INFO_TEST, path="ethtool_eth1"))
    assert ethtool_info.ifname == "eth1"


ETHTOOL_INFO_BAD_1 = """
Settings for dummy2:
No data available
""".strip()

ETHTOOL_INFO_BAD_2 = """
No data available
""".strip()

ETHTOOL_INFO_BAD_3 = """
Settings for eth1:
    Supported ports
    Supported link modes 10baseT/Half 10baseT/Full
                          100baseT/Half 100baseT/Full
"""


def test_ethtool_fail():
    with pytest.raises(ParseException):
        ethtool.Ethtool(context_wrap(FAIL_ETHTOOL_A_1, path="ethtool_eth1"))
    with pytest.raises(ParseException) as e:
        ethtool.Ethtool(context_wrap(ETHTOOL_INFO_BAD_1, path="ethtool_eth1"))
    assert "Fake ethnic as ethtool command argument" in str(e.value)

    with pytest.raises(ParseException) as e:
        ethtool.Ethtool(context_wrap(ETHTOOL_INFO_BAD_2, path="ethtool_eth1"))
    assert "Ethtool does not contain Settings for <nic>:" in str(e.value)

    with pytest.raises(ParseException) as e:
        ethtool.Ethtool(context_wrap(ETHTOOL_INFO_BAD_3, path="ethtool_eth1"))
    assert 'Ethtool unable to parse content' in str(e.value)


# Because tests are done at the module level, we have to put all the shared
# parser information in the one environment.  Fortunately this is normal.
# Also note that to support common usage, all of these are supplied in lists.
def test_ethtool_i_doc_examples():
    env = {
        'coalesce': [ethtool.CoalescingInfo(context_wrap(TEST_ETHTOOL_C_DOCS, path='ethtool_-c_eth0'))],
        'interfaces': [ethtool.Driver(context_wrap(TEST_ETHTOOL_I_DOCS, path='ethtool_-i_bond0'))],
        'ethers': [ethtool.Ethtool(context_wrap(TEST_ETHTOOL_DOCS, path='ethtool_eth0'))],
        'features': [ethtool.Features(context_wrap(ETHTOOL_K_STANDARD, path='ethtool_-k_bond0'))],
        'pause': [ethtool.Pause(context_wrap(TEST_ETHTOOL_A_DOCS, path='ethtool_-a_eth0'))],
        'ring': [ethtool.Ring(context_wrap(TEST_ETHTOOL_G_DOCS, path='ethtool_-g_eth0'))],
        'stats': [ethtool.Statistics(context_wrap(TEST_ETHTOOL_S_DOCS, path='ethtool_-S_eth0'))],
        'timestamp': [ethtool.TimeStamp(context_wrap(TEST_ETHTOOL_TIMESTAMP, path='ethtool_-T_eno1'))],
    }
    failed, total = doctest.testmod(ethtool, globs=env)
    assert failed == 0
