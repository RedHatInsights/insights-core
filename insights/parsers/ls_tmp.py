"""
LsTmp - command ``ls -ld /tmp``
===============================

The ``ls -l /tmp`` command provides information for only the ``/tmp`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    drwxrwxrwt. 8 root root 160 Apr 16 12:37 /tmp

Examples:

    >>> ls_tmp.listing_of("/dummy-sysroot")['tmp']
    {'group': 'root', 'name': 'tmp', 'links': 8, 'perms': 'rwxrwxrwt.', 'raw_entry': 'drwxrwxrwt. 8 root root 160 Apr 16 12:37 tmp', 'owner': 'root', 'date': 'Apr 16 12:37', 'type': 'd', 'dir': '/dummy-sysroot', 'size': 160}
    >>> ls_tmp.dir_entry("/dummy-sysroot", 'tmp')['perms']
    'rwxrwxrwt.'
"""


from insights.specs import Specs

from .. import FileListing
from .. import parser


@parser(Specs.ls_tmp)
class LsTmp(FileListing):
    """Parses output of ``ls -ld /tmp`` command."""
    def parse_content(self, content):
        """
        Reformat the one line output of ``ls -d /tmp``.
        Make the one line output be correctly handled by ``FileListing`` class

        Sample origin output::

            drwxrwxrwt. 8 root root 160 Apr 16 12:37 /tmp

        After reformat::

            /dummy-sysroot:
            drwxrwxrwt. 8 root root 160 Apr 16 12:37 tmp

        """
        if len(content) > 0 and not (content[0].startswith('/') and content[0].endswith(':')):
            # for the output "drwxrwxrwt. 8 root root 160 Apr 16 12:37 /tmp", the '/tmp' should be replaced by 'tmp', or it will not pass the FileListing check
            # for ls -ld /tmp, can not analysis the raw_list without line "/dir:", so append "dummy-sysroot" at head
            content[0] = content[0].replace('/tmp', 'tmp')
            content.insert(0, '/dummy-sysroot:')
        super(LsTmp, self).parse_content(content)
