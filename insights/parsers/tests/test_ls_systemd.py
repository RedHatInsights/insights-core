from insights.parsers.ls_systemd import LsEtcSystemd, LsUsrLibSystemd
from insights.parsers import ls_systemd
from insights.tests import context_wrap
import doctest

ETC_SYSTEMD = """
/etc/systemd:
total 48
drwxr-xr-x   10 501  20   320 Feb 23  2021 .
drwxr-xr-x  129 501  20  4128 Nov  7 15:01 ..
-rw-r--r--    1 501  20   720 Jan 16  2021 bootchart.conf
-rw-r--r--    1 501  20   615 Jan 16  2021 coredump.conf
-rw-r--r--    1 501  20   983 Jan 16  2021 journald.conf
-rw-r--r--    1 501  20   957 Jan 16  2021 logind.conf
drwxr-xr-x   39 501  20  1248 Oct 14 04:49 system
-rw-r--r--    1 501  20  1552 Jan 16  2021 system.conf
drwxr-xr-x    2 501  20    64 Jan 16  2021 user
-rw-r--r--    1 501  20  1127 Jan 16  2021 user.conf

/etc/systemd/system:
total 104
drwxr-xr-x  39 501  20  1248 Oct 14 04:49 .
drwxr-xr-x  10 501  20   320 Feb 23  2021 ..
drwxr-xr-x   5 501  20   160 Jun 19  2018 basic.target.wants
-rw-r--r--   1 501  20   657 Apr 16  2021 dbus-org.fedoraproject.FirewallD1.service
-rw-r--r--   1 501  20  1445 Sep 30  2020 dbus-org.freedesktop.NetworkManager.service
-rw-r--r--   1 501  20   353 Sep 30  2020 dbus-org.freedesktop.nm-dispatcher.service
-rw-r--r--   1 501  20   492 Jan 16  2021 default.target
-rw-r--r--   1 501  20   149 Oct 13 02:51 postgresql.service
-r--r--r--   1 501  20   946 Oct 13 03:02 pulpcore-api.service
-r--r--r--   1 501  20   157 Oct 13 03:02 pulpcore-api.socket
-r--r--r--   1 501  20   832 Oct 14 04:49 pulpcore-content.service
-r--r--r--   1 501  20   162 Oct 13 03:02 pulpcore-content.socket
-r--r--r--   1 501  20   813 Oct 13 03:02 pulpcore-resource-manager.service
-r--r--r--   1 501  20   861 Oct 13 03:02 pulpcore-worker@.service
-rw-r--r--   1 501  20   164 May 13  2020 receptor@.service
-rw-r--r--   1 501  20   602 Jan 16  2020 rh-mongodb34-mongod.service
crw-rw-rw-   1  0   0 1,   3 Mar  2 06:03 systemd-timedated.service

/etc/systemd/system/basic.target.wants:
total 24
drwxr-xr-x   5 501  20   160 Jun 19  2018 .
drwxr-xr-x  39 501  20  1248 Oct 14 04:49 ..
-rw-r--r--   1 501  20   657 Apr 16  2021 firewalld.service
-rw-r--r--   1 501  20   284 Jul 28  2021 microcode.service
-rw-r--r--   1 501  20   217 May 22  2020 rhel-dmesg.service

/etc/systemd/user:
total 0
drwxr-xr-x   2 501  20   64 Jan 16  2021 .
drwxr-xr-x  10 501  20  320 Feb 23  2021 ..
"""

ETC_SYSTEMD_EXAMPLE = """
/etc/systemd:
total 48
drwxr-xr-x   10 501  20   320 Feb 23  2021 .
drwxr-xr-x  129 501  20  4128 Nov  7 15:01 ..
-rw-r--r--    1 501  20   720 Jan 16  2021 bootchart.conf
-rw-r--r--    1 501  20   615 Jan 16  2021 coredump.conf
drwxr-xr-x    2 501  20    64 Jan 16  2021 user
-rw-r--r--    1 501  20  1127 Jan 16  2021 user.conf

/etc/systemd/user:
total 0
drwxr-xr-x   2 501  20   64 Jan 16  2021 .
drwxr-xr-x  10 501  20  320 Feb 23  2021 ..
"""

