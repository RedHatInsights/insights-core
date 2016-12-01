from falafel.mappers.bond import bondinfo, Bond
from falafel.tests import context_wrap

CONTEXT_PATH = "proc/net/bonding/bond0"

BONDINFO_1 = """
Ethernet Channel Bonding Driver: v3.7.1 (April 27, 2011)

Bonding Mode: load balancing (round-robin)
MII Status: up
MII Polling Interval (ms): 100
Up Delay (ms): 0
Down Delay (ms): 0

Slave Interface: eno1
MII Status: up
Speed: 1000 Mbps
Duplex: full
Link Failure Count: 0
Permanent HW addr: 2c:44:fd:80:5c:f8
Slave queue ID: 0

Slave Interface: eno2
MII Status: up
Speed: 1000 Mbps
Duplex: full
Link Failure Count: 0
Permanent HW addr: 2c:44:fd:80:5c:f9
Slave queue ID: 0
""".strip()

BONDINFO_MODE_4 = """
Ethernet Channel Bonding Driver: v3.2.4 (January 28, 2008)

Bonding Mode: IEEE 802.3ad Dynamic link aggregation
Transmit Hash Policy: layer2 (0)
MII Status: up
MII Polling Interval (ms): 500
Up Delay (ms): 0
Down Delay (ms): 0

802.3ad info
LACP rate: slow
Active Aggregator Info:
        Aggregator ID: 3
        Number of ports: 1
        Actor Key: 17
        Partner Key: 1
        Partner Mac Address: 00:00:00:00:00:00

Slave Interface: eth1
MII Status: up
Link Failure Count: 0
Permanent HW addr: 00:16:35:5e:42:fc
Aggregator ID: 3

Slave Interface: eth2
MII Status: up
Link Failure Count: 0
Permanent HW addr: 00:16:35:5e:02:7e
Aggregator ID: 2
""".strip()

BONDINFO_CORRUPT = """
Link Failure Count: 0
Permanent HW addr: 00:16:35:5e:02:7e
Aggregator ID:
""".strip()


def test_bondinfo():
    """The bondinfo mapper is deprecated.  Use the Bond class
    instead.
    """
    bond_info = bondinfo(context_wrap(BONDINFO_1, CONTEXT_PATH))
    assert bond_info.file_name == 'bond0'
    assert 'load balancing' in bond_info
    assert bond_info.get('Slave Interface') == \
        ['Slave Interface: eno1', 'Slave Interface: eno2']


def test_bond_class():

    bond_obj = Bond(context_wrap(BONDINFO_1, CONTEXT_PATH))
    assert bond_obj.file_name == 'bond0'
    assert not bond_obj.partner_mac_address
    assert bond_obj.bond_mode == '0'

    bond_obj = Bond(context_wrap(BONDINFO_MODE_4, CONTEXT_PATH))
    assert bond_obj.bond_mode == '4'
    assert bond_obj.partner_mac_address == "00:00:00:00:00:00"
    assert bond_obj.aggregator_id == ['3', '3', '2']

    bond_obj = Bond(context_wrap(BONDINFO_CORRUPT, CONTEXT_PATH))
    assert not bond_obj.bond_mode
