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
    >>> bond_info.slave_duplex
    ['full', 'full']
    >>> bond_info.slave_speed
    ['1000 Mbps', '1000 Mbps']
"""
from insights.core import Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs

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
        self._arp_polling_interval = None
        self._arp_ip_target = None
        self._mii_polling_interval = None
        self._slave_interface = []
        self._aggregator_id = []
        self._mii_status = []
        self._slave_link_failure_count = []
        self._slave_speed = []
        self._slave_duplex = []
        self._primary_slave = None
        self._up_delay = None
        self._down_delay = None
        self._data = {}

        name_slave = None
        for line in get_active_lines(content):
            if line.startswith("Bonding Mode: "):
                raw_mode = line.split(":", 1)[1].strip()
                self._bond_mode = raw_mode
                self._data['mode'] = self._bond_mode
                if raw_mode in BOND_PREFIX_MAP:
                    self._bond_mode = BOND_PREFIX_MAP[raw_mode]
                    self._data['mode'] = self._bond_mode
                else:
                    raise ParseException("Unrecognised bonding mode '{b}'".format(b=raw_mode))
            elif line.startswith("Partner Mac Address: "):
                self._partner_mac_address = line.split(":", 1)[1].strip()
                self._data['partner_mac'] = self._partner_mac_address
            elif line.startswith("Slave Interface: "):
                name_slave = line.split(":", 1)[1].strip()
                self._slave_interface.append(name_slave)
                self._data[name_slave] = {}
            elif line.strip().startswith("Aggregator ID: "):
                agg_id = line.strip().split(':', 1)[1].strip()
                self._aggregator_id.append(agg_id)
                if name_slave:
                    self._data[name_slave]['aggregator_id'] = agg_id
                else:
                    self._data['aggregator_id'] = agg_id
            elif line.strip().startswith("Transmit Hash Policy"):
                # No need of values in bracket:
                # Integer notification (0), (1), (2) of layer2, layer3+4, layer2+3 resp
                self.xmit_hash_policy = line.split(":", 1)[1].split()[0]
            elif line.strip().startswith("Currently Active Slave"):
                self._active_slave = line.split(":", 1)[1].split()[0]
            elif line.strip().startswith("MII Status: "):
                mii_status = line.strip().split(':', 1)[1].strip()
                self._mii_status.append(mii_status)
                if name_slave:
                    self._data[name_slave]['mii_status'] = mii_status
                else:
                    self._data['mii_status'] = mii_status
            elif line.strip().startswith("Link Failure Count: "):
                link_fail_cnt = line.strip().split(':', 1)[1].strip()
                self._slave_link_failure_count.append(link_fail_cnt)
                if name_slave:
                    self._data[name_slave]['link_fail_cnt'] = link_fail_cnt
            elif line.strip().startswith("Permanent HW addr: "):
                if name_slave:
                    self._data[name_slave]['permanent_hw_addr'] = line.strip().split(':', 1)[1].strip()
            elif line.strip().startswith("Speed: "):
                speed = line.strip().split(':', 1)[1].strip()
                self._slave_speed.append(speed)
                self._data[name_slave]['speed'] = speed
            elif line.strip().startswith("Duplex: "):
                duplex = line.strip().split(':', 1)[1].strip()
                self._slave_duplex.append(duplex)
                self._data[name_slave]['duplex'] = duplex
            elif line.strip().startswith("ARP Polling Interval (ms):"):
                self._arp_polling_interval = line.strip().split(':', 1)[1].strip()
            elif line.strip().startswith("ARP IP target/s (n.n.n.n form):"):
                self._arp_ip_target = line.strip().split(':', 1)[1].strip()
            elif line.strip().startswith("MII Polling Interval (ms):"):
                self._mii_polling_interval = line.strip().split(':', 1)[1].strip()
            elif line.strip().startswith("Primary Slave"):
                self._primary_slave = line.split(":", 1)[1].strip()
            elif line.strip().startswith("Up Delay (ms):"):
                self._up_delay = line.strip().split(':', 1)[1].strip()
            elif line.strip().startswith("Down Delay (ms):"):
                self._down_delay = line.strip().split(':', 1)[1].strip()

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

    @property
    def mii_status(self):
        """Returns the master and all the slaves "MII Status" value in the bond file wrapped
        a list if the key/value exists.  If the key is not in the
        bond file, ``[]`` is returned.
        """
        return self._mii_status

    @property
    def slave_link_failure_count(self):
        """Returns all the slaves "Link Failure Count" value in the bond file wrapped
        a list if the key/value exists.  If the key is not in the
        bond file, ``[]`` is returned.
        """
        return self._slave_link_failure_count

    @property
    def slave_speed(self):
        """Returns all the slaves "Speed" value in the bond file wrapped
        a list if the key/value exists.  If the key is not in the
        bond file, ``[]`` is returned.
        """
        return self._slave_speed

    @property
    def slave_duplex(self):
        """Returns all the slave "Duplex" value in the bond file wrapped
        a list if the key/value exists.  If the key is not in the
        bond file, ``[]`` is returned.
        """
        return self._slave_duplex

    @property
    def arp_polling_interval(self):
        """Returns the arp polling interval as a string. ``None`` is returned
        if no "ARP Polling Interval (ms)" key is found.
        """
        return self._arp_polling_interval

    @property
    def arp_ip_target(self):
        """Returns the arp ip target as a string. ``None`` is returned
        if no "ARP IP target/s (n.n.n.n form)" key is found.
        """
        return self._arp_ip_target

    @property
    def mii_polling_interval(self):
        """Returns the mii polling interval as a string. ``None`` is returned
        if no "MII Polling Interval (ms)" key is found.
        """
        return self._mii_polling_interval

    @property
    def primary_slave(self):
        """Returns the "Primary Slave" in the bond file if key/value exists.
        If the key is not in the bond file, ``None`` is returned.
        """
        return self._primary_slave

    @property
    def up_delay(self):
        """Returns the "Up Delay" in the bond file if key/value exists.
        If the key is not in the bond file, ``None`` is returned.
        """
        return self._up_delay

    @property
    def down_delay(self):
        """Returns the "Down Delay" in the bond file if key/value exists.
        If the key is not in the bond file, ``None`` is returned.
        """
        return self._down_delay

    @property
    def data(self):
        """Returns all the details of bond interface and corresponding slave details
        on sucess else it will return empty ``{}``.
        """
        return self._data
