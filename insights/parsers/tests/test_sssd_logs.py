from insights.parsers.sssd_logs import SSSDLog
from insights.tests import context_wrap
from datetime import datetime

SSSD_LOG_NORMAL = """
(Mon Feb 13 08:32:07 2017) [sssd[be[redhat.com]]] [sdap_get_generic_op_finished] (0x0400): Search result: Success(0), no errmsg set
(Mon Feb 13 08:32:07 2017) [sssd[be[redhat.com]]] [sdap_get_server_opts_from_rootdse] (0x0200): No known USN scheme is supported by this server!
(Mon Feb 13 08:32:07 2017) [sssd[be[redhat.com]]] [sdap_cli_auth_step] (0x0100): expire timeout is 900
(Tue Feb 14 07:41:03 2017) [[sssd[krb5_child[7231]]]] [main] (0x0400): krb5_child started.
(Tue Feb 14 07:41:03 2017) [[sssd[krb5_child[7231]]]] [unpack_buffer] (0x1000): total buffer size: [141]
(Tue Feb 14 07:41:03 2017) [[sssd[krb5_child[7231]]]] [unpack_buffer] (0x0100): cmd [241] uid [12345] gid [12345] validate [false] enterprise principal [false] offline [true] UPN [username@REDHAT.COM]
(Tue Feb 14 09:45:02 2017) [sssd] [sbus_remove_timeout] (0x2000): 0x7f5aceb6a970
(Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): dbus conn: 0x7f5aceb5cff0
(Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): Dispatching.
(Tue Feb 14 09:45:02 2017) [sssd] [sbus_remove_timeout] (0x2000): 0x7f5aceb63eb0
(Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): dbus conn: 0x7f5aceb578b0
(Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): Dispatching.
(Tue Feb 14 09:45:02 2017) [sssd] [sbus_remove_timeout] (0x2000): 0x7f5aceb60f30
(Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): dbus conn: 0x7f5aceb58360
(Tue Feb 14 09:45:02 2017) [sssd] [monitor_hup] (0x0020): Received SIGHUP.
(Tue Feb 14 09:45:02 2017) [sssd] [te_server_hup] (0x0020): Received SIGHUP. Rotating logfiles.
(Tue Feb 73 09:45:02 rock) Fake line to check that date parsing handles corrupted dates
"""

SSSDLog.keep_scan('sighups', 'SIGHUP')


def test_normal_sssd_logs():
    sssd_logs = SSSDLog(context_wrap(SSSD_LOG_NORMAL))
    assert len(sssd_logs.get('sssd')) == 16

    # Check different module formats:
    assert SSSDLog.parse_lines(
        sssd_logs.get('sdap_get_generic_op_finished')
    )[0]['module'] == 'sssd[be[redhat.com]]'
    assert SSSDLog.parse_lines(
        sssd_logs.get('krb5_child started')
    )[0]['module'] == 'sssd[krb5_child[7231]]'
    assert SSSDLog.parse_lines(
        sssd_logs.get('0x7f5aceb6a970')
    )[0]['module'] == 'sssd'
    assert len(SSSDLog.parse_lines(sssd_logs.get('Fake line'))) == 1

    # Check keep_scan to find data.
    sighups = sssd_logs.sighups
    assert len(sighups) == 2
    assert 'monitor_hup' in sighups[0]
    assert 'te_server_hup' in sighups[1]

    # Check parse_lines
    info = SSSDLog.parse_lines(sighups)
    assert info[0] == {
        'date': 'Tue Feb 14 09:45:02 2017',
        'datetime': datetime(2017, 2, 14, 9, 45, 2),
        'module': 'sssd',
        'function': 'monitor_hup',
        'level': '0x0020',
        'message': 'Received SIGHUP.'
    }
