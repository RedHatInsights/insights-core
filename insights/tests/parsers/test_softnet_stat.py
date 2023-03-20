import doctest
from insights.parsers import softnet_stat
from insights.tests import context_wrap

# RHEL 6,7
SOFTNET_STAT = """
00008e78 00000012 00000001 00000000 00000000 00000000 00000000 00000000 00000075 00000005
000040ee 000000ff 00000002 00000000 00000000 00000000 00000000 00000000 000000c4 00000006
0001608c 00000000 00000003 00000000 00000000 00000000 00000000 00000000 00000049 00000007
0000372f 00000001 00000004 00000000 00000000 00000000 00000000 00000000 00000021 00000008
"""

# RHEL 6,7
SOFTNET_STAT_2 = """
00008e78 00000001 00000011 00000000 00000000 00000000 00000000 00000000 00000020 00000010
000040ee 000000ee f003eca7 00000000 00000000 00000000 00000000 00000000 00000010 00000001
"""

# RHEL 9
SOFTNET_STAT_3 = """
00358fe3 00006283 00000000 00000000 00000000 00000000 00000000 00000000 00000000 000855fc 00000076 00000000 00000000
00953d1a 00000446 000000b1 00000000 00000000 00000000 00000000 00000000 00000000 008eeb9a 0000002b 000000dc 00000001
02600138 00004bc7 00000000 00000000 00000000 00000000 00000000 00000000 00000000 02328493 00000000 0000000a 00000002
02883c47 00007e2e 0000007b 00000000 00000000 00000000 00000000 00000000 00000000 02280d49 000000bd 00000000 00000003
01a35c9d 0002db94 00000001 00000000 00000000 00000000 00000000 00000000 00000000 008ee93a 00000000 0000008c 00000000
"""

# RHEL 5
SOFTNET_STAT_4 = """
6dcad223 00000000 00000001 00000000 00000000 00000000 00000000 00000000 00000005
"""

# RHEL 8
SOFTNET_STAT_5 = """
00022be3 000000fe 00000012 00000000 00000000 00000000 00000000 00000000 00000003 00000002 00000001
"""

SOFTNET_STAT_NO = """
"""

SOFTNET_STATS_DOC = """
00358fe3 00006283 00000000 00000000 00000000 00000000 00000000 00000000 00000000 000855fc 00000000 00000000 00000000
00953d1a 00000446 00000000 00000000 00000000 00000000 00000000 00000000 00000000 008eeb9a 00000000 00000000 00000001
02600138 00004bc7 00000000 00000000 00000000 00000000 00000000 00000000 00000000 02328493 00000000 00000000 00000002
02883c47 00007e2e 00000000 00000000 00000000 00000000 00000000 00000000 00000000 02280d49 00000000 00000000 00000003
01a35c9d 0002db94 00000001 00000000 00000000 00000000 00000000 00000000 00000000 008ee93a 00000000 00000000 00000004
"""


def test_softnet_stat():
    stats = softnet_stat.SoftNetStats(context_wrap(SOFTNET_STAT))
    assert stats.cpu_instances == 4
    assert stats.is_packet_drops
    assert stats is not None

    assert stats.per_cpu_nstat('packet_drops') == [18, 255, 0, 1]
    assert stats.per_cpu_nstat('time_squeeze') == [1, 2, 3, 4]
    assert stats.per_cpu_nstat('cpu_collision') == [117, 196, 73, 33]
    assert stats.per_cpu_nstat('received_rps') == [5, 6, 7, 8]
    assert stats.per_cpu_nstat('flow_limit_count') == [None, None, None, None]

    stats = softnet_stat.SoftNetStats(context_wrap(SOFTNET_STAT_NO))
    assert stats is not None
    assert stats.cpu_instances == 0
    assert not stats.is_packet_drops
    assert stats.per_cpu_nstat('packet_drops') == []
    assert stats.per_cpu_nstat('time_squeeze') == []
    assert stats.per_cpu_nstat('cpu_collision') == []
    assert stats.per_cpu_nstat('received_rps') == []
    assert stats.per_cpu_nstat('flow_limit_count') == []

    stats = softnet_stat.SoftNetStats(context_wrap(SOFTNET_STAT_2))
    assert stats is not None
    assert stats.cpu_instances == 2
    assert stats.per_cpu_nstat('packet_drops') == [1, 238]
    assert stats.per_cpu_nstat('time_squeeze') == [17, 4026789031]
    assert stats.per_cpu_nstat('cpu_collision') == [32, 16]
    assert stats.per_cpu_nstat('received_rps') == [16, 1]
    assert stats.per_cpu_nstat('flow_limit_count') == [None, None]
    assert stats.per_cpu_nstat('softnet_backlog_len') == [None, None]
    assert stats.per_cpu_nstat('packet_dr') == []
    assert stats.is_packet_drops

    stats = softnet_stat.SoftNetStats(context_wrap(SOFTNET_STAT_3))
    assert stats is not None
    assert stats.cpu_instances == 5
    assert stats.per_cpu_nstat('time_squeeze') == [0, 177, 0, 123, 1]
    assert stats.per_cpu_nstat('packet_drops') == [25219, 1094, 19399, 32302, 187284]
    assert stats.per_cpu_nstat('cpu_collision') == [0, 0, 0, 0, 0]
    assert stats.per_cpu_nstat('received_rps') == [546300, 9366426, 36865171, 36179273, 9365818]
    assert stats.per_cpu_nstat('flow_limit_count') == [118, 43, 0, 189, 0]
    assert stats.per_cpu_nstat('softnet_backlog_len') == [0, 220, 10, 0, 140]
    assert stats.per_cpu_nstat('packet_dr') == []
    assert stats.is_packet_drops

    stats = softnet_stat.SoftNetStats(context_wrap(SOFTNET_STAT_4))
    assert stats is not None
    assert stats.cpu_instances == 1
    assert stats.per_cpu_nstat('packet_drops') == [0]
    assert stats.per_cpu_nstat('time_squeeze') == [1]
    assert stats.per_cpu_nstat('cpu_collision') == [5]
    assert stats.per_cpu_nstat('received_rps') == [None]
    assert stats.per_cpu_nstat('packet_dr') == []
    assert not stats.is_packet_drops

    stats = softnet_stat.SoftNetStats(context_wrap(SOFTNET_STAT_5))
    assert stats is not None
    assert stats.cpu_instances == 1
    assert stats.per_cpu_nstat('packet_drops') == [254]
    assert stats.per_cpu_nstat('time_squeeze') == [18]
    assert stats.per_cpu_nstat('cpu_collision') == [3]
    assert stats.per_cpu_nstat('received_rps') == [2]
    assert stats.per_cpu_nstat('flow_limit_count') == [1]
    assert stats.per_cpu_nstat('packet_dr') == []
    assert stats.is_packet_drops


def test_softnet_stat_doc_examples():
    env = {
        'softnet_obj': softnet_stat.SoftNetStats(context_wrap(SOFTNET_STATS_DOC)),
        'SoftNetStats': softnet_stat.SoftNetStats
    }

    failed, total = doctest.testmod(softnet_stat, globs=env)
    assert failed == 0
