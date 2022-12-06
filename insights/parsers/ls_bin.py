"""
LsBin - command ``/bin/ls -lan /bin/``
======================================

The ``ls -lan /bin/`` command provides information for the listing of the
``/bin`` directory.

See the ``FileListing`` class for a more complete description of the
available features of the class.

Sample directory listing::

    total 214536
    dr-xr-xr-x.  2 0  0    49152 Nov  4 04:58 .
    drwxr-xr-x. 12 0  0      144 May 29  2022 ..
    -rwxr-xr-x.  1 0  0    54008 May 31  2022 [
    -rwxr-xr-x.  1 0  0    33416 Nov  1  2021 ac
    -rwxr-xr-x.  1 0  0    24480 Jul  9 05:16 aconnect
    -rwxr-xr-x.  1 0  0    29080 Jun 14 10:04 addr2line
    lrwxrwxrwx.  1 0  0       25 May 29  2022 apropos -> /etc/alternatives/apropos
    lrwxrwxrwx.  1 0  0        6 Aug 10  2021 apropos.man-db -> whatis
    -rwxr-xr-x.  1 0  0    58000 Jun 14 10:04 ar
    -rwxr-xr-x.  1 0  0    33368 May 31  2022 arch
    lrwxrwxrwx.  1 0  0        5 Jul  9 05:16 arecord -> aplay

Examples:

    >>> type(ls_bin)
    <class 'insights.parsers.ls_bin.LsBin'>
    >>> ls_bin.files_of('/bin')
    ['[', 'ac', 'aconnect', 'addr2line', 'apropos', 'apropos.man-db', 'ar', 'arch', 'arecord']
    >>> ls_bin.dirs_of('/bin')
    ['.', '..']
"""

from insights import FileListing, parser, CommandParser
from insights.specs import Specs


@parser(Specs.ls_bin)
class LsBin(CommandParser, FileListing):
    """
    Parse the /bin directory listing using a standard FileListing parser.
    """
    pass
