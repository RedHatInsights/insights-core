"""
Bond
====

Provides plugins access to the network bonding information gathered from
all the files starteing with "bond." located in the
``/proc/net/bonding`` directory.

Typical content of ``bond.*`` file is:

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

Data is modeled as an array of ``Bond`` objects (``bond`` being a
pattern file specification gathering data from files located in
``/proc/net/bonding``.

The ``bondinfo`` method is deprecated.  Plugins should use the ``Bond``
class instead.
"""
from .. import Mapper, LogFileOutput, mapper, get_active_lines

BOND_4_INDICATOR = "Bonding Mode: IEEE 802.3ad Dynamic link aggregation"
"""Deprecated, used by the deprecated ``bondinfo`` function"""

BOND_PREFIX_MAP = [
        ('load balancing (round-robin)', '0'),
        ('fault-tolerance (active-backup)', '1'),
        ('load balancing (xor)', '2'),
        ('fault-tolerance (broadcast)', '3'),
        ('IEEE 802.3ad Dynamic link aggregation', '4'),
        ('transmit load balancing', '5'),
        ('adaptive load balancing', '6')
]


@mapper('bond')
class Bond(Mapper):
    """Models the ``/proc/net/bonding`` file.

    Currently used information from ``/proc/net/bonding`` includes
    the "bond mode" and "partner mac address".
    """

    def parse_content(self, content):
        mode = None
        partner_mac_address = None
        slave_interface = []

        for line in get_active_lines(content):
            if line.startswith("Bonding Mode: "):
                raw_mode = line.split(":", 1)[1].strip()
                for prefix_map_item in BOND_PREFIX_MAP:
                    if raw_mode.startswith(prefix_map_item[0]):
                        mode = prefix_map_item[1]
                        break
                else:
                    mode = raw_mode
            elif line.startswith("Partner Mac Address: "):
                partner_mac_address = line.split(":", 1)[1].strip()
            elif line.startswith("Slave Interface: "):
                slave_interface.append(line.split(":", 1)[1].strip())

        self.bond_mode = mode
        """Returns the bond mode number as a string, or if there is no
        known mapping to a number, the raw "Bonding Mode" value.
        ``None`` is returned if no "Bonding Mode" key is found.
        """
        self.partner_mac_address = partner_mac_address
        """Returns the value of the "Partner Mac Address" in the bond
        file if the key/value exists.  If the key is not in the bond
        file, ``None`` is returned.
        """
        self.slave_interface = slave_interface
        """Returns all the slave interfaces of in the bond file wrapped
        a list if the key/value exists.  If the key is not in the
        bond file, ``[]`` is returned.
        """


@mapper('bond')
def bondinfo(context):
    """Deprecated, use Bond instead."""
    return LogFileOutput(context)
