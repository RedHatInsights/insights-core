"""
LsVarRun - command ``ls -lnL /var/run``
=======================================

The ``ls -lnL /var/run`` command provides information for the listing of the
``/var/run`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    total 20
    drwx--x---.  2   0 984   40 May 15 09:29 openvpn
    drwxr-xr-x.  2   0   0   40 May 15 09:30 plymouth
    drwxr-xr-x.  2   0   0   40 May 15 09:29 ppp
    drwxr-xr-x.  2  75  75   40 May 15 09:29 radvd
    -rw-r--r--.  1   0   0    5 May 15 09:30 rhnsd.pid
    drwxr-xr-x.  2   0   0   60 May 30 09:31 rhsm
    drwx------.  2  32  32   40 May 15 09:29 rpcbind
    -r--r--r--.  1   0   0    0 May 17 16:26 rpcbind.lock

Examples:

    >>> "rhnsd.pid" in ls_var_run
    False
    >>> "/var/run" in ls_var_run
    True
    >>> ls_var_run.dir_entry('/var/run', 'openvpn')['type']
    'd'
"""


from insights.specs import Specs
from insights.util import deprecated

from .. import FileListing
from .. import parser


@parser(Specs.ls_var_run)
class LsVarRun(FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSlanL` instead.

    Parses output of ``ls -lnL /var/run`` command.
    """
    def __init__(self, *args, **kwargs):
        deprecated(LsVarRun, "Please use the :class:`insights.parsers.ls.LSlanL` instead.", "3.5.0")
        super(LsVarRun, self).__init__(*args, **kwargs)
