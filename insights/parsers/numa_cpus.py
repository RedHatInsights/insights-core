"""
NUMACpus - file ``/sys/devices/system/node/node[0-9]*/cpulist``
===============================================================

This parser will parse the content from cpulist file, from individual
NUMA nodes. This parser will return data in (dict) format.

Sample Content from ``/sys/devices/system/node/node0/cpulist``::

    0-6,14-20

Examples:
    >>> type(numa_cpus_obj)
    <class 'insights.parsers.numa_cpus.NUMACpus'>
    >>> numa_cpus_obj.numa_node_name
    'node0'
    >>> numa_cpus_obj.numa_node_details() == {'numa_node_range': ['0-6', '14-20'], 'total_cpus': 14, 'numa_node_name': 'node0'}
    True
    >>> numa_cpus_obj.numa_node_cpus
    ['0-6', '14-20']
    >>> numa_cpus_obj.total_numa_node_cpus
    14
"""
from insights.core import LegacyItemAccess, Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.numa_cpus)
class NUMACpus(LegacyItemAccess, Parser):
    """
    Parse `/sys/devices/system/node/node[0-9]*/cpulist` file, return a dict
    which contains total number of CPUs per numa node.
    """

    def parse_content(self, content):
        if (not content) or (not self.file_path):
            raise SkipComponent("No Contents")

        self.data = {}
        self._cpu_ranges = []
        self.numa_node = self.file_path.rsplit("/")[-2] if self.file_path else None

        for line in content:
            total_cpus = 0
            self._cpu_ranges = line.split(',')
            self.data['numa_node_range'] = self._cpu_ranges
            self.data['numa_node_name'] = self.numa_node
            if '-' in self._cpu_ranges[0]:
                for cpu_range in self._cpu_ranges:
                    lower_num = int(cpu_range.split('-')[0])
                    higher_num = int(cpu_range.split('-')[1])
                    ncpus = (higher_num - lower_num + 1)
                    total_cpus = total_cpus + ncpus
            else:
                total_cpus = len(self._cpu_ranges)
            self.data['total_cpus'] = total_cpus

    @property
    def numa_node_name(self):
        """
        (str): It will return the CPU node name when set, else `None`.
        """
        return self.numa_node if self.numa_node else None

    @property
    def numa_node_cpus(self):
        """
        (list): It will return list of CPUs present under NUMA node when set, else `None`.
        """
        return self._cpu_ranges if self._cpu_ranges else None

    @property
    def total_numa_node_cpus(self):
        """
        (int): It will return total number of CPUs per NUMA node
        """
        return self.data['total_cpus'] if 'total_cpus' in self.data else None

    def numa_node_details(self):
        """
        (dict): it will return the number of CPUs per NUMA, NUMA node name, CPU range, when set, else `None`.
        """
        return self.data if self.data else None
