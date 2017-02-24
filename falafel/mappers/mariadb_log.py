"""
mariadb.log - File /var/log/mariadb/mariadb.log
===============================================

Module for parsing the log file for MariaDB

Typical content of ``mariadb.log`` file is::

    161109  9:25:42 [Note] WSREP: Read nil XID from storage engines, skipping position init
    161109  9:25:42 [Note] WSREP: wsrep_load(): loading provider library 'none'
    161109  9:25:42 [Warning] Failed to setup SSL
    161109  9:25:42 [Warning] SSL error: SSL_CTX_set_default_verify_paths failed
    161109  9:25:42 [Note] WSREP: Service disconnected.
    161109  9:25:43 [Note] WSREP: Some threads may fail to exit.
    161109  9:25:43 [Note] WSREP: Read nil XID from storage engines, skipping position init
    161109  9:25:43 [Note] WSREP: wsrep_load(): loading provider library 'none'
    161109  9:25:43 [Warning] Failed to setup SSL
    161109  9:25:43 [Warning] SSL error: SSL_CTX_set_default_verify_paths failed
    161109  9:25:43 [Note] WSREP: Service disconnected.
    161109  9:25:44 [Note] WSREP: Some threads may fail to exit.
    161109 14:28:22 mysqld_safe Starting mysqld daemon with databases from /var/lib/mysql
    161109 14:28:22 mysqld_safe WSREP: Running position recovery with --log_error='/var/lib/mysql/wsrep_recovery.OkURTZ' --pid-file='/var/lib/mysql/overcloud-controller-0.localdomain-recover.pid'
    161109 14:28:22 [Warning] option 'open_files_limit': unsigned value 18446744073709551615 adjusted to 4294967295
"""

from .. import LogFileOutput, mapper


@mapper('mariadb.log')
class MariaDBLog(LogFileOutput):
    """Class for parsing ``/var/log/mariadb/mariadb.log`` file.

    Note:
        Please refer to its super-class ``LogFileOutput``
    """
    pass
