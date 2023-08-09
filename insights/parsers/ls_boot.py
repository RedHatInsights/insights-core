"""
LsBoot - command ``ls -lanR /boot``
===================================

The ``ls -lanR /boot`` command provides information for the listing of the
``/boot`` directory.

See :class:`insights.parsers.ls.FileListing` for more information.

"""

from insights import CommandParser, parser
from insights.parsers.ls import FileListing
from insights.specs import Specs


@parser(Specs.ls_boot)
class LsBoot(CommandParser, FileListing):
    """
    Parse the /boot directory listing using a standard FileListing parser.

    .. warning::

        For Insights Advisor Rules, it's recommended to use the
        :class:`insights.parsers.ls.LSlanR` and add the ``"/boot"`` to
        the filter list of `Specs.ls_lanR_dirs` instead.

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
        >>> type(bootdir)
        <class 'insights.parsers.ls_boot.LsBoot'>
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
    __root_path = '/boot'
