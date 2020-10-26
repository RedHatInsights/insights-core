"""
DotNet- Comand ``/usr/bin/dotnet``
==================================

The parser for ``/usr/bin/dotnet --version`` is included in this module..

"""

from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.dotnet_version)
class DotNetVersion(CommandParser):
    """
    Class for parsing the output of the ``/usr/bin/dotnet --version`` command.

    Sample output::

        3.1.108

    Examples:
        >>> dotnet_ver.major
        3
        >>> dotnet_ver.minor
        1
        >>> dotnet_ver.raw
        '3.1.108'
    """

    def parse_content(self, content):
        if not content or len(content) > 1:
            raise SkipException

        self.major = self.minor = None
        self.raw = content[0].strip()

        if ' ' not in self.raw and '.' in self.raw:
            v_sp = [i.strip() for i in self.raw.split('.', 2)]
            if len(v_sp) >= 2 and v_sp[0].isdigit() and v_sp[1].isdigit():
                self.major = int(v_sp[0])
                self.minor = int(v_sp[1])

        if self.major is None:
            raise ParseException("Unrecognized version: {0}", self.raw)
