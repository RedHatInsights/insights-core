"""
Whoopsie - command ``/usr/bin/find /var/crash /var/tmp -path '*.reports-*/whoopsie-report' -print -quit``
=========================================================================================================
"""

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs
import re

WHOOPSIE_RE = re.compile(r'.*.reports-(\d+)-.*/whoopsie-report')


@parser(Specs.woopsie)
class Whoopsie(CommandParser):
    """
    Class for parsing the ``/usr/bin/find /var/crash /var/tmp -path '*.reports-*/whoopsie-report' -print -quit``
    command.

    Attributes:
        uid (string): uid parsed from the file path
        file (string): the line parsed from the command output

    Sample output of this command is::

        /var/crash/.reports-1000-user/whoopsie-report

    Examples:
        >>> type(whoopsie)
        <class 'insights.parsers.whoopsie.Whoopsie'>
        >>> whoopsie.uid
        '1000'
        >>> whoopsie.file
        '/var/crash/.reports-1000-user/whoopsie-report'
    """

    def parse_content(self, content):
        self.uid = None
        self.file = None

        match_whoopsie = WHOOPSIE_RE.search('\n'.join(content))
        if match_whoopsie:
            self.uid = match_whoopsie.group(1)
            self.file = match_whoopsie.group(0)
