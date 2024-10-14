"""
Localectl - command ``localectl``
=================================
Parser the output of localectl command.

"""

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.localectl)
class Localectl(CommandParser, dict):
    """
    Reads the output of localectl command

    Example output::

           System Locale: LANG=en_US.UTF-8
               VC Keymap: us
              X11 Layout: us

    Examples::
        >>> type(localectl)
        <class 'insights.parsers.localectl.Localectl'>
        >>> localectl['System Locale'] == 'LANG=en_US.UTF-8'
        True
        >>> localectl['VC Keymap'] == 'us'
        True
        >>> localectl['X11 Layout'] == 'us'
        True
    """
    def parse_content(self, content):
        for line in content:
            if ': ' in line:
                key, val = [_l.strip() for _l in line.split(': ', 1)]
                self[key] = val

        if not self:
            raise SkipComponent
