"""
LocaleCtlStatus - command ``localectl status``
==============================================
Parser the output of localectl status command.

"""

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.localectl_status)
class LocaleCtlStatus(CommandParser, dict):
    """
    Reads the output of `localectl status` command

    Example output::

           System Locale: LANG=en_US.UTF-8
               VC Keymap: us
              X11 Layout: us

    Examples::
        >>> type(localectl_status)
        <class 'insights.parsers.localectl.LocaleCtlStatus'>
        >>> localectl_status['System Locale'] == 'LANG=en_US.UTF-8'
        True
        >>> localectl_status['VC Keymap'] == 'us'
        True
        >>> localectl_status['X11 Layout'] == 'us'
        True
    """
    def parse_content(self, content):
        for line in content:
            if ': ' in line:
                key, val = [_l.strip() for _l in line.split(': ', 1)]
                self[key] = val

        if not self:
            raise SkipComponent
