"""
LsEtc - command ``/bin/ls -lanL /etc/ssh``
==========================================

The ``/bin/ls -lanL /etc/ssh`` command provides information for the
listing of the ``/etc/ssh`` directory. See ``FileListing`` class for
additional information.

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
    <class 'insights.parsers.ls_etc_ssh.LsEtcSsh'>
    >>> ls_etc_ssh.files_of("/etc/ssh")
    ['moduli', 'ssh_config', 'ssh_host_ecdsa_key', 'ssh_host_ecdsa_key.pub', 'ssh_host_ed25519_key', 'ssh_host_ed25519_key.pub', 'ssh_host_rsa_key', 'ssh_host_rsa_key.pub', 'sshd_config']
    >>> ls_etc_ssh.dir_entry('/etc/ssh', 'ssh_host_rsa_key')['perms']
    'rw-r-----.'
"""

from insights.core import CommandParser, FileListing
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ls_etc_ssh)
class LsEtcSsh(CommandParser, FileListing):
    """
    Parses output of ``ls -lanL /etc/ssh`` command.
    """
    pass