USR_LIB_SYSTEMD = """
/usr/lib/systemd:
total 0
drwxr-xr-x    4 501  20    128 Feb 23  2021 .
dr-xr-xr-x    8 501  20    256 Oct 13 01:34 ..
drwxr-xr-x  404 501  20  12928 Oct 13 02:50 system
drwxr-xr-x   15 501  20    480 Feb 23  2021 user

/usr/lib/systemd/user:
total 104
drwxr-xr-x  15 501  20  480 Feb 23  2021 .
drwxr-xr-x   4 501  20  128 Feb 23  2021 ..
-rw-r--r--   1 501  20  457 Jan 16  2021 basic.target
-rw-r--r--   1 501  20  379 Jan 16  2021 bluetooth.target
-rw-r--r--   1 501  20  414 Jan 16  2021 default.target
-rw-r--r--   1 501  20  499 Jan 16  2021 exit.target
-rw-r--r--   1 501  20  147 May 31  2018 glib-pacrunner.service
-rw-r--r--   1 501  20  354 Jan 16  2021 paths.target
-rw-r--r--   1 501  20  377 Jan 16  2021 printer.target
-rw-r--r--   1 501  20  402 Jan 16  2021 shutdown.target
-rw-r--r--   1 501  20  380 Jan 16  2021 smartcard.target
-rw-r--r--   1 501  20  356 Jan 16  2021 sockets.target
-rw-r--r--   1 501  20  380 Jan 16  2021 sound.target
-rw-r--r--   1 501  20  501 Jan 16  2021 systemd-exit.service
-rw-r--r--   1 501  20  405 Jan 16  2021 timers.target
"""


def test_etc_systemd():
    etc_systemd_perm = LsEtcSystemd(context_wrap(ETC_SYSTEMD))
    assert '/etc/systemd' in etc_systemd_perm
    assert '/etc/systemd/system' in etc_systemd_perm
    assert '/etc/systemd/system/basic.target.wants' in etc_systemd_perm
    assert '/etc/systemd/user' in etc_systemd_perm
    assert etc_systemd_perm.dirs_of('/etc/systemd') == ['.', '..', 'system', 'user']

    basic_target_wants = etc_systemd_perm.files_of('/etc/systemd/system/basic.target.wants')
    assert 'firewalld.service' in basic_target_wants
    assert 'microcode.service' in basic_target_wants
    assert 'rhel-dmesg.service' in basic_target_wants
    assert 'systemd-timedated.service' not in basic_target_wants
    assert len(basic_target_wants) == 3

    assert etc_systemd_perm.listing_of('/etc/systemd')['user.conf'] == {'type': '-', 'perms': 'rw-r--r--', 'links': 1, 'owner': '501', 'group': '20', 'size': 1127, 'date': 'Jan 16  2021', 'name': 'user.conf', 'raw_entry': '-rw-r--r--    1 501  20  1127 Jan 16  2021 user.conf', 'dir': '/etc/systemd'}


def test_usr_lib_systemd():
    usr_lib_systemd_perm = LsUsrLibSystemd(context_wrap(USR_LIB_SYSTEMD))
    assert '/usr/lib/systemd' in usr_lib_systemd_perm
    assert '/usr/lib/systemd/user' in usr_lib_systemd_perm
    assert usr_lib_systemd_perm.dirs_of('/usr/lib/systemd') == ['.', '..', 'system', 'user']

    usr_lib_systemd_use = usr_lib_systemd_perm.files_of('/usr/lib/systemd/user')
    assert 'basic.target' in usr_lib_systemd_use
    assert 'bluetooth.target' in usr_lib_systemd_use
    assert len(usr_lib_systemd_use) == 13

    assert usr_lib_systemd_perm.listing_of('/usr/lib/systemd/user')['timers.target'] == {'type': '-', 'perms': 'rw-r--r--', 'links': 1, 'owner': '501', 'group': '20', 'size': 405, 'date': 'Jan 16  2021', 'name': 'timers.target', 'raw_entry': '-rw-r--r--   1 501  20  405 Jan 16  2021 timers.target', 'dir': '/usr/lib/systemd/user'}


def test_systemd_examples():
    env = {
        'etc_systemd': LsEtcSystemd(context_wrap(ETC_SYSTEMD_EXAMPLE)),
        'usr_lib_systemd': LsUsrLibSystemd(context_wrap(USR_LIB_SYSTEMD))
    }
    failed, total = doctest.testmod(ls_systemd, globs=env)
    assert failed == 0
