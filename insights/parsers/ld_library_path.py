"""
LdLibraryPath - LD_LIBRARY_PATH of Users
========================================

Parser for parsing the environment variable LD_LIBRARY_PATH of each user

"""

from collections import namedtuple
from insights import parser, Parser
from insights.util import deprecated
from insights.parsers import SkipException, ParseException
from insights.specs import Specs

LdLibraryPathU = namedtuple('LdLibraryPathU', ('path', 'raw'))
"""namedtuple: Type for storing the LdLibraryPath of users"""


@parser(Specs.ld_library_path_of_user)
class UserLdLibraryPath(Parser, list):
    """
    Base class for parsing the ``LD_LIBRARY_PATH`` variable of each regular
    user of the system into a list.

    Typical content looks like::

        /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib

        /usr/sap/RH1/SYS/exe/uc/linuxx86_64:/usr/sap/RH1/SYS/exe/run

    Examples:
        >>> len(ld_lib_path)
        3
        >>> isinstance(ld_lib_path[0].path, list)
        True
        >>> len(ld_lib_path[0].path)
        3
        >>> '/sapdb/clients/RH1/lib' in ld_lib_path[0].path
        True
        >>> '' in ld_lib_path[1].path  # The empty value is kept.
        True

    Raises:
        SkipException: When the output is empty or nothing needs to parse.
    """

    def parse_content(self, content):
        if not content:
            raise SkipException

        llds = []
        for line in content:
            raw = line
            if line and line[0] == line[-1] and line[0] in ('\'', '"'):
                line = line[1:-1]
            llds.append(LdLibraryPathU(line.split(':'), raw))

        if not llds:
            raise SkipException("LD_LIBRARY_PATH not set.")

        self.extend(llds)


# Deprecated
LdLibraryPath = namedtuple('LdLibraryPath', ('pid', 'path', 'raw'))
"""namedtuple: Type for storing the LdLibraryPath of PID"""


class PidLdLibraryPath(Parser, list):
    """
    .. warning::

        This Parser is deprecated please use the :py:class:`UserLdLibraryPath`
        instead.

    Base class for parsing the ``LD_LIBRARY_PATH`` variable of each regular
    user of the system into a list.

    Typical content looks like::

        /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib
        /usr/sap/RH1/SYS/exe/uc/linuxx86_64:/usr/sap/RH1/SYS/exe/run

    Raises:
        SkipException: When the output is empty or nothing needs to parse.
        ParseException: When the line cannot be parsed.

    """
    def __init__(self, *args, **kwargs):
        deprecated(PidLdLibraryPath, "Please use the UserLdLibraryPath.")
        super(PidLdLibraryPath, self).__init__(*args, **kwargs)

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
