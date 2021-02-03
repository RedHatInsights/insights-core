"""
GFS2FileSystemBlockSize - command ``stat -fc %s <mount_point_path>``
====================================================================

The parser parse the output of ``stat -fc %s <mount_point_path>``
"""

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.gfs2_file_system_block_size)
class GFS2FileSystemBlockSize(CommandParser):
    """
    Class for parsing ``stat -fc %s <mount_point_path>`` command output.
    The size is kept in the ``block_size`` property.
    Typical output of command ``stat -fc %s <mount_point_path>`` looks like::

        4096

    Examples::

        >>> type(gfs2_mp)
        <class 'insights.parsers.gfs2_file_system_block_size.GFS2FileSystemBlockSize'>
        >>> gfs2_mp.block_size
        4096

    Raise::

        SkipException: When the content isn't in the expected format.

    Attributes::

        block_size (int): The block size of the gfs2 file system.
    """

    def parse_content(self, content):
        if len(content) == 1 and content[0].isdigit():
            self.block_size = int(content[0])
        else:
            raise SkipException('The output is invalid.')
