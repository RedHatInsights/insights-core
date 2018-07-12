"""
LsUsrSbin - command ``ls -ln /usr/sbin``
========================================

The ``ls -ln /usr/sbin`` command provides information for the listing of the
``/usr/sbin`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    total 41472
    -rwxr-xr-x. 1 0  0   11720 Mar 18  2014 accessdb
    -rwxr-xr-x. 1 0  0    3126 Oct  4  2013 addgnupghome
    -rwxr-xr-x. 1 0  0   20112 Jun  1  2017 addpart
    -rwxr-xr-x. 1 0  0  371912 Jan 27  2014 postconf
    -rwxr-sr-x. 1 0 90  218552 Jan 27  2014 postdrop

Examples:

    >>> add_filter(Specs.ls_usr_sbin, "accessdb")
    >>> "accessdb" in ls_usr_sbin
    False
    >>> "/usr/sbin" in ls_usr_sbin
    True
    >>> ls_usr_sbin.dir_entry('/usr/sbin', 'accessdb')['type']
    '-'

"""


from insights.core.filters import add_filter
from insights.specs import Specs

from .. import CommandParser, parser
from .. import FileListing


add_filter(Specs.ls_usr_sbin, "total")


@parser(Specs.ls_usr_sbin)
class LsUsrSbin(CommandParser, FileListing):
    """Parses output of ``ls -ln /usr/sbin`` command."""
    pass
