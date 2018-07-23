"""
LsVarLibMongodb - command ``ls -la /var/lib/mongodb``
=====================================================

The ``ls -la /var/lib/mongodb`` command provides information for the listing of the ``/var/lib/mongodb`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    total 6322200
    drwxr-xr-x.  3 mongodb mongodb        256 Jun  7 10:07 .
    drwxr-xr-x. 71 root    root          4096 Jun 22 10:35 ..
    drwxr-xr-x.  2 mongodb mongodb         65 Jul 10 09:33 journal
    -rw-------.  1 mongodb mongodb   67108864 Jul 10 09:32 local.0
    -rw-------.  1 mongodb mongodb   16777216 Jul 10 09:32 local.ns

Examples:

    >>> "journal" in ls_var_lib_mongodb
    False
    >>> "/var/lib/mongodb" in ls_var_lib_mongodb
    True
    >>> ls_var_lib_mongodb.dir_entry('/var/lib/mongodb', 'journal')['type']
    'd'
"""


from insights.specs import Specs

from .. import CommandParser, parser
from .. import FileListing


@parser(Specs.ls_var_lib_mongodb)
class LsVarLibMongodb(CommandParser, FileListing):
    """Parses output of ``ls -la /var/lib/mongodb`` command."""
    pass
