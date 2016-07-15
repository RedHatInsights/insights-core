from falafel.mappers.bond import bondinfo
from falafel.tests import context_wrap

CONTEXT_PATH = "proc/net/bonding/bond0"

BONDINFO = """
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


def test_bondinfo():
    bond_info = bondinfo(context_wrap(BONDINFO))
    bond_info.path = CONTEXT_PATH
    assert bond_info.bond_name().get('iface') == 'bond0'
    assert 'load balancing' in bond_info
    assert bond_info.get('Slave Interface') == \
            ['Slave Interface: eno1', 'Slave Interface: eno2']
