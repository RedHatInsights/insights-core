import pytest
import unittest
import re

from insights.tests import context_wrap
from insights.mappers import ethtool, ParseException
from insights.util import keys_in


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


class TestEthtool_A(unittest.TestCase):
    def test_ethtool_a(self):
        context = context_wrap(SUCCESS_ETHTOOL_A)
        context.path = SUCCESS_ETHTOOL_A_PATH
        result = ethtool.Pause(context)
        self.assertEqual(result.ifname, "enp0s25")
        self.assertEqual(result.autonegotiate, True)
        self.assertEqual(result.rx, False)
        self.assertEqual(result.tx, False)
        self.assertEqual(result.rx_negotiated, False)
        self.assertEqual(result.tx_negotiated, False)

    def test_ethtool_a_1(self):
        context = context_wrap(FAIL_ETHTOOL_A)
        context.path = FAIL_ETHTOOL_A_PATH
        result = ethtool.Pause(context)
        self.assertEqual(result.ifname, "__wlp3s0")
        self.assertFalse(result.autonegotiate)

    def test_ethtool_a_2(self):
        context = context_wrap(FAIL_ETHTOOL_A_1)
        context.path = FAIL_ETHTOOL_A_PATH_1
        result = ethtool.Pause(context)
        self.assertEqual(result.ifname, "bond0.1384@bond0")

    def test_ethtool_a_3(self):
        context = context_wrap(FAIL_ETHTOOL_A_2)
        context.path = FAIL_ETHTOOL_A_PATH_2
        result = ethtool.Pause(context)
        self.assertEqual(result.ifname, "g_bond2")


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


class TestEthtool_C(unittest.TestCase):
    def test_get_ethtool_c(self):
        context = context_wrap(TEST_ETHTOOL_C)
        context.path = TEST_ETHTOOL_C_PATH
        result = ethtool.CoalescingInfo(context)
        self.assertTrue(keys_in(["adaptive-rx", "adaptive-tx", "pkt-rate-high",
                                 "tx-usecs-irq", "tx-frame-low", "tx-usecs-high", "tx-frame-high"], result.data))
        self.assertEqual(result.ifname, "eth2")
        self.assertFalse(result.adaptive_rx)
        self.assertFalse(result.adaptive_tx)
        self.assertEqual(result.pkt_rate_high, 10)
        self.assertEqual(result.tx_usecs_irq, 0)
        self.assertEqual(result.tx_frame_low, 25)
        self.assertEqual(result.tx_usecs_high, 0)
        self.assertEqual(result.tx_frame_high, 0)

    def test_get_ethtool_c_cannot_get(self):
        context = context_wrap(TEST_ETHTOOL_C_CANNOT_GET)
        context.path = 'sos_commands/networking/ethtool_-c_usb0'
        result = ethtool.CoalescingInfo(context)
        self.assertEquals(result.ifname, 'usb0')

    def test_get_ethtool_c_bad_args(self):
        context = context_wrap(TEST_ETHTOOL_C_BAD_ARGS)
        context.path = 'sos_commands/networking/ethtool_-c_eth0'
        result = ethtool.CoalescingInfo(context)
        self.assertEquals(result.ifname, 'eth0')


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


