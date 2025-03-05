"""
Number of files or dirs from dirs
=================================

Parses the output of files or dirs number from dirs.
"""
from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.files_dirs_number)
class FilesDirsNumberOfDir(JSONParser):
    """
    Get the files number from dirs..

    Attributes:
        data (dict): Files number.

    Sample output of this command is::

        {
          "/var/spool/postfix/maildrop/": {"dirs_number": 1, "files_number": 5},
          "/var/spool/clientmqueue/": {"dirs_number": 1, "files_number": 2},
        }

    Examples:
        >>> type(filesnumberofdir)
        <class 'insights.parsers.files_dirs_number_of_dirs.FilesDirsNumberOfDir'>
        >>> filesnumberofdir.data["/var/spool/postfix/maildrop/"]["files_number"]
        5
    """
    pass
