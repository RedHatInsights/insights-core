from insights.parsers import numastat
from insights.tests import context_wrap

import re

"""
The following numastats -m comes from a RHEL 7.8 box.
There's some values that are in meminfo that are not in numastat
"""

NUMASTAT_MEM = """
Per-node system memory usage (in MBs):
                          Node 0          Node 1           Total
                 --------------- --------------- ---------------
MemTotal                95257.24        96732.40       191989.64
MemFree                 28190.93        31256.51        59447.43
MemUsed                 67066.31        65475.89       132542.21
Active                   5420.70         2210.93         7631.63
Inactive                 3422.76         2570.12         5992.89
Active(anon)              415.30          369.71          785.01
Inactive(anon)              1.23            0.26            1.49
Active(file)             5005.40         1841.22         6846.62
Inactive(file)           3421.53         2569.87         5991.39
Unevictable                96.62           40.25          136.87
Mlocked                    96.62           40.25          136.87
Dirty                       0.00            0.14            0.14
Writeback                   0.00            0.00            0.00
FilePages                8440.29         4427.57        12867.87
Mapped                    117.59          103.52          221.11
AnonPages                 499.09          393.97          893.05
Shmem                       3.41            2.55            5.96
KernelStack                 9.97           10.03           20.00
PageTables                 10.84            7.59           18.43
NFS_Unstable                0.00            0.00            0.00
Bounce                      0.00            0.00            0.00
WritebackTmp                0.00            0.00            0.00
Slab                      716.69          541.11         1257.80
SReclaimable              446.41          321.70          768.10
SUnreclaim                270.28          219.42          489.70
AnonHugePages              10.00           10.00           20.00
HugePages_Total         56320.00        56320.00       112640.00
HugePages_Free          52224.00        52224.00       104448.00
HugePages_Surp              0.00            0.00            0.00
""".strip()
NUMASTAT = """
                           node0           node1
numa_hit              4735090719      2770141501
numa_miss                      0           92981
numa_foreign               92981               0
interleave_hit             59485           59445
local_node            4734323881      2769543674
other_node                766838          690808
""".strip()


def test_numastat_mem():
    numas = numastat.NUMAStatMem(context_wrap(NUMASTAT_MEM))
    i = 0
    used_maths = {
                    'node0': 95257.24 - 28190.93,
                    'node1': 96732.40 - 31256.51,
                    'Total': 191989.64 - 59447.43
    }
    for node in numas.nodes:
        m = numas.meminfo[node]
        values = list()
        i += 1
        for l in NUMASTAT_MEM.splitlines():
            if re.match(r'^[\w]+[\s]+[0-9\.]+[\s]+[0-9\.]+', l):
                values.append(float(l.split()[i].strip()))
        actual = [
            m.total, m.free, m.active, m.inactive, m.anon.active, m.anon.inactive,
            m.file.active, m.file.inactive, m.unevictable, m.mlocked, m.dirty,
            m.writeback, m.anon.pages, m.mapped, m.shmem, m.slab.total, m.slab.reclaimable,
            m.slab.unreclaimable, m.kernel_stack, m.page_tables, m.nfs_unstable, m.bounce,
            m.writeback_tmp, m.huge_pages.total, m.huge_pages.free, m.huge_pages.surplus
        ]
        for j in range(len(actual)):
            assert isinstance(actual[j], (float, int)), "Line %d's value is not an int: %s" % (j, type(actual[j]))

        assert m.used == values[0] - values[1]
        assert m.used == used_maths[node]
        assert m.active == m.anon.active + m.file.active
    assert numas.meminfo['node0'].huge_pages.total + numas.meminfo['node1'].huge_pages.total == numas.meminfo['Total'].huge_pages.total
    assert numas.meminfo['node0'].total + numas.meminfo['node1'].total == numas.meminfo['Total'].total


def test_numastat():
    numas = numastat.NUMAStat(context_wrap(NUMASTAT))
    assert numas['node0']['foreign'] == numas['node1']['miss'], \
       "node0's foreign (%i) should be equal to the other node's miss (%i)" % (numas['node0']['foreign'],
                                                                               numas['node1']['miss'])
    assert numas['node1']['foreign'] == numas['node0']['miss']
    assert numas['node0']['hit'] + numas['node1']['hit'] == numas['Total']['hit']
    for node, m in numas.items():
        stat = numas[node]
        assert stat['hit'] - stat['local_node'] + stat['miss'] == stat['other_node'], \
            "hit: %i - local_node: %i + miss: %i != other_node: %i" % (stat['hit'], stat['local_node'], stat['miss'], stat['other_node'])
        assert numas.percent_miss[node] == round(stat['miss'] / numas.total_hits[node] * 100, 2)
        assert numas.percent_foreign[node] == round(stat['foreign'] / numas.total_hits[node] * 100, 2)
        assert numas.percent_load[node] == round(numas.total_hits[node] / numas.total_hits['Total'] * 100, 2)
