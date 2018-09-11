import doctest

from insights.parsers import ls_pgsql_data
from insights.parsers.ls_pgsql_data import LsPgsqlData
from insights.tests import context_wrap

LS_PGSQL_DATA = """
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
""".strip()

SPEC_PATH = 'insights_commands/ls_-lan_.var.lib.pgsql.data'


def test_ls_pgsql_data():
    r = LsPgsqlData(context_wrap(LS_PGSQL_DATA, SPEC_PATH))
    path = '/var/lib/pgsql/data'
    assert len(r.listing_of(path)) == 21
    assert len(r.files_of(path)) == 6
    assert r.files_of(path) == ['pg_hba.conf', 'pg_ident.conf', 'PG_VERSION',
            'postgresql.conf', 'postmaster.opts', 'postmaster.pid']
    assert r.dirs_of(path) == ['.', '..', 'base', 'global', 'pg_clog', 'pg_log',
            'pg_multixact', 'pg_notify', 'pg_serial', 'pg_snapshots',
            'pg_stat_tmp', 'pg_subtrans', 'pg_tblspc', 'pg_twophase', 'pg_xlog']


def test_ls_pgsql_data_doc_examples():
    env = {
        'ls_pgsql_data': LsPgsqlData(context_wrap(LS_PGSQL_DATA, path=SPEC_PATH))
    }
    failed, total = doctest.testmod(ls_pgsql_data, globs=env)
    assert failed == 0
