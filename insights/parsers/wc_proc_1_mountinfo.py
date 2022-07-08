"""
WcProc1Mountinfo - Command ``/usr/bin/wc -l /proc/1/mountinfo``
===============================================================

Parser for parsing the output of command ``/usr/bin/wc -l /proc/1/mountinfo``.
"""

from insights import Parser, parser
from insights.parsers import ParseException
from insights.specs import Specs


@parser(Specs.wc_proc_1_mountinfo)
class WcProc1Mountinfo(Parser):
    """
    Provides the newline counts of file ``/proc/1/mountinfo`` by parsing the
    output of command ``/usr/bin/wc -l /proc/1/mountinfo``.

    Attributes:
        count(int): the newline counts of file ``/proc/1/mountinfo``, default
            to -1 for unparsable content

    Typical content looks like::

        37 /proc/1/mountinfo

    Examples:
        >>> type(wc_info)
        <class 'insights.parsers.wc_proc_1_mountinfo.WcProc1Mountinfo'>
        >>> wc_info.count
        37

    Raises:
        insights.parsers.ParseException: if the command output is empty or
        unparsable.
    """

    def parse_content(self, content):
        if len(content) == 0 or 'No such file or directory' in content[0]:
            raise ParseException("Error: ", content[0] if content else 'empty file')
        count_str = content[0].split()[0]
        if not count_str.isdigit():
            raise ParseException("Error: unparsable output from command wc: ", content[0])
        self.count = int(count_str)
