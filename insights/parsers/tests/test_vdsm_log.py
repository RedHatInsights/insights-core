from datetime import datetime

from insights.parsers.vdsm_log import VDSMLog
from insights.tests import context_wrap


# This log commonly has \n in it - hence r""
VDSM_VER_3_LOG = r"""
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


def test_vdsm_version_3_log():
    vdsm_log = VDSMLog(context_wrap(VDSM_VER_3_LOG))
    assert "VM Channels Listener" in vdsm_log
    test_newline_handling = vdsm_log.get('SUCCESS')
    assert len(test_newline_handling) == 3
    assert test_newline_handling[0]['raw_message'] == "Thread-60::DEBUG::2015-05-04 00:01:07,490::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\\n1+0 records out\\n4096 bytes (4.1 kB) copied, 0.000147196 s, 27.8 MB/s\\n'; <rc> = 0"
    parsed_newlines = list(vdsm_log.parse_lines(test_newline_handling))
    assert parsed_newlines[0] == {
        'thread': "Thread-60",
        'level': "DEBUG",
        'asctime': datetime(2015, 5, 4, 0, 1, 7, 490000),
        'module': "blockSD",
        'line': "600",
        'logname': "Storage.Misc.excCmd",
        'message': "SUCCESS: <err> = '1+0 records in\\n1+0 records out\\n4096 bytes (4.1 kB) copied, 0.000147196 s, 27.8 MB/s\\n'; <rc> = 0"
    }
    # test get_after()
    assert len(list(vdsm_log.get_after(datetime(2015, 5, 4, 0, 1, 10)))) == 4
    assert len(list(vdsm_log.get_after(datetime(2015, 5, 4, 0, 1, 10), 'dispatcher'))) == 2


BAD_VDSM_VER_3_LOG = r"""
Thread-11::INFO::2015-05-03 00:01:15,853
Thread-12::INFO::2015-05-04 00:01:15,854::
Thread-13::INFO::2015-05-04 00:01:15,854::logUtils::47::dispatcher::(wrapper) Run and protect: repoStats, Return response: {u'cf7dab23-6b5b-45f4-9e27-ab06fbc01759': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000153278', 'lastCheck': '8.8', 'valid': True}, u'5a30691d-4fae-4023-ae96-50704f6b253c': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000147196', 'lastCheck': '8.4', 'valid': True}, u'b0c17a6d-c5a5-4646-b4b5-edd85bc658db': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000632011', 'lastCheck': '7.8', 'valid': True}, u'fe4d8910-ac67-4307-a3e7-be8a56d1c559': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.00020047', 'lastCheck': '7.9', 'valid': True}, u'e70cce65-0d02-4da4-8781-6aeeef5c86ff': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000208457', 'lastCheck': '9.6', 'valid': True}, u'c3a10b1e-574e-4edd-ad00-a59cacc705b5': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000201237', 'lastCheck': '8.8', 'valid': True}}
FATAL ERROR
"""


def test_bad_vdsm_log_parsing():
    vdsm_log = VDSMLog(context_wrap(BAD_VDSM_VER_3_LOG))
    parsed = list(vdsm_log.parse_lines(vdsm_log.lines))
    assert len(parsed) == 4
    assert parsed[0] == {
        'thread': 'Thread-11',
        'level': 'INFO',
        'asctime': datetime(2015, 5, 3, 0, 1, 15, 853000),
    }
    assert parsed[1] == {
        'thread': 'Thread-12',
        'level': 'INFO',
        'asctime': datetime(2015, 5, 4, 0, 1, 15, 854000),
    }
    assert parsed[2] == {
        'thread': 'Thread-13',
        'level': 'INFO',
        'asctime': datetime(2015, 5, 4, 0, 1, 15, 854000),
        'module': 'logUtils',
        'line': '47',
        'logname': 'dispatcher',
        'message': "Run and protect: repoStats, Return response: {u'cf7dab23-6b5b-45f4-9e27-ab06fbc01759': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000153278', 'lastCheck': '8.8', 'valid': True}, u'5a30691d-4fae-4023-ae96-50704f6b253c': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000147196', 'lastCheck': '8.4', 'valid': True}, u'b0c17a6d-c5a5-4646-b4b5-edd85bc658db': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000632011', 'lastCheck': '7.8', 'valid': True}, u'fe4d8910-ac67-4307-a3e7-be8a56d1c559': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.00020047', 'lastCheck': '7.9', 'valid': True}, u'e70cce65-0d02-4da4-8781-6aeeef5c86ff': {'code': 0, 'version': 3, 'acquired': True, 'delay': '0.000208457', 'lastCheck': '9.6', 'valid': True}, u'c3a10b1e-574e-4edd-ad00-a59cacc705b5': {'code': 0, 'version': 0, 'acquired': True, 'delay': '0.000201237', 'lastCheck': '8.8', 'valid': True}}"
    }
    assert parsed[3] == {
        'thread': 'FATAL ERROR'
    }


VDSM_VER_4_LOG_1 = r"""
2017-04-18 13:56:28,096+0200 ERROR (vm/27f1a8d4) [virt.vm] (vmId='27f1a8d4-1f81-49e6-bd83-4ecb0a462b54') The vm start process failed (vm:617)
Traceback (most recent call last):
  File "/usr/share/vdsm/virt/vm.py", line 553, in _startUnderlyingVm
    self._run()
  File "/usr/share/vdsm/virt/vm.py", line 2006, in _run
    self._connection.createXML(domxml, flags),
  File "/usr/lib/python2.7/site-packages/vdsm/libvirtconnection.py", line 123, in wrapper
    ret = f(*args, **kwargs)
  File "/usr/lib/python2.7/site-packages/vdsm/utils.py", line 941, in wrapper
    return func(inst, *args, **kwargs)
  File "/usr/lib64/python2.7/site-packages/libvirt.py", line 3777, in createXML
    if ret is None:raise libvirtError('virDomainCreateXML() failed', conn=self)
