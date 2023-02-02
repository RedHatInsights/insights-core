"""
UpdateInfo - command ``yum updateinfo list -C``
===============================================
Provides a list of available advisories
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import parse_delimited_table
from insights.specs import Specs


@parser(Specs.yum_updateinfo)
class YumUpdateinfo(CommandParser):
    """
    Class for parsing the output of `yum updateinfo list -C`.

    Expected output of the command is::

        RSHA-2020-0001 security       firefox-83.0-13.fc32.x86_64
        RHBA-2020-0002 bugfix         flatpak-libs-1.8.3-1.fc32.x86_64
        RHEA-2020-0003 enhancement    flatpak-selinux-1.8.3-1.fc32.noarch

    Examples:
        >>> len(updateinfo.items)
        3
        >>> updateinfo.items[0]
        {'advisory': 'RSHA-2020-0001', 'type': 'security', 'package': 'firefox-83.0-13.fc32.x86_64'}

    """

    def parse_content(self, content):
        """Parse the command output"""
        with_header = ['advisory type package'] + content
        table = parse_delimited_table(with_header)
        if not table:
            raise SkipComponent('No data.')
        self._items = table

    @property
    def items(self):
        """
        list: Updatable packages, along with minimal advisory metadata
        """
        return self._items
