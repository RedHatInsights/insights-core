"""
Ethtool parsers
===============

Classes to parse ``ethtool`` command information.

The interface information for a machine is stored as lists.  Each interface
is accessed by iterating through the shared parser list.

The interface classes all provide the following properties:

* ``iface`` and ``ifname``: the interface name (derived from the output file).
* ``data``: the data for that interface

Parsers provided by this module include:

CoalescingInfo - command ``/sbin/ethtool -c {interface}``
---------------------------------------------------------

Driver - command ``/sbin/ethtool -i {interface}``
-------------------------------------------------

Ethtool - command ``/sbin/ethtool {interface}``
-----------------------------------------------

Features - command ``/sbin/ethtool -k {interface}``
---------------------------------------------------

Pause - command ``/sbin/ethtool -a {interface}``
------------------------------------------------

Ring - command ``/sbin/ethtool -g {interface}``
-----------------------------------------------

Statistics - command ``/sbin/ethtool -S {interface}``
-----------------------------------------------------

TimeStamp - command ``/sbin/ethtool -T {interface}``
----------------------------------------------------

"""

import os
import re
from collections import namedtuple
from ..parsers import ParseException
from .. import parser, LegacyItemAccess, CommandParser
from insights.specs import Specs


def extract_iface_name_from_path(path, name):
    """
    Extract the 'real' interface name from the path name.  Basically this
    puts the '@' back in the name in place of the underscore, where the name
    contains a '.' or contains 'macvtap' or 'macvlan'.

    Examples:

    +------------------+-----------------+
    | real name        | path name       |
    +==================+=================+
    | bond0.104\@bond0 | bond0.104_bond0 |
    +------------------+-----------------+
    | __tmp1111        | __tmp1111       |
    +------------------+-----------------+
    | macvtap\@bond0   | macvlan_bond0   |
    +------------------+-----------------+
    | prod_bond        | prod_bond       |
    +------------------+-----------------+
    """
    if name in path:
        ifname = os.path.basename(path).split("_", 2)[-1].strip()
        if "." in ifname or "macvtap" in ifname or "macvlan" in ifname:
            ifname = ifname.replace("_", "@")
        return ifname


def extract_iface_name_from_content(content):
    """
    Extract the interface name from the third item in the content, delimited
    by spaces, up to its second-last character.  For example, this transmutes
    ``Features for bond0:`` to ``bond0``.
    """
    return content.split(" ", 3)[-1][:-1]


@parser(Specs.ethtool_i)
class Driver(CommandParser):
    """
    Parse information for the ``ethtool -i`` command.

    All the ``ethtool -i`` outputs are stored as a list, in no particular
    order.

    Each driver is stored as a dictionary in the ``data`` property.  If the
    key starts with 'supports', then the value is a boolean test of whether
    the string is 'yes'.  If the value is not given on the string (e.g.
    'bus-info:'), the value is set to None.

    All data is also set as attributes of the object with the attribute name
    being the key name with hyphens replaced with underscores.

    Attributes:
        data (dict): Dictionary of keys with values in a list.
        iface (str): Interface name.
        driver (str): The driver providing the interface.
        version (str): The version of the interface driver.
        firmware_version (str): The firmware version of the interface.
        supports_statistics (bool): Does the interface support statistics
            gathering?
        supports_test (bool): Does the interface support internal self-tests?
        supports_eeprom_access (bool): Does the interface support access to
            the EEPROM?
        supports_register_dump (bool): Does the interface support dumping the
            internal registers?
        supports_priv_flags (bool): Does the interface support use of
            privileged flags?

    Sample input for ``/sbin/ethtool -i bond0``::

        driver: bonding
        version: 3.6.0
        firmware-version: 2
        bus-info:
        supports-statistics: no
        supports-test: no
        supports-eeprom-access: no
        supports-register-dump: no
        supports-priv-flags: no

    Examples::
        >>> len(interfaces) # All interfaces in a list
        1
        >>> type(interfaces[0])
        <class 'insights.parsers.ethtool.Driver'>
        >>> bond0 = interfaces[0] # Would normally iterate through interfaces
        >>> bond0.iface
        'bond0'
        >>> bond0.ifname
        'bond0'
        >>> bond0.data['driver'] # Old-style access
        'bonding'
        >>> bond0.driver # New-style access
        'bonding'
        >>> hasattr(bond0, 'bus_info')
        True
        >>> bond0.bus_info is None
        True
        >>> bond0.supports_statistics
        False
    """

    @property
    def ifname(self):
        """(str): the interface name"""
        return self.iface

    def parse_content(self, content):
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-i_")
        self.data = {}
        self.driver = None
        self.version = None
        self.firmware_version = None
        self.bus_info = None
        self.supports_statistics = None
        self.supports_test = None
        self.supports_eeprom_access = None
        self.supports_register_dump = None
        self.supports_priv_flags = None

        for line in content:
            if ":" in line:
                key, value = [s.strip() for s in line.split(":", 1)]
                value = value if value else None
                if key.startswith("supports"):
                    value = value == "yes"
                self.data[key] = value
                setattr(self, key.replace("-", "_"), value)


