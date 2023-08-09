"""
LsVarWwwPerms - command ``/bin/ls -la /dev/null /var/www``
==========================================================
"""

from insights.core import CommandParser, FileListing
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated
from insights.util.file_permissions import FilePermissions


@parser(Specs.ls_var_www)
class LsVarWwwPerms(CommandParser, FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSla` instead.

    Class for parsing ``/bin/ls -la /dev/null /var/www`` command.

    Attributes:
        file_permissions (list): list of `FilePermissions` objects for every file from the output

    Sample output of this command is::

        crw-rw-rw-. 1 root root 1, 3 Dec 18 09:18 /dev/null

        /var/www:
        total 16
        drwxr-xr-x.  4 root root  33 Dec 15 08:12 .
        drwxr-xr-x. 20 root root 278 Dec 15 08:12 ..
        drwxr-xr-x.  2 root root   6 Oct  3 09:37 cgi-bin
        drwxr-xr-x.  2 root root   6 Oct  3 09:37 html

    Examples:

        >>> type(ls_var_www_perms)
        <class 'insights.parsers.ls_var_www_perms.LsVarWwwPerms'>
        >>> ls_var_www_perms.file_permissions[2]
        FilePermissions(cgi-bin)
        >>> ls_var_www_perms.file_permissions[2].line
        'drwxr-xr-x.  2 root root   6 Oct  3 09:37 cgi-bin'
    """
    def __init__(self, *args, **kwargs):
        deprecated(LsVarWwwPerms, "Please use the :class:`insights.parsers.ls.LSla` instead.", "3.5.0")
        super(LsVarWwwPerms, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        super(LsVarWwwPerms, self).parse_content(content)

        self.file_permissions = []
        if "/var/www" in self:
            for filename, info in sorted(self.listing_of("/var/www").items()):
                self.file_permissions.append(FilePermissions(info["raw_entry"]))
