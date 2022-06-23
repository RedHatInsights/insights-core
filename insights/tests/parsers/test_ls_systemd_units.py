import doctest
import pytest

from insights.parsers import ls_systemd_units
from insights.parsers.ls_systemd_units import LsEtcSystemd, LsRunSystemd, LsUsrLibSystemd, LsUsrLocalLibSystemd
from insights.tests import context_wrap

# ls outputs are similar, so continuing only with the full "ls -lanRL /etc/systemd" output
LS_OUTPUT = """
/etc/systemd:
total 40
drwxr-xr-x.   4 0 0  150 May  7  2019 .
drwxr-xr-x. 100 0 0 8192 Jun 22 14:55 ..
-rw-r--r--.   1 0 0  615 Jun 22  2018 coredump.conf
-rw-r--r--.   1 0 0 1027 Jun 22  2018 journald.conf
-rw-r--r--.   1 0 0 1041 Feb 26  2019 logind.conf
-rw-r--r--.   1 0 0  631 Feb 26  2019 resolved.conf
drwxr-xr-x.  10 0 0 4096 May  7  2019 system
-rw-r--r--.   1 0 0 1682 Feb 26  2019 system.conf
drwxr-xr-x.   2 0 0    6 Feb 26  2019 user
-rw-r--r--.   1 0 0 1130 Jun 22  2018 user.conf

/etc/systemd/system:
total 32
drwxr-xr-x. 10 0 0 4096 May  7  2019 .
drwxr-xr-x.  4 0 0  150 May  7  2019 ..
drwxr-xr-x.  2 0 0   31 May  7  2019 basic.target.wants
-rw-r--r--.  1 0 0  657 Jan 14  2019 dbus-org.fedoraproject.FirewallD1.service
-rw-r--r--.  1 0 0 1341 Feb  8  2019 dbus-org.freedesktop.NetworkManager.service
-rw-r--r--.  1 0 0  353 Feb  8  2019 dbus-org.freedesktop.nm-dispatcher.service
-rw-r--r--.  1 0 0  238 Nov  7  2017 dbus-org.freedesktop.timedate1.service
-rw-r--r--.  1 0 0  532 Jun 22  2018 default.target
drwxr-xr-x.  2 0 0   32 May  7  2019 getty.target.wants
drwxr-xr-x.  2 0 0   29 May  7  2019 graphical.target.wants
drwxr-xr-x.  2 0 0 4096 May  7  2019 multi-user.target.wants
drwxr-xr-x.  2 0 0   48 May  7  2019 network-online.target.wants
drwxr-xr-x.  2 0 0  121 May  7  2019 sockets.target.wants
drwxr-xr-x.  2 0 0  254 May  7  2019 sysinit.target.wants
-rw-r--r--.  1 0 0  583 Dec 17  2018 syslog.service
crw-rw-rw-.  1 0 0 1, 3 Jun 22 14:55 systemd-timedated.service
drwxr-xr-x.  2 0 0   34 May  7  2019 timers.target.wants

/etc/systemd/system/basic.target.wants:
total 8
drwxr-xr-x.  2 0 0   31 May  7  2019 .
drwxr-xr-x. 10 0 0 4096 May  7  2019 ..
-rw-r--r--.  1 0 0  284 Nov  6  2018 microcode.service

/etc/systemd/system/getty.target.wants:
total 8
drwxr-xr-x.  2 0 0   32 May  7  2019 .
drwxr-xr-x. 10 0 0 4096 May  7  2019 ..
-rw-r--r--.  1 0 0 1975 Feb 26  2019 getty@tty1.service

/etc/systemd/system/graphical.target.wants:
total 8
drwxr-xr-x.  2 0 0   29 May  7  2019 .
drwxr-xr-x. 10 0 0 4096 May  7  2019 ..
-rw-r--r--.  1 0 0  207 Oct  8  2018 udisks2.service

/etc/systemd/system/multi-user.target.wants:
total 88
drwxr-xr-x.  2 0 0 4096 May  7  2019 .
drwxr-xr-x. 10 0 0 4096 May  7  2019 ..
-rw-r--r--.  1 0 0  222 Aug 12  2018 atd.service
-rw-r--r--.  1 0 0 1516 Jan  9  2019 auditd.service
-rw-r--r--.  1 0 0  495 Aug 13  2018 chronyd.service
-rw-r--r--.  1 0 0  322 Oct  2  2018 crond.service
-rw-r--r--.  1 0 0  301 Jan  4  2019 dnf-makecache.timer
-rw-r--r--.  1 0 0  657 Jan 14  2019 firewalld.service
-rw-r--r--.  1 0 0  224 Nov  6  2018 irqbalance.service
-rw-r--r--.  1 0 0  349 Feb 22  2019 kdump.service
-rw-r--r--.  1 0 0  198 Sep 25  2018 libstoragemgmt.service
-rw-r--r--.  1 0 0  170 Aug 12  2018 mcelog.service
-rw-r--r--.  1 0 0  310 Jan 11  2019 mdmonitor.service
-rw-r--r--.  1 0 0 1341 Feb  8  2019 NetworkManager.service
-rw-r--r--.  1 0 0  522 Jun 22  2018 remote-fs.target
-rw-r--r--.  1 0 0  184 Mar  6  2019 rhsmcertd.service
-rw-r--r--.  1 0 0  583 Dec 17  2018 rsyslog.service
-rw-r--r--.  1 0 0  337 Aug 12  2018 smartd.service
-rw-r--r--.  1 0 0  456 Nov 26  2018 sshd.service
-rw-r--r--.  1 0 0  420 Feb 11  2019 sssd.service
-rw-r--r--.  1 0 0  376 Jul  4  2018 tuned.service
-rw-r--r--.  1 0 0  278 Dec 14  2018 vdo.service

/etc/systemd/system/network-online.target.wants:
total 8
drwxr-xr-x.  2 0 0   48 May  7  2019 .
drwxr-xr-x. 10 0 0 4096 May  7  2019 ..
-rw-r--r--.  1 0 0  302 Feb  8  2019 NetworkManager-wait-online.service

/etc/systemd/system/sockets.target.wants:
total 24
drwxr-xr-x.  2 0 0  121 May  7  2019 .
drwxr-xr-x. 10 0 0 4096 May  7  2019 ..
-r--r--r--.  1 0 0  248 Feb 22  2019 dm-event.socket
-rw-r--r--.  1 0 0  175 Feb 25  2019 iscsid.socket
-rw-r--r--.  1 0 0  165 Feb 25  2019 iscsiuio.socket
-rw-r--r--.  1 0 0  186 Feb 26  2019 multipathd.socket
-rw-r--r--.  1 0 0  187 Feb 11  2019 sssd-kcm.socket

/etc/systemd/system/sysinit.target.wants:
total 40
drwxr-xr-x.  2 0 0  254 May  7  2019 .
drwxr-xr-x. 10 0 0 4096 May  7  2019 ..
-rw-r--r--.  1 0 0  441 Aug  3  2018 import-state.service
-rw-r--r--.  1 0 0  645 Feb 25  2019 iscsi.service
-rw-r--r--.  1 0 0  355 Aug  3  2018 loadmodules.service
-r--r--r--.  1 0 0  239 Feb 22  2019 lvm2-lvmpolld.socket
-r--r--r--.  1 0 0  559 Feb 22  2019 lvm2-monitor.service
-rw-r--r--.  1 0 0  815 Feb 26  2019 multipathd.service
-rw-r--r--.  1 0 0  378 Aug 12  2018 nis-domainname.service
-rw-r--r--.  1 0 0  126 Dec 21  2018 rngd.service
-rw-r--r--.  1 0 0  406 Dec 14  2018 selinux-autorelabel-mark.service

/etc/systemd/system/timers.target.wants:
total 8
drwxr-xr-x.  2 0 0   34 May  7  2019 .
drwxr-xr-x. 10 0 0 4096 May  7  2019 ..
-rw-r--r--.  1 0 0  346 Aug 12  2018 unbound-anchor.timer

/etc/systemd/user:
total 0
drwxr-xr-x. 2 0 0   6 Feb 26  2019 .
drwxr-xr-x. 4 0 0 150 May  7  2019 ..
""".strip()


