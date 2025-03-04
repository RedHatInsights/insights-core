"""
Number of files from dirs
=========================

Parses the output of files number from dirs.
"""
from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.files_number)
class FilesNumberOfDir(JSONParser):
    """
    Get the files number from dirs..

    Attributes:
        data (dict): Files number.

    Sample output of this command is::

        {
          "/var/spool/postfix/maildrop/": 5,
          "/var/spool/clientmqueue/": 7,
        }

    Examples:
        >>> type(filesnumberofdir)
        <class 'insights.parsers.files_number_of_dir.FilesNumberOfDir'>
        >>> filesnumberofdir.data["/var/spool/postfix/maildrop/"]
        5
    """
    pass
