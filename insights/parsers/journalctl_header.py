"""
JournalctlHeader - command ``"/usr/bin/journalctl --header"``
=============================================================

This command shows internal header information of the journal fields accessed.

Sample Output::

    File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system.journal
    File ID: b1390ea69aa747e9ac5c597835c3c562
    Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
    Boot ID: 082ada53f8184c4896c73101ad793eb5
    Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
    State: ONLINE
    Compatible Flags:
    Incompatible Flags: COMPRESSED-LZ4
    Header size: 240
    Arena size: 8388368
    Data Hash Table Size: 19904
    Field Hash Table Size: 333
    Rotate Suggested: no
    Head Sequential Number: 74388 (12294)
    Tail Sequential Number: 81647 (13eef)
    Head Realtime Timestamp: Mon 2022-08-15 12:01:10 CST (5e63fae9e6e58)
    Tail Realtime Timestamp: Wed 2022-08-17 18:38:48 CST (5e66d7852bb3e)
    Tail Monotonic Timestamp: 1month 2w 3d 14h 19min 3.733s (3c647d7ce0f)
    Objects: 19073
    Entry Objects: 7260
    Data Objects: 9297
    Data Hash Table Fill: 46.7%
    Field Objects: 52
    Field Hash Table Fill: 15.6%
    Tag Objects: 0
    Entry Array Objects: 2462
    Disk usage: 8.0M

Examples:

    >>> type(journalctl_header)
    <class 'insights.parsers.journalctl_header.JournalctlHeader'>
    >>> journalctl_header.data[0]['File Path']
    '/run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system.journal'
    >>> journalctl_header.data[0]['File ID']
    'b1390ea69aa747e9ac5c597835c3c562'

Attributes:
    data (dict): Dictionary containing each of the key:value pairs from the command output.

Raises:
    ParseException: raised if data is not parsable.
"""

from insights.core.plugins import parser
from insights.core import CommandParser, LegacyItemAccess
from insights.parsers import SkipException, get_active_lines
from insights.specs import Specs


@parser(Specs.journalctl_header)
class JournalctlHeader(LegacyItemAccess, CommandParser):

    def parse_content(self, content):

        self.data = []
        self.errors = []
        body = {}

        for line in get_active_lines(content):
            if ':' in line:
                key, value = [item.strip() for item in line.split(":", 1)]
                if key == 'File Path' and 'File Path' in body:
                    self.data.append(body)
                    body = {}
                if key == 'File Path' or 'File Path' in body:
                    body[key] = value
                else:
                    self.errors.append(line.strip())
            else:
                self.errors.append(line.strip())

        if body and not self.errors:
            self.data.append(body)

        if not self.data and not self.errors:
            raise SkipException("Unrecognised Output")
