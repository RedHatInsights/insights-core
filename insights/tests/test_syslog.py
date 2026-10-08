import datetime

from insights.core import Syslog
from insights.parsers.pacemaker_log import PacemakerLog
from insights.tests import context_wrap

MSGINFO = """
Apr 22 10:35:01 boy-bona CROND[27921]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
Apr 22 10:37:32 boy-bona crontab[28951]: (root) LIST (root)
Apr 22 10:40:01 boy-bona CROND[30677]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
Apr 22 10:41:13 boy-bona crontab[32515]: (root) LIST (root)
Apr 29 11:33:36 kvmr7u5 ehtest: crontab[12345]: {
April 29 11:33:36 kvmr7u5 ehtest: crontab[12345]: { # this line will be skipped by `_parse_line`
May  5 03:50:01 kvmr7u5 systemd: Removed slice user-0.slice.
May  9 15:13:34 lxc-rhel68-sat56 jabberd/sm[11057]: session started: jid=rhn-dispatcher-sat@lxc-rhel6-sat56.redhat.com/superclient
May  9 15:13:36 lxc-rhel68-sat56 wrapper[11375]: --> Wrapper Started as Daemon
May  9 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM...
May 10 15:24:28 lxc-rhel68-sat56 yum[11597]: Installed: lynx-2.8.6-27.el6.x86_64
May 10 15:36:19 lxc-rhel68-sat56 yum[11954]: Updated: sos-3.2-40.el6.noarch
""".strip()


MSGINFO_FEB29 = """
Feb 28 12:00:01 testhost CROND[1234]: (root) CMD (/usr/bin/test)
Feb 29 09:15:42 testhost watchdog[5678]: shutting down the system because of error 1
Feb 29 10:30:00 testhost sshd[9012]: Accepted publickey for user1
Mar  1 08:00:01 testhost CROND[3456]: (root) CMD (/usr/bin/test)
""".strip()


MSGINFO_INVALID_DATE = """
Feb 31 12:00:01 testhost CROND[1234]: (root) CMD (/usr/bin/test)
Feb 29 09:15:42 testhost watchdog[5678]: shutting down the system because of error 1
""".strip()


MSGINFO_FEB29_LEAP_YEAR_FAILED = """
Feb 30 12:00:01 testhost CROND[1234]: (root) CMD (/usr/bin/test)
Feb 29 09:15:42 testhost watchdog[5678]: shutting down the system because of error 1
""".strip()


def test_syslog_feb29():
    """Feb 29 log lines must parse correctly despite strptime defaulting to 1900 (not a leap year)."""
    msg_info = Syslog(context_wrap(MSGINFO_FEB29))
    feb29_lines = msg_info.get('shutting down')
    assert len(feb29_lines) == 1
    assert feb29_lines[0].get('timestamp') == 'Feb 29 09:15:42'
    assert feb29_lines[0].get('hostname') == 'testhost'
    assert feb29_lines[0].get('procname') == 'watchdog[5678]'
    assert feb29_lines[0].get('message') == 'shutting down the system because of error 1'

    sshd_lines = msg_info.get('Accepted publickey')
    assert len(sshd_lines) == 1
    assert sshd_lines[0].get('timestamp') == 'Feb 29 10:30:00'
    assert sshd_lines[0].get('procname') == 'sshd[9012]'

    all_lines = msg_info.get('CMD')
    assert len(all_lines) == 2
    assert all_lines[0].get('timestamp') == 'Feb 28 12:00:01'
    assert all_lines[1].get('timestamp') == 'Mar  1 08:00:01'


def test_syslog_invalid_date():
    """Invalid date like Feb 31 should not be parsed as timestamp."""
    msg_info = Syslog(context_wrap(MSGINFO_INVALID_DATE))
    invalid_lines = msg_info.get('CROND')
    assert len(invalid_lines) == 1
    # When date is invalid, timestamp/hostname/procname should not be set
    assert invalid_lines[0].get('timestamp') is None
    assert invalid_lines[0].get('hostname') is None
    assert invalid_lines[0].get('procname') is None
    # Message is still extracted (from the part after ': ')
    assert invalid_lines[0].get('message') == '(root) CMD (/usr/bin/test)'
    assert invalid_lines[0].get('raw_message') == 'Feb 31 12:00:01 testhost CROND[1234]: (root) CMD (/usr/bin/test)'

    # Valid Feb 29 should still parse correctly
    watchdog_lines = msg_info.get('shutting down')
    assert len(watchdog_lines) == 1
    assert watchdog_lines[0].get('timestamp') == 'Feb 29 09:15:42'
    assert watchdog_lines[0].get('hostname') == 'testhost'