@parser(Specs.ethtool_k)
class Features(LegacyItemAccess, CommandParser):
    """
    Parse information for the ``ethtool -k`` command.

    Features are stored as a flat set of key: value pairs, with no hierarchy
    that the indentation of the input might imply.  This means, that the
    output below will provide data for 'tx-checksumming' and
    'tx-checksum-ipv4'.

    Each key stores a two-key dictionary:

    * 'on' (boolean) - whether the value (before any '[fixed]') is 'on'.
    * 'fixed' (boolean) - whether the value contains 'fixed'.

    Attributes:
        data (dict): Dictionary of keys with values in a list.
        iface (str): Interface name.

    Sample input for ``/sbin/ethtool -k bond0``::

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

    Examples:

        >>> len(features) # All interfaces in a list
        1
        >>> type(features[0])
        <class 'insights.parsers.ethtool.Features'>
        >>> bond0 = features[0] # Would normally iterate through interfaces
        >>> bond0.iface
        'bond0'
        >>> bond0.ifname
        'bond0'
        >>> bond0.data['rx-vlan-offload']['on'] # Traditional access
        True
        >>> bond0.data['rx-vlan-offload']['fixed']
        False
        >>> bond0.data['tx-checksum-sctp']['on']
        False
        >>> bond0.data['tx-checksum-sctp']['fixed']
        True
        >>> bond0.is_on('ntuple-filters')
        False
        >>> bond0.is_on('large-receive-offload')
        True
        >>> bond0.is_fixed('receive-hashing')
        False
        >>> bond0.is_fixed('fcoe-mtu')
        True
    """

    @property
    def ifname(self):
        """(str): the interface name"""
        return self.iface

    def is_on(self, feature):
        """(bool): Does this feature exist and is it on?"""
        return self.get(feature, {}).get('on', False)

    def is_fixed(self, feature):
        """(bool): Does this feature exist and is it fixed?"""
        return self.get(feature, {}).get('fixed', False)

    def parse_content(self, content):
        self.data = {}
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-k_")
        # Handle e.g. '/sbin/ethtool: file not found'
        if "ethtool" in content[0]:
            return
        # Handle 'Cannot get feature settings: Operation not supported'
        if "Cannot get" in content[0]:
            return

        # Need to strip header line that's only on -k
        for line in content[1:]:
            if ":" in line:
                key, value = [s.strip() for s in line.strip().split(":", 1)]
                fixed = "fixed" in value
                if fixed:
                    value = value.split()[0].strip()
                self.data[key.strip()] = {
                    "on": value == "on",
                    "fixed": fixed
                }


@parser(Specs.ethtool_a)
class Pause(CommandParser):
    """
    Parse information for the ``ethtool -a`` command.

    Each parameter in the input is stored as a key in a dictionary, with the
    value being whether the found string equals 'on'.

    Attributes:
        data (dict): Dictionary of keys with values in a list.
        iface (str): Interface name.
        autonegotiate (bool): Is autonegotiate present and set to 'on'?
        rx (bool): Is receive pausing present and set to 'on'?
        tx (bool): Is transmit pausing present and set to 'on'?
        rx_negotiated (bool): Is receive pause autonegotiate present and set to 'on'?
        tx_negotiated (bool): Is transmit pause autonegotiate present and set to 'on'?

    Sample input from ``/sbin/ethtool -a 0``::

        Pause parameters for eth0:
        Autonegotiate:  on
        RX:             on
        TX:             on
        RX negotiated:  off
        TX negotiated:  off

    Examples:
        >>> len(pause) # All interfaces in a list
        1
        >>> type(pause[0])
        <class 'insights.parsers.ethtool.Pause'>
        >>> eth0 = pause[0] # Would normally iterate through interfaces
        >>> eth0.iface
        'eth0'
        >>> eth0.ifname
        'eth0'
        >>> eth0.data['RX'] # Old-style accessor
        True
        >>> eth0.autonegotiate # New-style accessor
        True
        >>> eth0.rx_negotiated
        False
    """

    @property
    def ifname(self):
        return self.iface

    @property
    def autonegotiate(self):
        return self.data.get("Autonegotiate", False)

    @property
    def rx(self):
        return self.data.get("RX", False)

    @property
    def tx(self):
        return self.data.get("TX", False)

    @property
    def rx_negotiated(self):
        return self.data.get("RX Autonegotiate", False)

    @property
    def tx_negotiated(self):
        return self.data.get("TX Autonegotiate", False)

    def parse_content(self, content):
        """
        Return ethtool -a result as a dict.

        If ethtool -a outputs an error or could not get the pause state for
        the device, the "iface" property will be set but the data dictionary
        will be blank and all properties will return False.
        """
        self.data = {}
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-a_")
        # Handle e.g. '/sbin/ethtool: file not found'
        if "ethtool" in content[0]:
            return
        # Handle 'Cannot get device pause settings: Operation not supported'
        if "Cannot get" in content[0]:
            return

        for line in content[1:]:
            if line.strip():
                (key, value) = [s.strip() for s in line.split(":", 1)]
                self.data[key] = (value == "on")
                # Can't use key if it has a space in it, and we provide these
                # as properties anyway.
                # setattr(self, key, value == "on")