@pytest.mark.parametrize("parser", [LsEtcSystemd, LsRunSystemd, LsUsrLibSystemd, LsUsrLocalLibSystemd])
def test(parser):
    systemd = parser(context_wrap(LS_OUTPUT))
    assert systemd
    assert len(systemd.listings) == 11
    assert systemd.dirs_of("/etc/systemd/system") == [
        '.',
        '..',
        'basic.target.wants',
        'getty.target.wants',
        'graphical.target.wants',
        'multi-user.target.wants',
        'network-online.target.wants',
        'sockets.target.wants',
        'sysinit.target.wants',
        'timers.target.wants'
    ]
    assert systemd.files_of("/etc/systemd/system") == [
        'dbus-org.fedoraproject.FirewallD1.service',
        'dbus-org.freedesktop.NetworkManager.service',
        'dbus-org.freedesktop.nm-dispatcher.service',
        'dbus-org.freedesktop.timedate1.service',
        'default.target',
        'syslog.service'
    ]
    assert systemd.specials_of("/etc/systemd/system") == [
        'systemd-timedated.service'
    ]
    assert systemd.listing_of("/etc/systemd/system")["syslog.service"] == {
        'date': 'Dec 17  2018',
        'dir': '/etc/systemd/system',
        'group': '0',
        'links': 1,
        'name': 'syslog.service',
        'owner': '0',
        'perms': 'rw-r--r--.',
        'raw_entry': '-rw-r--r--.  1 0 0  583 Dec 17  2018 syslog.service',
        'size': 583,
        'type': '-'
    }


def test_doc_examples():
    env = {
        "ls_etc_systemd": LsEtcSystemd(context_wrap(LS_OUTPUT))
    }
    failed, total = doctest.testmod(ls_systemd_units, globs=env)
    assert failed == 0
