"""
LdLibraryPath - LD_LIBRARY_PATH of users
========================================

Parser for parsing the environment variable LD_LIBRARY_PATH of the regular
users of the system.

"""

from insights import Parser, parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.ld_library_path)
class LdLibraryPath(Parser, list):
    """
    Base class for parsing the ``LD_LIBRARY_PATH`` variable of each regular
    user of the system into a list.

    Typical content looks like::

        /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib

    Examples:
        >>> len(ld_lib_path)
        3
        >>> '/sapdb/clients/RH1/lib' in ld_lib_path
        True
        >>> ld_lib_path.user
        'sr2adm'

    Raises:
        SkipException: When the output is empty or nothing needs to parse.

    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty output.")

        paths = None
        for line in content:
            if line.startswith('/'):
                paths = line.split(':')

        if not paths:
            raise SkipException("LD_LIBRARY_PATH not set.")

        self.extend(paths)
        self.user = self.file_name.split('_')[2]
