from insights.parsers.lsscsi import LsSCSI
from insights.tests import context_wrap


LSSCSI_1 = """
[1:0:0:0]    storage IET      Controller       0001  -
[1:0:0:1]    disk    IET      VIRTUAL-DISK     0001  /dev/sdb
[3:0:5:0]    tape    HP       C5713A           H910  /dev/st0
"""


def test_lsscsi():
    lsscsi = LsSCSI(context_wrap(LSSCSI_1))
    assert len(lsscsi.data) == 3
    assert lsscsi[0] == {'Model': 'Controller', 'Vendor': 'IET',
                         'HCTL': '[1:0:0:0]', 'Peripheral-Type': 'storage',
                         'Primary-Device-Node': '-', 'Revision': '0001'}
    assert ['-', '/dev/sdb', '/dev/st0'] == lsscsi.device_nodes
