"""
LsVarLog - command ``ls -laR /var/log``
=======================================

This parser reads the ``/var/log`` directory listings and uses the FileListing
parser class to provide a common access to them.

Examples:

    >>> varlog = shared[LsVarLog]
    >>> '/var/log' in varlog
    True
    >>> varlog.dir_contains('/var/log', 'messages')
    True
    >>> messages = varlog.dir_entry('/var/log', 'messages')
    >>> messages['type']
    '-'
    >>> messages['perms']
    'rw-------'
"""

from .. import FileListing, parser, CommandParser

from insights.util.file_permissions import FilePermissions
from insights.specs import Specs


@parser(Specs.ls_var_log)
class LsVarLog(CommandParser, FileListing):
    """
    A parser for accessing "ls -laR /var/log".
    """

    def get_filepermissions(self, dir_name_where_to_search, dir_or_file_name_to_get):
        """
        Returns a FilePermissions object, if found, for the specified dir or
        file name in the specified directory. The directory must be specified
        by the full path without trailing slash. The dir or file name to get
        must be specified by the name only (without path).

        This is provided for several parsers which rely on this functionality,
        and may be deprecated and removed in the future.

        Args:
            dir_name_where_to_search (string): Full path without trailing
                slash where to search.
            dir_or_file_name_to_getl (string): Name of the dir or file to get
                FilePermissions for.

        Returns:
            FilePermissions: If found or None if not found.
        """
        if dir_name_where_to_search in self:
            d = self.listings[dir_name_where_to_search]['entries']
            if dir_or_file_name_to_get in d:
                return FilePermissions(d[dir_or_file_name_to_get]['raw_entry'])
