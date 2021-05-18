"""
LdLibraryPath - LD_LIBRARY_PATH of Users
========================================

Parser for parsing the environment variable LD_LIBRARY_PATH of each user

"""

from collections import namedtuple
from insights import parser, Parser
from insights.parsers import SkipException
from insights.specs import Specs

LdLibraryPath = namedtuple('LdLibraryPath', ('user', 'path', 'raw'))
"""namedtuple: Type for storing the LD_LIBRARY_PATH of users"""


@parser(Specs.ld_library_path_of_user)
class UserLdLibraryPath(Parser, list):
    """
    Base class for parsing the ``LD_LIBRARY_PATH`` variable of each regular
    user of the system into a list.

    .. note::

        Currently, only the LD_LIBRARY_PATH SAP users is collected, where the
        username is merged by SID and "adm".

    Typical content looks like::

        sr1adm /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib
        sr2adm
        rh1adm /usr/sap/RH1/SYS/exe/uc/linuxx86_64:/usr/sap/RH1/SYS/exe/run

    Examples:
        >>> len(ld_lib_path)
        3
        >>> isinstance(ld_lib_path[0].path, list)
        True
        >>> len(ld_lib_path[0].path)
        3
        >>> '/sapdb/clients/RH1/lib' in ld_lib_path[0].path
        True
        >>> ld_lib_path[1].user  # The empty value is kept.
        'sr2adm'
        >>> '' in ld_lib_path[1].path  # The empty value is kept.
        True

    Raises:
        SkipException: When the output is empty or nothing needs to parse.
    """

    def parse_content(self, content):
        llds = []
        for line in content:
            user, _, raw = [s.strip() for s in line.partition(' ')]
            paths = raw
            if raw and raw[0] == raw[-1] and raw[0] in ('\'', '"'):
                paths = raw[1:-1]
            llds.append(LdLibraryPath(user, paths.split(':'), raw))

        if not llds:
            raise SkipException("LD_LIBRARY_PATH not set.")

        self.extend(llds)
