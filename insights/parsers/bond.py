"""
bonding - File /proc/net/bonding
================================

Provides plugins access to the network bonding information gathered from
all the files starteing with "bond." located in the
``/proc/net/bonding`` directory.

Typical content of ``bond.*`` file is::

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

Examples:
    >>> bond_info = shared[Bond]
    >>> bond_info.bond_mode
    '0'
    >>> bond_info.partner_mac_address
    None
    >>> bond_info.slave_interface
    ['eno1', 'eno2']
    >>> bond_info.aggregator_id
    ['3', '2', '3']
"""
from .. import Parser, parser, get_active_lines

BOND_PREFIX_MAP = [
        ('load balancing (round-robin)', '0'),
        ('fault-tolerance (active-backup)', '1'),
        ('load balancing (xor)', '2'),
        ('fault-tolerance (broadcast)', '3'),
        ('IEEE 802.3ad Dynamic link aggregation', '4'),
        ('transmit load balancing', '5'),
        ('adaptive load balancing', '6')
]
"""list: List of strings indicating bonding mode parameter."""


@parser('bond')
class Bond(Parser):
    """Models the ``/proc/net/bonding`` file.

    Currently used information from ``/proc/net/bonding`` includes
    the "bond mode" and "partner mac address".

    Attributes:
        bond_mode (str): Bond mode number as a string, or if there is no
            known mapping to a number, the raw "Bonding Mode" value. Default is
            ``None`` if no "Bonding Mode" key is found.
        partner_mac_address (str): Value of the "Partner Mac Address" in the bond
            file if the key/value exists. Default is ``None``.
        slave_interface (list): List of the slave interfaces in the bond file
            if the key/value exists. Default is ``[]``.
        aggregator_id (list): List of the "Aggregator ID" in the bond file
            if the key/value exists. Default is ``[]``.
    """

    def parse_content(self, content):
        self._bond_mode = None
        self._partner_mac_address = None
        self._slave_interface = []
        self._aggregator_id = []

        for line in get_active_lines(content):
            if line.startswith("Bonding Mode: "):
                raw_mode = line.split(":", 1)[1].strip()
                self._bond_mode = raw_mode
                for prefix_map_item in BOND_PREFIX_MAP:
                    if raw_mode.startswith(prefix_map_item[0]):
                        self._bond_mode = prefix_map_item[1]
                        break
            elif line.startswith("Partner Mac Address: "):
                self._partner_mac_address = line.split(":", 1)[1].strip()
            elif line.startswith("Slave Interface: "):
                self._slave_interface.append(line.split(":", 1)[1].strip())
            elif line.strip().startswith("Aggregator ID: "):
                self._aggregator_id.append(line.strip().split(':', 1)[1].strip())

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
