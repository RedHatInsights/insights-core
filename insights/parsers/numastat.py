"""
NUMAStat - Commands ``numactl`` and ``numastat``
================================================

Shared parsers for parsing commands ``numastat``, ``numastat -m`` and
``numactl --hardware``.

Parsers included in this module are:

``NUMAStat`` - command ``numastat``

``NUMAStatMem`` - command ``numastat -m``

``NUMActlHw`` - command ``numactl --hardware`` (WIP)

"""

from .. import parser, CommandParser
from ..parsers.meminfo import MemInfo, AnonMemInfo, FileMemInfo, SlabMemInfo, HugePageMemInfo
from insights.specs import Specs
import re
from os import linesep


@parser(Specs.numastat)
class NUMAStat(CommandParser, dict):
    """
    Class to process the output of ``numastat`` command.

    From the manpages:

        ``numa_hit`` memory successfully allocated on this node as intended.

        ``numa_miss`` memory allocated on this node despite the process preferring some different node. Each numa_miss has a numa_foreign on another node.

        ``numa_foreign`` memory intended for this node, but actually allocated on some different node. Each numa_foreign has a numa_miss on another node.

        ``interleave_hit`` interleaved memory successfully allocated on this node as intended.

        ``local_node`` memory allocated on this node while a process was running on it.

        ``other_node`` memory allocated on this node while a process was running on some other node.

    Attributes:


        NUMAStat (dict): A dict containing key, value for each line of the output in the form::

            'Total': {
                        'foreign': 92981,
                        'hit': 7505232220,
                        'interleave_hit': 118930,
                        'local_node': 7503867555,
                        'miss': 92981,
                        'other_node': 1457646
            },
            'node0': {
                        'foreign': 92981,
                        'hit': 4735090719,
                        'interleave_hit': 59485,
                        'local_node': 4734323881,
                        'miss': 0,
                        'other_node': 766838
            },
            'node1': {
                        'foreign': 0,
                        'hit': 2770141501,
                        'interleave_hit': 59445,
                        'local_node': 2769543674,
                        'miss': 92981,
                        'other_node': 690808
            }

        nodes (list): A list containing all numa nodes

        total_hits (dict): Total number of hits, misses and foreign for each nodes::

            {'Total': 7505418182, 'node0': 4735183700, 'node1': 2770234482}

        percent_miss (dict): Percentage of misses of all nodes::

            {'Total': 0.0, 'node0': 0.0, 'node1': 0.0}

        percent_foreign (dict): Percentage of foreign of all nodes::

            {'Total': 0.0, 'node0': 0.0, 'node1': 0.0}

        percent_load (dict): Show the percentage of hits on each node::

            {'Total': 100.0, 'node0': 63.09, 'node1': 36.91}

    Sample output::

                                   node0           node1
        numa_hit              2275454343      1714113351
        numa_miss                      0               0
        numa_foreign                   0               0
        interleave_hit            221986          223091
        local_node            2275111046      1713807637
        other_node                343297          305714

    Examples:

        >>> numastat.percent_load
        {'node0': 100.0, 'Total': 100.0}
        >>> numastat.total_hits
        {'node0': 7543691179, 'Total': 7543691179}
        >>> numastat.nodes
        ['node0', 'Total']
        >>> numastat.percent_miss
        {'node0': 0.0, 'Total': 0.0}
        >>> numastat
        {'node0': {'hit': 7543691179,
          'miss': 0,
          'foreign': 0,
          'interleave_hit': 23138,
          'local_node': 7543691179,
          'other_node': 0},
         'Total': {'hit': 7543691179,
          'miss': 0,
          'foreign': 0,
          'interleave_hit': 23138,
          'local_node': 7543691179,
          'other_node': 0}}
        >>> numastat['node0']['miss']
        0

    """

    def parse_content(self, content):
        self.nodes = []
        for line in content:
            linesplit = line.split()
            if re.match(r'node[\d]+', linesplit[0]):
                self.nodes = linesplit
                self.nodes.append('Total')
                for node in self.nodes:
                    self[node] = {}
                continue
            keyname = linesplit.pop(0).replace('numa_', '')
            self['Total'][keyname] = 0
            for idx, val in enumerate(linesplit):
                self[self.nodes[idx]][keyname] = int(val)
                self['Total'][keyname] += int(val)

    @property
    def total_hits(self):
        return dict((h, i['miss'] + i['hit'] + i['foreign']) for h, i in self.items())

    @property
    def percent_miss(self):
        return dict((h, round(i['miss'] / self.total_hits[h] * 100, 2)) for h, i in self.items())

    @property
    def percent_foreign(self):
        return dict((h, round(i['foreign'] / self.total_hits[h] * 100, 2)) for h, i in self.items())

    @property
    def percent_load(self):
        return dict((h, round(self.total_hits[h] / self.total_hits['Total'] * 100, 2)) for h, i in self.items())


