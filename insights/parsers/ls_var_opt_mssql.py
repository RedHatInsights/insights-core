"""
LsVarOptMSSql - command ``ls -laR /var/opt/mssql``
==================================================

The ``ls -laR /var/opt/mssql`` command provides information for the listing of
the ``/var/opt/mssql`` directory. See ``FileListing`` class for addtional information.


Sample ``ls -laR /var/opt/mssql`` output::

    /var/opt/mssql:
    total 0
    drwxr-xr-x. 2 mssql mssql  6 Apr 16 09:42 .
    drwxr-xr-x. 3 root  root  19 Apr 16 09:42 ..

Examples:

    >>> ls_var_opt_mssql.listing_of("/var/opt/mssql").get(".").get("owner")
    'mssql'
    >>> ls_var_opt_mssql.listing_of("/var/opt/mssql").get(".").get("group")
    'mssql'
"""
from insights.specs import Specs
from .. import parser, CommandParser
from .. import FileListing


@parser(Specs.ls_var_opt_mssql)
class LsVarOptMSSql(CommandParser, FileListing):
    """Parses output of ``ls -laR /var/opt/mssql`` command."""
