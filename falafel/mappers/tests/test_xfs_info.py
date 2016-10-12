from falafel.mappers import xfs_info
from falafel.tests import context_wrap

class TestXFSInfo():
    def test_example_xfs_info(self):
        xfs_info = xfs_info.XFSInfo(context_wrap("""
 meta-data=/dev/sda      isize=256    agcount=32, agsize=16777184 blks
          =              sectsz=512   attr=2
 data     =              bsize=4096   blocks=536869888, imaxpct=5
          =              sunit=32     swidth=128 blks
 naming   =version 2     bsize=4096
 log      =internal      bsize=4096   blocks=32768, version=2
          =              sectsz=512   sunit=32 blks, lazy-count=1
 realtime =none          extsz=524288 blocks=0, rtextents=0
        """.strip()))

        # Section checks
        assert 'meta-data' in xfs_info
        assert 'data' in xfs_info
        assert 'naming' in xfs_info
        assert 'log' in xfs_info
        assert 'realtime' in xfs_info

        # Section specifier checks
        assert xfs_info['meta-data']['specifier'] == '/dev/sda'
        assert xfs_info['naming']['specifier'] == 'version'
        assert xfs_info['naming']['specifier value'] == '2'
        assert xfs_info['log']['specifier'] == 'internal'
        assert xfs_info['realtime']['specifier'] == 'none'

        # Data checks
        assert xfs_info['meta-data']['isize'] == 256
        assert xfs_info['meta-data']['agcount'] == 32
        assert xfs_info['meta-data']['agsize'] == '16777184 blks'
        assert xfs_info['meta-data']['sectsz'] == 512
        assert xfs_info['meta-data']['attr'] == 2

        assert xfs_info['data']['bsize'] == 4096
        assert xfs_info['data']['blocks'] == 536869888
        assert xfs_info['data']['imaxpct'] == 5
        assert xfs_info['data']['sunit'] == 32
        assert xfs_info['data']['swidth'] == '128 blks'
        

        assert xfs_info['naming']['bsize'] == 4096

        assert xfs_info['log']['bsize'] == 4096
        assert xfs_info['log']['blocks'] == 32768
        assert xfs_info['log']['version'] == 2
        assert xfs_info['log']['sectsz'] == 512
        assert xfs_info['log']['sunit'] == '32 blks'
        assert xfs_info['log']['lazy-count'] == 1

        assert xfs_info['realtime']['extsz'] == 524288
        assert xfs_info['realtime']['blocks'] == 0
        assert xfs_info['realtime']['rtextents'] == 0
