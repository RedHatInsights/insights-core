"""
InitScript - files ``/etc/rc.d/init.d/*``
=========================================

InitScript is a parser for the initscripts in ``/etc/rc.d/init.d``.

Because this parser read multiple files, the initscripts are stored as a list
within the parser and need to be iterated through in order to find specific
initscripts.

Examples:

    >>> for initscript in shared[InitScript]: # Parser contains list of all initscripts
    ...     print "Name:", initscript.file_name
    ...
    Name: netconsole
    Name: rhnsd

"""
import re

from insights.core import Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs

CHKCONFIG_REGEX = re.compile(r"^#\s+chkconfig:\s+.*$")
LSB_REGEX = re.compile(r"^#\s+Provides:\s+.*$")

SHEBANG_REGEX = re.compile(r"^#!\s*/.*$")
COMMENT_REGEX = re.compile(r"^\s*#.*$")
STARTSTOPSTATUS_REGEX = re.compile(r"\b(start|stop|status)\b")


class EmptyFileException(ParseException):
    pass


class NotInitscriptException(ParseException):
    pass


@parser(Specs.initscript)
class InitScript(Parser):
    """
    Parse initscript files. Each item is a dictionary with following fields:

    Attributes:
        file_name (str): initscript name
        file_path (str): initscript path without leading '/'
        file_content (list): initscript content, line by line

    Because some files may not be real initscripts, to determine whether a file
    in ``etc/rc.d/init.d/`` is an initscript, the parser checks for
    ``# chkconfig: <values>`` or ``# Provides: <names>`` strings in the script.
    If that matches, then it assumes it is an initscript.

    Otherwise, it tries to find out if it is by searching for

    * shebang (e.g. ``#!/bin/bash``) on first line
    * ``start``/``stop``/``status`` tokens in non-commented out lines

    If 3 or more items are found (half the items searched for + 1), called
    *confidence* in the code (e.g.  shebang + start + stop), then we assume it
    is an initscript.

    Otherwise the parser raises a ``ParseException``.
    """

    def parse_content(self, content):
        """
        Raises:
            EmptyFileException: Raised if file is empty.
            NotInitscriptException: Raised if likely not an initscript.
        """
        self.file_content = content

        # If we find 'chkconfig: XYZ' or 'Provides: NAME', assume we have an
        # initscript
        for line in content:
            if CHKCONFIG_REGEX.match(line) or LSB_REGEX.match(line):
                return

        # Otherwise, check for hints (shebang + presence of start/stop/status
        # keywords)
        #
        # Allocate 1 point for each item found. And declare as valid if
        # confidence >= 3 (half of the number of items + 1).
        confidence = 0
        try:
            line = content[0]
            if SHEBANG_REGEX.match(line):
                confidence += 1
        except IndexError:
            raise EmptyFileException(self.file_path)

        key = {'start': 0, 'stop': 0, 'status': 0}
        for line in content:
            if COMMENT_REGEX.match(line):
                continue
            m = STARTSTOPSTATUS_REGEX.search(line)
            if m:
                key[m.group(1)] += 1
        confidence += len([v for v in key.values() if v != 0])

        if confidence < 3:
            raise NotInitscriptException("path: %s, confidence: %d" % (self.file_path, confidence))
