"""
ProcStat - File ``/proc/stat``
======================================================

This parser reads the content of ``/proc/stat``.
"""

from .. import parser, CommandParser

from ..parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.proc_stat)
class ProcStat(CommandParser):
    """
    Class ``ProcStat`` parses the content of the ``/proc/stat``.

    Attributes:
        cpu_percentage (string):     The CPU usage percentage since boot.
        intr (int):     The total of all interrupts serviced including unnumbered
                        architecture specific interrupts.
        ctxt (int):     The number of context switches that the system under went.
        btime (string): boot time, in seconds since the Epoch, 1970-01-01
                        00:00:00 +0000 (UTC).
        processes (int):Number of forks since boot.
        procs_running (int):  Number of processes in runnable state. (Linux 2.5.45
                              onward.)
        procs_blocked (int):  Number of processes blocked waiting for I/O to complete.
                              (Linux 2.5.45 onward.)
        softirq (int) : The total of all softirqs and each subsequent column is
                        the total for particular softirq.
                        (Linux 2.6.31 onward.)

    A small sample of the content of this file looks like::

        cpu  32270961 89036 23647730 1073132344 1140756 0 1522035 18738206 0 0
        cpu0 3547155 11248 2563031 135342787 113432 0 199615 2199379 0 0
        cpu1 4660934 10954 3248126 132271933 120282 0 279870 2660186 0 0
        cpu2 4421035 10729 3306081 132914999 126705 0 194141 2505565 0 0
        cpu3 4224551 10633 3139695 133634676 121035 0 181213 2380738 0 0
        cpu4 3985452 11151 2946570 134064686 205568 0 165839 2478471 0 0
        cpu5 3914912 11396 2896447 134635676 117341 0 164794 2260011 0 0
        cpu6 3802544 11418 2817453 134878674 222855 0 182738 2150276 0 0
        cpu7 3714375 11503 2730323 135388911 113534 0 153821 2103576 0 0
        intr 21359029 22 106 0 0 0 0 3 0 1 0 16 155 357 0 0 671261 0 0 0 0 0 0 0 0 0 0 0 32223 0 4699385 2 0 8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        ctxt 17852681
        btime 1542179825
        processes 19212
        procs_running 1
        procs_blocked 0
        softirq 11867930 1 3501158 6 4705528 368244 0 79 2021509 0 1271405



    Examples:
        >>> type(proc_stat)
        <class 'insights.parsers.proc_stat.ProcStat'>
        >>> proc_stat.cpu_percentage
        '6.63%'
        >>> proc_stat.ctxt
        17852681
        >>> proc_stat.btime
        '1542179825'
        >>> proc_stat.softirq
        11867930
    """

    def parse_content(self, content):
        proc_stat_dict = {}
        for line in get_active_lines(content):
            key, value = line.split(None, 1)
            if key not in proc_stat_dict:
                proc_stat_dict[key] = value
        self.data = proc_stat_dict

    @property
    def cpu_percentage(self):
        if 'cpu' in self.data:
            cpu_list = list(map(lambda x: int(x), self.data['cpu'].split()))
            cpu_total = float(sum(cpu_list[:8]))
            cpu_idle = float(sum([cpu_list[3], cpu_list[4]]))
            cpu_pct = (cpu_total - cpu_idle) * 100 / cpu_total
            return "{0:.2f}".format(cpu_pct) + '%'
        return None

    @property
    def intr(self):
        return int(self.data['intr'].split(None, 1)[0]) if 'intr' in self.data else None

    @property
    def ctxt(self):
        return int(self.data['ctxt']) if 'ctxt' in self.data else None

    @property
    def btime(self):
        return self.data['btime'] if 'btime' in self.data else None

    @property
    def processes(self):
        return int(self.data['processes']) if 'processes' in self.data else None

    @property
    def procs_running(self):
        return int(self.data['procs_running']) if 'procs_running' in self.data else None

    @property
    def procs_blocked(self):
        return int(self.data['procs_blocked']) if 'procs_blocked' in self.data else None

    @property
    def softirq(self):
        return int(self.data['softirq'].split(None, 1)[0]) if 'softirq' in self.data else None
