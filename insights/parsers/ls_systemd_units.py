"""
Systemd Units File Listing parsers
==================================

Parsers included in this module are:

LsEtcSystemd - command ``ls -lanRL /etc/systemd``
-------------------------------------------------
LsRunSystemd - command ``ls -lanRL /run/systemd``
-------------------------------------------------
LsUsrLibSystemd - command ``ls -lanRL /usr/lib/systemd``
--------------------------------------------------------
LsUsrLocalLibSystemd - command ``ls -lanRL /usr/local/lib/systemd``
-------------------------------------------------------------------

The paths "/usr/local/share/systemd" and "/usr/share/systemd"
were also checked, but no results were found for them.


The shortened sample output of e.g. ``ls -lanRL /etc/systemd`` command is::

    /etc/systemd:
    total 40
    drwxr-xr-x.   4 0 0  150 May  7  2019 .
    drwxr-xr-x. 100 0 0 8192 Jun 22 14:55 ..
    -rw-r--r--.   1 0 0  615 Jun 22  2018 coredump.conf
    -rw-r--r--.   1 0 0 1027 Jun 22  2018 journald.conf
    -rw-r--r--.   1 0 0 1041 Feb 26  2019 logind.conf
    -rw-r--r--.   1 0 0  631 Feb 26  2019 resolved.conf
    drwxr-xr-x.   5 0 0 4096 Jun 22 16:01 system
    -rw-r--r--.   1 0 0 1682 Feb 26  2019 system.conf
    drwxr-xr-x.   2 0 0    6 Feb 26  2019 user
    -rw-r--r--.   1 0 0 1130 Jun 22  2018 user.conf

    /etc/systemd/system:
    total 28
    drwxr-xr-x. 5 0 0 4096 Jun 22 16:01 .
    drwxr-xr-x. 4 0 0  150 May  7  2019 ..
    drwxr-xr-x. 2 0 0   31 May  7  2019 basic.target.wants
    -rw-r--r--. 1 0 0  657 Jan 14  2019 dbus-org.fedoraproject.FirewallD1.service
    -rw-r--r--. 1 0 0 1341 Feb  8  2019 dbus-org.freedesktop.NetworkManager.service
    -rw-r--r--. 1 0 0  353 Feb  8  2019 dbus-org.freedesktop.nm-dispatcher.service
    -rw-r--r--. 1 0 0  238 Nov  7  2017 dbus-org.freedesktop.timedate1.service
    -rw-r--r--. 1 0 0  532 Jun 22  2018 default.target
    drwxr-xr-x. 2 0 0   32 May  7  2019 getty.target.wants
    drwxr-xr-x. 2 0 0  254 May  7  2019 sysinit.target.wants
    -rw-r--r--. 1 0 0  583 Dec 17  2018 syslog.service
    crw-rw-rw-. 1 0 0 1, 3 Jun 22 14:55 systemd-timedated.service

    /etc/systemd/system/basic.target.wants:
    total 8
    drwxr-xr-x. 2 0 0   31 May  7  2019 .
    drwxr-xr-x. 5 0 0 4096 Jun 22 16:01 ..
    -rw-r--r--. 1 0 0  284 Nov  6  2018 microcode.service

    /etc/systemd/system/getty.target.wants:
    total 8
    drwxr-xr-x. 2 0 0   32 May  7  2019 .
    drwxr-xr-x. 5 0 0 4096 Jun 22 16:01 ..
    -rw-r--r--. 1 0 0 1975 Feb 26  2019 getty@tty1.service

    /etc/systemd/system/sysinit.target.wants:
    total 40
    drwxr-xr-x. 2 0 0  254 May  7  2019 .
    drwxr-xr-x. 5 0 0 4096 Jun 22 16:01 ..
    -rw-r--r--. 1 0 0  441 Aug  3  2018 import-state.service
    -rw-r--r--. 1 0 0  645 Feb 25  2019 iscsi.service
    -rw-r--r--. 1 0 0  355 Aug  3  2018 loadmodules.service
    -r--r--r--. 1 0 0  239 Feb 22  2019 lvm2-lvmpolld.socket
    -r--r--r--. 1 0 0  559 Feb 22  2019 lvm2-monitor.service
    -rw-r--r--. 1 0 0  815 Feb 26  2019 multipathd.service
    -rw-r--r--. 1 0 0  378 Aug 12  2018 nis-domainname.service
    -rw-r--r--. 1 0 0  126 Dec 21  2018 rngd.service
    -rw-r--r--. 1 0 0  406 Dec 14  2018 selinux-autorelabel-mark.service

    /etc/systemd/user:
    total 0
    drwxr-xr-x. 2 0 0   6 Feb 26  2019 .
    drwxr-xr-x. 4 0 0 150 May  7  2019 ..

Examples:
    >>> type(ls_etc_systemd)
    <class 'insights.parsers.ls_systemd_units.LsEtcSystemd'>
    >>> ls_etc_systemd.dirs_of("/etc/systemd")
    ['.', '..', 'system', 'user']
    >>> ls_etc_systemd.files_of("/etc/systemd/system/basic.target.wants")
    ['microcode.service']
    >>> ls_etc_systemd.specials_of("/etc/systemd/system")
    ['systemd-timedated.service']
    >>> ls_etc_systemd.dir_contains("/etc/systemd/system", "default.target")
    True
    >>> ls_etc_systemd.dir_entry("/etc/systemd/system", "syslog.service")["perms"]
    'rw-r--r--.'
"""

from insights.core import CommandParser, FileListing
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ls_etc_systemd)
class LsEtcSystemd(CommandParser, FileListing):
    """
    Class for parsing the ``ls -lanRL /etc/systemd`` command.
    For more information, see the ``FileListing`` class.
    """
    pass


@parser(Specs.ls_run_systemd)
class LsRunSystemd(CommandParser, FileListing):
    """
    Class for parsing the ``ls -lanRL /run/systemd`` command.
    For more information, see the ``FileListing`` class.
    """
    pass


@parser(Specs.ls_usr_lib_systemd)
class LsUsrLibSystemd(CommandParser, FileListing):
    """
    Class for parsing the ``ls -lanRL /usr/lib/systemd`` command.
    For more information, see the ``FileListing`` class.
    """
    pass


@parser(Specs.ls_usr_local_lib_systemd)
class LsUsrLocalLibSystemd(CommandParser, FileListing):
    """
    Class for parsing the ``ls -lanRL /usr/local/lib/systemd`` command.
    For more information, see the ``FileListing`` class.
    """
    pass
