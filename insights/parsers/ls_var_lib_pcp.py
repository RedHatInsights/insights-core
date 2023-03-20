"""
LsVarLibPcp - command ``ls -la /var/lib/pcp``
=============================================

The ``ls -la /var/lib/pcp`` command provides information for the listing of the ``/var/lib/pcp`` directory.

The parsers class in this module uses base parser class
``CommandParser`` & ``FileListing`` to list files & directories.

Sample output of this command is::

    total 16
    drwxr-xr-x.  4 root root  33 Dec 15 08:12 .
    drwxr-xr-x. 20 root root 278 Dec 15 08:12 ..
    drwxr-xr-x.  2 root root   6 Oct  3 09:37 pmcd
    drwxr-xr-x.  2 root root   6 Oct  3 09:37 pmie
    drwxrwxr-x.  4 root root 128 Aug 22 17:55 pmdas

Examples:

    >>> "pmdas" in ls_var_lib_pcp
    False
    >>> "/var/lib/pcp" in ls_var_lib_pcp
    True
    >>> ls_var_lib_pcp.dir_entry('/var/lib/pcp', 'pmdas')['type']
    'd'
"""


from insights.specs import Specs
from insights import CommandParser, parser
from insights.core import FileListing


@parser(Specs.ls_var_lib_pcp)
class LsVarLibPcp(CommandParser, FileListing):
    """Parses output of ``ls -la /var/lib/pcp`` command."""
    pass
