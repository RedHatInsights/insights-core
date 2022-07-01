"""
LsSystemdUnits - command ``/bin/ls -lanRL /etc/systemd /run/systemd /usr/lib/systemd /usr/local/lib/systemd``
=============================================================================================================

This parser provides file listing for Systemd Units gathered from
the ``/bin/ls -lanRL /etc/systemd /run/systemd /usr/lib/systemd /usr/local/lib/systemd`` command.

The paths ``/usr/local/share/systemd`` and ``/usr/share/systemd`` were also checked,
but no results were found for them.


The shortened sample output of the command is::

    /etc/systemd:
    total 40
    drwxr-xr-x.  4 0 0  150 Apr  4  2019 .
    drwxr-xr-x. 88 0 0 8192 Jun 28 06:56 ..
    -rw-r--r--.  1 0 0  615 Jun 22  2018 coredump.conf
    -rw-r--r--.  1 0 0 1027 Jun 22  2018 journald.conf
    -rw-r--r--.  1 0 0 1052 Apr  4  2019 logind.conf
    -rw-r--r--.  1 0 0  631 Feb 26  2019 resolved.conf
    drwxr-xr-x. 17 0 0 4096 Apr  4  2019 system
    -rw-r--r--.  1 0 0 1682 Feb 26  2019 system.conf
    drwxr-xr-x.  2 0 0    6 Feb 26  2019 user
    -rw-r--r--.  1 0 0 1130 Jun 22  2018 user.conf

    /etc/systemd/system:
    total 28
    drwxr-xr-x. 17 0 0 4096 Apr  4  2019 .
    drwxr-xr-x.  4 0 0  150 Apr  4  2019 ..
    drwxr-xr-x.  2 0 0   31 Apr  4  2019 basic.target.wants
    -rw-r--r--.  1 0 0 1341 Feb  8  2019 dbus-org.freedesktop.NetworkManager.service
    -rw-r--r--.  1 0 0  353 Feb  8  2019 dbus-org.freedesktop.nm-dispatcher.service
    -rw-r--r--.  1 0 0  238 Nov  7  2017 dbus-org.freedesktop.timedate1.service
    -rw-r--r--.  1 0 0  532 Jun 22  2018 default.target
    drwxr-xr-x.  2 0 0   32 Apr  4  2019 getty.target.wants
    drwxr-xr-x.  2 0 0 4096 Apr  4  2019 multi-user.target.wants
    drwxr-xr-x.  2 0 0   48 Apr  4  2019 network-online.target.wants
    drwxr-xr-x.  2 0 0   33 Apr  4  2019 nfs-blkmap.service.requires
    drwxr-xr-x.  2 0 0   33 Apr  4  2019 nfs-idmapd.service.requires
    drwxr-xr-x.  2 0 0   33 Apr  4  2019 nfs-mountd.service.requires
    drwxr-xr-x.  2 0 0   33 Apr  4  2019 nfs-server.service.requires
    drwxr-xr-x.  2 0 0   31 Apr  4  2019 remote-fs.target.wants
    drwxr-xr-x.  2 0 0   33 Apr  4  2019 rpc-gssd.service.requires
    drwxr-xr-x.  2 0 0   33 Apr  4  2019 rpc-statd-notify.service.requires
    drwxr-xr-x.  2 0 0   33 Apr  4  2019 rpc-statd.service.requires
    drwxr-xr-x.  2 0 0   51 Apr  4  2019 sockets.target.wants
    drwxr-xr-x.  2 0 0  151 Apr  4  2019 sysinit.target.wants
    -rw-r--r--.  1 0 0  583 Dec 17  2018 syslog.service
    crw-rw-rw-.  1 0 0 1, 3 Jun 28 06:56 systemd-timedated.service
    drwxr-xr-x.  2 0 0   34 Apr  4  2019 timers.target.wants

    /etc/systemd/system/basic.target.wants:
    total 8
    drwxr-xr-x.  2 0 0   31 Apr  4  2019 .
    drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
    -rw-r--r--.  1 0 0  284 Nov  6  2018 microcode.service

Examples:
    >>> type(ls_systemd_units)
    <class 'insights.parsers.ls_systemd_units.LsSystemdUnits'>
    >>> ls_systemd_units.dirs_of("/etc/systemd")
    ['.', '..', 'system', 'user']
    >>> ls_systemd_units.files_of("/etc/systemd/system/basic.target.wants")
    ['microcode.service']
    >>> ls_systemd_units.specials_of("/etc/systemd/system")
    ['systemd-timedated.service']
    >>> ls_systemd_units.dir_contains("/etc/systemd/system", "default.target")
    True
    >>> ls_systemd_units.dir_entry("/etc/systemd/system", "syslog.service")["perms"]
    'rw-r--r--.'
"""

from insights.core import CommandParser, FileListing
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ls_systemd_units)
class LsSystemdUnits(CommandParser, FileListing):
    """
    Class for parsing the ``/bin/ls -lanRL /etc/systemd /run/systemd /usr/lib/systemd /usr/local/lib/systemd`` command.
    For more information, see the ``FileListing`` class.
    """
    pass
