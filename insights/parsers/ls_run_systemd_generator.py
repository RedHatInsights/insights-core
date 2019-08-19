"""
LsRunSystemdGenerator - command ``ls -lan /run/systemd/generator``
==================================================================

The ``ls -lan /run/systemd/generator`` command provides information for only
the ``/run/systemd/generator`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    total 28
    drwxr-xr-x.  6 0 0 260 Aug  5 07:35 .
    drwxr-xr-x. 18 0 0 440 Aug  5 07:35 ..
    -rw-r--r--.  1 0 0 254 Aug  5 07:35 boot.mount
    -rw-r--r--.  1 0 0 259 Aug  5 07:35 boot\x2dfake.mount
    -rw-r--r--.  1 0 0 176 Aug  5 07:35 dev-mapper-rhel\x2dswap.swap
    drwxr-xr-x.  2 0 0 100 Aug  5 07:35 local-fs.target.requires
    -rw-r--r--.  1 0 0 217 Aug  5 07:35 -.mount
    drwxr-xr-x.  2 0 0  60 Aug  5 07:35 nfs-server.service.d
    drwxr-xr-x.  2 0 0 100 Aug  5 07:35 remote-fs.target.requires
    -rw-r--r--.  1 0 0 261 Aug  5 07:35 root-mnt_nfs3.mount
    -rw-r--r--.  1 0 0 261 Aug  5 07:35 root-mnt\x2dnfs1.mount
    -rw-r--r--.  1 0 0 261 Aug  5 07:35 root-mnt\x2dnfs2.mount
    drwxr-xr-x.  2 0 0  60 Aug  5 07:35 swap.target.requires

Examples:

    >>> ls.files_of("/run/systemd/generator") == ['boot.mount', 'boot-fake.mount', 'dev-mapper-rhel-swap.swap', '-.mount', 'root-mnt_nfs3.mount', 'root-mnt-nfs1.mount', 'root-mnt-nfs2.mount']
    True
    >>> ls.dir_entry("/run/systemd/generator", '-.mount')['perms']
    'rw-r--r--.'
"""

from insights import parser, CommandParser, FileListing
from insights.specs import Specs


@parser(Specs.ls_run_systemd_generator)
class LsRunSystemdGenerator(CommandParser, FileListing):
    """Parses output of ``ls -lan /run/systemd/generator`` command."""
    pass