@parser(Specs.ethtool_c)
class CoalescingInfo(CommandParser):
    """
    Parse information for the ``ethtool -c`` command.

    The parsing is fairly similar to other ``ethtool`` parsers - the
    interface name is available as the ``ifname`` and ``iface`` properties,
    and the data about the coalescing information is stored in the ``data``
    property as a dictionary.  The one difference is the 'Adaptive RX' data,
    which is stored as two keys - 'adaptive-rx' and 'adaptive-tx', for RX
    and TX respectively.  Both these return a boolean for whether the
    respective state equals 'on'.

    Otherwise, all values are made available as keys in the ``data``
    dictionary, and as properties with the hyphen transmuted to an underscore
    - e.g. ``obj.data['tx-usecs']`` is available as ``obj.tx_usecs``.

    Attributes:
        data (dict): Dictionary of keys with values in a list.
        iface (str): Interface name.

    Sample input for ``/sbin/ethtool -c eth0``::

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

    Examples:
        >>> len(coalesce) # All interfaces in a list
        1
        >>> type(coalesce[0])
        <class 'insights.parsers.ethtool.CoalescingInfo'>
        >>> eth0 = coalesce[0] # Would normally iterate through interfaces
        >>> eth0.iface
        'eth0'
        >>> eth0.ifname
        'eth0'
        >>> eth0.data['adaptive-rx'] # Old-style accessor
        False
        >>> eth0.adaptive_rx # New-style accessor
        False
        >>> eth0.rx_usecs # Note integer value
        20
    """

    @property
    def ifname(self):
        """(str): the interface name"""
        return self.iface

    def parse_content(self, content):
        """
        Parse the output of ``ethtool -c`` into a dictionary.

        If ethtool -c outputs an error or could not get the pause state for
        the device, the "iface" property will be set but the data dictionary
        will be blank.
        """
        content = list(content)
        self.data = {}
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-c_")

        if "ethtool" in content[0]:
            return

        if "Cannot get" in content[0]:
            # cannot got pause param in ethtool
            self.iface = extract_iface_name_from_content(content[1])
            return

        self.iface = extract_iface_name_from_content(content[0])

        if len(content) <= 1:
            raise ParseException("Command output missing value data")

        second_line_content = content[1].split(" ")
        self.data["adaptive-rx"] = (second_line_content[2] == "on")
        self.adaptive_rx = (second_line_content[2] == "on")
        self.data["adaptive-tx"] = (second_line_content[5] == "on")
        self.adaptive_tx = (second_line_content[5] == "on")

        for line in content[2:]:
            if line.strip():
                (key, value) = [s.strip() for s in line.split(":", 1)]
                value = int(value)
                self.data[key] = value
                setattr(self, key.replace("-", "_"), value)


