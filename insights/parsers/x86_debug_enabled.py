"""
Parsers for file ``/sys/kernel/debug/x86/*_enabled`` outputs
============================================================

This module provides the following parsers:

X86Enabled - file ``/sys/kernel/debug/x86/*_enabled``
------------------------------------------------------------
"""

from insights import Parser
from insights.parsers import ParseException
from insights.parsers import SkipException


class X86DebugEnabled(Parser):
    """
    Class for parsing file ``/sys/kernel/debug/x86/*_enabled``

    Attributes:
        value (int): the result parsed of '/sys/kernel/debug/x86/*_enabled'

    Raises:
        SkipException: When input content is empty
        ParseException: When input content is not available to parse
    """
    def parse_content(self, content):
        EMPTY = "Input content is empty"
        BADWD = "No useful data parsed in content: '{0}'".format(content)

        if not content:
            raise SkipException(EMPTY)

        if str(content[0]).isdigit():
            self.value = int(content[0])
        else:
            self.value = content[0]
