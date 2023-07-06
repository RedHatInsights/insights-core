"""
Lists ALL the firmware packages
===============================

Parsers included in this module are:

LsLibFW - command ``/bin/ls -lanR /lib/firmware``
----------------------------------------------------

"""
from .. import parser, CommandParser, FileListing
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.ls_lib_firmware)
class LsLibFW(CommandParser, FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSlanR` instead.

    This parser will help to parse the output of command ``/bin/ls -lanR /lib/firmware``

    Typical output of the ``/bin/ls -lanR /lib/firmware`` command is::

    \t/lib/firmware:
    \ttotal 37592
    \tdrwxr-xr-x. 83 0 0    8192 Aug 14 02:43 .
    \tdr-xr-xr-x. 26 0 0    4096 Aug 14 02:22 ..
    \tdrwxr-xr-x.  2 0 0      40 Aug 14 02:42 3com
    \tlrwxrwxrwx.  1 0 0      16 Aug 14 02:42 a300_pfp.fw -> qcom/a300_pfp.fw
    \tlrwxrwxrwx.  1 0 0      16 Aug 14 02:42 a300_pm4.fw -> qcom/a300_pm4.fw
    \tdrwxr-xr-x.  2 0 0      34 Aug 14 02:42 acenic
    \tdrwxr-xr-x.  2 0 0      50 Aug 14 02:42 adaptec
    \tdrwxr-xr-x.  2 0 0      73 Aug 14 02:42 advansys
    \t
    \t/lib/firmware/3com:
    \ttotal 84
    \tdrwxr-xr-x.  2 0 0    40 Aug 14 02:42 .
    \tdrwxr-xr-x. 83 0 0  8192 Aug 14 02:43 ..
    \t-rw-r--r--.  1 0 0 24880 Jun  6 10:14 3C359.bin
    \t-rw-r--r--.  1 0 0 44548 Jun  6 10:14 typhoon.bin
    \t
    \t/lib/firmware/acenic:
    \ttotal 160
    \tdrwxr-xr-x.  2 0 0    34 Aug 14 02:42 .
    \tdrwxr-xr-x. 83 0 0  8192 Aug 14 02:43 ..
    \t-rw-r--r--.  1 0 0 73116 Jun  6 10:14 tg1.bin
    \t-rw-r--r--.  1 0 0 77452 Jun  6 10:14 tg2.bin

    Example:

        >>> type(lslibfw)
        <class 'insights.parsers.ls_lib_firmware.LsLibFW'>
        >>> lslibfw.files_of("/lib/firmware/bnx2x")
        ['bnx2x-e1-6.0.34.0.fw', 'bnx2x-e1-6.2.5.0.fw', 'bnx2x-e1-6.2.9.0.fw', 'bnx2x-e1-7.0.20.0.fw', 'bnx2x-e1-7.0.23.0.fw']
        >>> lslibfw.dir_contains("/lib/firmware/bnx2x", "bnx2x-e1-6.0.34.0.fw")
        True
        >>> lslibfw.dirs_of("/lib/firmware")
        ['.', '..', '3com', 'acenic', 'adaptec', 'advansys']
        >>> lslibfw.total_of("/lib/firmware")
        37592
    """
    def __init__(self, *args, **kwargs):
        deprecated(LsLibFW, "Please use the :class:`insights.parsers.ls.LSlanR` instead.", "3.5.0")
        super(LsLibFW, self).__init__(*args, **kwargs)
