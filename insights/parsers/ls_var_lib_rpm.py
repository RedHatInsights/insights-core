"""
LsVarLibRpm - command ``ls -lan /var/lib/rpm``
==============================================
"""


from insights.core import CommandParser, FileListing
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ls_var_lib_rpm)
class LsVarLibRpm(CommandParser, FileListing):
    """
    Parses output of ``ls -lan /var/lib/rpm`` command.

    Sample output::

        total 172400
        drwxr-xr-x.  2 0 0      4096 Oct 19  2022 .
        drwxr-xr-x. 31 0 0      4096 Nov 26  2021 ..
        -rw-r--r--.  1 0 0   4034560 Apr 17 16:06 Basenames
        -rw-r--r--.  1 0 0      8192 Apr 17 16:06 Conflictname
        -rw-r--r--.  1 0 0     16384 Apr 17 10:43 Obsoletename
        -rw-r--r--.  1 0 0 165253120 Apr 17 16:06 Packages
        -rw-r--r--.  1 0 0   2461696 Apr 17 16:06 Providename
        -rw-r--r--.  1 0 0      8192 Apr 17 10:42 Recommendname

    Examples:
        >>> type(var_lib_rpm)
        <class 'insights.parsers.ls_var_lib_rpm.LsVarLibRpm'>
        >>> var_lib_rpm.dir_contains('/var/lib/rpm', 'Packages')
        True
        >>> var_lib_rpm.files_of('/var/lib/rpm')
        ['Basenames', 'Conflictname', 'Obsoletename', 'Packages', 'Providename', 'Recommendname']

    """
    pass
