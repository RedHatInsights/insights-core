#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.parsers.odbc import ODBCIni, ODBCinstIni
from insights.tests import context_wrap

ODBC_INI = """
[myodbc5w]
Driver       = /usr/lib64/libmyodbc5w.so
Description  = DSN to MySQL server
SERVER       = localhost
NO_SSPS     = 1

[mysqlDSN]
Driver      = /usr/lib64/libmyodbc5.so
SERVER      = localhost

[myodbc]
Driver=MySQL
SERVER=localhost
#NO_SSPS=1
""".strip()


def test_odbc_ini():
    res = ODBCIni(context_wrap(ODBC_INI))
    assert res.data.get("mysqlDSN", "Driver") == "/usr/lib64/libmyodbc5.so"
    assert res.data.get("mysqlDSN", "SERVER") == "localhost"
    assert not res.has_option("mysqlDSN", 'NO_SSPS')

    assert len(res.items("myodbc5w")) == 4
    assert res.getint("myodbc5w", 'NO_SSPS') == 1
    assert res.getint("myodbc5w", 'No_Ssps') == 1
    assert res.getint("myodbc5w", 'NO_SSPS'.lower()) == 1

    assert 'myodbc' in res
    assert res.data.get("myodbc", "Driver") == "MySQL"
    assert not res.has_option("myodbc", 'NO_SSPS')


ODBCINST_INI = """
# Example driver definitions

# Driver from the postgresql-odbc package
# Setup from the unixODBC package
[PostgreSQL]
Description	= ODBC for PostgreSQL
Driver		= /usr/lib/psqlodbcw.so
Setup		= /usr/lib/libodbcpsqlS.so
Driver64	= /usr/lib64/psqlodbcw.so
Setup64		= /usr/lib64/libodbcpsqlS.so
FileUsage	= 1


# Driver from the mysql-connector-odbc package
# Setup from the unixODBC package
[MySQL]
Description	= ODBC for MySQL
Driver		= /usr/lib/libmyodbc5.so
Setup		= /usr/lib/libodbcmyS.so
Driver64	= /usr/lib64/libmyodbc5.so
Setup64		= /usr/lib64/libodbcmyS.so
FileUsage	= 1
""".strip()


def test_odbcinst_ini():
    res = ODBCinstIni(context_wrap(ODBCINST_INI))
    assert 'PostgreSQL' in res
    assert 'MySQL' in res
    assert 'XXSQL' not in res
    assert res.data.get("MySQL", "Driver64") == "/usr/lib64/libmyodbc5.so"
