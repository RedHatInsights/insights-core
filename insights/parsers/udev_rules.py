"""
UdevRules - file ``/usr/lib/udev/rules.d/59-fc-wwpn-id.rules``
==============================================================

The parser UdevRules parses the file "/usr/lib/udev/rules.d/59-fc-wwpn-id.rules",
and set the property file_valid to a boolean value by checking if it is a valid
rule file and the property invalid_lines contains all the lines that are invalid.

Examples:

    >>> type(udev_rules)
    <class 'insights.parsers.udev_rules.UdevRules'>
    >>> udev_rules.file_valid
    True
"""
import re

from insights.core import ConfigParser
from insights import parser, get_active_lines
from insights.specs import Specs

LINE_REGEX = re.compile(r'^([A-Z_-{}]*?(==|!=|=|\+=|:=|-=)".*?")(.*?)$')


@parser(Specs.udev_fc_wwpn_id_rules)
class UdevRules(ConfigParser):
    """
    Parse data from the ``/usr/lib/udev/rules.d/59-fc-wwpn-id.rules`` file.

    Attributes:
        invalid_lines (list): It contains all the invalid lines.
    """

    def parse_content(self, content):
        self.invalid_lines = []
        content = get_active_lines(content)
        for line in content:
            original_line = line
            line_valid = True
            while line_valid and line:
                line_valid, line = _check_line_valid(line)
                if not line_valid:
                    self.invalid_lines.append(original_line)
                    break

    @property
    def file_valid(self):
        return len(self.invalid_lines) == 0


def _check_line_valid(line):
    if line and LINE_REGEX.match(line) and LINE_REGEX.match(line).group(3):
        if not LINE_REGEX.match(line).group(3).startswith(','):
            return (False, '')
        else:
            return (True, LINE_REGEX.match(line).group(3).strip(',').strip())
    return (True, '')
