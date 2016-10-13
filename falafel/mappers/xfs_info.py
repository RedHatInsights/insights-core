from .. import Mapper, mapper
import re

@mapper('xfs_info')
class XFSInfo(Mapper):

    info_re = re.compile(r'^(?P<section>[\w-]+)?\s*' +
        r'=(?:(?P<specifier>\S+)(?:\s(?P<specval>\w+))?)?\s+' +
        r'(?P<keyvaldata>\w.*\w)$'
    )
    keyval_re = re.compile(r'(?P<key>[\w-]+)=(?P<value>\d+(?: blks)?)')

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

        xfs_info = {}
        sect_info = None

        for line in content:
            match = self.info_re.search(line)
            if match:
                if match.group('section'):
                    # Change of section - make new sect_info dict and link
                    sect_info = {}
                    xfs_info[match.group('section')] = sect_info
                if match.group('specifier'):
                    sect_info['specifier'] = match.group('specifier')
                    if match.group('specval'):
                        sect_info['specifier value'] = match.group('specval')
                for pair in self.keyval_re.findall(match.group('keyvaldata')):
                    (key, value) = pair
                    if value[-1] != 's':
                        # Value doesn't end with 'blks', so convert it to int.
                        value = int(value)
                    sect_info[key] = value
#            else:
#                print "Warning: didn't match line regex"

        self.xfs_info = xfs_info

        # Calculate a few things
        self.data_size = xfs_info['data']['blocks'] * xfs_info['data']['bsize']
        self.log_size = xfs_info['log']['blocks'] * xfs_info['log']['bsize']

    def __repr__(self):
        return 'xfs_info of ' + self.xfs_info['meta-data']['specifier']\
         + ' with sections [' + ', '.join(self.xfs_info.keys()) + ']'
