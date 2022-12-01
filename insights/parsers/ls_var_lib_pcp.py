"""
LsVarLibPcp - command ``ls -la /var/lib/pcp/pmdas/openmetrics/config.d``
========================================================================

The ``ls -la /var/lib/pcp/pmdas/openmetrics/config.d`` command provides information for the listing of the ``/var/lib/pcp/pmdas/openmetrics/config.d`` directory.

The parsers class in this module uses base parser class
``CommandParser`` & ``FileListing`` to list files & directories.

Sample output of this command is::

    total 16
    drwxr-xr-x.  4 root root  33 Dec 15 08:12 .
    drwxr-xr-x. 20 root root 278 Dec 15 08:12 ..
    -rwxr-xr-x.  2 root root   6 Oct  3 09:37 grafana.url

Examples:

    >>> "grafana.url" in ls_var_lib_pcp
    False
    >>> "/var/lib/pcp/pmdas/openmetrics/config.d" in ls_var_lib_pcp
    False
"""


from insights.specs import Specs
from insights import CommandParser, parser
from insights.core import FileListing


@parser(Specs.ls_var_lib_pcp)
class LsVarLibPcpOpenmetricsConfigd(CommandParser, FileListing):
    """Parses output of ``ls -la /var/lib/pcp/pmdas/openmetrics/config.d`` command."""
    pass
