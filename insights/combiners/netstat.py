"""
Link Layer stats
================

Combiner for link layer stats. It uses the results of
the ``netstat -i`` parser and the ``ip -s link`` parser to determine the
network stats of link layer. ``ip -s link`` is the preferred source
of data and return object which can be used to access ``group_by_iface``.

Examples:
    >>> type(nstat)
    <class 'insights.combiners.netstat.NetworkStats'>
    >>> stats = nstat.group_by_iface
    >>> stats["lo"]
    {'RX-OK': 98, 'TX-OK': 100, 'MTU': 65536, 'RX-ERR': 0, 'TX-DRP': 0, 'TX-ERR': 0, 'RX-DRP': 0, 'RX-OVR': 0, 'Flg': 'LRU'}
    >>> stats["enp0s8"]
    {'RX-OK': 6, 'TX-DRP': 0, 'TX-OK': 4, 'MTU': 1500, 'RX-ERR': 0, 'TX-ERR': 0, 'RX-DRP': 0, 'RX-OVR': 0, 'Flg': 'BMRU'}
    >>> print nstat.data[0]['Iface']
    enp0s8
    >>> for dev_item in nstat.data:
    >>>     print dev_item
    {'RX-OK': '842447', 'TX-OVR': '0', 'Iface': 'bond1', 'TX-OK': '4233', 'MTU': '1500', 'Met': '0', 'RX-ERR': '0', 'TX-DRP': '0', 'TX-ERR': '0', 'RX-DRP': '0', 'RX-OVR': '0', 'Flg': 'BMmRU'}
    {'RX-OK': '422518', 'TX-OVR': '0', 'Iface': 'eth0', 'TX-OK': '1703', 'MTU': '1500', 'Met': '0', 'RX-ERR': '0', 'TX-DRP': '0', 'TX-ERR': '0', 'RX-DRP': '0', 'RX-OVR': '0', 'Flg': 'BMsRU'}
    ...
    ...
"""

from insights.core.plugins import combiner
from insights.parsers.netstat import Netstat_I
from insights.parsers.ip import IpLinkInfo
from copy import deepcopy
HANDLD_FLAGS = ["LOWER_UP", "NOARP", "NO-CARRIER"]


@combiner([Netstat_I, IpLinkInfo])
class NetworkStats(object):
    """
    A combiner for working with both ``netstat -i`` and ``ip -s link`` That is if
    ``netstat -i`` gets deprecated then we can continue with ``ip -s link``.

    This interface closely follow interface Netstat_I it has following Attributes:

    Attributes:
        group_by_iface(dict): This property returns network stats organised per interface in dict format.
        data (list): List of network stats as per devices.
    """

    def __init__(self, net_stats, ip_stats):
        self.group_by_iface = {}
        self.data = []
        if net_stats:
            self.data = net_stats.data
            ldata = deepcopy(self.data)
            self.group_by_iface = self._group_by_iface(ldata)
        elif ip_stats:
            self.group_by_iface, self.data = self._organize_for_netstat(ip_stats.data)

    def _group_by_iface(self, ldata):
        periface = {}
        for ifdata in ldata:
            iface_name = ifdata["Iface"]
            del ifdata["Iface"]
            periface[iface_name] = ifdata
        return periface

    def _organize_for_netstat(self, ldata):

        def _get_flags(flags):
            flg_str = ""
            if "NOARP" in flags:
                flg_str += "O"
            elif "NO-CARRIER" not in flags or "LOWER_UP" in flags:
                flg_str += "R"
            for i in flags:
                if i not in HANDLD_FLAGS:
                    flg_str += str(i[0])
            flg_str = ''.join(sorted(flg_str))
            return flg_str

        stats = {}
        data = []
        map_table = {"MTU": "mtu", "RX-OK": "rx_packets", "RX-ERR": "rx_errors",
                "RX-DRP": "rx_dropped", "RX-OVR": "rx_overrun",
                "TX-OK": "tx_packets", "TX-ERR": "tx_errors", "Iface": "name",
                "TX-DRP": "tx_dropped"}

        for (k, v) in ldata.items():
            ifstat = {}
            for key_idx, value_idx in map_table.items():
                ifstat[key_idx] = v[value_idx]
            flg_str = _get_flags(v["flags"])
            ifstat["Flg"] = flg_str
            data_add = deepcopy(ifstat)
            data.append(data_add)
            del ifstat["Iface"]
            stats[v["name"]] = ifstat
        return stats, data
