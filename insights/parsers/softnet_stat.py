"""
SoftNetStats - file ``/proc/net/softnet_stat``
==============================================
"""

from .. import Parser, parser
from insights.specs import Specs


@parser(Specs.softnet_stat)
class SoftNetStats(Parser):
    """
    Parses ``/proc/net/softnet_stat`` file contains


    This parser parses the stats from network devices. These stats includes events
    per cpu(in row), number of packets processed i.e packet_process (first column),
    number of packet drops packet_drops (second column), time squeeze i.e net_rx_action
    performed time_squeeze(third column), cpu collision i.e collision occur while obtaining
    device lock while transmitting cpu_collision packets (eighth column), received_rps
    number of times cpu woken up received_rps (ninth column), number of times reached flow
    limit count flow_limit_count (tenth column), backlog status (eleventh column),
    core id (twelfth column).

    The typical contents of ``cat /proc/net/softnet_stat`` file is as below::

        00358fe3 00006283 00000000 00000000 00000000 00000000 00000000 00000000 00000000 000855fc 00000000 00000000 00000000
        00953d1a 00000446 00000000 00000000 00000000 00000000 00000000 00000000 00000000 008eeb9a 00000000 00000000 00000001
        02600138 00004bc7 00000000 00000000 00000000 00000000 00000000 00000000 00000000 02328493 00000000 00000000 00000002
        02883c47 00007e2e 00000000 00000000 00000000 00000000 00000000 00000000 00000000 02280d49 00000000 00000000 00000003
        01a35c9d 0002db94 00000001 00000000 00000000 00000000 00000000 00000000 00000000 008ee93a 00000000 00000000 00000004

        Column-01: packet_process: Packet processed by each CPU.
        Column-02: packet_drop: Packets dropped.
        Column-03: time_squeeze: net_rx_action.
        Column-09: cpu_collision: collision occur while obtaining device lock while transmitting.
        Column-10: received_rps: number of times cpu woken up received_rps.
        Column-11: flow_limit_count: number of times reached flow limit count.
        Column-12: softnet_backlog_len: Backlog status
        Column-13: index: core id owning this softnet_data

    For the proc file format details,
    See:
    * Linux 2.6.39 https://elixir.bootlin.com/linux/v2.6.39/source/net/core/dev.c#L4086
    * * example : "6dcad223 00000000 00000001 00000000 00000000 00000000 00000000 00000000 00000000 00000000"
    * Linux 4.18 https://elixir.bootlin.com/linux/v4.18/source/net/core/net-procfs.c#L162
    * * example : "00022be3 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000"
    * Linux 5.14 https://elixir.bootlin.com/linux/v5.14/source/net/core/net-procfs.c#L169
    * * example : "00358fe3 00006283 00000000 00000000 00000000 00000000 00000000 00000000 00000000 000855fc 00000000 00000000 00000000"

    .. Note::
                There is minimal documentation about these fields in the file, columns are not labeled and
                could change between the kernel releases. This format is compatible for RHEL-6,
                RHEL-7, RHEL-8 and RHEL-9 releases. Also it is unlikely that the positions of those values will
                change in short term.

    Sample softnet_data::

         00358fe3 00006283 00000000 00000000 00000000 00000000 00000000 00000000 00000000 000855fc 00000000 00000000 00000000
         00953d1a 00000446 00000000 00000000 00000000 00000000 00000000 00000000 00000000 008eeb9a 00000000 00000000 00000001
         02600138 00004bc7 00000000 00000000 00000000 00000000 00000000 00000000 00000000 02328493 00000000 00000000 00000002
         02883c47 00007e2e 00000000 00000000 00000000 00000000 00000000 00000000 00000000 02280d49 00000000 00000000 00000003
         01a35c9d 0002db94 00000001 00000000 00000000 00000000 00000000 00000000 00000000 008ee93a 00000000 00000000 00000004

    Examples:
        >>> softnet_obj.is_packet_drops
        True
        >>> softnet_obj.cpu_instances
        5
        >>> softnet_obj.per_cpu_nstat('packet_drops')
        [25219, 1094, 19399, 32302, 187284]
    """

    def __init__(self, context):

        """ Total number of CPUs listed in the stats records"""
        self.cpu_instances = 0

        """ List of network stats per cpu instace """
        self.cpu_nstats = []
        super(SoftNetStats, self).__init__(context)

    def parse_content(self, contents):
        for line in contents:
            stats = [int(st, 16) for st in line.split(None)]
            nstats = {
                    'packet_process': stats[0],
                    'packet_drops': stats[1],
                    'time_squeeze': stats[2],
                    'cpu_collision': stats[8],
                    'received_rps': None,
                    'flow_limit_count': None,
                    'softnet_backlog_len': None,
                    'index': None,
            }

            # RHEL 6,7
            if len(stats) >= 10:
                nstats.update({'received_rps': stats[9]})

            # RHEL 8
            if len(stats) >= 11:
                nstats.update({'flow_limit_count': stats[10]})

            # RHEL 9
            if len(stats) >= 13:
                nstats.update({
                    'softnet_backlog_len': stats[11],
                    'index': stats[12]
                })

            self.cpu_nstats.append(nstats)

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
