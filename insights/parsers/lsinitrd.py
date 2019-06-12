"""
LSINITRD - command ``lsinitrd``
===============================

This parser parses the filtered output of command ``lsinitrd`` and provides the
info of listed files.
"""

from insights import parser, CommandParser
from insights.core.ls_parser import Directory
from insights.specs import Specs
from insights.parsers import keyword_search


@parser(Specs.lsinitrd)
class LSINITRD(CommandParser):
    """
    A parser for command "lsinitrd".

    Attributes:
        data (dict): The key is the filename, the value is a dict describe
            the file's info.
        unparsed_lines(list): List of strings for unparsed lines.

    As this lsinitrd spec is set to filterable, the structure of the output
    is broken. Hence, this parser will parse only filelisting like lines in
    output of 'lisinitrd', and also store all the unparsed lines.
    If the other parts of the output structure are required in the future,
    an enhancement may be performed then.

    Examples:
        >>> len(ls.data)
        5
        >>> ls.search(name__contains='kernel')
        [{'type': 'd', 'perms': 'rwxr-xr-x', 'links': 3, 'owner': 'root', 'group': 'root', 'size': 0, 'date': 'Apr 20 15:58', 'name': 'kernel/x86', 'raw_entry': 'drwxr-xr-x   3 root     root            0 Apr 20 15:58 kernel/x86', 'dir': ''}]
        >>> "udev-rules" in ls.unparsed_lines
        True
    """

    def parse_content(self, content):
        file_types = set(['s', 'd', 'p', 'l', '-', 'c', 'b'])
        perm = set(['-w-', 'rw-', '--x', '-wx', '---', 'rwx', 'r--', 'r-x'])
        entries = []
        _unparsed_lines = []

        for l in content:
            if l and l[0] in file_types and l[1:4] in perm:
                entries.append(l)
            else:
                _unparsed_lines.append(l)

        d = Directory("", len(entries), entries)
        d._load()  # call _load() directly to parse the content

        self.data = d['entries']
        self.unparsed_lines = _unparsed_lines

    def search(self, **kwargs):
        """
        Search the listed files for matching rows based on key-value pairs.

        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details.  If no search
        parameters are given, no rows are returned.

        Returns:
            list: A list of dictionaries of files that match the given
            search criteria.

        Examples:
            >>> ls.search(name__contains='dev') == [
            ...    {'type': 'c', 'perms': 'rw-r--r--', 'links': 1, 'owner': 'root', 'group': 'root',
            ...     'major': 5, 'minor': 1, 'date': 'Apr 20 15:57', 'name': 'dev/console', 'dir': '',
            ...     'raw_entry': 'crw-r--r--   1 root     root       5,   1 Apr 20 15:57 dev/console'},
            ...    {'type': 'c', 'perms': 'rw-r--r--', 'links': 1, 'owner': 'root', 'group': 'root',
            ...     'major': 1, 'minor': 11, 'date': 'Apr 20 15:57', 'name': 'dev/kmsg', 'dir': '',
            ...     'raw_entry': 'crw-r--r--   1 root     root       1,  11 Apr 20 15:57 dev/kmsg'},
            ...    {'type': 'c', 'perms': 'rw-r--r--', 'links': 1, 'owner': 'root', 'group': 'root',
            ...     'major': 1, 'minor': 3, 'date': 'Apr 20 15:57', 'name': 'dev/null', 'dir': '',
            ...     'raw_entry': 'crw-r--r--   1 root     root       1,   3 Apr 20 15:57 dev/null'}
            ... ]
            True

        """
        return keyword_search(self.data.values(), **kwargs)
