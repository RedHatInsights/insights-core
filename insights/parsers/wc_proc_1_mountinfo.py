"""
WcProc1Mountinfo - Command ``/usr/bin/wc -l /proc/1/mountinfo``
===============================================================

Parser for parsing the output of command ``/usr/bin/wc -l /proc/1/mountinfo``.
"""

from insights import Parser, parser
from insights.core.dr import SkipComponent
from insights.parsers import ParseException
from insights.specs import Specs


@parser(Specs.wc_proc_1_mountinfo)
class WcProc1Mountinfo(Parser):
    """
    Provides the line counts of file ``/proc/1/mountinfo`` by parsing the
    output of command ``/usr/bin/wc -l /proc/1/mountinfo``.

    Attributes:
        line_count(int): the line counts of file ``/proc/1/mountinfo``

    Typical content looks like::

        37 /proc/1/mountinfo

    Examples:
        >>> type(wc_info)
        <class 'insights.parsers.wc_proc_1_mountinfo.WcProc1Mountinfo'>
        >>> wc_info.line_count
        37

    Raises:
        SkipComponent: if the command output is empty or missing file
        ParseException: if the command output is unparsable
    """

    def parse_content(self, content):
        if len(content) == 0 or 'No such file or directory' in content[0]:
            raise SkipComponent("Error: ", content[0] if content else 'empty file')
        count_str = content[0].split()[0]
        if not count_str.isdigit():
            raise ParseException("Error: unparsable output from command wc: ", content[0])
        self.line_count = int(count_str)
