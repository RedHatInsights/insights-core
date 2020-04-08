import doctest
import pytest
from insights.parsers import ParseException
from insights.parsers.bond import Bond
from insights.parsers import bond
from insights.tests import context_wrap

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
Speed: 1000 Mbps
Duplex: full
Link Failure Count: 0
Permanent HW addr: 00:16:35:5e:42:fc
Aggregator ID: 3

Slave Interface: eth2
MII Status: up
Speed: 1000 Mbps
Duplex: full
Speed
Link Failure Count: 0
Permanent HW addr: 00:16:35:5e:02:7e
Aggregator ID: 2
""".strip()

BONDINFO_MODE_2 = """
Ethernet Channel Bonding Driver: v3.7.1 (April 27, 2011)

Bonding Mode: load balancing (xor)
Transmit Hash Policy: layer2+3 (2)
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


BONDINFO_CORRUPT = """
Link Failure Count: 0
Permanent HW addr: 00:16:35:5e:02:7e
Aggregator ID:
""".strip()

BONDINFO_UNKNOWN_BOND_MODE = """
Bonding Mode: reverse proximity hash combination mode
""".strip()


BONDINFO_MODE_5 = """
Ethernet Channel Bonding Driver: v3.7.1 (April 27, 2011)

Bonding Mode: fault-tolerance (active-backup)
Primary Slave: None
Currently Active Slave: enp17s0f0
MII Status: up
MII Polling Interval (ms): 100
Up Delay (ms): 0
Down Delay (ms): 0

Slave Interface: enp17s0f0
MII Status: up
Speed: 10000 Mbps
Duplex: full
Link Failure Count: 0
Permanent HW addr: 00:1f:f3:af:d3:f0
Slave queue ID: 0

Slave Interface: enp17s0f1
MII Status: up
Speed: 10000 Mbps
Duplex: full
Link Failure Count: 0
Permanent HW addr: 00:1f:f3:af:d3:f1
Slave queue ID: 0
""".strip()


BONDINFO_MODE_6 = BONDINFO_MODE_5.replace("Currently Active Slave: enp17s0f0", "")

BONDINFO_MODE_7 = """
Ethernet Channel Bonding Driver: v3.7.1 (April 27, 2011)

Bonding Mode: fault-tolerance (active-backup)
Primary Slave: em3 (primary_reselect failure)
Currently Active Slave: em3
MII Status: up
MII Polling Interval (ms): 0
Up Delay (ms): 0
Down Delay (ms): 0
ARP Polling Interval (ms): 1000
ARP IP target/s (n.n.n.n form): 10.152.1.1

Slave Interface: em3
MII Status: up
Speed: 1000 Mbps
Duplex: full
Link Failure Count: 92028
Permanent HW addr: 00:1f:f3:af:d3:f1
Slave queue ID: 0

Slave Interface: p2p3
MII Status: up
Speed: 1000 Mbps
Duplex: full
Link Failure Count: 71524
Permanent HW addr: 00:1f:f3:af:d3:f1
Slave queue ID: 0
""".strip()

BOND_MODE_4 = """
Ethernet Channel Bonding Driver: v3.7.1 (April 27, 2011)

Bonding Mode: IEEE 802.3ad Dynamic link aggregation
Transmit Hash Policy: layer2 (0)
MII Status: up
MII Polling Interval (ms): 100
Up Delay (ms): 2000
Down Delay (ms): 1000

802.3ad info
LACP rate: slow
Min links: 0
Aggregator selection policy (ad_select): stable
System priority: 65535
System MAC address: 08:00:27:99:a3:6b
Active Aggregator Info:
\t\t\t\tAggregator ID: 1
\t\t\t\tNumber of ports: 1
\t\t\t\tActor Key: 9
\t\t\t\tPartner Key: 1
\t\t\t\tPartner Mac Address: 00:00:00:00:00:00

Slave Interface: enp0s9
MII Status: up
Speed: 1000 Mbps
Duplex: full
Link Failure Count: 0
Permanent HW addr: 08:00:27:99:a3:6b
Slave queue ID: 0
Aggregator ID: 1
Actor Churn State: none
Partner Churn State: churned
Actor Churned Count: 0
Partner Churned Count: 1
details actor lacp pdu:
    system priority: 65535
    system mac address: 08:00:27:99:a3:6b
    port key: 9
    port priority: 255
    port number: 1
    port state: 77
details partner lacp pdu:
    system priority: 65535
    system mac address: 00:00:00:00:00:00
    oper key: 1
    port priority: 255
    port number: 1
    port state: 1

Slave Interface: enp0s8
MII Status: down
Speed: Unknown
Duplex: Unknown
Link Failure Count: 0
Permanent HW addr: 08:00:27:a2:8d:f5
Slave queue ID: 0
Aggregator ID: 2
Actor Churn State: churned
Partner Churn State: churned
Actor Churned Count: 1
Partner Churned Count: 1
details actor lacp pdu:
    system priority: 65535
    system mac address: 08:00:27:99:a3:6b
    port key: 0
    port priority: 255
    port number: 2
    port state: 69
details partner lacp pdu:
    system priority: 65535
    system mac address: 00:00:00:00:00:00
    oper key: 1
    port priority: 255
    port number: 1
    port state: 1
""".strip()


