"""
xfs_db Commands
===============

Parser contains in this module is:

XFSDbFrag - command ``/usr/sbin/xfs_db -r -c frag <mounted_device>``
--------------------------------------------------------------------

XFSDbFreesp - command ``/usr/sbin/xfs_db -r -c freesp <mounted_device>``
------------------------------------------------------------------------

"""
from insights import SkipComponent
from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.parsers import calc_offset
from insights.parsers import get_active_lines
from insights.parsers import keyword_search
from insights.parsers import parse_delimited_table


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


@parser(Specs.xfs_db_freesp)
class XFSDbFreesp(CommandParser):
    """
    The ``/usr/sbin/xfs_db -r -c freesp <mounted_device>`` command provides free space information
    for the xfs filesystem.

    Sample output::

        from      to extents  blocks    pct
           1       1      16      16   0.01
           2       3       1       2   0.00
          64     127       1     103   0.04
        32768   65536      4   23113   99.95

    Attributes:
        free_stat(list of dict): A list of dictionaries with the key-value data from the table.

    Examples:
        >>> type(xfs_db_freesp)
        <class 'insights.parsers.xfs_db.XFSDbFreesp'>
        >>> len(xfs_db_freesp.free_stat) == 4
        True
        >>> xfs_db_freesp.free_stat[0]['from']
        '1'
        >>> len(xfs_db_freesp.search(pct='0.00')) == 1
        True
    """

    def parse_content(self, content):
        keys = ["from", "to", "extents", "blocks", "pct"]

        active_lines = get_active_lines(content)
        try:
            header_line_off = calc_offset(active_lines, keys, require_all=True)
        except ValueError:
            raise SkipComponent("Invalid output of xfs free space")

        if active_lines[header_line_off].split() != keys:
            raise SkipComponent("Invalid output of xfs free space")

        self.free_stat = parse_delimited_table(active_lines[header_line_off:])

    def search(self, **kwargs):
        """
        Search for rows in the data matching keywords in the search.

        This method uses the :py:func:`insights.parsers.keyword_search`
        function - see its documentation for a complete description of its
        keyword recognition capabilities.

        Arguments:
            **kwargs: Key-value pairs of search parameters.

        Returns:
            (list): A list of subscriptions that matched the search criteria.

        """
        return keyword_search(self.free_stat, **kwargs)
