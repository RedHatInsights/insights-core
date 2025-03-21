"""
Number of files or dirs from dirs
=================================

Parses the output of files or dirs number from dirs.
"""

import os

from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.files_dirs_number)
class FilesDirsNumberOfDir(JSONParser):
    """
    Get the files and dirs number from dirs.

    Sample output of this command is::

        {
          "/var/spool/postfix/maildrop/": {"dirs_number": 1, "files_number": 5},
          "/var/spool/clientmqueue/": {"dirs_number": 1, "files_number": 2},
        }

    Examples:
        >>> type(filesnumberofdir)
        <class 'insights.parsers.files_dirs_number_of_dirs.FilesDirsNumberOfDir'>
        >>> filesnumberofdir.files_number_of("/var/spool/postfix/maildrop")
        5
        >>> filesnumberofdir.dirs_number_of("/var/spool/clientmqueue/")
        1
    """

    def dirs_number_of(self, _dir):
        """Return the number of dirs under specified `_dir`, None when no such `_dir`"""
        _dir = os.path.join(_dir, '')  # ensure endswith '/'
        if _dir in self.data:
            return self.data[_dir]["dirs_number"]

    def files_number_of(self, _dir):
        """Return the number of files under specified `_dir`, None when no such `_dir`"""
        _dir = os.path.join(_dir, '')  # ensure endswith '/'
        if _dir in self.data:
            return self.data[_dir]["files_number"]
