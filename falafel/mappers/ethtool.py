import os
import re
from collections import namedtuple
from .. import Mapper, mapper, LegacyItemAccess


def extract_iface_name_from_path(path, name):
    """
    extract iface name from path
    there are some special name:
    |----------------|----------------|
    |   real name    |   path name    |
    |----------------|----------------|
    | bond0.104@bond0|bond0.104_bond0 |
    |  __tmp1111     |  __tmp1111     |
    |  macvtap@bond0 |  macvlan_bond0 |
    |  prod_bond     |  prod_bond     |
    |----------------|----------------|
    """
    if name in path:
        ifname = os.path.basename(path).split("_", 2)[-1].strip()
        if "." in ifname or "macvtap" in ifname or "macvlan" in ifname:
            ifname = ifname.replace("_", "@")
        return ifname


def extract_iface_name_from_content(content):
    return content.split(" ", 3)[-1][:-1]


@mapper("ethtool-i")
class Driver(Mapper):

    driver = None
    version = None
    firmware_version = None
    supports_statistics = None
    supports_test = None
    supports_eeprom_access = None
    supports_register_dump = None
    supports_priv_flags = None

    @property
    def ifname(self):
        return self.iface

    def parse_content(self, content):
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-i_")
        self.data = {}
        for line in content:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                key, value = key.strip(), value.strip()
                value = value if value else None
                if key.startswith("supports"):
                    value = value == "yes"
                self.data[key] = value
                setattr(self, key.replace("-", "_"), value)


@mapper("ethtool-k")
class Features(LegacyItemAccess, Mapper):

    @property
    def ifname(self):
        return extract_iface_name_from_path(self.file_path, "ethtool_-k_")

    def is_on(self, feature):
        return self.get(feature, {}).get('on', None)

    def is_fixed(self, feature):
        return self.get(feature, {}).get('fixed', None)

    def parse_content(self, content):
        self.data = {}
        # Need to strip header line that's only on -k
        for line in content[1:]:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                value = value.strip()
                fixed = "fixed" in value
                if fixed:
                    value = value.split()[0].strip()
                self.data[key.strip()] = {
                    "on": value == "on",
                    "fixed": fixed
                }


@mapper("ethtool-a")
class Pause(Mapper):

    @property
    def ifname(self):
        return self.iface

    @property
    def autonegotiate(self):
        return self.data.get("Autonegotiate")

    @property
    def rx(self):
        return self.data.get("RX")

    @property
    def tx(self):
        return self.data.get("TX")

    @property
    def rx_negotiated(self):
        return self.data.get("RX Autonegotiate")

    @property
    def tx_negotiated(self):
        return self.data.get("TX Autonegotiate")

    def parse_content(self, content):
        """
        Return ethtool -a result as a dict.
        If ethtool -a output a error, only return "iface" key as a network interface
        input: "RX: on"
        Output: result["RX"] = true
        """
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-a_")
        self.data = {}
        if "ethtool" in content[0]:
            return
        if "Cannot get" in content[0]:
            # cannot got pause param in ethtool
            self.iface = extract_iface_name_from_content(content[1])
            return

        self.iface = extract_iface_name_from_content(content[0])
        for line in content[1:]:
            if line.strip():
                (key, value) = line.split(":", 1)
                key, value = key.strip(), value.strip()
                self.data[key] = (value == "on")
                setattr(self, key, value == "on")
        return self.data


@mapper("ethtool-c")
class CoalescingInfo(Mapper):

    @property
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        return self.iface

    def parse_content(self, content):
        """
        Return ethtool -c result as a dict
        if interface error, only return interface name
        "iface" key is network interface name
        Adaptive rx in "adaptive-rx" key, value is boolean
        Adaptive tx in "adaptive-tx" key, value is boolean
        Other value is int
        """
        content = list(content)
        self.data = {}

        if "ethtool" in content[0]:
            return

        if "Cannot get" in content[0]:
            # cannot got pause param in ethtool
            self.iface = extract_iface_name_from_content(content[1])
            return

        self.iface = extract_iface_name_from_content(content[0])

        if len(content) > 1:
            second_line_content = content[1].split(" ")
            self.data["adaptive-rx"] = (second_line_content[2] == "on")
            self.data["adaptive-tx"] = (second_line_content[5] == "on")

            for line in content[2:]:
                if line.strip():
                    (key, value) = line.split(":", 1)
                    key, value = key.strip(), value.strip()
                    self.data[key] = int(value)
            for key, value in self.data.iteritems():
                setattr(self, key.replace("-", "_"), value)


