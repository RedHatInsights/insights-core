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

"""
obdc configuration file - Files
===============================

Shared mappers for parsing and extracting data from ``/etc/odbc.ini`` and
``/etc/odbcinst.ini`` files. Parsers contained in this module are:

ODBCIni - file ``/etc/odbc.ini``
--------------------------------

ODBCinstIni - file ``/etc/odbcinst.ini``
----------------------------------------

"""

from .. import parser, IniConfigFile, add_filter
from insights.specs import Specs

# Since the key values in file odbc.ini is case insensitive,
# and curent filter_list is not support case insensitive,
# will add several duplicate keys here to filter out more useful data.
filter_list = [
        '[',
        'DRIVER', 'Driver', 'driver',
        'SERVER', 'Server', 'server',
        'NO_SSPS', 'No_ssps', 'no_ssps',
]
add_filter(Specs.odbc_ini, filter_list)


@parser(Specs.odbc_ini)
class ODBCIni(IniConfigFile):
    """
    The ``/etc/odbc.ini`` file is in a standard '.ini' format,
    and this parser uses the IniConfigFile base class to read this.

    Sample command output::

        [myodbc5w]
        Driver       = /usr/lib64/libmyodbc5w.so
        Description  = DSN to MySQL server
        SERVER       = localhost
        NO_SSPS     = 1

        [myodbc]
        Driver=MySQL
        SERVER=localhost
        #NO_SSPS=1

    Example:
        >>> config.sections()
        ['myodbc5w', 'myodbc']
        >>> config.has_option('myodbc5w', 'Driver')
        True
        >>> config.get('myodbc5w', 'Driver')
        '/usr/lib64/libmyodbc5w.so'
        >>> config.getint('myodbc5w', 'NO_SSPS')
        1
    """
    pass


@parser(Specs.odbcinst_ini)
class ODBCinstIni(IniConfigFile):
    """
    The ``/etc/odbcinst.ini`` file is in a standard '.ini' format,
    and this parser uses the IniConfigFile base class to read this.

    Sample command output::

        # Driver from the postgresql-odbc package
        # Setup from the unixODBC package
        [PostgreSQL]
        Description     = ODBC for PostgreSQL
        Driver          = /usr/lib/psqlodbcw.so
        Setup           = /usr/lib/libodbcpsqlS.so
        Driver64        = /usr/lib64/psqlodbcw.so
        Setup64         = /usr/lib64/libodbcpsqlS.so
        FileUsage       = 1

    Example:
        >>> config.sections()
        ['PostgreSQL']
        >>> config.has_option('PostgreSQL', 'Driver')
        True
        >>> config.get('PostgreSQL', 'Driver')
        '/usr/lib/psqlodbcw.so'
        >>> config.getint('PostgreSQL', 'FileUsage')
        1
    """
    pass
