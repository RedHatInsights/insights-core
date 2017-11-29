"""
FCMatch - command ``/usr/bin/fc-match -sv 'sans:regular:roman' family fontformat``
==================================================================================

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

Examples:
    >>> fc_match = shared[FCMatch]
    >>> fc_match_info = fc_match[0]
    >>> fc_match_info
    {'fontformat': '"TrueType"(w)', 'family': '"DejaVu Sans"(s)'}
"""

from .. import Parser, parser


@parser("fc-match")
class FCMatch(Parser):
    """
    Class to parse command `/usr/bin/fc-match -sv 'sans:regular:roman' family fontformat`.
    This object provides the ' __getitem__' and '__iter__' methods to allow it to
    be used as a list to iterate over the ``data`` data, e.g.::

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
