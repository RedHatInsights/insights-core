"""
FilefragGrubenv - Command ``/sbin/filefrag /boot/grub2/grubenv``
================================================================

Parser for parsing the output of command ``/sbin/filefrag /boot/grub2/grubenv``.
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.filefrag_grubenv)
class FilefragGrubenv(Parser):
    """
    Provides the extent counts of ``/boot/grub2/grubenv`` by parsing the
    output of command ``filefrag /boot/grub2/grubenv``.

    Attributes:
        extents(int): the extent counts of file ``/boot/grub2/grubenv``

    Typical content looks like::

        /boot/grub2/grubenv: 1 extent found

    Examples:
        >>> type(grubenv)
        <class 'insights.parsers.filefrag.FilefragGrubenv'>
        >>> grubenv.extents
        1

    Raises:
        SkipComponent: if the command output is empty or missing file
    """

    def parse_content(self, content):
        if len(content) == 0 or 'No such file or directory' in content[0]:
            raise SkipComponent("Error: ", content[0] if content else 'empty file')
        extents = content[0].split()[1]
        if not extents.isdigit():
            raise SkipComponent("Error: unparsable output", content[0])
        self.extents = int(extents)
