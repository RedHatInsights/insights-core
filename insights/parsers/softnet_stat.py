"""
SoftNetStats - file ``/proc/net/softnet_stat``
==============================================

This parser parses the stats from network devices. These stats includes events
per cpu(in row), number of packets processed i.e packet_process (first column),
number of packet drops packet_drops (second column), time squeeze i.e net_rx_action
performed time_squeeze(third column), cpu collision i.e collision occur while obtaining
device lock while transmitting cpu_collision packets (eighth column), received_rps
number of times cpu woken up received_rps (ninth column), number of times reached flow
limit count flow_limit_count (tenth column).

The typical contents of ``cat /proc/net/softnet_stat`` file is as below::

    00008e78 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    000040ee 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    0001608c 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    0000372f 00000001 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000

    Column-01: packet_process: Packet processed by each CPU.
    Column-02: packet_drop: Packets dropped.
    Column-03: time_squeeze: net_rx_action.
    Column-08: cpu_collision: collision occur while obtaining device lock while transmitting.
    Column-09: received_rps: number of times cpu woken up received_rps.
    Column-10: flow_limit_count: number of times reached flow limit count.

.. Note::
            There is minimal documentation about these fields in the file, columns are not labeled and
            could change between the kernel releases. This format is compatible for RHEL-6
            and RHEL-7 releases. Also it is unlikely that the positions of those values will
            change in short term.

Examples:
    >>> SOFTNET_STATS = '''
    ... 00008e78 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    ... 000040ee 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    ... 0001608c 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    ... 0000372f 00000001 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
    ...'''.strip()
    >>> softnet_obj = SoftNetStats(context_wrap(SOFTNET_STATS))
    >>> softnet_obj.is_packet_drops()
    True
    >>> softnet_obj.cpu_instances
    4
    >>> softnet_obj.per_cpu_nstat('packet_drops')
    [0, 0, 0, 1]
"""

from .. import Parser, parser
from insights.specs import Specs


@parser(Specs.softnet_stat)
class SoftNetStats(Parser):
    """Parses ``/proc/net/softnet_stat`` file contains"""

    def __init__(self, context):

        """ Total number of CPUs listed in the stats records"""
        self.cpu_instances = 0

        """ List of network stats per cpu instace """
        self.cpu_nstats = []
        super(SoftNetStats, self).__init__(context)

    def parse_content(self, contents):
        for line in contents:
            stats = [int(st, 16) for st in line.split(None)]
            self.cpu_nstats.append({'packet_process': stats[0],
                            'packet_drops': stats[1],
                            'time_squeeze': stats[2],
                            'cpu_collision': stats[7],
                            'received_rps': stats[8],
                            'flow_limit_count': stats[9]})
        self.cpu_instances = len(self.cpu_nstats)

    def per_cpu_nstat(self, key):
        """
        Get network stats per column for all cpu.

        Arguments:
            (str): Column name for eg. packet_drops or received_rps.

        Returns:
            (list): Column states per cpu.
        """
        if not self.cpu_nstats:
            return []

        if key not in self.cpu_nstats[0]:
            return []

        return [cpu[key] for cpu in self.cpu_nstats]

    @property
    def is_packet_drops(self):
        """
        It will check for if there is packet drop occurred on any cpu.

        Arguments:
            None: No input argument for the function

        Returns:
            (bool): It will return True if observed packet drops.
        """
        return any(cpu["packet_drops"] > 0 for cpu in self.cpu_nstats)
