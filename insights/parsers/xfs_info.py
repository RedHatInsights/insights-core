"""
XFSInfo - command ``/usr/sbin/xfs_info``
========================================

This mapper reads the output of the ``xfs_info`` command.

"""

from .. import Parser, parser
from insights.parsers import ParseException
import re


@parser('xfs_info')
class XFSInfo(Parser):
    """
    This mapper reads the output of the ``xfs_info`` command.

    As this spec can collect more than one file, the mapper will return a
    list of XFSInfo objects, which need to be iterated through to find the
    information on the mount point or device you need.

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
        >>> xfs_list = shared[XFSInfo] # A list of devices
        >>> for xfs in xfs_list:
        ...     print 'Mount {mnt} -> {dev}: {blks} blocks, {bytes} bytes'.format(
        ...         mnt=xfs.mount, dev=xfs.device,
        ...         blks=xfs.xfs_info['data']['blocks'], bytes=xfs.data_size
        ...     )
        Mount /data -> /dev/sda: 536869888 blocks, 2199019061248 bytes
        >>> data = xfs_list[0].xfs_info  # Direct access to data dictionary
        >>> data['meta-data']['specifier']
        '/dev/sda'
        >>> data['meta-data']['agsize']  # blocks values not parsed
        '16777184 blks'
        >>> data['realtime']['rtextents']
        0
    """

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
        E.g.::

             meta-data=/dev/sda      isize=256    agcount=32, agsize=16777184 blks
                      =              sectsz=512   attr=2
             data     =              bsize=4096   blocks=536869888, imaxpct=5
                      =              sunit=32     swidth=128 blks
             naming   =version 2     bsize=4096
             log      =internal      bsize=4096   blocks=32768, version=2
                      =              sectsz=512   sunit=32 blks, lazy-count=1
             realtime =none          extsz=524288 blocks=0, rtextents=0
        """

        info_re = re.compile(r'^(?P<section>[\w-]+)?\s*' +
                             r'=(?:(?P<specifier>\S+)(?:\s(?P<specval>\w+))?)?' +
                             r'\s+(?P<keyvaldata>\w.*\w)$'
                             )
        keyval_re = re.compile(r'(?P<key>[\w-]+)=(?P<value>\d+(?: blks)?)')

        xfs_info = {}
        sect_info = None
        self.mount = ''

        for line in content:
            match = info_re.search(line)
            if match:
                if match.group('section'):
                    # Change of section - make new sect_info dict and link
                    sect_info = {}
                    xfs_info[match.group('section')] = sect_info
                if match.group('specifier'):
                    sect_info['specifier'] = match.group('specifier')
                    if match.group('specval'):
                        sect_info['specifier_value'] = match.group('specval')
                for key, value in keyval_re.findall(match.group('keyvaldata')):
                    if value[-1] != 's':
                        # Value doesn't end with 'blks', so convert it to int.
                        value = int(value)
                    sect_info[key] = value

        self.xfs_info = xfs_info

        # Check that the meta-data and data sections are there and contain
        # the things we expect
        if 'meta-data' not in xfs_info:
            raise ParseException("No 'meta-data' section found")
        if 'specifier' not in xfs_info['meta-data']:
            raise ParseException("Device specifier not found in meta-data")
        if 'data' not in xfs_info:
            raise ParseException("No 'data' section found")
        if 'blocks' not in xfs_info['data']:
            raise ParseException("'blocks' not defined in data section")
        if 'bsize' not in xfs_info['data']:
            raise ParseException("'bsize' not defined in data section")
        if 'log' not in xfs_info:
            raise ParseException("No 'log' section found")
        if 'blocks' not in xfs_info['log']:
            raise ParseException("'blocks' not defined in log section")
        if 'bsize' not in xfs_info['log']:
            raise ParseException("'bsize' not defined in log section")

        # Store a few handy properties
        self.device = xfs_info['meta-data']['specifier']

        # Calculate a few things
        self.data_size = xfs_info['data']['blocks'] * xfs_info['data']['bsize']
        self.log_size = xfs_info['log']['blocks'] * xfs_info['log']['bsize']

        # Determine mount from file name if possible:
        mount_name_re = re.compile('xfs_info_(?P<mount>.*)')
        match = mount_name_re.search(self.file_name)
        if match:
            # Try to put slashes back...
            self.mount = match.group('mount').replace('.', '/')

    def __repr__(self):
        return 'xfs_info of ' + self.xfs_info['meta-data']['specifier']
