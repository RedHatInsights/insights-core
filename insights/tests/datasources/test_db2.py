import pytest

from mock.mock import Mock
from insights.core.exceptions import SkipComponent
from insights.specs.datasources.db2 import LocalSpecs, db2_users, db2_databases_info
from insights.parsers.ps import PsAuxcww
from insights.combiners.ps import Ps
from insights.core import dr
from insights.tests import context_wrap


PS_AUXCWW = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
root      1821  0.0  0.0      0     0 ?        S    May31   0:29 kondemand/0
root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient
dbp1      1161530  0.1  1.3 2306928 314076 ?      Sl   Apr19   8:42 db2sysc
dbp2      1161531  0.1  1.3 2306928 314076 ?      Sl   Apr19   8:42 db2sysc
root      1161532  0.1  1.3 2306928 314076 ?      Sl   Apr19   8:42 db2sysc
""".strip()

PS_AUXCWW_NG = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
root      1821  0.0  0.0      0     0 ?        S    May31   0:29 kondemand/0
root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient
""".strip()

DATABASE_LIST_DBP1 = """

 System Database Directory

 Number of entries in the directory = 2

Database 1 entry:

 Database alias                       = TESTD1
 Database name                        = TESTD1
 Local database directory             = /home/dbp
 Database release level               = 15.00
 Comment                              =
 Directory entry type                 = Indirect
 Catalog database partition number    = 0
 Alternate server hostname            =
 Alternate server port number         =

Database 2 entry:

 Database alias                       = TESTD2
 Database name                        = TESTD2
 Local database directory             = /home/dbp
 Database release level               = 15.00
 Comment                              =
 Directory entry type                 = Indirect
 Catalog database partition number    = 0
 Alternate server hostname            =
 Alternate server port number         =

""".strip()


DATABASE_LIST_DBP2 = """

 System Database Directory

 Number of entries in the directory = 1

Database 1 entry:

 Database alias                       = TESTD1
 Database name                        = TESTD1
 Local database directory             = /home/dbp2
 Database release level               = 15.00
 Comment                              =
 Directory entry type                 = Indirect
 Catalog database partition number    = 0
 Alternate server hostname            =
 Alternate server port number         =

""".strip()

DATABASE_LIST_NO_DBP1 = """

 System Database Directory

 Number of entries in the directory = 1

Database 1 entry:

 Database alias                       = TESTD1
 Local database directory             = /home/dbp
 Database release level               = 15.00
 Comment                              =
 Directory entry type                 = Indirect
 Catalog database partition number    = 0
 Alternate server hostname            =
 Alternate server port number         =

""".strip()


DATABASE_LIST_NO_DBP2 = """

 System Database Directory

 Number of entries in the directory = 1

Database 1 entry:

 Database alias                       = TESTD1
 Local database directory             = /home/dbp2
 Database release level               = 15.00
 Comment                              =
 Directory entry type                 = Indirect
 Catalog database partition number    = 0
 Alternate server hostname            =
 Alternate server port number         =

""".strip()


def test_db2_users():
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW))
    ps = Ps(None, None, None, None, ps_auxcww, None)

    broker = dr.Broker()
    broker[Ps] = ps
    result = db2_users(broker)
    assert result == ["dbp1", "dbp2"]


def test_no_db2_users():
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_NG))
    ps = Ps(None, None, None, None, ps_auxcww, None)

    broker = dr.Broker()
    broker[Ps] = ps
    with pytest.raises(SkipComponent):
        db2_users(broker)


def test_db2_databases_info():
    database_list_dbp1 = Mock()
    database_list_dbp1.content = DATABASE_LIST_DBP1.splitlines()
    database_list_dbp1.cmd = "/usr/sbin/runuser -l  dbp1  -c 'db2 list database directory'"

    database_list_dbp2 = Mock()
    database_list_dbp2.content = DATABASE_LIST_DBP2.splitlines()
    database_list_dbp2.cmd = "/usr/sbin/runuser -l  dbp2  -c 'db2 list database directory'"

    broker = {LocalSpecs.db2_databases: [database_list_dbp1, database_list_dbp2]}
    result = db2_databases_info(broker)
    assert result == [('dbp1', 'TESTD1'), ('dbp1', 'TESTD2'), ('dbp2', 'TESTD1')]


def test_no_db2_databases_info():
    database_list_dbp1 = Mock()
    database_list_dbp1.content = DATABASE_LIST_NO_DBP1.splitlines()
    database_list_dbp1.cmd = "/usr/sbin/runuser -l  dbp1  -c 'db2 list database directory'"

    database_list_dbp2 = Mock()
    database_list_dbp2.content = DATABASE_LIST_NO_DBP2.splitlines()
    database_list_dbp2.cmd = "/usr/sbin/runuser -l  dbp2  -c 'db2 list database directory'"

    broker = {LocalSpecs.db2_databases: [database_list_dbp1, database_list_dbp2]}
    with pytest.raises(SkipComponent):
        db2_databases_info(broker)
