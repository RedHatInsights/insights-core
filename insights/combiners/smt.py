"""
Simultaneous Multithreading (SMT) combiner
==========================================

Combiner for Simultaneous Multithreading (SMT). It uses the results of the following parsers:
:class:`insights.parsers.smt.CpuCoreOnline`,
:class:`insights.parsers.smt.CpuSiblings`.
"""

from insights.core.plugins import combiner
from insights.parsers.smt import CpuCoreOnline, CpuSiblings


@combiner(CpuCoreOnline, CpuSiblings)
class CpuTopology(object):
    """
    Class for collecting the online/siblings status for all CPU cores.

    Sample output of the ``CpuCoreOnline`` parser is::

        [[Core 0: Online], [Core 1: Online], [Core 2: Online], [Core 3: Online]]

    Sample output of the ``CpuSiblings`` parser is::

        [[Core 0 Siblings: [0, 2]], [Core 1 Siblings: [1, 3]], [Core 2 Siblings: [0, 2]], [Core 3 Siblings: [1, 3]]]

    Attributes:
        cores (list of dictionaries): List of all cores.
        all_solitary (bool): True, if hyperthreading is not used.

    Examples:
        >>> type(cpu_topology)
        <class 'insights.combiners.smt.CpuTopology'>
        >>> cpu_topology.cores == [{'online': True, 'siblings': [0, 2]}, {'online': True, 'siblings': [1, 3]}, {'online': True, 'siblings': [0, 2]}, {'online': True, 'siblings': [1, 3]}]
        True
        >>> cpu_topology.all_solitary
        False
    """

    def __init__(self, cpu_online, cpu_siblings):
        self.cores = []

        max_cpu_core_id = max([core.core_id for core in cpu_online])
        for n in range(max_cpu_core_id + 1):
            online = [core for core in cpu_online if core.core_id == n]
            # On some boxes cpu0 doesn't have the online file, since technically cpu0 will always
            # be online. So check if online returns anything before trying to access online[0].
            # If it returns nothing and n is 0 set online to True.
            if online:
                online = online[0].on
            elif not online and n == 0:
                online = True
            siblings = [sibling for sibling in cpu_siblings if sibling.core_id == n]
            if len(siblings) != 0:
                siblings = siblings[0].siblings

            one_core = {"online": online, "siblings": siblings}
            self.cores.append(one_core)

        self.all_solitary = all([len(core["siblings"]) <= 1 for core in self.cores])

    def online(self, core_id):
        """
        Returns bool value obtained from "online" file for given core_id.
        """
        if core_id >= len(self.cores) or core_id < 0:
            return None
        return self.cores[core_id]["online"]

    def siblings(self, core_id):
        """
        Returns list of siblings for given core_id.
        """
        if core_id >= len(self.cores) or core_id < 0:
            return None
        return self.cores[core_id]["siblings"]
