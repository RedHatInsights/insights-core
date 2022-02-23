"""
Systemd File Permissions parsers
================================

Parsers included in this module are:

LsEtcSystemd - command ``ls -lanRL /etc/systemd``
-------------------------------------------------

LsUsrLibSystemd - command ``ls -lanRL /usr/lib/systemd``
--------------------------------------------------------

"""
from insights.core import CommandParser, FileListing
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ls_etc_systemd)
class LsEtcSystemd(CommandParser, FileListing):
    """
    Class for parsing ``ls -lanRL /etc/systemd`` command.

    The ``ls -lanRL /etc/systemd`` command provides information for the listing of the ``/etc/systemd`` directory.

    See the ``FileListing`` class for a more complete description of the available features of the class.

    Sample output of ``ls -lanRL /etc/systemd`` command is::

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

    Examples:
        >>> type(etc_systemd)
        <class 'insights.parsers.ls_systemd.LsEtcSystemd'>
        >>> '/etc/systemd' in etc_systemd
        True
        >>> '/etc/systemd/system' in etc_systemd
        False
        >>> etc_systemd.files_of('/etc/systemd')
        ['bootchart.conf', 'coredump.conf', 'user.conf']
        >>> etc_systemd.dirs_of('/etc/systemd')
        ['.', '..', 'user']
        >>> etc_systemd.dir_contains('/etc/systemd', 'coredump.conf')
        True
        >>> etc_systemd_dict = etc_systemd.listing_of('/etc/systemd')
        >>> etc_systemd_dict['coredump.conf']['perms']
        'rw-r--r--'
        >>> etc_systemd_dict['user']['perms']
        'rwxr-xr-x'

"""
    pass


@parser(Specs.ls_usr_lib_systemd)
class LsUsrLibSystemd(CommandParser, FileListing):
    """
    Class for parsing ``ls -lanRL /usr/lib/systemd`` command.

    The ``ls -lanRL /usr/lib/systemd`` command provides information for the listing of the ``/usr/lib/systemd`` directory.

    See the ``FileListing`` class for a more complete description of the available features of the class.

    Sample output of ``ls -lanRL /usr/lib/systemd`` command is::

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

    Examples:
        >>> type(usr_lib_systemd)
        <class 'insights.parsers.ls_systemd.LsUsrLibSystemd'>
        >>> '/usr/lib/systemd' in usr_lib_systemd
        True
        >>> '/usr/lib/systemd/system' in usr_lib_systemd
        False
        >>> usr_lib_systemd.files_of('/usr/lib/systemd/user')
        ['basic.target', 'bluetooth.target', 'default.target', 'exit.target', 'glib-pacrunner.service', 'paths.target', 'printer.target', 'shutdown.target', 'smartcard.target', 'sockets.target', 'sound.target', 'systemd-exit.service', 'timers.target']
        >>> usr_lib_systemd.dirs_of('/usr/lib/systemd')
        ['.', '..', 'system', 'user']
        >>> usr_lib_systemd.dir_contains('/usr/lib/systemd/user', 'basic.target')
        True
        >>> usr_lib_systemd_dict = usr_lib_systemd.listing_of('/usr/lib/systemd/user')
        >>> usr_lib_systemd_dict['basic.target']['perms']
        'rw-r--r--'
        >>> usr_lib_systemd_dir_dict = usr_lib_systemd.listing_of('/usr/lib/systemd')
        >>> usr_lib_systemd_dir_dict['user']['perms']
        'rwxr-xr-x'

    """
    pass
