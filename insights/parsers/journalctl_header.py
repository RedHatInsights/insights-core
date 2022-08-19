"""
JournalctlHeader - Datasource ``journalctl_header``
===================================================

This parser parse the output of the datasource ``journalctl_header``.
This datasource is used to count the number of the journal fields
accessed by using ``/usr/bin/journalctl --header`` command

"""

from insights import Parser, parser
from insights.specs import Specs


@parser(Specs.journalctl_header)
class JournalctlHeader(Parser):
    """
    Sample Output::

       '8'

    Attributes:
        number (int):   The number of the journal fields accessed

    Examples:
        >>> type(journalctl_header)
        <class 'insights.parsers.journalctl_header.JournalctlHeader'>
        >>> journalctl_header.number
        8
    """

    def parse_content(self, content):
        self.number = int(content[0].strip())
