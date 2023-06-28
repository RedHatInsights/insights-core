"""
LsDVarOptMSSql - command ``ls -ld /var/opt/mssql``
==================================================
"""
from insights.specs import Specs
from .. import CommandParser, parser, FileListing
from insights.util import deprecated


@parser(Specs.ls_var_opt_mssql)
class LsDVarOptMSSql(CommandParser, FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSla` instead (NOT ``LSld``).

    Parses output of ``ls -ld /var/opt/mssql`` command.

    The ``ls -ld /var/opt/mssql`` command provides information for the listing
    of the ``/var/opt/mssql`` directory. See ``FileListing`` class for addtional
    information.


    Sample ``ls -ld /var/opt/mssql`` output::

        drwxrwx---. 5 root root 58 Apr 16 07:20 /var/opt/mssql

    Examples:

        >>> content.listing_of('/var/opt/mssql').get('/var/opt/mssql').get('owner')
        'root'
        >>> content.listing_of('/var/opt/mssql').get('/var/opt/mssql').get('group')
        'root'
    """
    def __init__(self, *args, **kwargs):
        deprecated(LsDVarOptMSSql, "Please use the :class:`insights.parsers.ls.LSla` instead.", "3.5.0")
        super(LsDVarOptMSSql, self).__init__(*args, **kwargs)
