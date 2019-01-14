"""
Bond - file ``/proc/net/bonding``
=================================

Provides plugins access to the network bonding information gathered from
all the files starteing with "bond." located in the
``/proc/net/bonding`` directory.

Typical content of ``bond.*`` file is::

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

Data is modeled as an array of ``Bond`` objects (``bond`` being a
pattern file specification gathering data from files located in
``/proc/net/bonding``.

Examples:
    >>> type(bond_info)
    <class 'insights.parsers.bond.Bond'>
    >>> bond_info.bond_mode
    '4'
    >>> bond_info.partner_mac_address
    '00:00:00:00:00:00'
    >>> bond_info.slave_interface
    ['eth1', 'eth2']
    >>> bond_info.aggregator_id
    ['3', '3', '2']
    >>> bond_info.xmit_hash_policy
    'layer2'
    >>> bond_info.active_slave
"""

from insights import Parser, parser, get_active_lines
from insights.specs import Specs
from insights.parsers import ParseException


"""dict: bonding mode parameter string linked to bond type index."""
BOND_PREFIX_MAP = {
    'load balancing (round-robin)': '0',
    'fault-tolerance (active-backup)': '1',
    'fault-tolerance (active-backup) (fail_over_mac active)': '1',
    'load balancing (xor)': '2',
    'fault-tolerance (broadcast)': '3',
    'IEEE 802.3ad Dynamic link aggregation': '4',
    'transmit load balancing': '5',
    'adaptive load balancing': '6'
}


@parser(Specs.bond)
class Bond(Parser):
    """
    Models the ``/proc/net/bonding`` file.

    Currently used information from ``/proc/net/bonding`` includes
    the "bond mode" and "partner mac address".
    """

    def parse_content(self, content):
        self._bond_mode = None
        self._partner_mac_address = None
        self._active_slave = None
        self.xmit_hash_policy = None
        self._slave_interface = []
        self._aggregator_id = []

        for line in get_active_lines(content):
            if line.startswith("Bonding Mode: "):
                raw_mode = line.split(":", 1)[1].strip()
                self._bond_mode = raw_mode
                if raw_mode in BOND_PREFIX_MAP:
                    self._bond_mode = BOND_PREFIX_MAP[raw_mode]
                else:
                    raise ParseException("Unrecognised bonding mode '{b}'".format(b=raw_mode))
            elif line.startswith("Partner Mac Address: "):
                self._partner_mac_address = line.split(":", 1)[1].strip()
            elif line.startswith("Slave Interface: "):
                self._slave_interface.append(line.split(":", 1)[1].strip())
            elif line.strip().startswith("Aggregator ID: "):
                self._aggregator_id.append(line.strip().split(':', 1)[1].strip())
            elif line.strip().startswith("Transmit Hash Policy"):
                # No need of values in bracket:
                # Integer notification (0), (1), (2) of layer2, layer3+4, layer2+3 resp
                self.xmit_hash_policy = line.split(":", 1)[1].split()[0]
            elif line.strip().startswith("Currently Active Slave"):
                self._active_slave = line.split(":", 1)[1].split()[0]

    @property
    def bond_mode(self):
        """Returns the bond mode number as a string, or if there is no
        known mapping to a number, the raw "Bonding Mode" value.
        ``None`` is returned if no "Bonding Mode" key is found.
        """
        return self._bond_mode

    @property
    def partner_mac_address(self):
        """Returns the value of the "Partner Mac Address" in the bond
        file if the key/value exists.  If the key is not in the bond
        file, ``None`` is returned.
        """
        return self._partner_mac_address

    @property
    def slave_interface(self):
        """Returns all the slave interfaces of in the bond file wrapped
        a list if the key/value exists.  If the key is not in the
        bond file, ``[]`` is returned.
        """
        return self._slave_interface

    @property
    def aggregator_id(self):
        """Returns all the aggregator id of in the bond file wrapped
        a list if the key/value exists.  If the key is not in the
        bond file, ``[]`` is returned.
        """
        return self._aggregator_id

    @property
    def active_slave(self):
        """Returns the active slave of the "Currently Active Slave" in the bond
        file if key/value exists. If the key is not in the bond file, ``None``
        is returned.
        """
        return self._active_slave
