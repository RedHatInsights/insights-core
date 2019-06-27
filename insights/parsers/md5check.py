"""
NormalMD5 - md5 checksums of specified binary or library files
==============================================================

Module for processing output of the ``md5sum`` command.

The name and md5 checksums of the specified file are stored as attributes.
"""

from .. import parser, CommandParser
from ..parsers import ParseException
from ..specs import Specs


@parser(Specs.md5chk_files)
class NormalMD5(CommandParser):
    """
    Class to parse the ``md5sum`` command information.

    The output of this command contains two fields, the first is the
    md5 checksum and the second is the file name.

    Sample output of the ``md5sum`` command::

        d1e6613cfb62d3f111db7bdda39ac821  /usr/lib64/libsoftokn3.so

    Examples:

        >>> type(md5info)
        <class 'insights.parsers.md5check.NormalMD5'>
        >>> md5info.filename
        '/etc/localtime'
        >>> md5info.md5sum
        '7d4855248419b8a3ce6616bbc0e58301'

    Attributes:
        filename (str): Filename for which the MD5 checksum was computed.
        md5sum (str): MD5 checksum value.
    """

    def parse_content(self, content):
        if len(content) != 1:
            raise ParseException("Incorrect length for input {length}.".format(length=len(content)))
        for line in content:
            self.md5sum, self.filename = content[-1].strip().split(None, 1)
            if len(self.md5sum) != 32:
                raise ParseException("Invalid MD5sum value {length}.".format(length=self.md5sum))
