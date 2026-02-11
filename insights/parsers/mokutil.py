"""
Mokutil Entries
===============

Parsers provided in this module includes:

MokutilDbShort - command ``mokutil --db --short``
-------------------------------------------------
MokutilSbstate - command ``mokutil --sb-state``
-----------------------------------------------
"""

from insights.core import CommandParser, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.mokutil_db_short)
class MokutilDbShort(CommandParser, dict):
    """
    Class for parsing the ``mokutil --db --short`` command. It stores the output
    into a dict. For each line, the hash key is stored as a key and the left part is the value.

    Sample output of this command is::

        b7b180e323 Signature Database key
        46def63b5c Microsoft Corporation UEFI CA 2011

    Raises:
        SkipComponent: When the content is empty or has no valid lines.

    Examples:

        >>> type(mokutil_db_short)
        <class 'insights.parsers.mokutil.MokutilDbShort'>
        >>> len(mokutil_db_short)
        2
        >>> 'b7b180e323' in mokutil_db_short
        True
        >>> mokutil_db_short['b7b180e323']
        'Signature Database key'
    """

    def parse_content(self, content):
        for line in content:
            line = line.strip()
            parts = line.split(None, 1)
            if len(parts) < 2:
                raise SkipComponent('Bad format content')
            self[parts[0].strip()] = parts[1].strip()
        if not self:
            raise SkipComponent('No valid content')


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
        <class 'insights.parsers.mokutil.MokutilSbstate'>
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