@parser(Specs.ethtool_g)
class Ring(CommandParser):
    """
    Parse information for the ``ethtool -g`` command.

    In addition to the standard ``iface`` and ``ifname`` parameters, as well
    as being available in the ``data`` property, the interface statistics
    are accessed using two parameters: ``max`` and ``current``.
    Within each the interface settings are available as four parameters -
    ``rx``, ``rx_mini``, ``rx_jumbo`` and ``tx``.

    Attributes:
        data (dict): Dictionary of keys with values in a list.
        iface (str): Interface name.
        max (dict): Dictonary of maximum ring buffer settings.
        current (dict): Dictionary of current ring buffer settings.

    Sample input for ``/sbin/ethtool -g eth0``::

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


    Examples:
        >>> len(ring) # All interfaces in a list
        1
        >>> type(ring[0])
        <class 'insights.parsers.ethtool.Ring'>
        >>> eth0 = ring[0] # Would normally iterate through interfaces
        >>> eth0.iface
        'eth0'
        >>> eth0.ifname
        'eth0'
        >>> eth0.data['max'].rx # Old-style access
        2047
        >>> eth0.max.rx # New-style access
        2047

    """

    Parameters = namedtuple("Parameters", ["rx", "rx_mini", "rx_jumbo", "tx"])

    @property
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        return self.iface

    def parse_content(self, content):
        """
        Parse ``ethtool -g`` info into a dictionary.
        """
        self.data = {}
        # First guess from path information
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-g_")
        self.max = self.current = None
        if "ethtool" in content[0]:
            return

        if "Cannot get" in content[0]:
            # cannot got pause param in ethtool
            self.iface = extract_iface_name_from_content(content[1])
            return

        self.iface = extract_iface_name_from_content(content[0])

        def set_section(section, data):
            if section:
                ringdata = Ring.Parameters(**section_data)
                setattr(self, section, ringdata)
                self.data[section] = ringdata

        section = None
        sections = {'Pre-set maximums:': 'max', 'Current hardware settings:': 'current'}
        section_data = {}
        # Skip "Ring parameters for interface:"
        for line in content[1:]:
            if line in sections:
                set_section(section, section_data)
                section = sections[line]
                section_data = {}
            elif ':' in line:
                # key: value, store in section data for now
                key, value = (s.strip() for s in line.split(":", 1))
                section_data[key.replace(" ", "_").lower()] = int(value)

        # Handle last found section, if any
        set_section(section, section_data)


@parser(Specs.ethtool_S)
class Statistics(CommandParser):
    """
    Parse information for the ``ethtool -S`` command.

    All values are made available as keys in the ``data`` dictionary, and as
    properties - e.g. ``obj.data['rx_jabbers']`` is available as
    ``obj.rx_jabbers``.

    Attributes:
        data (dict): Dictionary of keys with values in a list.
        iface (str): Interface name.

    Sample partial input for ``/sbin/ethtool -S eth0``::

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

    Examples:
        >>> len(stats) # All interfaces in a list
        1
        >>> type(stats[0])
        <class 'insights.parsers.ethtool.Statistics'>
        >>> eth0 = stats[0] # Would normally iterate through interfaces
        >>> eth0.iface
        'eth0'
        >>> eth0.ifname
        'eth0'
        >>> eth0.data['rx_octets']  # Data as integers
        808488730
        >>> eth0.data['rx_fcs_errors']
        0
    """

    @property
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        return self.iface

    def search(self, pattern, flags=0):
        """
        Finds all the parameters matching a given regular expression.

        Parameters:
            pattern (raw): A regular expression
            flags (int): Regular expression flags summed from ``re`` constants.

        Returns:
            (dict): A dictionary of the key/value pairs where the key matches
            the given regular expression.  An empty dictionary is returned if
            no keys matched.
        """
        results = {}
        for k, v in self.data.items():
            if re.search(pattern, k, flags):
                results[k] = v
        return results

    def parse_content(self, content):
        '''
        Parse the output of ``ethtool -S``.
        '''
        self.data = {}
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-S_")

        if "NIC statistics:" not in content[0]:
            # if there's no data, then return self.data immediately.
            # in this situation, content may looks like:
            # "no stats available" or
            # "Cannot get stats strings self.datarmation: Operation not supported"
            return

        for line in content[1:]:  # ignore 'NIC statistics' line
            if ':' not in line:
                continue
            # Some interfaces can report keys with colons in them, e.g.
            # "rxq0: rx_pkts", so look for the last colon and strip from
            # there.
            i = line.rfind(':')
            key = line[:i].strip()
            value = line[i + 2:].strip()
            value = int(value)
            self.data[key] = value


