"""
MD5CheckSum - md5 checksums of specified binary or library files
================================================================

Module for processing output of the ``prelink -y --md5`` or ``md5sum`` command.

The name and md5 checksums of specified files are stored as lists. Each
entry will be processed by the shared parser.
"""

from .. import parser, CommandParser, LegacyItemAccess
from ..parsers import ParseException
from ..specs import Specs


class MD5CheckSum(LegacyItemAccess, CommandParser):
    """
    Common class to parse ``prelink -y --md5`` or ``md5sum`` command information.

    The output of these two commands contains two fields, the first is the
    md5 checksum and the second is the file name.

    Especially, we add /dev/null as one of the specified file to be checked,
    as ``md5sum`` command can read from stdin without feeding a file.

    Sample input for ``prelink -y --md5`` or ``md5sum`` command::

        d1e6613cfb62d3f111db7bdda39ac821  /usr/lib64/libsoftokn3.so

    Examples:

        >>> type(md5info)
        <class 'insights.parsers.md5check.MD5CheckSum'>
        >>> len(md5info.files)
        1
        >>> "/usr/lib64/libsoftokn3.so" in md5info.files
        True
        >>> md5info['/usr/lib64/libsoftokn3.so']
        'd1e6613cfb62d3f111db7bdda39ac821'

    Attributes:
        data (dict): All MD5 checksums are stored in this dictionary with the
                     filename as the key and the checksum as the value.
        files (list): Return the all file names in the checksum results.
    """

    def parse_content(self, content):
        if not content:
            raise ParseException("Input content is empty.")
        self.data = {}
        self.files = []
        for line in content:
            md5sum, filename = line.strip().split(' ', 1)
            md5sum, filename = md5sum.strip(), filename.strip()
            # skip the '/dev/null'
            if len(md5sum) == 32 and filename != "/dev/null":
                self.data[filename] = md5sum
        if self.data:
            self.files = self.data.keys()


@parser(Specs.prelink_orig_md5)
class PrelinkMD5(MD5CheckSum):
    """
    A parser for parsing the output of the ``prelink -y --md5``
    """
    pass


@parser(Specs.md5chk_files)
class NormalMD5(MD5CheckSum):
    """
    A parser for parsing the output of the ``md5sum``
    """
    pass
