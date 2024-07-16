"""
Secure -  file ``/etc/securetty``
=================================
"""
from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.securetty)
class Securetty(Parser):
    """Parser for ``/etc/securetty`` file.

    Sample Content::

        console
        # tty0
        tty1
        tty2
        tty3

    Attributes:
        terminals(list): a list of terminal names(without leading /dev/) which are considered
                         secure for the transmission of certain authentication tokens.

    Examples::
        >>> securetty.terminals
        ['console', 'tty1', 'tty2', 'tty3']
    """

    def parse_content(self, content):
        self.terminals = []
        for line in content:
            if not line or line.startswith('#'):
                continue
            self.terminals.append(line)
