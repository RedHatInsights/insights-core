"""
LsPgsqlData - command ``/bin/ls -lan /var/lib/pgsql/data``
==========================================================

The ``/bin/ls -lan /var/lib/pgsql/data`` command provides information for the
listing of the ``/var/lib/pgsql/data`` directory.
Sample input is shown in the Examples.
See ``FileListing`` class for additional information.

Sample directory list::

    total 92
    drwx------. 15 26 26  4096 Sep  5 03:01 .
    drwx------.  4 26 26    68 Sep  5 02:42 ..
    drwx------.  5 26 26    38 Sep  5 02:42 base
    drwx------.  2 26 26  4096 Sep  5 03:01 global
    drwx------.  2 26 26    17 Sep  5 02:42 pg_clog
    -rw-------.  1 26 26  4232 Sep  5 02:42 pg_hba.conf
    -rw-------.  1 26 26  1636 Sep  5 02:42 pg_ident.conf
    drwx------.  2 26 26    82 Sep  5 02:57 pg_log
    drwx------.  4 26 26    34 Sep  5 02:42 pg_multixact
    drwx------.  2 26 26    17 Sep  5 03:01 pg_notify
    drwx------.  2 26 26     6 Sep  5 02:42 pg_serial
    drwx------.  2 26 26     6 Sep  5 02:42 pg_snapshots
    drwx------.  2 26 26    24 Sep  5 04:48 pg_stat_tmp
    drwx------.  2 26 26    17 Sep  5 02:42 pg_subtrans
    drwx------.  2 26 26     6 Sep  5 02:42 pg_tblspc
    drwx------.  2 26 26     6 Sep  5 02:42 pg_twophase
    -rw-------.  1 26 26     4 Sep  5 02:42 PG_VERSION
    drwx------.  3 26 26    58 Sep  5 02:42 pg_xlog
    -rw-------.  1 26 26 19842 Sep  5 03:01 postgresql.conf
    -rw-------.  1 26 26    57 Sep  5 03:01 postmaster.opts
    -rw-------.  1 26 26    91 Sep  5 03:01 postmaster.pid

Examples:

    >>> ls_pgsql_data.files_of('/var/lib/pgsql/data')
    ['pg_hba.conf', 'pg_ident.conf', 'PG_VERSION', 'postgresql.conf', 'postmaster.opts', 'postmaster.pid']
"""

from insights.specs import Specs

from .. import FileListing
from .. import parser, CommandParser


@parser(Specs.ls_pgsql_data)
class LsPgsqlData(CommandParser, FileListing):
    """Parses output of ``/bin/ls -lan /var/lib/pgsql/data`` command."""
    pass