libvirtError: internal error: Attempted double use of PCI slot 0000:00:01.0 (may need "multifunction='on'" for device on function 0)
2017-04-18 13:56:28,100+0200 INFO  (vm/27f1a8d4) [virt.vm] (vmId='27f1a8d4-1f81-49e6-bd83-4ecb0a462b54') Changed state to Down: internal error: Attempted double use of PCI slot 0000:00:01.0 (may need "multifunction='on'" for device on function 0) (code=1) (vm:1207)
2017-04-18 13:56:28,101+0200 INFO  (vm/27f1a8d4) [virt.vm] (vmId='27f1a8d4-1f81-49e6-bd83-4ecb0a462b54') Stopping connection (guestagent:430)
2017-04-18 13:56:29,121+0200 INFO  (jsonrpc/1) [vdsm.api] START destroy(gracefulAttempts=1) (api:39)
2017-04-18 13:56:29,122+0200 INFO  (jsonrpc/1) [virt.vm] (vmId='27f1a8d4-1f81-49e6-bd83-4ecb0a462b54') Release VM resources (vm:4199)
"""

VDSM_VER_4_LOG_2 = r"""
2017-05-22 11:50:45,363+0530 ERROR (vm/1b8dc1a2) [virt.vm] (vmId='1b8dc1a2-acd3-4a57-9a2b-23f12ae52e38') The vm start process failed (vm:617)
Traceback (most recent call last):
  File "/usr/share/vdsm/virt/vm.py", line 553, in _startUnderlyingVm
    self._run()
  File "/usr/share/vdsm/virt/vm.py", line 2006, in _run
    self._connection.createXML(domxml, flags),
  File "/usr/lib/python2.7/site-packages/vdsm/libvirtconnection.py", line 123, in wrapper
    ret = f(*args, **kwargs)
  File "/usr/lib/python2.7/site-packages/vdsm/utils.py", line 941, in wrapperrr
    return func(inst, *args, **kwargs)
  File "/usr/lib64/python2.7/site-packages/libvirt.py", line 3777, in createXML
    if ret is None:raise libvirtError('virDomainCreateXML() failed', conn=self)
