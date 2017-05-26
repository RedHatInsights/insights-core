from insights.mappers import openvswitch_logs
from insights.tests import context_wrap

LOG_LINES = """
2017-03-12T11:56:54.989Z|00001|vlog|INFO|opened log file /var/log/openvswitch/ovsdb-server.log
2017-03-12T11:56:55.053Z|00002|ovsdb_server|INFO|ovsdb-server (Open vSwitch) 2.4.0
2017-03-12T11:57:04.988Z|00003|memory|INFO|2664 kB peak resident set size after 10.0 seconds
2017-03-12T11:57:04.988Z|00004|memory|INFO|cells:816 monitors:1 sessions:2
2017-03-13T07:41:01.524Z|00005|vlog|INFO|closing log file
"""


def test_ovsdb_server():
    logs = openvswitch_logs.OVSDB_Server_Log(context_wrap(LOG_LINES))

    assert len(logs) == 5
    vlogs = logs.get('vlog')
    print vlogs
    assert len(vlogs) == 2
    assert vlogs[0] == {
        'raw_line': '2017-03-12T11:56:54.989Z|00001|vlog|INFO|opened log file /var/log/openvswitch/ovsdb-server.log',
        'timestamp': '2017-03-12T11:56:54.989Z',
        'sequence': '00001',
        'module': 'vlog',
        'level': 'INFO',
        'message': 'opened log file /var/log/openvswitch/ovsdb-server.log'
    }
    assert vlogs[1] == {
        'raw_line': '2017-03-13T07:41:01.524Z|00005|vlog|INFO|closing log file',
        'timestamp': '2017-03-13T07:41:01.524Z',
        'sequence': '00005',
        'module': 'vlog',
        'level': 'INFO',
        'message': 'closing log file'
    }


# Same tests, same file, just a different mapper name.
def test_ovs_vswitch():
    logs = openvswitch_logs.OVS_VSwitchd_Log(context_wrap(LOG_LINES))

    assert len(logs) == 5
    vlogs = logs.get('vlog')
    assert len(vlogs) == 2
    assert vlogs[0] == {
        'raw_line': '2017-03-12T11:56:54.989Z|00001|vlog|INFO|opened log file /var/log/openvswitch/ovsdb-server.log',
        'timestamp': '2017-03-12T11:56:54.989Z',
        'sequence': '00001',
        'module': 'vlog',
        'level': 'INFO',
        'message': 'opened log file /var/log/openvswitch/ovsdb-server.log'
    }
    assert vlogs[1] == {
        'raw_line': '2017-03-13T07:41:01.524Z|00005|vlog|INFO|closing log file',
        'timestamp': '2017-03-13T07:41:01.524Z',
        'sequence': '00005',
        'module': 'vlog',
        'level': 'INFO',
        'message': 'closing log file'
    }
