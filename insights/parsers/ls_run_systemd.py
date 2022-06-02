"""
LsRunSystemd - command ``ls -lanRL /run/systemd``
=================================================

The ``ls -lanRL /run/systemd`` command provides information for the listing of the ``/run/systemd`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample output of ``ls -lanRL /run/systemd`` command is::

    /run/systemd:
    total 0
    drwxr-xr-x. 16 0 0  400 May 25 09:03 .
    drwxr-xr-x. 33 0 0  940 May 25 09:03 ..
    srwx------.  1 0 0    0 May 25 09:03 cgroups-agent
    srw-------.  1 0 0    0 May 25 09:03 coredump
    drwxr-xr-x.  4 0 0  140 May 25 09:03 generator
    d---------.  3 0 0  160 May 25 09:03 inaccessible
    srwxrwxrwx.  1 0 0    0 May 25 09:03 notify
    srwxrwxrwx.  1 0 0    0 May 25 09:03 private
    drwxr-xr-x.  2 0 0   40 May 25 09:03 system
    drwxr-xr-x.  2 0 0  100 May 25 09:17 transient

    /run/systemd/generator:
    total 12
    drwxr-xr-x.  4 0 0 140 May 25 09:03 .
    drwxr-xr-x. 16 0 0 400 May 25 09:03 ..
    -rw-r--r--.  1 0 0 254 May 25 09:03 boot.mount
    -rw-r--r--.  1 0 0 230 May 25 09:03 dev-mapper-rhel\x2dswap.swap
    drwxr-xr-x.  2 0 0  80 May 25 09:03 local-fs.target.requires
    -rw-r--r--.  1 0 0 217 May 25 09:03 -.mount
    drwxr-xr-x.  2 0 0  60 May 25 09:03 swap.target.requires

    /run/systemd/generator/local-fs.target.requires:
    total 8
    drwxr-xr-x. 2 0 0  80 May 25 09:03 .
    drwxr-xr-x. 4 0 0 140 May 25 09:03 ..
    -rw-r--r--. 1 0 0 254 May 25 09:03 boot.mount
    -rw-r--r--. 1 0 0 217 May 25 09:03 -.mount

    /run/systemd/generator/swap.target.requires:
    total 4
    drwxr-xr-x. 2 0 0  60 May 25 09:03 .
    drwxr-xr-x. 4 0 0 140 May 25 09:03 ..
    -rw-r--r--. 1 0 0 230 May 25 09:03 dev-mapper-rhel\x2dswap.swap

    /run/systemd/system:
    total 0
    drwxr-xr-x.  2 0 0  40 May 25 09:03 .
    drwxr-xr-x. 16 0 0 400 May 25 09:03 ..

    /run/systemd/transient:
    total 12
    drwxr-xr-x.  2 0 0 100 May 25 09:17 .
    drwxr-xr-x. 16 0 0 400 May 25 09:03 ..
    -rw-r--r--.  1 0 0 275 May 25 09:04 session-6.scope
    -rw-r--r--.  1 0 0 275 May 25 09:17 session-7.scope
    -rw-r--r--.  1 0 0 275 May 25 09:17 session-8.scope

Examples:
    >>> type(ls_run_systemd)
    <class 'insights.parsers.ls_run_systemd.LsRunSystemd'>
    >>> ls_run_systemd.files_of("/run/systemd/generator") == ['boot.mount', 'dev-mapper-rhel-swap.swap', '-.mount']
    True
    >>> ls_run_systemd.dir_entry("/run/systemd/generator", "-.mount")["perms"]
    'rw-r--r--.'
"""

from insights import parser, CommandParser, FileListing
from insights.specs import Specs


@parser(Specs.ls_run_systemd)
class LsRunSystemd(CommandParser, FileListing):
    """Parses output of ``ls -lanRL /run/systemd`` command."""
    pass
