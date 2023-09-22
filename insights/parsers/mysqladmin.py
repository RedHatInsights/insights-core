"""
mysqladmin command - Command
============================

Parsing and extracting data from output of command ``/bin/mysqladmin variables``.
Parsers contained in this module are:

MysqladminStatus - command ``/bin/mysqladmin status``
-----------------------------------------------------

MysqladminVars - command ``/bin/mysqladmin variables``
------------------------------------------------------

"""

import re

from insights.core import CommandParser, LegacyItemAccess
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


@parser(Specs.mysqladmin_status)
class MysqladminStatus(CommandParser):
    """
    Module for parsing the output of the ``mysqladmin status`` command.

    Typical output looks like::

        Uptime: 1103965 Threads: 1820 Questions: 44778091 Slow queries: 0 Opens: 1919 Flush tables: 1 Open tables: 592 Queries per second avg: 40.561

    Examples:
        >>> result.status['Uptime'] == '1103965'
        True
        >>> result.status['Threads']
        '1820'
        >>> result.status['Queries per second avg'] == '1919'
        False
    """
    pattern = re.compile("(Uptime):.(\d+).(Threads):.(\d+).(Questions):.(\d+).(Slow queries):.(\d+).(Opens):.(\d+).(Flush tables):.(\d+).(Open tables):.(\d+).(Queries per second avg):.(\d+.\d*)")

    def grouper(self, iterable, n, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Content is empty.")

        self.status = {}
        if self.pattern.search(content[0]):
            groups = self.pattern.search(content[0]).groups()
            for group in self.grouper(groups, 2):
                self.status[group[0]] = group[1]
        else:
            raise ParseException("Unable to parse the output.")


@parser(Specs.mysqladmin_vars)
class MysqladminVars(LegacyItemAccess, CommandParser):
    """
    The output of command ``/bin/mysqladmin variables`` is in mysql table format,
    contains 'Variable_name' and 'Value' two columns.
    This parser will parse the table and set each variable as an class
    attribute. The unparsable lines are stored in the ``bad_lines`` property list.

    Example:
        >>> output.get('version')
        '5.5.56-MariaDB'
        >>> 'datadir' in output
        True
        >>> output.get('what', '233')
        '233'
        >>> output.getint('aria_block_size')
        8192
    """

    def parse_content(self, content):
        """
        Parse output content table of command ``/bin/mysqladmin variables``.
        Set each variable as an class attribute.
        """
        bad_lines = []
        if not content:
            raise SkipComponent("Empty content.")
        if len(content) < 5:
            raise ParseException("Wrong content in table: '{0}'.".format(content))

        data = {}
        for _l in content[3:-1]:
            l = _l.strip()
            if not (l.startswith('|') and l.endswith('|')):
                bad_lines.append(_l)
                continue
            l = l[1:-1]
            lsp = l.split('|', 1)
            if len(lsp) < 2:
                bad_lines.append(_l)
                continue
            data[lsp[0].strip().lower()] = lsp[1].strip()
        self.data = data
        self.bad_lines = bad_lines

    def getint(self, keyword, default=None):
        """
        Get value for specified keyword, use default if keyword not found.

        Example:

            >>> output.getint('wait_timeout')
            28800
            >>> output.getint('wait_what', 100)
            100

        Args:

            keyword (str): Key to get from ``self.data``.
            default (int): Default value to return if key is not present.

        Returns:

            value (int): Int value of the stored item, or the default if not found.
        """
        if default and not isinstance(default, int):
            raise TypeError("Default value should be int type.")
        v = self.data.get(keyword)
        return int(v) if v and v.isdigit() else default
