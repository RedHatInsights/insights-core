"""
SystemctlGetDefault - command ``systemctl get-default``
=======================================================

Parser to parse the output of command ``systemctl get-default``
"""

from insights.core.exceptions import SkipComponent
from insights import CommandParser, parser
from insights.specs import Specs


@parser(Specs.systemctl_get_default)
class SystemctlGetDefault(CommandParser):
    """
    Class for parsing ``systemctl get-default`` command output.

    Sample output for command::

        graphical.target

    Examples:
        >>> type(systemctl_get_default)
        <class 'insights.parsers.systemctl_get_default.SystemctlGetDefault'>
        >>> systemctl_get_default.default_target
        'graphical.target'

    Attributes:
        default_target (String): The default target

    Raises:
        SkipComponent: When nothing needs to parse

    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Input content is empty")

        self.default_target = content[0].strip()
