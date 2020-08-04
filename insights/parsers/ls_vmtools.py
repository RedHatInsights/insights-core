"""
LsVMTools - command ``/bin/ls -l /etc/rc.d/init.d/vmware-tools``
===============================================================

The ``ls -l /etc/rc.d/init.d/vmware-tools`` command provides information for the file vmware-tools.

Sample listing::

    lrwxrwxrwx. 1 root root 30 Jun 11 19:32 etc/rc.d/init.d/vmware-tools -> ../../vmware-tools/services.sh

Examples:

    >>> type(vmtools)


"""

from .. import FileListing, parser, CommandParser
from insights.specs import Specs


@parser(Specs.ls_vmtools)
class LsVMTools(CommandParser, FileListing):
    """
    Parse the /etc/rc.d/init.d/vmware-tools  file listing using a standard FileListing parser.
    """
    pass
