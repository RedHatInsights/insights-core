"""
db2 - db2 database information
==============================
Parsers included in this module are:

Db2ls - command ``db2ls -a -c``
-------------------------------

Db2DatabaseConfiguration - Command ``/usr/sbin/runuser -l  <user name>  -c 'db2 get database configuration for %s'``
--------------------------------------------------------------------------------------------------------------------

Db2DatabaseManager - Command ``/usr/sbin/runuser -l  <user name>  -c 'db2 get dbm cfg'``
----------------------------------------------------------------------------------------
"""

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.db2ls_a_c)
class Db2ls(CommandParser, list):
    """
    Parse the output of `db2ls -a -c` into a list of dictionaries.

    Typical output of this command::

        #PATH:VRMF:FIXPACK:SPECIAL:INSTALLTIME:INSTALLERUID
        /opt/ibm/db2/V11.5:11.5.6.0:0 ::Fri Jan 14 20:20:07 2022 CST :0
        /opt/ibm/db2/V11.5_01:11.5.7.0:0 ::Fri Feb 11 10:34:51 2022 CST :0

    Examples:
        >>> type(db2ls)
        <class 'insights.parsers.db2.Db2ls'>
        >>> len(db2ls)
        2
        >>> db2ls[0]['PATH']
        '/opt/ibm/db2/V11.5'
        >>> db2ls[1]['PATH']
        '/opt/ibm/db2/V11.5_01'
        >>> db2ls[1]['VRMF']
        '11.5.7.0'
        >>> db2ls[1]['INSTALLERUID']
        '0'
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty.")
        keys = []
        for line in content:
            if not keys and line.startswith('#PATH'):
                keys = [i.strip('#') for i in line.split(':')]
                continue
            line_splits = [i.strip() for i in line.split(':', 4)]
            line_splits.extend([i.strip(': ') for i in line_splits.pop(-1).rsplit(':', 1)])
            self.append(dict(zip(keys, line_splits)))
        if len(self) == 0:
            raise SkipComponent('Nothing to parse.')


@parser(Specs.db2_database_configuration)
class Db2DatabaseConfiguration(CommandParser, dict):
    """
    Parse the output of the ``/usr/sbin/runuser -l  <user name>  -c 'db2 get database configuration for %s'`` command.

    Attributes:
        default (dict): the database configuration details

    Sample Input::

               Database Configuration for Database TESTD1

        Database configuration release level                    = 0x1500
        Database release level                                  = 0x1500

        Update to database level pending                        = NO (0x0)
        Database territory                                      = US
        Database code page                                      = 1208

    Examples:
        >>> db2databaseconfiguration["Database configuration release level"]
        '0x1500'
        >>> db2databaseconfiguration["user"]
        'dbp'
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("The result is empty")

        result = {}

        for line in content:
            if "=" in line:
                key, value = line.split("=")
                result[key.strip()] = value.strip()

        if not result:
            raise SkipComponent("The format is incorrect")

        result["user"] = self.file_path.split("_")[3].strip()
        result["db_name"] = self.file_path.split("_")[-1].strip()
        self.update(result)


@parser(Specs.db2_database_manager)
class Db2DatabaseManager(CommandParser, dict):
    """
    Parse the output of the ``/usr/sbin/runuser -l  <user name>  -c 'db2 get dbm cfg'`` command.

    Attributes:
        default (dict): the database management details

    Sample Input::


              Database Manager Configuration

        Node type = Enterprise Server Edition with local and remote clients

        Database manager configuration release level            = 0x1500

        CPU speed (millisec/instruction)             (CPUSPEED) = 3.306409e-07
        Communications bandwidth (MB/sec)      (COMM_BANDWIDTH) = 1.000000e+02

        Max number of concurrently active databases     (NUMDB) = 32
        Federated Database System Support           (FEDERATED) = NO

    Examples:
        >>> db2databasemanager["Max number of concurrently active databases     (NUMDB)"]
        '32'
        >>> db2databasemanager["user"]
        'dbp'
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("The result is empty")

        result = {}

        for line in content:
            if "=" in line:
                key, value = line.split("=")
                result[key.strip()] = value.strip()

        if not result:
            raise SkipComponent("The format is incorrect")

        result["user"] = self.file_path.split("_")[3]

        self.update(result)
