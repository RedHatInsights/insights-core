"""
Filefrag - Command ``/sbin/filefrag /boot/grub2/grubenv``
=========================================================

Parser for parsing the output of command ``/sbin/filefrag /boot/grub2/grubenv``.
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.filefrag)
class Filefrag(Parser, dict):
    """
    Provides the extent counts of the specified file by parsing the
    output of command ``filefrag <specified file>``.

    Typical content looks like::

        /boot/grub2/grubenv: 1 extent found

    Examples:
        >>> type(filefrag)
        <class 'insights.parsers.filefrag.Filefrag'>
        >>> filefrag['/boot/grub2/grubenv']
        1

    Raises:
        SkipComponent: if the command output is empty or missing file
    """

    def parse_content(self, content):
        if len(content) == 0 or (len(content) == 1 and 'No such file or directory' in content[0]):
            raise SkipComponent("Error: ", content[0] if content else 'empty file')
        for line in content:
            file = line.split()[0].strip(':')
            extents = line.split()[1]
            if extents.isdigit():
                self[file] = int(extents)
