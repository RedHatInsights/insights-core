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
