"""
Ls Etc Directory
================

Parsers provided in this module includes:

LsEtc - command ``ls -lan /etc </etc/sub-dirs>``
------------------------------------------------

LsEtcSsh - command ``/bin/ls -lanL /etc/ssh``
---------------------------------------------
"""
from .. import parser, CommandParser
from .. import FileListing
from insights.specs import Specs


@parser(Specs.ls_etc)
class LsEtc(CommandParser, FileListing):
    """
    Parses output of ``ls -lan /etc </etc/sub-directories>`` command.

    The ``ls -lan /etc </etc/sub-directories>`` command provides information for
    the listing of the ``/etc`` directory and specified sub-directories.
    See ``FileListing`` class for additional information.

    Sample ``ls -lan /etc/sysconfig /etc/rc.d/rc3.d`` output::

        /etc/sysconfig:
        total 96
        drwxr-xr-x.  7 0 0 4096 Jul  6 23:41 .
        drwxr-xr-x. 77 0 0 8192 Jul 13 03:55 ..
        drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq
        drwxr-xr-x.  2 0 0    6 Sep 16  2015 console
        -rw-------.  1 0 0 1390 Mar  4  2014 ebtables-config
        -rw-r--r--.  1 0 0   72 Sep 15  2015 firewalld
        lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub

        /etc/rc.d/rc3.d:
        total 4
        drwxr-xr-x.  2 0 0   58 Jul  6 23:32 .
        drwxr-xr-x. 10 0 0 4096 Sep 16  2015 ..
        lrwxrwxrwx.  1 0 0   20 Jul  6 23:32 K50netconsole -> ../init.d/netconsole
        lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 S10network -> ../init.d/network
        lrwxrwxrwx.  1 0 0   15 Jul  6 23:32 S97rhnsd -> ../init.d/rhnsd

    Examples:

        >>> "sysconfig" in ls_etc
        False
        >>> "/etc/sysconfig" in ls_etc
        True
        >>> len(ls_etc.files_of('/etc/sysconfig'))
        3
        >>> ls_etc.files_of("/etc/sysconfig")
        ['ebtables-config', 'firewalld', 'grub']
        >>> ls_etc.dirs_of("/etc/sysconfig")
        ['.', '..', 'cbq', 'console']
        >>> ls_etc.specials_of("/etc/sysconfig")
        []
        >>> ls_etc.total_of("/etc/sysconfig")
        96
        >>> ls_etc.dir_entry('/etc/sysconfig', 'grub') == {'group': '0', 'name': 'grub', 'links': 1, 'perms': 'rwxrwxrwx.', 'raw_entry': 'lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub', 'owner': '0', 'link': '/etc/default/grub', 'date': 'Jul  6 23:32', 'type': 'l', 'dir': '/etc/sysconfig', 'size': 17}
        True
        >>> ls_etc.files_of('/etc/rc.d/rc3.d')
        ['K50netconsole', 'S10network', 'S97rhnsd']
        >>> sorted(ls_etc.listing_of("/etc/sysconfig").keys()) == sorted(['console', 'grub', '..', 'firewalld', '.', 'cbq', 'ebtables-config'])
        True
        >>> sorted(ls_etc.listing_of("/etc/sysconfig")['console'].keys()) == sorted(['group', 'name', 'links', 'perms', 'raw_entry', 'owner', 'date', 'type', 'dir', 'size'])
        True
        >>> ls_etc.listing_of("/etc/sysconfig")['console']['type']
        'd'
        >>> ls_etc.listing_of("/etc/sysconfig")['console']['perms']
        'rwxr-xr-x.'
        >>> ls_etc.dir_contains("/etc/sysconfig", "console")
        True
        >>> ls_etc.dir_entry("/etc/sysconfig", "console") == {'group': '0', 'name': 'console', 'links': 2, 'perms': 'rwxr-xr-x.', 'raw_entry': 'drwxr-xr-x.  2 0 0    6 Sep 16  2015 console', 'owner': '0', 'date': 'Sep 16  2015', 'type': 'd', 'dir': '/etc/sysconfig', 'size': 6}
        True
        >>> ls_etc.dir_entry("/etc/sysconfig", "grub")['type']
        'l'
        >>> ls_etc.dir_entry("/etc/sysconfig", "grub")['link']
        '/etc/default/grub'
    """
    pass


@parser(Specs.ls_etc_ssh)
class LsEtcSsh(CommandParser, FileListing):
    """
    Parses output of ``ls -lanL /etc/ssh`` command.

    Sample ``ls -lanL /etc/ssh`` output::

        total 612
        drwxr-xr-x.   3 0   0    245 Aug 11 14:19 .
        drwxr-xr-x. 138 0   0   8192 Jul 29 19:11 ..
        -rw-r--r--.   1 0   0 577388 Mar 27  2020 moduli
        -rw-r--r--.   1 0   0   1770 Mar 27  2020 ssh_config
        drwxr-xr-x.   2 0   0     28 May 12 17:10 ssh_config.d
        -rw-r-----.   1 0 994    480 May 13 09:58 ssh_host_ecdsa_key
        -rw-r--r--.   1 0   0    162 May 13 09:58 ssh_host_ecdsa_key.pub
        -rw-r-----.   1 0 994    387 May 13 09:58 ssh_host_ed25519_key
        -rw-r--r--.   1 0   0     82 May 13 09:58 ssh_host_ed25519_key.pub
        -rw-r-----.   1 0 994   2578 May 13 09:58 ssh_host_rsa_key
        -rw-r--r--.   1 0   0    554 May 13 09:58 ssh_host_rsa_key.pub
        -rw-------.   1 0   0   4260 Aug 11 14:19 sshd_config

    Examples:
        >>> type(ls_etc_ssh)
        <class 'insights.parsers.ls_etc.LsEtcSsh'>
        >>> ls_etc_ssh.files_of("/etc/ssh")
        ['moduli', 'ssh_config', 'ssh_host_ecdsa_key', 'ssh_host_ecdsa_key.pub', 'ssh_host_ed25519_key', 'ssh_host_ed25519_key.pub', 'ssh_host_rsa_key', 'ssh_host_rsa_key.pub', 'sshd_config']
        >>> ls_etc_ssh.dir_entry('/etc/ssh', 'ssh_host_rsa_key')['perms']
        'rw-r-----.'
    """
    pass
