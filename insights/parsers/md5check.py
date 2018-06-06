"""
MD5CheckSum - md5 checksums of specified binary or library files
================================================================

Module for processing output of the ``prelink -y --md5`` or ``md5sum`` command.

The name and md5 checksums of specified files are stored as lists. Each
entry will be processed by the shared parser.

This MD5CheckSum class provide the following properties:

* ``filename``: the file name which derived from the output.
* ``md5sum``: the checksums for the file.
"""
from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.prelink_orig_md5)
class MD5CheckSum(CommandParser):
    """
    Class to parse ``prelink -y --md5`` or ``md5sum`` command information.

    The output of these two commands contains two fields, the first is the
    md5 checksum and the second is the file name.

    Especially, we add /dev/null as one of the specified file to be checked,
    as ``md5sum`` command can read from stdin without feeding a file.

    Attributes::

        filename (str): File name.
        md5sum (str): MD5 checksums of that file.

    Sample input for ``prelink -y --md5`` or ``md5sum`` command::

        d1e6613cfb62d3f111db7bdda39ac821  /usr/lib64/libsoftokn3.so

    Examples::

        >>> collection = shared[MD5CheckSum]
        >>> len(collection) # All MD5 checksums in a list
        1
        >>> record = collection[0]
        >>> record.filename
        /usr/lib64/libsoftokn3.so
        >>> record.md5sum
        d1e6613cfb62d3f111db7bdda39ac821

    """
    @property
    def filename(self):
        """ str: Return the file name for the current file."""
        return self.data.get('filename')

    @property
    def md5sum(self):
        """ str: Return the checksum for the current file."""
        return self.data.get('md5sum')

    def parse_content(self, content):
        self.data = {}
        fields = content[0].strip().split() if content else None
        # skip the '/dev/null'
        if fields and len(fields) == 2 and fields[1] != "/dev/null":
            self.data["md5sum"] = fields[0]
            self.data["filename"] = fields[1]
