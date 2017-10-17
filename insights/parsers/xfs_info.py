"""
XFSInfo - command ``/usr/sbin/xfs_info {mount}``
================================================

The ``XFSInfo`` parser reads the output of the ``xfs_info`` command and turns
it into a dictionary of keys and values in several sections, as given in the
output of the command::

     meta-data=/dev/sda      isize=256    agcount=32, agsize=16777184 blks
              =              sectsz=512   attr=2
     data     =              bsize=4096   blocks=536869888, imaxpct=5
              =              sunit=32     swidth=128 blks
     naming   =version 2     bsize=4096
     log      =internal      bsize=4096   blocks=32768, version=2
              =              sectsz=512   sunit=32 blks, lazy-count=1
     realtime =none          extsz=524288 blocks=0, rtextents=0

The main sections are ``meta-data``, ``data``, ``naming``, ``log`` and
``realtime``, stored under those keys in the object's ``xfs_info`` property.
Each section can optionally have a '**specifier**', which is the first thing
after the section name (e.g. ``version`` or ``/dev/sda``).  If no specifier
is found on the line, none is recorded for the section.  The specifier can
also have a value (e.g. ``2`` for the version), which is recorded in the
``specifier_value`` key in the section.

Each 'key=value' pair until the next given section start (or end of file), is
recorded as an entry in the section dictionary, with all values that are
numeric being converted to integers (i.e. usually anything without a '`blks`'
suffix).

Because the spec for this parser can collect multiple files, the shared
parser information contains a list of XFSInfo objects, one per file system.

In addition, the ``data_size`` and ``log_size`` values are calculated as
properties from the block size and blocks in the data and log, respectively.

Attributes:

    xfs_info (dict): The sections of data in the ``xfs_info`` output.
    data_size (int): The size of the data section in bytes.
    log_size (int): The size of the log section in bytes.

Examples:

    >>> xfs = shared[XFSInfo][0]  # first XFS filesystem as an example
    >>> xfs.xfs_info['meta-data']['specifier']
    '/dev/sda'
    >>> 'specifier_value' in xfs.xfs_info['meta-data']
    False
    >>> xfs.xfs_info['meta-data']['agcount']
    32
    >>> xfs.xfs_info['meta-data']['agsize']
    '16777184 blks'
    >>> xfs.data_size
    2199019061248
    >>> 'crc' in xfs.xfs_info['data']
    False

"""
from .. import Parser, parser
import re


@parser('xfs_info')
class XFSInfo(Parser):

    def __init__(self, context):
        self.xfs_info = {}
        self.data_size = 0
        self.log_size = 0
        super(XFSInfo, self).__init__(context)

    def parse_content(self, content):
        """
        In general the pattern is:
        section = key1=value1 key2=value2, key3=value3
                = key4=value4
        nextsec =sectionkey sectionvalue  key=value otherkey=othervalue
        Sections are continued over lines as per RFC822.  The first equals
        sign is column-aligned, and the first key=value is too, but the
        rest seems to be comma separated.  Specifiers come after the first
        equals sign, and sometimes have a value property, but sometimes not.
        E.g.:

         meta-data=/dev/sda      isize=256    agcount=32, agsize=16777184 blks
                  =              sectsz=512   attr=2
         data     =              bsize=4096   blocks=536869888, imaxpct=5
                  =              sunit=32     swidth=128 blks
         naming   =version 2     bsize=4096
         log      =internal      bsize=4096   blocks=32768, version=2
                  =              sectsz=512   sunit=32 blks, lazy-count=1
         realtime =none          extsz=524288 blocks=0, rtextents=0
        """

        sect_info = None

        info_re = re.compile(r'^(?P<section>[\w-]+)?\s*' +
                             r'=(?:(?P<specifier>\S+)(?:\s(?P<specval>\w+))?)?' +
                             r'\s+(?P<keyvaldata>\w.*\w)$')
        keyval_re = re.compile(r'(?P<key>[\w-]+)=(?P<value>\d+(?: blks)?)')

        for line in content:
            match = info_re.search(line)
            if match:
                if match.group('section'):
                    # Change of section - make new sect_info dict and link
                    sect_info = {}
                    self.xfs_info[match.group('section')] = sect_info
                if match.group('specifier'):
                    sect_info['specifier'] = match.group('specifier')
                    if match.group('specval'):
                        sect_info['specifier_value'] = match.group('specval')
                for pair in keyval_re.findall(match.group('keyvaldata')):
                    (key, value) = pair
                    if value.isdigit():
                        # Convert numeric values to integers as a convenience
                        value = int(value)
                    sect_info[key] = value

        # Calculate a few things
        if 'data' in self.xfs_info:
            self.data_size = self.xfs_info['data']['blocks'] * self.xfs_info['data']['bsize']
        if 'log' in self.xfs_info:
            self.log_size = self.xfs_info['log']['blocks'] * self.xfs_info['log']['bsize']

    def __str__(self):
        return 'xfs_info of ' + self.xfs_info['meta-data']['specifier']\
            + ' with sections [' + ', '.join(sorted(self.xfs_info.keys())) + ']'
