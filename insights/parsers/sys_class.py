"""
System class files under ``/sys/class``
=======================================

This module contains the following parsers:

TtyConsoleActive - file ``/sys/class/tty/console/active``
---------------------------------------------------------
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.tty_console_active)
class TtyConsoleActive(Parser):
    """
    Parser for the `/sys/class/tty/console/active` file.

    Sample Content::

        tty0 ttyS0

    Raises:
        SkipComponent: When content has more than one lines.

    Attributes:
        devices(list): a list of kernel console devices.

    Examples::

        >>> tty_console_active.devices
        ['tty0', 'ttyS0']
    """

    def parse_content(self, content):
        if len(content) > 1:
            raise SkipComponent("This should be an one line file")
        if not content:
            raise SkipComponent("Empty content.")
        else:
            self.devices = content[0].split()
