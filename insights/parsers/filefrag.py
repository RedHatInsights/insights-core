"""
Filefrag - Command ``/sbin/filefrag <specified file>``
======================================================

Parser for parsing the output of command ``/sbin/filefrag <specified file>``.
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

        open: No such file or directory
        /boot/grub2/grubenv: 1 extent found

    Examples:
        >>> type(filefrag)
        <class 'insights.parsers.filefrag.Filefrag'>
        >>> filefrag['/boot/grub2/grubenv']
        1
        >>> filefrag.unparsed_lines
        []

    Raises:
        SkipComponent: if the command output is empty or missing file
    """

    def parse_content(self, content):
        self.unparsed_lines = []
        for line in content:
            if 'No such file or directory' in line:
                # Skip non-exist dirs
                continue
            try:
                file, frag = line.split(': ')
                extents = frag.strip().split()[0]
                self[file] = int(extents)
            except Exception:
                self.unparsed_lines.append(line)
        if not self and not self.unparsed_lines:
            raise SkipComponent
