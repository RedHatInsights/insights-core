from datetime import datetime

from insights.core import Syslog
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


MSGINFO_FEB29 = """
Feb 28 10:35:01 boy-bona CROND[27921]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
Feb 29 10:37:32 boy-bona crontab[28951]: (root) LIST (root)
Mar  1 10:40:01 boy-bona CROND[30677]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
""".strip()


def test_syslog_feb29_parsing():
    """Test that Syslog._parse_line() handles Feb 29 timestamps via _is_feb29 check."""
    msg_info = Syslog(context_wrap(MSGINFO_FEB29))
    feb28_list = msg_info.get('Feb 28')
    assert len(feb28_list) == 1
    assert feb28_list[0].get('timestamp') == "Feb 28 10:35:01"

    feb29_list = msg_info.get('Feb 29')
    assert len(feb29_list) == 1
    assert feb29_list[0].get('timestamp') == "Feb 29 10:37:32"
    assert feb29_list[0].get('procname') == "crontab[28951]"

    mar1_list = msg_info.get('Mar  1')
    assert len(mar1_list) == 1
    assert mar1_list[0].get('timestamp') == "Mar  1 10:40:01"


def test_syslog_get_after_feb29():
    """Test that Syslog.get_after() handles Feb 29 timestamps."""
    msg_info = Syslog(context_wrap(MSGINFO_FEB29))

    # Get lines after Feb 28 10:35:00 (includes Feb 28 10:35:01, Feb 29, and Mar 1)
    after_feb28 = list(msg_info.get_after(datetime(2020, 2, 28, 10, 35, 0)))
    assert len(after_feb28) == 3  # Feb 28, Feb 29 and Mar 1
    assert after_feb28[0].get('timestamp') == "Feb 28 10:35:01"
    assert after_feb28[1].get('timestamp') == "Feb 29 10:37:32"
    assert after_feb28[2].get('timestamp') == "Mar  1 10:40:01"

    # Get lines after Feb 29 10:37:32 (includes Feb 29 and Mar 1, because >= condition)
    after_feb29 = list(msg_info.get_after(datetime(2020, 2, 29, 10, 37, 32)))
    assert len(after_feb29) == 2
    assert after_feb29[0].get('timestamp') == "Feb 29 10:37:32"
    assert after_feb29[1].get('timestamp') == "Mar  1 10:40:01"

    # Get lines after Mar 1 10:40:01 (includes Mar 1 due to >= condition)
    after_mar1 = list(msg_info.get_after(datetime(2020, 3, 1, 10, 40, 1)))
    assert len(after_mar1) == 1
    assert after_mar1[0].get('timestamp') == "Mar  1 10:40:01"


class SyslogMultiFormat(Syslog):
    """Syslog with multiple time formats (list-based)."""
    time_format = ['%b %d %H:%M:%S', '%d/%b/%Y:%H:%M:%S']


MSGINFO_MULTI_FORMAT = """
Feb 28 10:35:01 boy-bona CROND[27921]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
Feb 29 10:37:32 boy-bona crontab[28951]: (root) LIST (root)
Mar  1 10:40:01 boy-bona CROND[30677]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
""".strip()


def test_syslog_get_after_feb29_multi_format():
    """Test that Syslog.get_after() handles Feb 29 with list-based time_format."""
    msg_info = SyslogMultiFormat(context_wrap(MSGINFO_MULTI_FORMAT))

    # Get lines after Feb 28 10:35:00
    after_feb28 = list(msg_info.get_after(datetime(2020, 2, 28, 10, 35, 0)))
    assert len(after_feb28) == 3
    assert after_feb28[0].get('timestamp') == "Feb 28 10:35:01"
    assert after_feb28[1].get('timestamp') == "Feb 29 10:37:32"
    assert after_feb28[2].get('timestamp') == "Mar  1 10:40:01"

    # Get lines after Feb 29 10:37:32
    after_feb29 = list(msg_info.get_after(datetime(2020, 2, 29, 10, 37, 32)))
    assert len(after_feb29) == 2
    assert after_feb29[0].get('timestamp') == "Feb 29 10:37:32"
    assert after_feb29[1].get('timestamp') == "Mar  1 10:40:01"
