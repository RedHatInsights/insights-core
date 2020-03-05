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
