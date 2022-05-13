from insights.parsers.postgresql_log import PostgreSQLLog
from insights.tests import context_wrap

POSTGRESQL_LOG = """
LOG:  unexpected EOF on client connection
LOG:  received fast shutdown request
LOG:  aborting any active transactions
FATAL:  terminating connection due to administrator command
FATAL:  terminating connection due to administrator command
LOG:  autovacuum launcher shutting down
FATAL:  terminating connection due to administrator command
LOG:  shutting down
LOG:  database system is shut down
LOG:  database system was shut down at 2015-11-10 18:36:41 EST
LOG:  database system is ready to accept connections
LOG:  autovacuum launcher started
"""


def test_postgresql_log():
    log = PostgreSQLLog(context_wrap(POSTGRESQL_LOG))
    assert "FATAL:  terminating connection" in log
