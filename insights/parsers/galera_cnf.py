"""
GaleraCnf - file ``/etc/my.cnf.d/galera.cnf``
=============================================

This module provides parsing for the galera configuration of
MySQL. The input is the contents of the file
`/etc/my.cnf.d/galera.cnf`.  Typical contents of the `galera.cnf`
file looks like this::

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

See the ``IniConfigFile`` base class for examples.

"""
from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.galera_cnf)
class GaleraCnf(IniConfigFile):
    """Parses the content of `/etc/my.cnf.d/galera.cnf`."""

    def parse_content(self, content, allow_no_value=True):
        """Calls parent method to parse contents but overrides parameters.

        The galera config file may have keys with no value. This class
        implements ``parse_content`` in order to pass the flag
        ``allow_no_value`` to the parent parser in order to allow parsing
        of the no-value keys.
        """
        super(GaleraCnf, self).parse_content(content, allow_no_value=allow_no_value)
