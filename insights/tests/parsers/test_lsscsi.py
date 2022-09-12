import doctest
import pytest

from insights.parsers import lsscsi, ParseException
from insights.tests import context_wrap


LSSCSI_1 = """
[1:0:0:0]    storage IET      Controller       0001  -
[1:0:0:1]    cd/dvd  QEMU     QEMU DVD-ROM     2.5+  /dev/sr0
[1:0:0:2]    disk    IET      VIRTUAL-DISK     0001  /dev/sdb
[3:0:5:0]    tape    HP       C5713A           H910  /dev/st0
"""

LSSCSI_2 = """
[1:0:0:1]    cd/dvd  QEMU     QEMU DVD-ROM     2.5+  /dev/sr0
"""

LSSCSI_3 = """
[1:0:0:1]    cd/dvd  QEMU     QEMU  DVD-ROM     2.5+  /dev/sr0
"""

LSSCSI_4 = """
[1:0:0:1]    cd/dvd  QEMU     QEMU DVD-ROM     2.5+  /dev/sr0
[1:0:0:2]    cd/dvd  QEMU     QEMU DVD-ROM     2.5+  /dev/sr1
[1:0:0:3]    disk    IET      VIRTUAL-DISK     0001  /dev/sdb
[3:0:5:0]    tape    HP       C5713A           H910  /dev/st0
"""

LSSCSI_5 = """
[1:0:0:2]    disk    IET      VIRTUAL-DISK     0001
[3:0:5:0]    tape    HP       C5713A           H910  /dev/st0
"""


def test_lsscsi():
    scsi = lsscsi.LsSCSI(context_wrap(LSSCSI_1))
    assert len(scsi.data) == 4
    assert scsi[0] == {'Model': 'Controller', 'Vendor': 'IET',
                         'HCTL': '[1:0:0:0]', 'Peripheral-Type': 'storage',
                         'Primary-Device-Node': '-', 'Revision': '0001'}
    assert scsi[1]['Peripheral-Type'] == 'cd/dvd'
    assert ['-', '/dev/sr0', '/dev/sdb', '/dev/st0'] == scsi.device_nodes

    assert scsi[1]['Vendor'] == 'QEMU'
    assert ['IET', 'QEMU', 'IET', 'HP'] == scsi.device_vendors

    scsi = lsscsi.LsSCSI(context_wrap(LSSCSI_2))
    assert len(scsi.data) == 1
    assert scsi[0] == {'Model': 'QEMU DVD-ROM', 'Vendor': 'QEMU',
                       'HCTL': '[1:0:0:1]', 'Peripheral-Type': 'cd/dvd',
                       'Primary-Device-Node': '/dev/sr0', 'Revision': '2.5+'}

    scsi = lsscsi.LsSCSI(context_wrap(LSSCSI_3))
    assert len(scsi.data) == 1
    assert scsi[0]['Model'] == 'QEMU  DVD-ROM'

    scsi = lsscsi.LsSCSI(context_wrap(LSSCSI_4))
    assert len(scsi.data) == 4
    assert len(scsi[0]) == 6


def test_bad_lsscsi():
    with pytest.raises(ParseException) as e_info:
        lsscsi.LsSCSI(context_wrap(""))
    assert "Empty content of command output" in str(e_info.value)

    with pytest.raises(ParseException) as e_info:
        lsscsi.LsSCSI(context_wrap(LSSCSI_5))
    assert "Invalid format of content, unparsable" in str(e_info.value)


def test_lsscsi_documentation():
    failed_count, tests = doctest.testmod(
        lsscsi,
        globs={'lsscsi': lsscsi.LsSCSI(context_wrap(LSSCSI_1))}
    )
    assert failed_count == 0
