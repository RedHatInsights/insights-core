from falafel.mappers import xfs_info
from falafel.tests import context_wrap

class TestXFSInfo():
    def test_example_xfs_info(self):
        xfs = xfs_info.XFSInfo(context_wrap("""
meta-data=/dev/sda      isize=256    agcount=32, agsize=16777184 blks
         =              sectsz=512   attr=2
data     =              bsize=4096   blocks=536869888, imaxpct=5
         =              sunit=32     swidth=128 blks
naming   =version 2     bsize=4096
log      =internal      bsize=4096   blocks=32768, version=2
         =              sectsz=512   sunit=32 blks, lazy-count=1
realtime =none          extsz=524288 blocks=0, rtextents=0
        """.strip())).xfs_info

        # Section checks
        assert 'meta-data' in xfs
        assert 'data' in xfs
        assert 'naming' in xfs
        assert 'log' in xfs
        assert 'realtime' in xfs

        # Section specifier checks
        assert xfs['meta-data']['specifier'] == '/dev/sda'
        assert xfs['naming']['specifier'] == 'version'
        assert xfs['naming']['specifier value'] == '2'
        assert xfs['log']['specifier'] == 'internal'
        assert xfs['realtime']['specifier'] == 'none'

        # Data checks
        assert xfs['meta-data']['isize'] == 256
        assert xfs['meta-data']['agcount'] == 32
        assert xfs['meta-data']['agsize'] == '16777184 blks'
        assert xfs['meta-data']['sectsz'] == 512
        assert xfs['meta-data']['attr'] == 2

        assert xfs['data']['bsize'] == 4096
        assert xfs['data']['blocks'] == 536869888
        assert xfs['data']['imaxpct'] == 5
        assert xfs['data']['sunit'] == 32
        assert xfs['data']['swidth'] == '128 blks'
        
        assert xfs['naming']['bsize'] == 4096

        assert xfs['log']['bsize'] == 4096
        assert xfs['log']['blocks'] == 32768
        assert xfs['log']['version'] == 2
        assert xfs['log']['sectsz'] == 512
        assert xfs['log']['sunit'] == '32 blks'
        assert xfs['log']['lazy-count'] == 1

        assert xfs['realtime']['extsz'] == 524288
        assert xfs['realtime']['blocks'] == 0
        assert xfs['realtime']['rtextents'] == 0

    def test_root_xfs_info(self):
        xfs = xfs_info.XFSInfo(context_wrap("""
meta-data=/dev/mapper/vgSys-lvRoot isize=256    agcount=4, agsize=320000 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=0        finobt=0
data     =                       bsize=4096   blocks=1280000, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0 ftype=0
log      =internal               bsize=4096   blocks=2560, version=2
         =                       sectsz=512   sunit=0 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0

        """.strip())).xfs_info

        # Section checks
        assert 'meta-data' in xfs
        assert 'data' in xfs
        assert 'naming' in xfs
        assert 'log' in xfs
        assert 'realtime' in xfs

        # Section specifier checks
        assert xfs['meta-data']['specifier'] == '/dev/mapper/vgSys-lvRoot'
        assert xfs['naming']['specifier'] == 'version'
        assert xfs['naming']['specifier value'] == '2'
        assert xfs['log']['specifier'] == 'internal'
        assert xfs['realtime']['specifier'] == 'none'

        # Data checks
        assert xfs['meta-data']['isize'] == 256
        assert xfs['meta-data']['agcount'] == 4
        assert xfs['meta-data']['agsize'] == '320000 blks'
        assert xfs['meta-data']['sectsz'] == 512
        assert xfs['meta-data']['attr'] == 2
        assert xfs['meta-data']['projid32bit'] == 1
        assert xfs['meta-data']['crc'] == 0
        assert xfs['meta-data']['finobt'] == 0

        assert xfs['data']['bsize'] == 4096
        assert xfs['data']['blocks'] == 1280000
        assert xfs['data']['imaxpct'] == 25
        assert xfs['data']['sunit'] == 0
        assert xfs['data']['swidth'] == '0 blks'

        assert xfs['naming']['bsize'] == 4096
        assert xfs['naming']['ascii-ci'] == 0
        assert xfs['naming']['ftype'] == 0

        assert xfs['log']['bsize'] == 4096
        assert xfs['log']['blocks'] == 2560
        assert xfs['log']['version'] == 2
        assert xfs['log']['sectsz'] == 512
        assert xfs['log']['sunit'] == '0 blks'
        assert xfs['log']['lazy-count'] == 1

        assert xfs['realtime']['extsz'] == 4096
        assert xfs['realtime']['blocks'] == 0
        assert xfs['realtime']['rtextents'] == 0
