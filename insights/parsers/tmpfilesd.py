"""
Tmpfiles.d configuration - files  in ``/etc/tmpfiles.d``
========================================================

The ``TmpfilesD`` class parser provides a 'rules' list, as well as a
``find_file`` method to find rules for a particular tmp file.
"""

from .. import Parser, parser, get_active_lines
from ..specs import Specs


@parser(Specs.tmpfilesd)
class TmpFilesD(Parser):
    """
    Parse files in /etc/tmpfiles.d, /usr/lib/tmpfiles.d/, and /run/tmpfiles.d.

    This parser reads the files and records the filename in each line.

    Attributes:
        files(list): A list of the files that tmpfiles.d is managing.
        rules(list): A list of dictionaries with the values of each rule.

    Sample input::

        # /usr/lib/tmpfiles.d/dnf.conf
        r! /var/cache/dnf/*/*/download_lock.pid
        e  /var/cache/dnf/ - - - 30d

    Examples:

        >>> tmpfiles = shared[TmpFilesd][0] # List is per filename
        >>> len(tmpfiles.rules)
        2
        >>> tmpfiles.files
        ['/var/cache/dnf/*/*/download_lock.pid', '/var/cache/dnf/']
        >>> tmpfiles.rules[1]
        {'path': '/var/cache/dnf/', 'type': 'e', 'mode': '-', 'age': '30d',
         'gid': '-', 'uid': '-', 'argument': None}
        >>> tmpfiles.find_file('download_lock.pid')
        [{'path': '/var/cache/dnf/*/*/download_lock.pid', 'type': 'r!',
          'mode': None, 'age': None, 'gid': None, 'uid': None, 'argument': None}]
    """

    def parse_content(self, content):
        self.files = []
        self.rules = []
        for line in get_active_lines(content):
            linelist = line.split()
            keys = ['type', 'path', 'mode', 'uid', 'gid', 'age', 'argument']
            d = dict(zip(keys, linelist))

            # each key should be available  even if the tmpfile does not contain
            # a value for that key
            [d.update({key: d.get(key)}) for key in keys]

            self.rules.append(d)

        for i in self.rules:
            self.files.append(i['path'])

    def find_file(self, filename):
        """
        Find any rules containing the file being searched.

        This method returns a list of dictionaries where the the managed file is
        found.
        """

        matched = []

        for rule in self.rules:
            if filename.split('/')[-1] in rule['path'].split('/'):
                matched.append(rule)

        return matched
