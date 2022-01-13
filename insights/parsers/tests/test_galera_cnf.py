import doctest

from insights.parsers import galera_cnf
from insights.tests import context_wrap

GALERA_CNF = """
[client]
port = 3306
socket = /var/lib/mysql/mysql.sock

[isamchk]
key_buffer_size = 16M # inline comment test

[mysqld]
basedir = /usr
binlog_format = ROW
datadir = /var/lib/mysql
default-storage-engine = innodb
expire_logs_days = 10
innodb_autoinc_lock_mode = 2
innodb_locks_unsafe_for_binlog = 1
key_buffer_size = 16M
log-error = /var/log/mariadb/mariadb.log
max_allowed_packet = 16M
max_binlog_size = 100M
max_connections = 8192
wsrep_max_ws_rows = 131072
wsrep_max_ws_size = 1073741824

[mysqld_safe]
log-error = /var/log/mariadb/mariadb.log
nice = 0
socket = /var/lib/mysql/mysql.sock

[mysqldump]
max_allowed_packet = 16M
quick
quote-names
"""


def test_doc_examples():
    env = {
        'galera_conf': galera_cnf.GaleraCnf(context_wrap(GALERA_CNF))
    }
    failed, total = doctest.testmod(galera_cnf, globs=env)
    assert failed == 0


def test_galera_cnf():
    cnf = galera_cnf.GaleraCnf(context_wrap(GALERA_CNF))
    assert cnf is not None
    assert cnf.get('client', 'port') == '3306'
    assert cnf.get('isamchk', 'key_buffer_size') == '16M'
    assert cnf.get('mysqld', 'max_connections') == '8192'
    assert 'not_there' not in cnf
    assert cnf.get('mysqldump', 'quick') is None
