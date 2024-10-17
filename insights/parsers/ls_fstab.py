"""
LsBoot - command ``ls -lanR /boot`` or ``ls -alZR /boot``
=========================================================

The ``ls -lanR /boot`` or ``ls -alZR /boot`` command provides information for the listing of the
``/boot`` directory.

See :class:`insights.parsers.ls.FileListing` for more information.

"""

from insights.core import Parser, ls_parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ls_fstab)
class LSladFSTab(Parser):
    """
    Parses output of ``ls -lad <mounts point in fstab>`` command.
    The list of mount points in fstab is return from datasource mount.fstab_mount_points.
    See :py:class:`FileListing` for more information.

    Sample directory listing::
        ls: cannot access 'swap': No such file or directory
        dr-xr-xr-x. 21 root root 4096 Oct 15 08:19 /
        drwxr-xr-x.  2 root root    6 Nov  9  2021 /boot


    Examples:
        >>> type(ls_fstab)
        <class 'insights.parsers.ls_fstab.LSladFSTab'>
        >>> '/' in ls_fstab.entries
        True
        >>> ls_fstab.entries.get('/').get('owner')
        'root'
        >>> ls_fstab.entries.get('/boot')
        {'type': 'd', 'perms': 'rwxr-xr-x.', 'links': 2, 'owner': 'root', 'group': 'root', 'size': 6, 'date': 'Nov  9  2021', 'name': '/boot', 'raw_entry': 'drwxr-xr-x.  2 root root    6 Nov  9  2021 /boot', 'dir': ''}
    """

    def parse_content(self, content):
        parsed_content = []
        for line in content:
            if 'No such file or directory' not in line:
                parsed_content.append(line)
        if not parsed_content:
            raise ParseException('Error: {0}', content)
        ls_data = ls_parser.parse(parsed_content, '').get('')
        self.entries = ls_data.get('entries')