class TestEthtool_G(unittest.TestCase):
    def test_ethtool_g(self):
        context = context_wrap(TEST_ETHTOOL_G)
        context.path = TEST_ETHTOOL_G_PATH
        result = ethtool.Ring(context)
        self.assertTrue(keys_in(["max", "current"], result.data))
        self.assertEqual(result.ifname, "eth2")
        self.assertEqual(result.max.rx, 2047)
        self.assertEqual(result.max.rx_mini, 0)
        self.assertEqual(result.max.rx_jumbo, 0)
        self.assertEqual(result.max.tx, 511)

        self.assertEqual(result.current.rx, 200)
        self.assertEqual(result.current.rx_mini, 0)
        self.assertEqual(result.current.rx_jumbo, 0)
        self.assertEqual(result.current.tx, 511)

    def test_ethtool_g_1(self):
        context = context_wrap(TEST_ETHTOOL_G_1)
        context.path = TEST_ETHTOOL_G_PATH_1
        result = ethtool.Ring(context)
        self.assertEqual(result.ifname, "bond0.102@bond0")

    def test_ethtool_g_2(self):
        context = context_wrap(TEST_ETHTOOL_G_2)
        context.path = TEST_ETHTOOL_G_PATH_2
        result = ethtool.Ring(context)
        self.assertEqual(result.ifname, "eth2")


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
"""


class TestEthtool_I(unittest.TestCase):

    def test_good(self):
        context = context_wrap(TEST_ETHTOOL_I_GOOD)
        parsed = ethtool.Driver(context)
        assert parsed.version == "1.0.0"

    def test_missing_version(self):
        context = context_wrap(TEST_ETHTOOL_I_MISSING_KEYS)
        parsed = ethtool.Driver(context)
        assert parsed.version is None

    def test_missing_value(self):
        context = context_wrap(TEST_ETHTOOL_I_GOOD)
        parsed = ethtool.Driver(context)
        assert parsed.firmware_version is None

    def test_iface(self):
        context = context_wrap(TEST_ETHTOOL_I_GOOD, path="sbin/ethtool_-i_eth0")
        parsed = ethtool.Driver(context)
        assert parsed.ifname == "eth0"

    def test_no_iface(self):
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


class TestEthtool_K(unittest.TestCase):
    def test_Features_good(self):
        # Test picking up interface from header line rather than path
        features = ethtool.Features(
            context_wrap(ETHTOOL_K_STANDARD, path='sos_commands/networking/ethtool_-k_bond0'))
        self.assertEqual(features.ifname, 'bond0')
        self.assertEqual(features.iface, 'bond0')

        self.assertFalse(features.is_on('rx-checksumming'))
        self.assertTrue(features.is_on('tx-checksumming'))

        self.assertTrue(features.is_fixed('rx-checksumming'))
        self.assertFalse(features.is_fixed('tx-checksumming'))

    def test_Features_bad_args(self):
        # Even if content is bad, interface should be available from path
        features = ethtool.Features(
            context_wrap(ETHTOOL_K_BAD_ARGS, path="sbin/ethtool_-k_bond0"))
        self.assertEqual(features.ifname, 'bond0')
        self.assertEqual(features.iface, 'bond0')

        self.assertEqual(features.data, {})

    def test_Features_cannot_get(self):
        features = ethtool.Features(
            context_wrap(ETHTOOL_K_CANNOT_GET, path="sbin/ethtool_-k_eth1"))
        self.assertEqual(features.ifname, 'eth1')
        self.assertEqual(features.iface, 'eth1')

        self.assertEqual(features.data, {})


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


class TestEthtool_S(unittest.TestCase):
    def test_ethtool_S(self):
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
        self.assertEqual(ethtool_S_info.search(r'RX_QUEUE_3', flags=re.IGNORECASE), {
            'rx_queue_3_packets': 0,
            'rx_queue_3_bytes': 0,
            'rx_queue_3_drops': 0,
            'rx_queue_3_csum_err': 0,
            'rx_queue_3_alloc_failed': 0,
        })

    def test_ethtool_S_subinterface(self):
        ethtool_S_info = ethtool.Statistics(context_wrap(ETHTOOL_S_eth0_1))
        self.assertEqual(
            sorted(ethtool_S_info.data.keys()),
            sorted(['rxq0: rx_pkts', 'rxq0: rx_drops_no_frags',
                'rxq1: rx_pkts', 'rxq1: rx_drops_no_frags'])
        )
        self.assertEqual(ethtool_S_info.data['rxq0: rx_pkts'], 5000000)

    def test_ethtool_S_f(self):
        ethtool_S_info_f1 = ethtool.Statistics(context_wrap(FAILED_ETHTOOL_S_ONE))
        self.assertFalse(ethtool_S_info_f1.ifname)
        ethtool_S_info_f2 = ethtool.Statistics(context_wrap(FAILED_ETHTOOL_S_TWO))
        self.assertFalse(ethtool_S_info_f2.ifname)
        ethtool_S_info_f2 = ethtool.Statistics(context_wrap(FAILED_ETHTOOL_S_THREE))
        self.assertFalse(ethtool_S_info_f2.ifname)


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


class TestEthtool_ifname(unittest.TestCase):
    def test_extract_from_path_1(self):
        ifname = ethtool.extract_iface_name_from_path(TEST_EXTRACT_FROM_PATH_1, TEST_EXTRACT_FROM_PATH_PARAM)
        self.assertEqual(ifname, "eth0")
        ifname = ethtool.extract_iface_name_from_path(TEST_EXTRACT_FROM_PATH_2, TEST_EXTRACT_FROM_PATH_PARAM)
        self.assertEqual(ifname, "bond0.104@bond0")
        ifname = ethtool.extract_iface_name_from_path(TEST_EXTRACT_FROM_PATH_3, TEST_EXTRACT_FROM_PATH_PARAM)
        self.assertEqual(ifname, "__tmp199222")
        ifname = ethtool.extract_iface_name_from_path(TEST_EXTRACT_FROM_PATH_4, TEST_EXTRACT_FROM_PATH_PARAM)
        self.assertEqual(ifname, "macvtap@bond0")
        ifname = ethtool.extract_iface_name_from_path(TEST_EXTRACT_FROM_PATH_5, TEST_EXTRACT_FROM_PATH_PARAM)
        self.assertEqual(ifname, "p3p2.2002-fcoe@p3p2")


ETHTOOL_INFO = """
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


class TestEthtool(unittest.TestCase):
    def test_ethtool(self):
        ethtool_info = ethtool.Ethtool(context_wrap(ETHTOOL_INFO, path="ethtool_eth1"))
        self.assertEqual(ethtool_info.ifname, "eth1")
        self.assertTrue(ethtool_info.link_detected)
        self.assertEqual(ethtool_info.speed, ['1000Mb/s'])
        self.assertEqual(ethtool_info.supported_link_modes,
                         ['10baseT/Half', '10baseT/Full',
                          '100baseT/Half', '100baseT/Full',
                          '1000baseT/Full'])
        self.assertEqual(ethtool_info.advertised_link_modes,
                         ['10baseT/Half', '10baseT/Full',
                          '100baseT/Half', '100baseT/Full',
                          '1000baseT/Full'])
        self.assertEqual(ethtool_info.supported_ports,
                         ['TP', 'MII'])

    def test_ethtool_fail(self):
        with pytest.raises(ParseException):
            ethtool.Ethtool(context_wrap(FAIL_ETHTOOL_A_1, path="ethtool_eth1"))