def test_netstat_doc_examples():
    env = {
        'bond_info': Bond(context_wrap(BONDINFO_MODE_4)),
    }
    failed, total = doctest.testmod(bond, globs=env)
    assert failed == 0


def test_bond_class():
    bond_obj = Bond(context_wrap(BONDINFO_1, CONTEXT_PATH))
    assert bond_obj.file_name == 'bond0'
    assert not bond_obj.partner_mac_address
    assert bond_obj.bond_mode == '0'
    assert bond_obj.slave_interface == ['eno1', 'eno2']
    assert bond_obj.up_delay == '0'
    assert bond_obj.down_delay == '0'
    assert bond_obj.data['eno1']['speed'] == '1000 Mbps'
    assert bond_obj.data['eno1']['mii_status'] == 'up'
    assert bond_obj.data['eno2']['mii_status'] == 'up'

    bond_obj = Bond(context_wrap(BONDINFO_MODE_4, CONTEXT_PATH))
    assert bond_obj.bond_mode == '4'
    assert bond_obj.partner_mac_address == "00:00:00:00:00:00"
    assert bond_obj.aggregator_id == ['3', '3', '2']
    assert bond_obj.xmit_hash_policy == "layer2"
    assert bond_obj.active_slave is None

    bond_obj = Bond(context_wrap(BONDINFO_CORRUPT, CONTEXT_PATH))
    assert bond_obj.bond_mode is None
    assert bond_obj.slave_interface == []
    assert not bond_obj.xmit_hash_policy

    bond_obj = Bond(context_wrap(BONDINFO_MODE_2, CONTEXT_PATH))
    assert bond_obj.xmit_hash_policy == "layer2+3"

    bond_obj = Bond(context_wrap(BONDINFO_MODE_5, CONTEXT_PATH))
    assert bond_obj.bond_mode == '1'
    assert bond_obj.active_slave == "enp17s0f0"

    bond_obj_2 = Bond(context_wrap(BONDINFO_MODE_6, CONTEXT_PATH))
    assert bond_obj_2.bond_mode == '1'
    assert bond_obj_2.active_slave is None

    bond_obj_3 = Bond(context_wrap(BONDINFO_1, CONTEXT_PATH))
    assert bond_obj_3.file_name == 'bond0'
    assert bond_obj_3.slave_interface == ['eno1', 'eno2']
    assert bond_obj_3.slave_duplex == ['full', 'full']
    assert bond_obj_3.slave_speed == ['1000 Mbps', '1000 Mbps']
    assert bond_obj_3.slave_link_failure_count == ['0', '0']
    assert bond_obj_3.mii_status == ['up', 'up', 'up']
    assert bond_obj_3.arp_polling_interval is None
    assert bond_obj_3.arp_ip_target is None

    bond_obj_4 = Bond(context_wrap(BONDINFO_MODE_7, CONTEXT_PATH))
    assert bond_obj_4.file_name == 'bond0'
    assert bond_obj_4.arp_polling_interval == "1000"
    assert bond_obj_4.arp_ip_target == "10.152.1.1"
    assert bond_obj_4.primary_slave == 'em3 (primary_reselect failure)'

    bond_obj = Bond(context_wrap(BOND_MODE_4, CONTEXT_PATH))
    assert bond_obj.file_name == 'bond0'
    assert bond_obj.up_delay == '2000'
    assert bond_obj.down_delay == '1000'
    assert bond_obj.data['mii_status'] == 'up'
    assert bond_obj.data['enp0s9']['mii_status'] == 'up'
    assert bond_obj.data['enp0s8']['mii_status'] == 'down'
    assert bond_obj.data['enp0s8']['aggregator_id'] == '2'
    assert bond_obj.data['enp0s9']['aggregator_id'] == '1'

    with pytest.raises(ParseException) as exc:
        bond_obj = Bond(context_wrap(BONDINFO_UNKNOWN_BOND_MODE, CONTEXT_PATH))
        assert not bond_obj.bond_mode
    assert 'Unrecognised bonding mode' in str(exc)
