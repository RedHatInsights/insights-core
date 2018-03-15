"""
MysqlLog - File ``/var/log/mysqld.log``
=======================================

Module for parsing the log file for Mysql, including ``/var/log/mysqld.log`` and
``/var/opt/rh/rh-mysql*/log/mysql/mysqld.log``.

.. note::
    By default, logrotate of mysql.log is set to daily.
    In some lines of log, there are no timestamp.

Typical content of ``mysql.log`` file is::

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

Examples:

    >>> my = MysqlLog((context_wrap(MYSQLLOG)))
    >>> my.get('mysqld')[0]['raw_message']
    '06:37:41 UTC - mysqld got signal 6 ;'
    >>> 'ready for connections' in my
    True
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.mysql_log)
class MysqlLog(LogFileOutput):
    """Class for parsing ``/var/log/mysqld.log`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass
