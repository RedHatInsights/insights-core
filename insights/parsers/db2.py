"""
db2 - db2 databases
===================
Parsers included in this module are:

Db2DatabasesConfiguration - Command ``/usr/sbin/runuser -l  <user name>  -c 'db2 get database configuration for %s'``
=====================================================================================================================

Db2DatabasesManager - Command ``/usr/sbin/runuser -l  <user name>  -c 'db2 get dbm cfg'``
=========================================================================================
"""

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.db2_databases_configuration)
class Db2DatabasesConfiguration(CommandParser, dict):
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

        result["user"] = self.file_path.split("_")[3]
        self.update(result)


@parser(Specs.db2_database_manager)
class Db2DatabasesManager(CommandParser, dict):
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
