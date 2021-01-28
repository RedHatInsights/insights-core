"""
LdLibraryPath - LD_LIBRARY_PATH of PIDs
=======================================

Parser for parsing the environment variable LD_LIBRARY_PATH of each PID.

"""

from collections import namedtuple
from insights import parser, Parser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs

LdLibraryPath = namedtuple('LdLibraryPath', ('pid', 'path', 'raw'))
"""namedtuple: Type for storing the LdLibraryPath of PID"""


@parser(Specs.ld_library_path_of_pid)
class PidLdLibraryPath(Parser, list):
    """
    Base class for parsing the ``LD_LIBRARY_PATH`` variable of each PID of the
    system into a list.

    Typical content looks like::

        105901 /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib
        105902 /usr/sap/RH1/SYS/exe/uc/linuxx86_64:/usr/sap/RH1/SYS/exe/run

    Examples:
        >>> len(ld_lib_path)
        2
        >>> isinstance(ld_lib_path[0].path, list)
        True
        >>> len(ld_lib_path[0].path)
        3
        >>> '/sapdb/clients/RH1/lib' in ld_lib_path[0].path
        True
        >>> ld_lib_path[0].pid
        '105901'

    Raises:
        SkipException: When the output is empty or nothing needs to parse.
        ParseException: When the line cannot be parsed.

    """

    def parse_content(self, content):
        if not content:
            raise SkipException

        llds = []
        for line in content:
            pid, _, raw = [s.strip() for s in line.partition(' ')]
            paths = raw
            if not pid.isdigit():
                raise ParseException('Incorrect line: {0}'.format(line))
            if raw and raw[0] == raw[-1] and raw[0] in ('\'', '"'):
                paths = raw[1:-1]
            paths = paths.split(':')
            llds.append(LdLibraryPath(pid, paths, raw))

        if not llds:
            raise SkipException("LD_LIBRARY_PATH not set.")

        self.extend(llds)
