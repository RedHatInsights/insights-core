from insights.parsers.vdsm_log import VDSMLog
from insights.tests import context_wrap

from datetime import datetime

# This log commonly has \n in it - hence r""
VDSM_LOG = r"""
Thread-60::DEBUG::2015-05-04 00:01:07,490::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\n1+0 records out\n4096 bytes (4.1 kB) copied, 0.000147196 s, 27.8 MB/s\n'; <rc> = 0
Thread-64::DEBUG::2015-05-04 00:01:07,894::blockSD::600::Storage.Misc.excCmd::(getReadDelay) '/bin/dd if=/dev/fe4d8910-ac67-4307-a3e7-be8a56d1c559/metadata iflag=direct of=/dev/null bs=4096 count=1' (cwd None)
Thread-64::DEBUG::2015-05-04 00:01:07,909::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\n1+0 records out\n4096 bytes (4.1 kB) copied, 0.00020047 s, 20.4 MB/s\n'; <rc> = 0
Thread-63::DEBUG::2015-05-04 00:01:08,050::blockSD::600::Storage.Misc.excCmd::(getReadDelay) '/bin/dd if=/dev/b0c17a6d-c5a5-4646-b4b5-edd85bc658db/metadata iflag=direct of=/dev/null bs=4096 count=1' (cwd None)
Thread-63::DEBUG::2015-05-04 00:01:08,061::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\n1+0 records out\n4096 bytes (4.1 kB) copied, 0.000632011 s, 6.5 MB/s\n'; <rc> = 0
VM Channels Listener::DEBUG::2015-05-04 00:01:10,830::vmChannels::95::vds::(_handle_timeouts) Timeout on fileno 47.
Thread-13::DEBUG::2015-05-04 00:01:15,853::task::595::TaskManager.Task::(_updateState) Task=`57faf240-0efe-44e2-8485-ffa182bbc9dd`::moving from state init -> state preparing
Thread-13::INFO::2015-05-04 00:01:15,854::logUtils::44::dispatcher::(wrapper) Run and protect: repoStats(options=None)
Thread-13::INFO::2015-05-04 00:01:15,854::logUtils::47::dispatcher::(wrapper) Run and protect: repoStats, Return response: {u'cf7dab23-6b5b-45f4-9e27-ab06fbc01759': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000153278', 'lastCheck': '8.8', 'valid': True}, u'5a30691d-4fae-4023-ae96-50704f6b253c': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000147196', 'lastCheck': '8.4', 'valid': True}, u'b0c17a6d-c5a5-4646-b4b5-edd85bc658db': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000632011', 'lastCheck': '7.8', 'valid': True}, u'fe4d8910-ac67-4307-a3e7-be8a56d1c559': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.00020047', 'lastCheck': '7.9', 'valid': True}, u'e70cce65-0d02-4da4-8781-6aeeef5c86ff': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000208457', 'lastCheck': '9.6', 'valid': True}, u'c3a10b1e-574e-4edd-ad00-a59cacc705b5': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000201237', 'lastCheck': '8.8', 'valid': True}}
"""


def test_vdsm_log():
    vdsm_log = VDSMLog(context_wrap(VDSM_LOG))
    assert "VM Channels Listener" in vdsm_log
    test_newline_handling = vdsm_log.get('SUCCESS')
    assert len(test_newline_handling) == 3
    assert test_newline_handling[0] == "Thread-60::DEBUG::2015-05-04 00:01:07,490::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\\n1+0 records out\\n4096 bytes (4.1 kB) copied, 0.000147196 s, 27.8 MB/s\\n'; <rc> = 0"
    parsed_newlines = list(vdsm_log.parse_lines(test_newline_handling))
    assert parsed_newlines[0] == {
        'raw_line': "Thread-60::DEBUG::2015-05-04 00:01:07,490::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\\n1+0 records out\\n4096 bytes (4.1 kB) copied, 0.000147196 s, 27.8 MB/s\\n'; <rc> = 0",
        'thread': "Thread-60",
        'level': "DEBUG",
        'timestamp': "2015-05-04 00:01:07,490",
        'datetime': datetime(2015, 5, 4, 0, 1, 7),
        'module': "blockSD",
        'line': "600",
        'logname': "Storage.Misc.excCmd",
        'funcname': "getReadDelay",
        'message': "SUCCESS: <err> = '1+0 records in\\n1+0 records out\\n4096 bytes (4.1 kB) copied, 0.000147196 s, 27.8 MB/s\\n'; <rc> = 0"
    }
    # test get_after()
    assert len(list(vdsm_log.get_after(datetime(2015, 5, 4, 0, 1, 10)))) == 4
    assert len(list(vdsm_log.get_after(
        datetime(2015, 5, 4, 0, 1, 10), vdsm_log.get('dispatcher')
    ))) == 2
    assert len(list(vdsm_log.get_after(
        datetime(2015, 5, 4, 0, 1, 10), vdsm_log.parse_lines(vdsm_log.get('dispatcher'))
    ))) == 2


