"""
GaleraCnf - file ``/etc/my.cnf.d/galera.cnf``
=============================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.galera_cnf)
class GaleraCnf(IniConfigFile):
    """
    This module provides parsing for the galera configuration of
    MySQL. The input is the contents of the file
    `/etc/my.cnf.d/galera.cnf`.

    Typical contents of the `galera.cnf` file looks like this::

        [client]
        port = 3306
        socket = /var/lib/mysql/mysql.sock

        [isamchk]
        key_buffer_size = 16M

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

    Examples:
        >>> type(galera_conf)
        <class 'insights.parsers.galera_cnf.GaleraCnf'>
        >>> 'mysqld' in galera_conf
        True
        >>> 'client' in galera_conf
        True
        >>> galera_conf.has_option('isamchk', 'key_buffer_size')
        True
        >>> galera_conf.has_option('mysqld', 'foo')
        False
        >>> galera_conf.get('client', 'port')
        '3306'
        >>> expected = {'port': '3306', 'socket': '/var/lib/mysql/mysql.sock'}
        >>> galera_conf.items('client') == expected
        True
    """
    def parse_content(self, content, allow_no_value=True):
        super(GaleraCnf, self).parse_content(content, allow_no_value)
