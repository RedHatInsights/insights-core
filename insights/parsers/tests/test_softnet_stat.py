from insights.parsers.softnet_stat import SoftNetStats
from insights.tests import context_wrap

SOFTNET_STAT = """
00008e78 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
000040ee 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
0001608c 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
0000372f 00000001 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
"""

SOFTNET_STAT_2 = """
00008e78 00000000 000000011 00000000 00000000 00000000 00000000 00000000 00000020 00000010
000040ee 00000000 00000000 00000000 00000000 00000000 00000000 00000000 000000010 00000001
"""
SOFTNET_STAT_NO = """
"""


def test_softnet_stat():
    stats = SoftNetStats(context_wrap(SOFTNET_STAT))
    assert stats.cpu_instances == 4
    assert stats.is_packet_drops
    assert stats is not None

    assert stats.per_cpu_nstat('packet_drops') == [0, 0, 0, 1]
    assert stats.per_cpu_nstat('time_squeeze') == [0, 0, 0, 0]
    assert stats.per_cpu_nstat('cpu_collision') == [0, 0, 0, 0]
    assert stats.per_cpu_nstat('received_rps') == [0, 0, 0, 0]
    assert stats.per_cpu_nstat('flow_limit_count') == [0, 0, 0, 0]

    stats = SoftNetStats(context_wrap(SOFTNET_STAT_NO))
    assert stats is not None
    assert stats.cpu_instances == 0
    assert not stats.is_packet_drops
    assert stats.per_cpu_nstat('packet_drops') == []
    assert stats.per_cpu_nstat('time_squeeze') == []
    assert stats.per_cpu_nstat('cpu_collision') == []
    assert stats.per_cpu_nstat('received_rps') == []
    assert stats.per_cpu_nstat('flow_limit_count') == []

    stats = SoftNetStats(context_wrap(SOFTNET_STAT_2))
    assert stats is not None
    assert stats.cpu_instances == 2
    assert stats.per_cpu_nstat('packet_drops') == [0, 0]
    assert stats.per_cpu_nstat('time_squeeze') == [17, 0]
    assert stats.per_cpu_nstat('cpu_collision') == [0, 0]
    assert stats.per_cpu_nstat('received_rps') == [32, 16]
    assert stats.per_cpu_nstat('flow_limit_count') == [16, 1]
    assert stats.per_cpu_nstat('packet_dr') == []
    assert not stats.is_packet_drops