@mapper("ethtool-g")
class Ring(Mapper):

    Parameters = namedtuple("Parameters", ["rx", "rx_mini", "rx_jumbo", "tx"])

    @property
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        return self.iface

    def parse_content(self, content):
        """
        Return ethtool -g info into a dict contain 3 keys which is "max", "current", "iface"
        "max" and "current" dict contain "rx", "rx_mini","rx_jumbo","tx", type is int
        "iface" contain a interface name
        """
        self.data = {}
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-g_")
        self.max = self.current = None
        if "ethtool" in content[0]:
            return

        if "Cannot get" in content[0]:
            # cannot got pause param in ethtool
            self.iface = extract_iface_name_from_content(content[1])
            return

        self.iface = extract_iface_name_from_content(content[0])

        # parse max value
        self.max = self.data["max"] = Ring.parse_value(content[2:6])
        # parse current value
        self.current = self.data["current"] = Ring.parse_value(content[7:11])

        return self.data

    @staticmethod
    def parse_value(content):
        r = {}
        for line in content:
            if line.strip():
                key, value = line.split(":", 1)
                r[key.strip().replace(" ", "-").lower()] = int(value.strip())
        return Ring.Parameters(r["rx"], r["rx-mini"], r["rx-jumbo"], r["tx"])


@mapper("ethtool-S")
class Statistics(Mapper):

    @property
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        return self.iface

    def search(self, pattern, flags=0):
        results = {}
        for k, v in self.data.iteritems():
            if re.search(pattern, k, flags):
                results[k] = v
        return results

    def parse_content(self, content):
        '''
        return the ethtool -S result as a dict
        '''
        self.data = {}
        self.iface = extract_iface_name_from_path(self.file_path, "ethtool_-S_")

        if "NIC statistics:" not in content[0]:
            # if there's no data, then return self.data immediately.
            # in this situation, content may looks like:
            # "no stats available" or
            # "Cannot get stats strings self.datarmation: Operation not supported"
            return

        for line in content[1:]:  # ignore first line
            # the correct description lines look like below, but we will ignore the
            # first line "NIC statistics":
            # ~~~~~
            # NIC statistics:
            #     rx_packets: 7357503
            #     tx_packets: 7159010
            #     rx_bytes: 1687906514
            #     tx_bytes: 2747645082
            # ...
            # ~~~~~
            line = line.strip()
            if line:
                i = line.rfind(':')
                if i != -1:
                    key = line[:i].strip()
                    value = line[i:].strip(': ')
                    value = int(value) if value else None
                    self.data[key] = value


@mapper("ethtool")
class Ethtool(Mapper):

    @property
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        return self.iface

    @property
    def speed(self):
        """
        return field in Speed.
        """
        return self.data.get('Speed')

    @property
    def link_detected(self):
        """
        returns field in Link detected.
        """
        return self.data.get('Link detected', ['no'])[0] == 'yes'

    def parse_content(self, content):
        """
        Returns an object of EthtoolInfo
        -----------------------------------------------------
        Settings for eth1:
            Supported ports: [ TP ]
            Supported link modes: 10baseT/Half 10baseT/Full
                                  100baseT/Half 100baseT/Full
                                  1000baseT/Full
            Supported pause frame use: Symmetric
            Supports auto-negotiation: Yes
            Advertised link modes: 10baseT/Half 10baseT/Full
                                   100baseT/Half 100baseT/Full
                                   1000baseT/Full

            Current message level: 0x00000007 (7)
                                   drv probe link
        -----------------------------------------------------
        After using pandas to do some more research, I found
        the value of the current multi-line parameters
        "Supported link modes" could also be a sigle line and
        the current single line para "Supported pause frame use"
        could also be multi-line. Since the multi-line or
        single-line is not fixable, I just put the value in the list.
        """
        self.data = {}
        self.iface = self.file_name.replace("ethtool_", "")

        if "Settings for" in content[0]:
            self.data['ETHNIC'] = content[0].split()[-1].strip(':')
        key = value = None
        for line in content[1:]:
            line = line.strip()
            if line:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    self.data[key] = [value.strip()]
                else:
                    self.data[key].append(line)
