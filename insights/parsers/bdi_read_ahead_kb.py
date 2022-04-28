"""
BDIReadAheadKB - file ``/sys/class/bdi/*/read_ahead_kb``
========================================================

This parser reads the content of ``/sys/class/bdi/*/read_ahead_kb``.
"""

from insights import Parser, parser
from insights.specs import Specs
from insights.parsers import ParseException


@parser(Specs.bdi_read_ahead_kb)
class BDIReadAheadKB(Parser):
    """
    Class ``BDIReadAheadKB`` parses the content of the ``/sys/class/bdi/*/read_ahead_kb``.

    Raises:
        ParseException: When content is empty or unparseable

    A typical sample of the content of this file looks like::

        128

    Examples:
        >>> type(bdi_read_ahead_kb)
        <class 'insights.parsers.bdi_read_ahead_kb.BDIReadAheadKB'>
        >>> bdi_read_ahead_kb.read_ahead_kb
        128
    """

    def parse_content(self, content):
        if len(content) != 1:
            raise ParseException('Error: {0}'.format(content if content else 'empty file'))
        try:
            self._read_ahead_kb = int(content[0].strip())
        except ValueError:
            raise ParseException("Error: unparseable content: {0}".format(content[0]))

    @property
    def read_ahead_kb(self):
        """ int: Value of ``read_ahead_kb``."""
        return self._read_ahead_kb