@parser(Specs.numastat_memory)
class NUMAStatMem(CommandParser, dict):
    """
    Class to process the output of ``numastat -m`` command.
    This generates a dict of ``MemInfo`` objects.
    Details: https://access.redhat.com/solutions/406773

    Attributes:

        NUMAStatMem (dict): A dict containing key, value for each line of the output in the form of::

            'Total': {
               'active': 7631.63,
               'active(anon)': 785.01,
               'active(file)': 6846.62,
               'anonhugepages': 0,
               'anonpages': 893.05,
               'bounce': 0.0,
               'calculated_anonhugepages': 20.0,
               'calculated_hugepages_free': 104448.0,
               'calculated_hugepages_surp': 0.0,
               'calculated_hugepages_total': 112640.0,
               'dirty': 0.14,
               'filepages': 12867.87,
               'hugepages_free': 102,
               'hugepages_surp': 0,
               'hugepages_total': 110,
               'inactive': 5992.89,
               'inactive(anon)': 1.49,
               'inactive(file)': 5991.39,
               'kernelstack': 20.0,
               'mapped': 221.11,
               'memfree': 59447.43,
               'memtotal': 191989.64,
               'memused': 132542.21,
               'mlocked': 136.87,
               'nfs_unstable': 0.0,
               'pagetables': 18.43,
               'shmem': 5.96,
               'slab': 1257.8,
               'sreclaimable': 768.1,
               'sunreclaim': 489.7,
               'unevictable': 136.87,
               'writeback': 0.0,
               'writebacktmp': 0.0
            },
            'node0': {
               'active': 5420.7,
               [...]
               'writebacktmp': 0.0
            }

        nodes (list): A list containing all numa nodes

        meminfo (dict): Dicitonnary of nodes with ``MemInfo`` objects::

            {
             'Total': <insights.parsers.numastat.NUMAMemInfo object at 0x7f42d8646278>,
             'node0': <insights.parsers.numastat.NUMAMemInfo object at 0x7f42d8633860>,
             'node1': <insights.parsers.numastat.NUMAMemInfo object at 0x7f42d8633f28>},
            }

    Sample output::

        Per-node system memory usage (in MBs):
                                  Node 0          Node 1           Total
                         --------------- --------------- ---------------
        MemTotal               391813.42       393216.00       785029.42
        MemFree                239202.81       269521.21       508724.02
        MemUsed                152610.61       123694.79       276305.39
        Active                 134564.00       107435.80       241999.80
        Inactive                 3168.00         1575.72         4743.72
        Active(anon)           133489.42       106972.68       240462.09
        Inactive(anon)              0.99            6.85            7.84
        Active(file)             1074.58          463.12         1537.71
        Inactive(file)           3167.00         1568.87         4735.88
        Unevictable               676.06           32.93          708.99
        Mlocked                  2214.06         1614.93         3828.99
        Dirty                       4.39          227.97          232.36
        Writeback                   0.00            0.00            0.00
        FilePages                4246.77         2057.76         6304.54
        Mapped                     62.82          123.68          186.50
        AnonPages              134158.74       107048.42       241207.16
        Shmem                       3.16           10.59           13.75
        KernelStack                30.75           44.61           75.36
        PageTables                261.28          289.40          550.68
        NFS_Unstable                0.00            0.00            0.00
        Bounce                      0.00            0.00            0.00
        WritebackTmp                0.00            0.00            0.00
        Slab                     1068.41         1185.79         2254.20
        SReclaimable              301.56          469.13          770.70
        SUnreclaim                766.85          716.65         1483.50
        AnonHugePages          129238.00       105334.00       234572.00
        HugePages_Total             0.00            0.00            0.00
        HugePages_Free              0.00            0.00            0.00
        HugePages_Surp              0.00            0.00            0.00

    Examples:

        >>> numamem.meminfo['node0'].used
        30994.95
        >>> numamem.meminfo['node0'].total
        31858.2
        >>> numamem.meminfo['node0'].huge_pages.free
        0
        >>> numamem.meminfo['node0'].huge_pages.total
        0
        >>> numamem.meminfo['node0'].slab.reclaimable
        688.19
        >>> numamem.percent_free('node0')
        4.66
        >>> numamem.percent_hugepaes_allocated('node0')
        0.0
        >>> numamem.percent_used('node0')
        95.34
        >>> numamem['node0']['memtotal']
        31858.2
        >>> numamem['node0']['calculated_hugepages_total']
        0.0

    """

    # Not sure how to get this info from here
    # so I made it a constant. This is pretty
    # much standard anyways, at least in OSP
    HUPAGESIZE = 1048576

    def parse_content(self, content):
        self.nodes = []
        # dict of MemInfo objects
        self.meminfo = {}
        # This is used to pass to the MemInfo class for parsing
        raw = {}
        for line in content:
            if re.match(r'.*Node [0-9]+', line):
                line = re.sub(r'Node ([0-9]+)', r'node\1', line)
                linesplit = line.split()
                self.nodes = linesplit
                for node in self.nodes:
                    self[node] = {}
                    raw[node] = ""
                continue

            if re.match(r'^[\w\(\)]+[\s]+[0-9\.]+.*', line):
                linesplit = line.split()
                keyname = linesplit.pop(0).strip().lower()
                for idx, val in enumerate(linesplit):
                    if "hugepages" in keyname:
                        hp_number = int(float(val) * 1024 / self.HUPAGESIZE)
                        self[self.nodes[idx]][keyname] = hp_number
                        self[self.nodes[idx]]["calculated_" + keyname] = float(val)
                        raw[self.nodes[idx]] += str(keyname) + ': ' + str(hp_number) + linesep
                    else:
                        self[self.nodes[idx]][keyname] = float(val)
                        raw[self.nodes[idx]] += str(keyname) + ': ' + str(int(round(float(val), 0)) * 1024) + linesep
        for node in raw:
            self.meminfo[node] = NUMAMemInfo(raw[node], self[node])

    def percent_free(self, node):
        return round(self.meminfo[node].free / self.meminfo[node].total * 100, 2)

    def percent_used(self, node):
        return round(self.meminfo[node].used / self.meminfo[node].total * 100, 2)

    def percent_hugepaes_allocated(self, node):
        # Instead of using that fake number to recalculate the amount, we have to use the real number
        return round(self[node]['calculated_hugepages_total'] / self.meminfo[node].total * 100, 2)

    def percent_hugepages_used(self, node):
        return round((self.meminfo[node].huge_pages.total - self.meminfo[node].huge_pages.free) / self.meminfo[node].huge_pages.total * 100, 2)


class NUMAMemInfo(MemInfo):
    """
    Wrapper class on top of ``MemInfo`` and adapted with the data
    from ``numastat -m``
    """
    def __init__(self, content, data):
        self.data = data
        sub_classes = {
            "anon": AnonMemInfo(self.data),
            "file": FileMemInfo(self.data),
            "slab": SlabMemInfo(self.data),
            "huge_pages": HugePageMemInfo(self.data),
        }
        for name, cls in sub_classes.items():
            setattr(self, name, cls)
        for meminfo_key, k in self.mem_keys:
            setattr(self, k, self.data.get(meminfo_key))
        super(NUMAMemInfo, self).parse_content(content.splitlines())
