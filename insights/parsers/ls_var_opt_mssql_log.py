"""
LsVarOptMssqlLog - command ``ls -la /var/opt/mssql/log``
========================================================

This parser reads the ``/var/opt/mssql/log`` directory listings and uses the
FileListing parser class to provide a common access to them.

"""

from insights import FileListing, parser, CommandParser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.ls_var_opt_mssql_log)
class LsVarOptMssqlLog(CommandParser, FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSla` instead.

    A parser for accessing "ls -la /var/opt/mssql/log".

    Examples:
        >>> '/var/opt/mssql/log' in ls_mssql_log
        True
        >>> ls_mssql_log.dir_contains('/var/opt/mssql/log', 'messages')
        False
    """
    def __init__(self, *args, **kwargs):
        deprecated(LsVarOptMssqlLog, "Please use the :class:`insights.parsers.ls.LSla` instead.", "3.5.0")
        super(LsVarOptMssqlLog, self).__init__(*args, **kwargs)
