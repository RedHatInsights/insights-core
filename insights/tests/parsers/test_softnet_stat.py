from insights.parsers.softnet_stat import SoftNetStats
from insights.tests import context_wrap

SOFTNET_STAT = """
00008e78 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
000040ee 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
0001608c 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
0000372f 00000001 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
"""

SOFTNET_STAT_2 = """
00008e78 00000000 00000011 00000000 00000000 00000000 00000000 00000000 00000020 00000010
000040ee 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000010 00000001
"""


SOFTNET_STAT_3 = """
00358fe3 00006283 00000000 00000000 00000000 00000000 00000000 00000000 00000000 000855fc 00000000 00000000 00000000
00953d1a 00000446 00000000 00000000 00000000 00000000 00000000 00000000 00000000 008eeb9a 00000000 00000000 00000001
02600138 00004bc7 00000000 00000000 00000000 00000000 00000000 00000000 00000000 02328493 00000000 00000000 00000002
02883c47 00007e2e 00000000 00000000 00000000 00000000 00000000 00000000 00000000 02280d49 00000000 00000000 00000003
01a35c9d 0002db94 00000001 00000000 00000000 00000000 00000000 00000000 00000000 008ee93a 00000000 00000000 00000000
"""

SOFTNET_STAT_4 = """
6dcad223 00000000 00000001 00000000 00000000 00000000 00000000 00000000 00000000
"""

SOFTNET_STAT_5 = """
00022be3 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000003 00000002 00000001
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
    assert stats.per_cpu_nstat('cpu_collision') == [32, 16]
    assert stats.per_cpu_nstat('received_rps') == [0, 0]
    assert stats.per_cpu_nstat('flow_limit_count') == [0, 0]
    assert stats.per_cpu_nstat('softnet_backlog_len') == [0 ,0]
    assert stats.per_cpu_nstat('packet_dr') == []
    assert not stats.is_packet_drops

    stats = SoftNetStats(context_wrap(SOFTNET_STAT_3))
    assert stats is not None
    assert stats.cpu_instances == 5
    assert stats.per_cpu_nstat('time_squeeze') == [0, 0, 0, 0, 1]
    assert stats.per_cpu_nstat('packet_drops') == [25219, 1094, 19399, 32302, 187284]
    assert stats.per_cpu_nstat('cpu_collision') == [0, 0, 0, 0, 0]
    assert stats.per_cpu_nstat('received_rps') == [546300, 9366426, 36865171, 36179273, 9365818]
    assert stats.per_cpu_nstat('flow_limit_count') == [0, 0, 0 ,0 ,0]
    assert stats.per_cpu_nstat('softnet_backlog_len') == [0, 0, 0 ,0 ,0]
    assert stats.per_cpu_nstat('packet_dr') == []
    assert stats.is_packet_drops

    stats = SoftNetStats(context_wrap(SOFTNET_STAT_4))
    assert stats is not None
    assert stats.cpu_instances == 1
    assert stats.per_cpu_nstat('packet_drops') == [0]
    assert stats.per_cpu_nstat('time_squeeze') == [1]
    assert stats.per_cpu_nstat('cpu_collision') == [0]
    assert stats.per_cpu_nstat('received_rps') == [0]
    assert stats.per_cpu_nstat('packet_dr') == []
    assert not stats.is_packet_drops

    stats = SoftNetStats(context_wrap(SOFTNET_STAT_5))
    assert stats is not None
    assert stats.cpu_instances == 1
    assert stats.per_cpu_nstat('packet_drops') == [0]
    assert stats.per_cpu_nstat('time_squeeze') == [0]
    assert stats.per_cpu_nstat('cpu_collision') == [3]
    assert stats.per_cpu_nstat('received_rps') == [2]
    assert stats.per_cpu_nstat('flow_limit_count') == [1]
    assert stats.per_cpu_nstat('packet_dr') == []
    assert not stats.is_packet_drops
