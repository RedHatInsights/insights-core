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
LsVarOptMssqlLog - command ``ls -la /var/opt/mssql/log``
========================================================

This parser reads the ``/var/opt/mssql/log`` directory listings and uses the
FileListing parser class to provide a common access to them.

"""

from insights import FileListing, parser, CommandParser
from insights.specs import Specs


@parser(Specs.ls_var_opt_mssql_log)
class LsVarOptMssqlLog(CommandParser, FileListing):
    """
    A parser for accessing "ls -la /var/opt/mssql/log".

    Examples:
        >>> '/var/opt/mssql/log' in ls_mssql_log
        True
        >>> ls_mssql_log.dir_contains('/var/opt/mssql/log', 'messages')
        False
    """
    pass
