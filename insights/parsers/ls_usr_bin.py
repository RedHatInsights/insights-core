"""
LsUsrBin - command ``ls -lan /usr/bin``
=======================================

The ``ls -lan /usr/bin`` command provides information for the listing of the
``/usr/bin`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

For ls_usr_bin, it may collect a lot of files or directories that may not be
necessary, so a default filter `add_filter(Specs.ls_usr_bin, "total")` has been
added in this parser.

If addtional file or directory need to be collected by this parser, please
add related filter to corresponding code.

Sample added filter:

    >>> add_filter(Specs.ls_usr_bin, "python")
    >>> add_filter(Specs.ls_usr_bin, "virt")

Sample directory list collected::

    total 41472
    lrwxrwxrwx.  1 0  0        7 Oct 22  2019 python -> python2
    -rwxr-xr-x.  1 0  0     2558 Apr 10  2019 python-argcomplete-check-easy-install-script
    -rwxr-xr-x.  1 0  0      318 Apr 10  2019 python-argcomplete-tcsh
    lrwxrwxrwx.  1 0  0       14 Oct 22  2019 python-config -> python2-config
    lrwxrwxrwx.  1 0  0        9 Oct 22  2019 python2 -> python2.7

Examples:

    >>> "accessdb" in ls_usr_bin
    False
    >>> "/usr/bin" in ls_usr_bin
    True
    >>> ls_usr_bin.dir_entry('/usr/bin', 'python-argcomplete-tcsh')['type']
    '-'
    >>> ls_usr_bin.dir_entry('/usr/bin', 'python2')['type']
    'l'
"""

from insights.core.filters import add_filter
from insights.specs import Specs
from insights.util import deprecated

from .. import CommandParser, parser
from .. import FileListing


add_filter(Specs.ls_usr_bin, "total")


@parser(Specs.ls_usr_bin)
class LsUsrBin(CommandParser, FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSlanFiltered` instead.

    Parses output of ``ls -lan /usr/bin`` command.
    """
    def __init__(self, *args, **kwargs):
        deprecated(LsUsrBin, "Please use the :class:`insights.parsers.ls.LSlanFiltered` instead.", "3.5.0")
        super(LsUsrBin, self).__init__(*args, **kwargs)
