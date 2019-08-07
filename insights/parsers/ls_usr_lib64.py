"""
LsUsrLib64 - command ``ls -lan /usr/lib64``
===========================================

The ``ls -lan /usr/lib64`` command provides information for the listing of the
``/usr/lib64`` directory.

See :class:`insights.core.FileListing` class for additional information.

Sample directory list::

    total 447460
    dr-xr-xr-x. 150 0 0    77824 Jul 30 16:39 .
    drwxr-xr-x.  13 0 0     4096 Apr 30  2017 ..
    drwxr-xr-x.   3 0 0       20 Nov  3  2016 krb5
    -rwxr-xr-x.   1 0 0   155464 Oct 28  2016 ld-2.17.so
    drwxr-xr-x.   3 0 0       20 Jun 10  2016 ldb
    lrwxrwxrwx.   1 0 0       10 Apr 30  2017 ld-linux-x86-64.so.2 -> ld-2.17.so
    lrwxrwxrwx.   1 0 0       21 Apr 30  2017 libabrt_dbus.so.0 -> libabrt_dbus.so.0.0.1

Examples:

    >>> "krb5" in ls_usr_lib64
    False
    >>> "/usr/lib64" in ls_usr_lib64
    True
    >>> "krb5" in ls_usr_lib64.dirs_of('/usr/lib64')
    True
    >>> ls_usr_lib64.dir_entry('/usr/lib64', 'ld-linux-x86-64.so.2')['type']
    'l'
"""


from insights.specs import Specs
from insights.core.filters import add_filter

from insights import parser, CommandParser, FileListing


add_filter(Specs.ls_usr_lib64, "total")


@parser(Specs.ls_usr_lib64)
class LsUsrLib64(CommandParser, FileListing):
    """Parses output of ``ls -lan /usr/lib64`` command."""
    pass
