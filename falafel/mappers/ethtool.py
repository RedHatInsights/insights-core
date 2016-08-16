import os
from collections import namedtuple
from falafel.core.plugins import mapper
from falafel.core import MapperOutput, DictMapperOutput, computed


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
class Driver(MapperOutput):

    def __init__(self, data, path):
        super(Driver, self).__init__(data, path)
        for k, v in data.iteritems():
            k = k.replace('-', '_')
            if k.startswith("supports"):
                v = v == "yes"
            self._add_to_computed(k, v)

    @computed
    def ifname(self):
        return extract_iface_name_from_path(self.file_path, "ethtool_-i_")

    @classmethod
    def parse_content(cls, content):
        d = {}
        for line in content:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                value = value.strip()
                value = value if value else None
                d[key.strip()] = value
        return d


@mapper("ethtool-k")
class Features(DictMapperOutput):

    Feature = namedtuple('Feature', ['on', 'fixed'])

    def __init__(self, data, path):
        super(Features, self).__init__(data, path)
        self.dict_data = {}
        for k, v in data.iteritems():
            f = Features.Feature(v.on, v.fixed)
            self.dict_data[k] = f

    @computed
    def ifname(self):
        return extract_iface_name_from_path(self.file_path, "ethtool_-k_")

    @classmethod
    def parse_content(cls, content):
        d = {}
        # Need to strip header line that's only on -k
        for line in content[1:]:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                value = value.strip()
                fixed = "fixed" in value
                if fixed:
                    value = value.split()[0].strip()
                d[key.strip()] = {
                    "on": value == "on",
                    "fixed": fixed
                }
        return d


@mapper("ethtool-a")
class Pause(MapperOutput):

    @computed
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        if "iface" in self.data:
            return self.data.get("iface")
        return extract_iface_name_from_path(self.file_path, "ethtool_-a_")

    @computed
    def autonegotiate(self):
        return self.data.get("Autonegotiate")

    @computed
    def rx(self):
        return self.data.get("RX")

    @computed
    def tx(self):
        return self.data.get("TX")

    @computed
    def rx_negotiated(self):
        return self.data.get("RX Autonegotiate")

    @computed
    def tx_negotiated(self):
        return self.data.get("TX Autonegotiate")

    @classmethod
    def parse_content(cls, content):
        """
        Return ethtool -a result as a dict.
        If ethtool -a output a error, only return "iface" key as a network interface
        input: "RX: on"
        Output: result["RX"] = true
        """
        result = {}
        if "ethtool" in content[0]:
            return result
        if "Cannot get" in content[0]:
            # cannot got pause param in ethtool
            result["iface"] = extract_iface_name_from_content(content[1])
            return result

        result["iface"] = extract_iface_name_from_content(content[0])
        for line in content[1:]:
            if line.strip():
                (key, value) = line.split(":", 1)
                result[key.strip()] = (value.strip() == "on")
        return result


@mapper("ethtool-c")
class CoalescingInfo(MapperOutput):

    def __init__(self, data, path):
        super(CoalescingInfo, self).__init__(data, path)
        for k, v in data.iteritems():
            k = k.replace('-','_')
            self._add_to_computed(k, v)

    @computed
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        if "iface" in self.data:
            return self.data.get("iface")
        return extract_iface_name_from_path(self.file_path, "ethtool_-c_")

    @classmethod
    def parse_content(cls, content):
        """
        Return ethtool -c result as a dict
        if interface error, only return interface name
        "iface" key is network interface name
        Adaptive rx in "adaptive-rx" key, value is boolean
        Adaptive tx in "adaptive-tx" key, value is boolean
        Other value is int
        """
        result = {}
        if "ethtool" in content[0]:
            return result
        if "Cannot get" in content[0]:
            # cannot got pause param in ethtool
            result["iface"] = extract_iface_name_from_content(content[1])
            return result

        result["iface"] = extract_iface_name_from_content(content[0])

        if len(content) > 1:
            second_line_content = content[1].split(" ")
            result["adaptive-rx"] = (second_line_content[2] == "on")
            result["adaptive-tx"] = (second_line_content[5] == "on")

            for line in content[2:]:
                if line.strip():
                    (key, value) = line.split(":", 1)
                    result[key.strip()] = int(value.strip())

        return result


@mapper("ethtool-g")
class Ring(MapperOutput):

    Parameters = namedtuple("Parameters", ["rx", "rx_mini", "rx_jumbo", "tx"])

    def __init__(self, data, path):
        super(Ring, self).__init__(data, path)
        m = data.get("max")
        c = data.get("current")
        self.max = None
        self.current = None
        if m:
            self.max = Ring.Parameters(m["rx"], m["rx-mini"], m["rx-jumbo"], m["tx"])
        if c:
            self.current = Ring.Parameters(c["rx"], c["rx-mini"], c["rx-jumbo"], c["tx"])

    @computed
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        if "iface" in self.data:
            return self.data.get("iface")
        return extract_iface_name_from_path(self.file_path, "ethtool_-g_")

    @classmethod
    def parse_content(cls, content):
        """
        Return ethtool -g info into a dict contain 3 keys which is "max", "current", "iface"
        "max" and "current" dict contain "rx", "rx_mini","rx_jumbo","tx", type is int
        "iface" contain a interface name
        """
        result = {}
        if "ethtool" in content[0]:
            return result
        if "Cannot get" in content[0]:
            # cannot got pause param in ethtool
            result["iface"] = extract_iface_name_from_content(content[1])
            return result
        result["iface"] = extract_iface_name_from_content(content[0])

        # parse max value
        result["max"] = cls.parse_value(content[2:6])
        # parse current value
        result["current"] = cls.parse_value(content[7:11])

        return result

    @classmethod
    def parse_value(cls, content):
        result = {}
        for line in content:
            if line.strip():
                key, value = line.split(":", 1)
                result[key.strip().replace(" ", "-").lower()] = int(value.strip())
        return result


@mapper("ethtool-S")
class Statistics(MapperOutput):

    @computed
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        return extract_iface_name_from_path(self.file_path, "ethtool_-S_")

    @classmethod
    def parse_content(cls, content):
        '''
        return the ethtool -S result as a dict
        '''
        info = {}

        if "NIC statistics:" not in content[0]:
            # if there's no data, then return info immediately.
            # in this situation, content may looks like:
            # "no stats available" or
            # "Cannot get stats strings information: Operation not supported"
            return info

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
            if line.strip():
                key, value = line.split(':', 1)
                info[key.strip()] = int(value.strip()) if value else None
        return info


@mapper("ethtool")
class Ethtool(MapperOutput):

    @computed
    def ifname(self):
        """
        Return the name of network interface in content.
        """
        return self.data.get('ETHNIC')

    @computed
    def speed(self):
        """
        return field in Speed.
        """
        return self.data.get('Speed')

    @computed
    def link_detected(self):
        """
        returns field in Link detected.
        """
        return self.data.get('Link detected')

    @classmethod
    def parse_content(cls, content):
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
        ethtool_dict = {}
        if "Settings for" in content[0]:
            ethtool_dict['ETHNIC'] = content[0].split()[-1].strip(':')
        key = value = None
        for line in content[1:]:
            line = line.strip()
            if line:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    ethtool_dict[key] = [value.strip()]
                else:
                    ethtool_dict[key].append(line)
        return ethtool_dict
