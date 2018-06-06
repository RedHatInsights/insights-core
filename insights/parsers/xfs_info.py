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
    xfs_info(dict): A dictionary of dictionaries containing the data from
        the report, keyed on the five section names in the output:
        '``meta-data``', '``data``', '``naming``', '``log``', and
        '``realtime``'.  '``meta-data``', '``data``' and '``log``' are
        always present.  Within each dictionary a special key
        '``specifier``' stores any data immediately after the section
        name - e.g. '/dev/sda' or 'version' in the case of the output
        below.  Any data immediately following that is stored in the
        ``specifier_value`` key.  Otherwise, data is read in key=value
        pairs - e.g. from the output below, the ``isize`` key will have
        the value ``32`` (an integer).  Data values given in blocks are
        left as is, so the value of the ``agsize`` key is '16777184 blks'
        as a string.
    mount(str): If the mount point can be derived from the file name of
        the original output, then this attribute contains the
        reconstructed mount point name.
    device(str): The device name immediately after the '``meta-data``'
        section heading.
    data_size(int): The size of the data segment in bytes, from
        multiplying the ``blocks`` and ``bsize`` values of the ``data``
        section together.
    log_size(int): The size of the log segment in bytes, from multiplying
        the ``blocks`` and ``bsize`` values of the ``log`` section
        together.

Sample output (from file '``sos_commands/xfs/xfs_info_.data``')::

     meta-data=/dev/sda      isize=256    agcount=32, agsize=16777184 blks
              =              sectsz=512   attr=2
     data     =              bsize=4096   blocks=536869888, imaxpct=5
              =              sunit=32     swidth=128 blks
     naming   =version 2     bsize=4096
     log      =internal      bsize=4096   blocks=32768, version=2
              =              sectsz=512   sunit=32 blks, lazy-count=1
     realtime =none          extsz=524288 blocks=0, rtextents=0

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
from .. import parser, CommandParser
from insights.parsers import ParseException
import re
from insights.specs import Specs


@parser(Specs.xfs_info)
class XFSInfo(CommandParser):
    """
    This mapper reads the output of the ``xfs_info`` command.

    As this spec can collect more than one file, the mapper will return a
    list of XFSInfo objects, which need to be iterated through to find the
    information on the mount point or device you need.

    """

    def __init__(self, context):
        self.xfs_info = {}
        self.device = ''
        self.data_size = 0
        self.log_size = 0
        self.mount = ''

        # Determine mount from file name if possible:
        mount_name_re = re.compile('xfs_info_(?P<mount>.*)')
        match = mount_name_re.search(context.path)
        if match:
            # Try to put slashes back...
            self.mount = match.group('mount').replace('.', '/')

        super(XFSInfo, self).__init__(context)

    def parse_content(self, content):
        """
        In general the pattern is::

            section =sectionkey key1=value1 key2=value2, key3=value3
                    = key4=value4
            nextsec =sectionkey sectionvalue  key=value otherkey=othervalue

        Sections are continued over lines as per RFC822.  The first equals
        sign is column-aligned, and the first key=value is too, but the
        rest seems to be comma separated.  Specifiers come after the first
        equals sign, and sometimes have a value property, but sometimes not.
        """

        info_re = re.compile(r'^(?P<section>[\w-]+)?\s*' +
                             r'=(?:(?P<specifier>\S+)(?:\s(?P<specval>\w+))?)?' +
                             r'\s+(?P<keyvaldata>\w.*\w)$'
                             )
        keyval_re = re.compile(r'(?P<key>[\w-]+)=(?P<value>\d+(?: blks)?)')

        sect_info = None

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
                for key, value in keyval_re.findall(match.group('keyvaldata')):
                    if value.isdigit():
                        # Convert numeric values to integers as a convenience
                        value = int(value)
                    sect_info[key] = value

        # Check that the meta-data and data sections are there and contain
        # the things we expect
        if 'meta-data' not in self.xfs_info:
            raise ParseException("No 'meta-data' section found")
        if 'specifier' not in self.xfs_info['meta-data']:
            raise ParseException("Device specifier not found in meta-data")
        if 'data' not in self.xfs_info:
            raise ParseException("No 'data' section found")
        if 'blocks' not in self.xfs_info['data']:
            raise ParseException("'blocks' not defined in data section")
        if 'bsize' not in self.xfs_info['data']:
            raise ParseException("'bsize' not defined in data section")
        if 'log' not in self.xfs_info:
            raise ParseException("No 'log' section found")
        if 'blocks' not in self.xfs_info['log']:
            raise ParseException("'blocks' not defined in log section")
        if 'bsize' not in self.xfs_info['log']:
            raise ParseException("'bsize' not defined in log section")

        # Store a few handy properties
        self.device = self.xfs_info['meta-data']['specifier']

        # Calculate a few things
        self.data_size = self.xfs_info['data']['blocks'] * self.xfs_info['data']['bsize']
        self.log_size = self.xfs_info['log']['blocks'] * self.xfs_info['log']['bsize']

    def __str__(self):
        return 'xfs_info of ' + self.xfs_info['meta-data']['specifier']
