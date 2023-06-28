"""
LsVarCachePulp - command ``ls -lan /var/cache/pulp``
====================================================

The ``ls -lan /var/cache/pulp`` command provides information for the listing of the ``/var/cache/pulp`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    total 0
    drwxrwxr-x.  5 48 1000 216 Jan 21 12:56 .
    drwxr-xr-x. 10  0    0 121 Jan 20 13:57 ..
    lrwxrwxrwx.  1  0    0  19 Jan 21 12:56 cache -> /var/lib/pulp/cache
    drwxr-xr-x.  2 48   48   6 Jan 21 13:03 reserved_resource_worker-0@dhcp130-202.gsslab.pnq2.redhat.com
    drwxr-xr-x.  2 48   48   6 Jan 21 02:03 reserved_resource_worker-1@dhcp130-202.gsslab.pnq2.redhat.com
    drwxr-xr-x.  2 48   48   6 Jan 20 14:03 resource_manager@dhcp130-202.gsslab.pnq2.redhat.com

Examples:

    >>> "journal" in ls_var_cache_pulp
    False
    >>> "/var/cache/pulp" in ls_var_cache_pulp
    True
"""


from insights.specs import Specs
from insights.util import deprecated

from insights import CommandParser, parser, FileListing


@parser(Specs.ls_var_cache_pulp)
class LsVarCachePulp(CommandParser, FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSlan` instead.

    Parses output of ``ls -lan /var/cache/pulp`` command.
    """
    def __init__(self, *args, **kwargs):
        deprecated(LsVarCachePulp, "Please use the :class:`insights.parsers.ls.LSlan` instead.", "3.5.0")
        super(LsVarCachePulp, self).__init__(*args, **kwargs)
