"""
FCMatch - command ``/bin/fc-match -sv 'sans:regular:roman' family fontformat``
==============================================================================

This command gets the fonts information in the current system.

Typical output of this command is::

    Pattern has 2 elts (size 16)
        family: "DejaVu Sans"(s)
        fontformat: "TrueType"(w)

    Pattern has 2 elts (size 16)
        family: "DejaVu Sans"(s)
        fontformat: "TrueType"(w)

    Pattern has 2 elts (size 16)
        family: "DejaVu Sans"(s)
        fontformat: "TrueType"(w)

    Pattern has 2 elts (size 16)
        family: "Nimbus Sans L"(s)
        fontformat: "Type 1"(s)

    Pattern has 2 elts (size 16)
        family: "Standard Symbols L"(s)
        fontformat: "Type 1"(s)

.. note::
    As there is a bug on RHEL6 that can cause segfault when executing ``fc-match`` command, we only parse the command output on RHEL7 before the bug is fixed.

Examples:
    >>> fc_match = shared[FCMatch]
    >>> fc_match_info = fc_match[0]
    >>> fc_match_info
    {'fontformat': '"TrueType"(w)', 'family': '"DejaVu Sans"(s)'}
"""

from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.fc_match)
class FCMatch(CommandParser):
    """
    Class to parse command `/bin/fc-match -sv 'sans:regular:roman' family fontformat`.
    This object provides the ' __getitem__' and '__iter__' methods to allow it to
    be used as a list to iterate over the ``data``, e.g.::

        >>> fc_match = shared[FCMatch]
        >>> for item in fc_match:
        >>>     print item["family"]
        >>> fc_match_info = fc_match[0]
    """

    def parse_content(self, content):
        self.data = []
        font = {}
        for l in content:
            if ":" in l:
                k, v = l.strip().split(":")
                if k == "family":
                    font["family"] = v.strip()
                else:
                    font["fontformat"] = v.strip()
                    if font not in self.data:
                        self.data.append(font)
                        font = {}

    def __getitem__(self, index):
        return self.data[index]

    def __iter__(self):
        for item in self.data:
            yield item