def test_syslog_leap_year_parsing_fails():
    """When both regular and leap-year parsing fail, date fields should not be set."""
    msg_info = Syslog(context_wrap(MSGINFO_FEB29_LEAP_YEAR_FAILED))
    # Feb 30 is invalid even in leap years
    crond_lines = msg_info.get('CROND')
    assert len(crond_lines) == 1
    parsed = crond_lines[0]
    assert parsed.get('raw_message') == 'Feb 30 12:00:01 testhost CROND[1234]: (root) CMD (/usr/bin/test)'
    # Date/host/proc fields should not be set when date parsing fails
    assert parsed.get('timestamp') is None
    assert parsed.get('hostname') is None
    assert parsed.get('procname') is None
    # Message is still extracted
    assert parsed.get('message') == '(root) CMD (/usr/bin/test)'


def test_syslog():
    msg_info = Syslog(context_wrap(MSGINFO))
    bona_list = msg_info.get('(root) LIST (root)')
    assert 2 == len(bona_list)
    assert bona_list[0].get('timestamp') == "Apr 22 10:37:32"
    assert bona_list[1].get('timestamp') == "Apr 22 10:41:13"
    crond = msg_info.get('CROND')
    assert 2 == len(crond)
    assert crond[0].get('procname') == "CROND[27921]"
    assert msg_info.get('jabberd/sm[11057]')[0].get('hostname') == "lxc-rhel68-sat56"
    assert msg_info.get('Wrapper')[0].get('message') == "--> Wrapper Started as Daemon"
    assert msg_info.get('Launching')[0].get('raw_message') == "May  9 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM..."
    assert 2 == len(msg_info.get('yum'))
    crontab_logs = list(msg_info.get_logs_by_procname('crontab'))
    assert len(crontab_logs) == 2
    assert crontab_logs[1]['raw_message'] == "Apr 22 10:41:13 boy-bona crontab[32515]: (root) LIST (root)"
    systemd_logs = list(msg_info.get_logs_by_procname('systemd'))
    assert len(systemd_logs) == 1
    assert systemd_logs[0]['timestamp'] == 'May  5 03:50:01'


def test_syslog_get_after_feb29():
    """get_after() must handle Feb 29 timestamps in no-year-format logs (Finding 1)."""
    msg_info = Syslog(context_wrap(MSGINFO_FEB29))
    # Fetch all lines after Feb 1
    lines = list(msg_info.get_after(datetime.datetime(2000, 2, 1)))
    assert len(lines) == 4
    # Verify Feb 29 lines are included
    feb29_lines = [l for l in lines if 'Feb 29' in l.get('timestamp', '')]
    assert len(feb29_lines) == 2
    # Verify all timestamps are parsed correctly
    assert lines[0].get('timestamp') == 'Feb 28 12:00:01'
    assert lines[1].get('timestamp') == 'Feb 29 09:15:42'
    assert lines[2].get('timestamp') == 'Feb 29 10:30:00'
    assert lines[3].get('timestamp') == 'Mar  1 08:00:01'


def test_syslog_get_after_invalid_date():
    """get_after() must skip genuinely invalid dates without crashing (Finding 2)."""
    content = '''
Feb 28 12:00:01 testhost CROND[1234]: (root) CMD (/usr/bin/test)
Feb 30 09:15:42 testhost watchdog[5678]: invalid date should be skipped
Mar  1 08:00:01 testhost CROND[3456]: (root) CMD (/usr/bin/test)
'''.strip()
    msg_info = Syslog(context_wrap(content))
    lines = list(msg_info.get_after(datetime.datetime(2000, 2, 1)))
    # Feb 30 is invalid, should be skipped; only 2 valid lines returned
    assert len(lines) == 2
    assert lines[0].get('timestamp') == 'Feb 28 12:00:01'
    assert lines[1].get('timestamp') == 'Mar  1 08:00:01'


def test_pacemaker_log_get_after_feb29():
    """get_after() must work for non-Syslog no-year LogFileOutput subclasses too (Finding 1)."""
    content = '''
Feb 28 12:00:01 [1234] example.redhat.com cib:     info: some message
Feb 29 09:15:42 [5678] example.redhat.com crmd:    info: feb 29 message
Mar  1 08:00:01 [3456] example.redhat.com pacemakerd: info: march message
'''.strip()
    log = PacemakerLog(context_wrap(content))
    lines = list(log.get_after(datetime.datetime(2000, 2, 1)))
    assert len(lines) == 3
    assert 'Feb 29' in lines[1].get('raw_message', '')
