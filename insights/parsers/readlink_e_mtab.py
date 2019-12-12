"""
ReadLinkEMtab - command ``readlink -e /etc/mtab``
=================================================

The ``readlink -e /etc/mtab`` command provides information about
the path of ``mtab`` file.

Sample content from command ``readlink -e /etc/mtab`` is::
    /proc/4578/mounts

Examples:
    >>> mtab.path
    '/proc/4578/mounts'
"""

from insights.specs import Specs
from insights.parsers import SkipException
from insights import parser, CommandParser


@parser(Specs.readlink_e_etc_mtab)
class ReadLinkEMtab(CommandParser):
    """Class for command: readlink -e /etc/mtab"""
    def parse_content(self, content):
        if content is None or len(content) == 0:
            raise SkipException("No Data from command: readlink -e /etc/mtab")

        for line in content:
            self._path = line  # use the last line

    @property
    def path(self):
        """Returns real file path from command"""
        return self._path