@parser(Specs.ethtool_T)
class TimeStamp(CommandParser):
    """
    Parse information for the ``ethtool -T`` command.

    Each parameter in the input is stored as a key in a dictionary.

    Attributes:
        data (dict): Dictionary of keys with values.

    Raises:
        ParseException: Raised when any problem parsing the command output.

    Sample partial input for ``/sbin/ethtool -T eno1``::

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

    Examples:
        >>> len(timestamp)
        1
        >>> type(timestamp[0])
        <class 'insights.parsers.ethtool.TimeStamp'>
        >>> eno1 = timestamp[0] # Would normally iterate through interfaces
        >>> eno1.ifname
        'eno1'
        >>> eno1.data['Capabilities']['hardware-transmit']
        'SOF_TIMESTAMPING_TX_HARDWARE'
        >>> eno1.data['Capabilities']['hardware-raw-clock']
        'SOF_TIMESTAMPING_RAW_HARDWARE'
        >>> eno1.data['PTP Hardware Clock']
        '0'
        >>> eno1.data['Hardware Transmit Timestamp Modes']['off']
        'HWTSTAMP_TX_OFF'
        >>> eno1.data['Hardware Receive Filter Modes']['all']
        'HWTSTAMP_FILTER_ALL'
    """
    @property
    def ifname(self):
        """(str): the interface name"""
        return self.iface

    def parse_content(self, content):
        self.data = {}
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-T_")

        group = None
        for line in content[1:]:
            if ":" in line:
                key, val = [i.strip() for i in line.split(':', 1)]
                group = {}
                self.data[key] = val if val else group
            elif line.endswith(')') and group is not None:
                key, val = [i.strip() for i in line.split(None, 1)]
                group[key] = val.strip('()')
            elif line:
                raise ParseException('bad line: {0}'.format(line))


@parser(Specs.ethtool)
class Ethtool(CommandParser):
    """
    Parses output of ``ethtool`` command.

    Raises:
        ParseException: Raised when any problem parsing the command output.

    Attributes:
        data (dict): Dictionary of keys with values in a list.
        iface (str): Interface name.
        supported_link_modes (list): A list of the 'Supported link modes'
            values, split into individual words.
        available_link_modes (list): A list of the 'Available link modes'
            values, split into individual words.
        supported_ports (list): A list of the 'Supported ports' values,
            split into individual words.

    Sample input::

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

    For historic reasons, values drawn from the data are stored as lists,
    with each item being the value on one line.

    Examples:
        >>> len(ethers) # All interfaces in a list
        1
        >>> type(ethers[0])
        <class 'insights.parsers.ethtool.Ethtool'>
        >>> ethinfo = ethers[0] # Would normally iterate through interfaces
        >>> ethinfo.ifname
        'eth0'
        >>> ethinfo.speed
        ['100Mb/s']
        >>> ethinfo.link_detected
        False
        >>> 'Cannot get link status' in ethinfo.data
        True
        >>> ethinfo.data['Cannot get link status']  # Dictionary for all data
        ['Operation not permitted']
        >>> ethinfo.data['Supported pause frame use']
        ['No']
        >>> ethinfo.data['PHYAD']  # Values as lists of strings for historic reasons
        ['32']
        >>> ethinfo.supported_link_modes  # This is collected across multiple lines and split
        ['10baseT/Half', '10baseT/Full', '100baseT/Half', '100baseT/Full']
        >>> ethinfo.advertised_link_modes
        ['10baseT/Half', '10baseT/Full', '100baseT/Half', '100baseT/Full']
        >>> ethinfo.supported_ports  # This is converted to a list of strings
        ['TP', 'MII']
    """
    @property
    def ifname(self):
        """str: Return the name of network interface in content."""
        return self.iface

    @property
    def speed(self):
        """list (str): Return field in Speed."""
        return self.data.get('Speed')

    @property
    def link_detected(self):
        """boolean: Returns field in Link detected."""
        return self.data.get('Link detected', ['no'])[0] == 'yes'

    def parse_content(self, content):
        self.data = {}
        self.iface = self.file_name.replace("ethtool_", "")

        # One way to get this result is run command '$ ethtool'.
        if "ethtool: bad command line argument(s)" in content[0]:
            raise ParseException('ethtool: bad command line argument for ethtool', content)

        if "Settings for" not in content[0]:
            raise ParseException("ethtool: unrecognised first line '{l}'".format(l=content[0]))

        self.data['ETHNIC'] = content[0].split()[-1].strip(':')

        if "No data available" in content[1]:
            raise ParseException('Fake ethnic as ethtool command argument', content)

        key = value = None
        for line in content[1:]:
            line = line.strip()
            if line:
                try:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        self.data[key] = [value.strip()]
                    else:
                        self.data[key].append(line)
                except:
                    raise ParseException('Ethtool unable to parse content', line)

        self.supported_link_modes = []
        if 'Supported link modes' in self.data:
            for pair in self.data['Supported link modes']:
                self.supported_link_modes += pair.split()

        self.advertised_link_modes = []
        if 'Advertised link modes' in self.data:
            for pair in self.data['Advertised link modes']:
                self.advertised_link_modes += pair.split()

        self.supported_ports = []
        if 'Supported ports' in self.data:
            self.supported_ports = self.data['Supported ports'][0].strip('[] ').split()
