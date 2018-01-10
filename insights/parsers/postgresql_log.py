"""
PostgreSQLLog - file ``/var/lib/pgsql/data/pg_log/postgresql-*.log``
====================================================================
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.postgresql_log)
class PostgreSQLLog(LogFileOutput):
    """
    Read the PostgreSQL log files.  Uses the ``LogFileOutput`` class parser
    functionality.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`


    The PostgreSQL log files contain no dates or times by default::

        LOG:  shutting down
        LOG:  database system is shut down
        LOG:  database system was shut down at 2015-03-31 05:05:12 UTC
        LOG:  database system is ready to accept connections
        LOG:  autovacuum launcher started

    Because this parser reads multiple log files, the contents of the shared
    parser information are a list of parsed files.  This means at present
    that you will need to iterate through the log file objects in that list
    in order to find what you want.

    Examples:
        >>> for log in shared(PacemakerLog):
        ...     print "File:", logs.file_path
        ...     print "Startups:", len(logs.get('ready to accept connections'))
        ...
        File: /var/log/pgsql/data/pg_log/postgresql-Fri
        Startups: 1
        File: /var/log/pgsql/data/pg_log/postgresql-Mon
        Startups: 0
        File: /var/log/pgsql/data/pg_log/postgresql-Sat
        Startups: 0
        File: /var/log/pgsql/data/pg_log/postgresql-Sun
        Startups: 2
        File: /var/log/pgsql/data/pg_log/postgresql-Thu
        Startups: 0
        File: /var/log/pgsql/data/pg_log/postgresql-Tue
        Startups: 0
        File: /var/log/pgsql/data/pg_log/postgresql-Wed
        Startups: 0
    """
    pass
