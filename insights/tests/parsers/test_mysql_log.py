from insights.parsers.mysql_log import MysqlLog
from insights.tests import context_wrap

MYSQL_LOG = """
2018-03-13T06:37:37.268209Z 0 [Warning] Changed limits: max_open_files: 1024 (requested 5000)
2018-03-13T06:37:37.268417Z 0 [Warning] Changed limits: table_open_cache: 431 (requested 2000)
2018-03-13T06:37:37.268549Z 0 [Warning] TIMESTAMP with implicit DEFAULT value is deprecated. Please use --explicit_defaults_for_timestamp server option (see documentation fo
r more details).
2018-03-13T06:37:39.651387Z 0 [Warning] InnoDB: New log files created, LSN=45790
2018-03-13T06:37:39.719166Z 0 [Warning] InnoDB: Creating foreign key constraint system tables.
2018-03-13T06:37:39.784406Z 0 [Warning] No existing UUID has been found, so we assume that this is the first time that this server has been started. Generating a new UUID: 0
698a7d6-2689-11e8-8944-0800274ac5ef.
2018-03-13T06:37:39.789636Z 0 [Warning] Gtid table is not ready to be used. Table 'mysql.gtid_executed' cannot be opened.
2018-03-13T06:37:40.498084Z 0 [Warning] CA certificate ca.pem is self signed.
2018-03-13T06:37:41.080591Z 1 [Warning] root@localhost is created with an empty password ! Please consider switching off the --initialize-insecure option.
md5_dgst.c(80): OpenSSL internal error, assertion failed: Digest MD5 forbidden in FIPS mode!
06:37:41 UTC - mysqld got signal 6 ;
2018-03-13T07:43:31.450772Z 0 [Note] Event Scheduler: Loaded 0 events
2018-03-13T07:43:31.450988Z 0 [Note] /opt/rh/rh-mysql57/root/usr/libexec/mysqld: ready for connections.
Version: '5.7.16'  socket: '/var/lib/mysql/mysql.sock'  port: 3306  MySQL Community Server (GPL)
md5_dgst.c(80): OpenSSL internal error, assertion failed: Digest MD5 forbidden in FIPS mode!
07:46:19 UTC - mysqld got signal 6 ;
"""


def test_mysql_log():
    log = MysqlLog(context_wrap(MYSQL_LOG))
    assert len(log.get("[Warning]")) == 9
    assert len(log.get("[Note]")) == 2
    assert 'ready for connections' in log
