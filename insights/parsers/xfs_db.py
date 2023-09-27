"""
xfs_db Commands
===============

Parser contains in this module is:

XFSDbFrag - command ``/usr/sbin/xfs_db -r -c frag <mounted_device>``
--------------------------------------------------------------------

"""
from insights import SkipComponent
from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.xfs_db_frag)
class XFSDbFrag(CommandParser):
    """
    The ``/usr/sbin/xfs_db -r -c frag <mounted_device>`` command provides information for the
    xfs fragmentation.

    Attributes:
        fragmentation_factor (str): the file fragmemtation percentage, like 0.38%.

    Sample output::

        actual 42641, ideal 42477, fragmentation factor 58.28%
        Note, this number is largely meaningless.
        Files on this filesystem average 1.00 extents per file

    Examples:
        >>> type(xfs_db_frag)
        <class 'insights.parsers.xfs_db.XFSDbFrag'>
        >>> xfs_db_frag.fragmentation_factor
        '58.28%'
    """

    def parse_content(self, content):
        self.fragmentation_factor = ""

        for line in content:
            if not line.strip():
                continue

            if len(line.split(",")) != 3:
                continue
            items = line.split(",")
            if (items[0].strip().startswith("actual ") and
                    items[1].strip().startswith("ideal ") and
                    items[2].strip().startswith("fragmentation factor ")):
                self.fragmentation_factor = items[2].strip().split()[-1]
                return

        if not self.fragmentation_factor:
            raise SkipComponent("Invalid output of xfs fragmentation")