BAD_VDSM_LOG = r"""
Thread-13::INFO::2015-33-45 00:01:15,854
Thread-13::INFO::2015-05-04 00:01:15,854::
Thread-13::INFO::2015-05-04 00:01:15,854::logUtils::47::dispatcher::(wrapper) Run and protect: repoStats, Return response: {u'cf7dab23-6b5b-45f4-9e27-ab06fbc01759': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000153278', 'lastCheck': '8.8', 'valid': True}, u'5a30691d-4fae-4023-ae96-50704f6b253c': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000147196', 'lastCheck': '8.4', 'valid': True}, u'b0c17a6d-c5a5-4646-b4b5-edd85bc658db': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000632011', 'lastCheck': '7.8', 'valid': True}, u'fe4d8910-ac67-4307-a3e7-be8a56d1c559': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.00020047', 'lastCheck': '7.9', 'valid': True}, u'e70cce65-0d02-4da4-8781-6aeeef5c86ff': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000208457', 'lastCheck': '9.6', 'valid': True}, u'c3a10b1e-574e-4edd-ad00-a59cacc705b5': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000201237', 'lastCheck': '8.8', 'valid': True}}
FATAL ERROR
"""


def test_bad_vdsm_log_parsing():
    vdsm_log = VDSMLog(context_wrap(BAD_VDSM_LOG))
    parsed = list(vdsm_log.parse_lines(vdsm_log.lines))
    assert len(parsed) == 4
    assert parsed[0] == {
        'raw_line': 'Thread-13::INFO::2015-33-45 00:01:15,854',
        'thread': 'Thread-13',
        'level': 'INFO',
        'timestamp': '2015-33-45 00:01:15,854',
    }
    assert parsed[1] == {
        'raw_line': 'Thread-13::INFO::2015-05-04 00:01:15,854::',
        'thread': 'Thread-13',
        'level': 'INFO',
        'timestamp': '2015-05-04 00:01:15,854',
        'datetime': datetime(2015, 5, 4, 0, 1, 15),
        'module': ''  # vestigial field
    }
    assert parsed[2] == {
        'raw_line': "Thread-13::INFO::2015-05-04 00:01:15,854::logUtils::47::dispatcher::(wrapper) Run and protect: repoStats, Return response: {u'cf7dab23-6b5b-45f4-9e27-ab06fbc01759': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000153278', 'lastCheck': '8.8', 'valid': True}, u'5a30691d-4fae-4023-ae96-50704f6b253c': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000147196', 'lastCheck': '8.4', 'valid': True}, u'b0c17a6d-c5a5-4646-b4b5-edd85bc658db': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000632011', 'lastCheck': '7.8', 'valid': True}, u'fe4d8910-ac67-4307-a3e7-be8a56d1c559': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.00020047', 'lastCheck': '7.9', 'valid': True}, u'e70cce65-0d02-4da4-8781-6aeeef5c86ff': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000208457', 'lastCheck': '9.6', 'valid': True}, u'c3a10b1e-574e-4edd-ad00-a59cacc705b5': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000201237', 'lastCheck': '8.8', 'valid': True}}",
        'thread': 'Thread-13',
        'level': 'INFO',
        'timestamp': '2015-05-04 00:01:15,854',
        'datetime': datetime(2015, 5, 4, 0, 1, 15),
        'module': 'logUtils',
        'line': '47',
        'logname': 'dispatcher',
        'funcname': 'wrapper',
        'message': "Run and protect: repoStats, Return response: {u'cf7dab23-6b5b-45f4-9e27-ab06fbc01759': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000153278', 'lastCheck': '8.8', 'valid': True}, u'5a30691d-4fae-4023-ae96-50704f6b253c': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000147196', 'lastCheck': '8.4', 'valid': True}, u'b0c17a6d-c5a5-4646-b4b5-edd85bc658db': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000632011', 'lastCheck': '7.8', 'valid': True}, u'fe4d8910-ac67-4307-a3e7-be8a56d1c559': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.00020047', 'lastCheck': '7.9', 'valid': True}, u'e70cce65-0d02-4da4-8781-6aeeef5c86ff': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000208457', 'lastCheck': '9.6', 'valid': True}, u'c3a10b1e-574e-4edd-ad00-a59cacc705b5': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000201237', 'lastCheck': '8.8', 'valid': True}}"
    }
    assert parsed[3] == {
        'raw_line': 'FATAL ERROR',
        'thread': 'FATAL ERROR'
    }
