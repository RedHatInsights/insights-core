"""
grubby - command ``/usr/sbin/grubby``
=====================================

This parser returns the output of the ``grubby --default-index`` command.

Examples:

    >>> grubby_default_index.default_index
    0
"""

from insights.specs import Specs
from .. import parser, Parser
from . import SkipException


@parser(Specs.grubby_default_index)
class GrubbyDefaultIndex(Parser):
    """
    This parser will parse the output of command ``grubby --default-index``.

    Attributes:
        default_index (int): the numeric index of the current default boot entry, count from 0
    """
    def parse_content(self, content):
        if content and content[0].isdigit():
            self.default_index = int(content[0])
        else:
            raise SkipException('Invalid default index value.')
