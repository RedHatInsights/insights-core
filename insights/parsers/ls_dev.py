"""
LsDev - Command ``ls -lanR /dev``
=================================

The ``ls -lanR /dev`` command provides information for the listing of the
``/dev`` directory.

See :class:`insights.parsers.ls.FileListing` for more information.

"""
from insights import CommandParser, FileListing, parser
from insights.specs import Specs


@parser(Specs.ls_dev)
class LsDev(CommandParser, FileListing):
    """
    Parses output of ``ls -lanR /dev`` command.

    .. warning::

        For Insights Advisor Rules, it's recommended to use the
        :class:`insights.parsers.ls.LSlanR` and add the ``"/dev"`` to
        the filter list of `Specs.ls_lanR_dirs` instead.

    Sample directory listing::
        /dev:
        total 3
        brw-rw----.  1 0  6 253,   0 Aug  4 16:56 dm-0
        brw-rw----.  1 0  6 253,   1 Aug  4 16:56 dm-1
        brw-rw----.  1 0  6 253,  10 Aug  4 16:56 dm-10
        crw-rw-rw-.  1 0  5   5,   2 Aug  5  2016 ptmx
        drwxr-xr-x.  2 0  0        0 Aug  4 16:56 pts
        lrwxrwxrwx.  1 0  0       25 Oct 25 14:48 initctl -> /run/systemd/initctl/fifo

        /dev/rhel:
        total 0
        drwxr-xr-x.  2 0 0  100 Jul 25 10:00 .
        drwxr-xr-x. 23 0 0 3720 Jul 25 12:43 ..
        lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 home -> ../dm-2
        lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 root -> ../dm-0
        lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 swap -> ../dm-1

    Examples:
        >>> type(ls_dev)
        <class 'insights.parsers.ls_dev.LsDev'>
        >>> "/dev/rhel" in ls_dev
        True
        >>> ls_dev.files_of("/dev/rhel")
        ['home', 'root', 'swap']
        >>> ls_dev.dirs_of("/dev/rhel")
        ['.', '..']
        >>> ls_dev.specials_of("/dev/rhel")
        []
        >>> sorted(ls_dev.listing_of("/dev/rhel").keys())
        ['.', '..', 'home', 'root', 'swap']
        >>> ls_dev.listing_of('/dev/rhel')['.']['type'] == 'd'
        True
        >>> ls_dev.listing_of('/dev/rhel')['home']['link']
        '../dm-2'
    """
    __root_path = '/dev'
