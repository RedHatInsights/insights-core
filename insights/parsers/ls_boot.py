"""
LsBoot - command ``ls -lanR /boot``
===================================

The ``ls -lanR /boot`` command provides information for the listing of the
``/boot`` directory.

See the ``FileListing`` class for a more complete description of the
available features of the class.

Sample directory listing::

    /boot:
    total 187380
    dr-xr-xr-x.  3 0 0     4096 Mar  4 16:19 .
    dr-xr-xr-x. 19 0 0     4096 Jul 14 09:10 ..
    -rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64

    /boot/grub2:
    total 36
    drwxr-xr-x. 6 0 0  104 Mar  4 16:16 .
    dr-xr-xr-x. 3 0 0 4096 Mar  4 16:19 ..
    lrwxrwxrwx. 1 0 0     11 Aug  4  2014 menu.lst -> ./grub.conf
    -rw-r--r--. 1 0 0   64 Sep 18  2015 device.map

Examples:

    >>> bootdir = shared[LsBoot]
    >>> '/boot' in bootdir
    True
    >>> '/boot/grub' in bootdir
    False
    >>> bootdir.files_of('/boot')
    ['config-3.10.0-229.14.1.el7.x86_64']
    >>> bootdir.dirs_of('/boot')
    ['.', '..', 'grub2']
    >>> bootdir.dir_contains('/boot/grub2', 'menu.lst')
    True
"""

from .. import FileListing, parser, CommandParser
from insights.specs import Specs


@parser(Specs.ls_boot)
class LsBoot(CommandParser, FileListing):
    """
    Parse the /boot directory listing using a standard FileListing parser.
    """
    pass
