"""
MokutilSbstate - command ``mokutil --sb-state``
===============================================
"""

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.mokutil_sbstate)
class MokutilSbstate(CommandParser):
    """
    Class for parsing the ``mokutil --sb-state`` command.

    Attributes:
        secureboot_enabled (bool): True if SecureBoot is enabled,
                                   False if SecureBoot is disabled, otherwise None.

    Sample output of this command is::

        SecureBoot enabled

    Examples:

        >>> type(mokutil)
        <class 'insights.parsers.mokutil_sbstate.MokutilSbstate'>
        >>> mokutil.secureboot_enabled
        True
    """

    def parse_content(self, content):
        self.secureboot_enabled = None

        non_empty_lines = [line for line in content if line]  # get rid of blank lines
        if "SecureBoot enabled" in non_empty_lines[0]:
            self.secureboot_enabled = True
        elif "SecureBoot disabled" in non_empty_lines[0]:
            self.secureboot_enabled = False
