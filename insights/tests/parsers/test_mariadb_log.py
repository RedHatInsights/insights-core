from insights.parsers.mariadb_log import MariaDBLog
from insights.tests import context_wrap

from datetime import datetime

MARIADB_LOG = """
161109  9:25:42 [Warning] SSL error: SSL_CTX_set_default_verify_paths failed
161109  9:25:42 [Note] WSREP: Service disconnected.
161109  9:25:43 [Note] WSREP: Some threads may fail to exit.
161109 14:28:24 InnoDB: Initializing buffer pool, size = 128.0M
161109 14:28:24 InnoDB: Completed initialization of buffer pool
"""


def test_mariadb_log():
    log = MariaDBLog(context_wrap(MARIADB_LOG))
    assert len(log.get("[Warning]")) == 1
    assert len(log.get("[Note]")) == 2
    assert 'SSL_CTX_set_default_verify_paths' in log
    assert len(list(log.get_after(datetime(2016, 11, 9, 14, 0, 0)))) == 2