libvirtError: internal error: Attempted double use of PCI slot 0000:00:01.0 (may need "multifunction='on'" for device on function 0)
2017-05-22 11:50:45,365+0530 INFO  (vm/1b8dc1a2) [virt.vm] (vmId='1b8dc1a2-acd3-4a57-9a2b-23f12ae52e38') Changed state to Down: internal error: Attempted double use of PCI slot 0000:00:01.0 (may need "multifunction='on'" for device on function 0) (code=1) (vm:1207)
2017-05-22 11:50:45,365+0530 INFO  (vm/1b8dc1a2) [virt.vm] (vmId='1b8dc1a2-acd3-4a57-9a2b-23f12ae52e38') Stopping connection (guestagent:430)
2017-05-22 11:50:46,061+0530 INFO  (jsonrpc/3) [dispatcher] Run and protect: getSpmStatus(spUUID=u'5a9ca74c-fbc1-4844-92db-18086447c491', options=None) (logUtils:51)
2017-05-22 11:50:46,073+0530 INFO  (jsonrpc/3) [dispatcher] Run and protect: getSpmStatus, Return response: {'spm_st': {'spmId': 2, 'spmStatus': 'SPM', 'spmLver': 40L}} (logUtils:54)
2017-05-22 11:50:46,073+0530 INFO  (jsonrpc/3) [jsonrpc.JsonRpcServer] RPC call StoragePool.getSpmStatus succeeded in 0.01 seconds (__init__:515)
2017-05-22 11:50:46,079+0530 INFO  (jsonrpc/1) [vdsm.api] START destroy(gracefulAttempts=1) (api:39)
2017-05-22 11:50:46,080+0530 INFO  (jsonrpc/1) [virt.vm] (vmId='1b8dc1a2-acd3-4a57-9a2b-23f12ae52e38') Release VM resources (vm:4199)
2017-05-22 11:50:46,080+0530 WARN  (jsonrpc/1) [virt.vm] (vmId='1b8dc1a2-acd3-4a57-9a2b-23f12ae52e38') trying to set state to Powering down when already Down (vm:352)
2017-05-22 11:50:46,080+0530 INFO  (jsonrpc/1) [virt.vm] (vmId='1b8dc1a2-acd3-4a57-9a2b-23f12ae52e38') Stopping connection (guestagent:430)
"""

VDSM_VER_4_LOG_3 = r"""
2017-04-18 13:56:33,718+0200 INFO  (jsonrpc/3) [jsonrpc.JsonRpcServer] RPC call Host.getStats succeeded in 0.03 seconds (__init__:515)
2017-04-18 13:56:35,208+0200 INFO  (jsonrpc/5) [jsonrpc.JsonRpcServer] RPC call Host.getAllVmStats succeeded in 0.01 seconds (__init__:515)
2017-04-18 13:56:38,297+0200 INFO  (itmap/0) [IOProcessClient] Starting client ioprocess-29890 (__init__:325)
2017-04-18 13:56:38,315+0200 INFO  (itmap/1) [IOProcessClient] Starting client ioprocess-29891 (__init__:325)
2017-04-18 13:56:38,330+0200 INFO  (ioprocess communication (16074)) [IOProcess] Starting ioprocess (__init__:447)
2017-04-18 13:56:38,335+0200 INFO  (itmap/2) [IOProcessClient] Starting client ioprocess-29892 (__init__:325)
2017-04-18 13:56:38,354+0200 INFO  (jsonrpc/2) [dispatcher] Run and protect: getSpmStatus(spUUID=u'00000002-0002-0002-0002-00000000024f', options=None) (logUtils:51)
2017-04-18 13:56:38,357+0200 INFO  (ioprocess communication (16082)) [IOProcess] Starting ioprocess (__init__:447)
2017-04-18 13:56:38,360+0200 INFO  (itmap/3) [IOProcessClient] Starting client ioprocess-29893 (__init__:325)
2017-04-18 13:56:38,374+0200 INFO  (jsonrpc/2) [dispatcher] Run and protect: getSpmStatus, Return response: {'spm_st': {'spmId': 1, 'spmStatus': 'SPM', 'spmLver': 3L}} (logUtils:54)
2017-04-18 13:56:38,376+0200 INFO  (jsonrpc/2) [jsonrpc.JsonRpcServer] RPC call StoragePool.getSpmStatus succeeded in 0.02 seconds (__init__:515)
2017-04-18 13:56:38,382+0200 INFO  (ioprocess communication (16090)) [IOProcess] Starting ioprocess (__init__:447)
2017-04-18 13:56:38,386+0200 INFO  (itmap/4) [IOProcessClient] Starting client ioprocess-29894 (__init__:325)
2017-04-18 13:56:38,401+0200 INFO  (ioprocess communication (16097)) [IOProcess] Starting ioprocess (__init__:447)
2017-04-18 13:56:38,405+0200 INFO  (ioprocess communication (16104)) [IOProcess] Starting ioprocess (__init__:447)
2017-04-18 13:56:38,427+0200 INFO  (monitor/0c78b4d) [storage.StorageDomain] Resource namespace 01_img_0c78b4d6-ba00-4d3e-9f9f-65c7d5899d71 already registered (sd:732)
"""

VDSM_VER_4_LOG_4 = r"""
2017-04-18 14:00:00,000+0200 INFO  (jsonrpc/2) [jsonrpc.JsonRpcServer] RPC call Host.getStats succeeded in 0.02 seconds (__init__:515)
2017-04-18 14:00:01,807+0200 INFO  (Reactor thread) [ProtocolDetector.AcceptorImpl] Accepted connection from ::ffff:10.34.60.219:49213 (protocoldetector:72)
2017-04-18 14:00:01,808+0200 ERROR (Reactor thread) [ProtocolDetector.SSLHandshakeDispatcher] Error during handshake: unexpected eof (m2cutils:304)
2017-04-18 14:00:03,304+0200 INFO  (jsonrpc/6) [jsonrpc.JsonRpcServer] RPC call Host.getAllVmStats succeeded in 0.00 seconds (__init__:515)
2017-04-18 14:00:05,870+0200 INFO  (jsonrpc/7) [dispatcher] Run and protect: getSpmStatus(spUUID=u'00000002-0002-0002-0002-00000000024f', options=None) (logUtils:51)
"""

VDSM_VER_4_LOG_5 = r"""
2018-01-31 09:20:02,658+0530 DEBUG (check/loop) [storage.check] FINISH check u'/rhev/data-center/mnt/rhevm.example.com:_home_exports_iso/be94b389-000f-4487-baf4-35ded403e579/dom_md/metadata' (rc=0, elapsed=0.05) (check:328)
2018-01-31 09:20:02,955+0530 DEBUG (mailbox-spm) [storage.Misc.excCmd] /usr/bin/taskset --cpu-list 0-15 dd if=/rhev/data-center/5a5e5d2a-0076-00b1-00b8-00000000006f/mastersd/dom_md/inbox iflag=direct,fullblock count=1 bs=1024000 (cwd None) (commands:69)
2018-01-31 09:20:03,006+0530 DEBUG (mailbox-spm) [storage.Misc.excCmd] SUCCESS: <err> = '1+0 records in\n1+0 records out\n1024000 bytes (1.0 MB) copied, 0.0350045 s, 29.3 MB/s\n'; <rc> = 0 (commands:93)
2018-01-31 09:20:05,016+0530 DEBUG (mailbox-spm) [storage.Misc.excCmd] /usr/bin/taskset --cpu-list 0-15 dd if=/rhev/data-center/5a5e5d2a-0076-00b1-00b8-00000000006f/mastersd/dom_md/inbox iflag=direct,fullblock count=1 bs=1024000 (cwd None) (commands:69)
2018-01-31 09:20:05,040+0530 DEBUG (mailbox-spm) [storage.Misc.excCmd] SUCCESS: <err> = '1+0 records in\n1+0 records out\n1024000 bytes (1.0 MB) copied, 0.0171592 s, 59.7 MB/s\n'; <rc> = 0 (commands:93)
"""


def test_vdsm_version_4_log():
    # Check lines with level 'ERROR'.
    # (psachin): This will NOT parse Python Traceback
    vdsm_log = VDSMLog(context_wrap(VDSM_VER_4_LOG_1))
    assert 'libvirtError' in vdsm_log
    lines_with_error = vdsm_log.get('The vm start process failed')
    parsed = list(vdsm_log.parse_lines(lines_with_error))
    assert parsed[0] == {
        'thread': 'vm/27f1a8d4',
        'level': 'ERROR',
        'logname': 'virt.vm',
        'module': 'vm',
        'asctime': datetime(2017, 4, 18, 13, 56, 28, 96000),
        'lineno': '617',
        'message': "(vmId='27f1a8d4-1f81-49e6-bd83-4ecb0a462b54') The vm start process failed"  # noqa
    }

    # Looks for traceback
    assert 'Traceback' in vdsm_log

    # This will not work(== 0) as get_after() don't work for milliseconds
    after_error_logs = vdsm_log.get_after(parsed[0]['asctime'], 'The vm start process failed')
    assert len(list(after_error_logs)) == 0

    # Try to see if the INFO logs with same thread has messages with content '..PCI slot' and 'Stopping connection'
    info_lines = list(vdsm_log.parse_lines(vdsm_log.get(parsed[0]['thread'])))
    assert len(info_lines) == 3
    for line in info_lines:
        if 'Attempted double use of PCI slot' in line['message'] and line['level'] == 'INFO':
            assert line['logname'] == 'virt.vm'
        if 'Stopping connection' in line['message'] and line['level'] == 'INFO':
            assert line['module'] == 'guestagent'

    # Another logs with line having 'ERROR' but with different
    # thread_name & datetime,
    vdsm_log = VDSMLog(context_wrap(VDSM_VER_4_LOG_2))
    assert 'libvirtError' in vdsm_log
    lines_with_error = vdsm_log.get('ERROR')
    parsed = list(vdsm_log.parse_lines(lines_with_error))
    assert parsed[0] == {
        'thread': 'vm/1b8dc1a2',
        'level': 'ERROR',
        'logname': 'virt.vm',
        'module': 'vm',
        'asctime': datetime(2017, 5, 22, 11, 50, 45, 363000),
        'lineno': '617',
        'message': "(vmId='1b8dc1a2-acd3-4a57-9a2b-23f12ae52e38') The vm start process failed"  # noqa
    }

    # Parse line with level 'WARN'
    assert 'WARN' in vdsm_log
    lines_with_warn = vdsm_log.get('WARN')
    parsed = list(vdsm_log.parse_lines(lines_with_warn))
    assert parsed[0] == {
        'asctime': datetime(2017, 5, 22, 11, 50, 46, 80000),
        'level': 'WARN',
        'lineno': '352',
        'message': "(vmId='1b8dc1a2-acd3-4a57-9a2b-23f12ae52e38') trying to set state to Powering down when already Down",  # noqa
        'module': 'vm',
        'logname': 'virt.vm',
        'thread': 'jsonrpc/1'
    }

    # Logs with lines having level 'INFO'
    vdsm_log = VDSMLog(context_wrap(VDSM_VER_4_LOG_3))
    lines_with_info = vdsm_log.get('INFO')
    parsed = list(vdsm_log.parse_lines(lines_with_info))
    assert len(parsed) == 16
    assert parsed[15] == {
        'asctime': datetime(2017, 4, 18, 13, 56, 38, 427000),
        'level': 'INFO',
        'lineno': '732',
        'message': 'Resource namespace 01_img_0c78b4d6-ba00-4d3e-9f9f-65c7d5899d71 already registered',  # noqa
        'module': 'sd',
        'logname': 'storage.StorageDomain',
        'thread': 'monitor/0c78b4d',
    }

    lines_with_spm_st = vdsm_log.get('spm_st')
    parsed = list(vdsm_log.parse_lines(lines_with_spm_st))
    assert parsed[0] == {
        'asctime': datetime(2017, 4, 18, 13, 56, 38, 374000),
        'level': 'INFO',
        'lineno': '54',
        'message': "Run and protect: getSpmStatus, Return response: {'spm_st': {'spmId': 1, 'spmStatus': 'SPM', 'spmLver': 3L}}",  # noqa
        'module': 'logUtils',
        'logname': 'dispatcher',
        'thread': 'jsonrpc/2'
    }

    # Logs with line having ERROR with different fields than
    # VDSM_LOG_1 & VDSM_LOG_2 altogether
    vdsm_log = VDSMLog(context_wrap(VDSM_VER_4_LOG_4))
    assert 'ERROR' in vdsm_log
    lines_with_error = vdsm_log.get('ERROR')
    parsed = list(vdsm_log.parse_lines(lines_with_error))
    assert parsed[0] == {
        'asctime': datetime(2017, 4, 18, 14, 0, 1, 808000),
        'level': 'ERROR',
        'lineno': '304',
        'message': 'Error during handshake: unexpected eof',
        'module': 'm2cutils',
        'logname': 'ProtocolDetector.SSLHandshakeDispatcher',
        'thread': 'Reactor thread'
    }

    # Check DEBUG logs
    vdsm_log = VDSMLog(context_wrap(VDSM_VER_4_LOG_5))

    assert 'DEBUG' in vdsm_log
    lines_with_debug = vdsm_log.get('DEBUG')
    parsed = list(vdsm_log.parse_lines(lines_with_debug))
    assert len(parsed) == 5

    lines_with_storage_check = vdsm_log.get('storage.check')
    parsed = list(vdsm_log.parse_lines(lines_with_storage_check))
    assert len(parsed) == 1
    assert parsed[0] == {
        'asctime': datetime(2018, 1, 31, 9, 20, 2, 658000),
        'level': 'DEBUG',
        'lineno': '328',
        'message': "FINISH check u'/rhev/data-center/mnt/rhevm.example.com:_home_exports_iso/be94b389-000f-4487-baf4-35ded403e579/dom_md/metadata' (rc=0, elapsed=0.05)",
        'module': 'check',
        'logname': 'storage.check',
        'thread': 'check/loop'
    }
