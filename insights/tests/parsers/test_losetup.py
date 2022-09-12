import pytest
import doctest
from insights.parsers import SkipException, losetup
from insights.parsers.losetup import LoSetup
from insights.tests import context_wrap

LOSETUP_RHEL8 = """
NAME       SIZELIMIT OFFSET AUTOCLEAR RO BACK-FILE       DIO LOG-SEC
/dev/loop2      4096    256         0  1 /root/disk2.img   0    1024
/dev/loop0         0      0         1  0 /root/disk1.img   1     512
"""

LOSETUP_RHEL7 = """
NAME       SIZELIMIT OFFSET AUTOCLEAR RO BACK-FILE
/dev/loop3      4096    256         0  1 /root/disk3.img
"""

LOSETUP_EMPTY = ""

LOSETUP_DOCTEST = """
NAME       SIZELIMIT OFFSET AUTOCLEAR RO BACK-FILE      DIO LOG-SEC
/dev/loop0         0      0         0  0 /root/disk.img   1     512
"""


def test_losetup():
    losetup = LoSetup(context_wrap(LOSETUP_RHEL8))
    assert len(losetup) == 2
    assert losetup[0]['NAME'] == '/dev/loop2'
    assert losetup[0]['SIZELIMIT'] == 4096
    assert losetup[0]['OFFSET'] == 256
    assert losetup[0]['AUTOCLEAR'] is False
    assert losetup[0]['RO'] is True
    assert losetup[0]['BACK-FILE'] == '/root/disk2.img'
    assert losetup[0]['DIO'] is False
    assert losetup[0]['LOG-SEC'] == 1024
    assert losetup[1]['NAME'] == '/dev/loop0'
    assert losetup[1]['SIZELIMIT'] == 0
    assert losetup[1]['OFFSET'] == 0
    assert losetup[1]['AUTOCLEAR'] is True
    assert losetup[1]['RO'] is False
    assert losetup[1]['BACK-FILE'] == '/root/disk1.img'
    assert losetup[1]['DIO'] is True
    assert losetup[1]['LOG-SEC'] == 512

    losetup = LoSetup(context_wrap(LOSETUP_RHEL7))
    assert len(losetup) == 1
    assert losetup[0]['NAME'] == '/dev/loop3'
    assert losetup[0]['SIZELIMIT'] == 4096
    assert losetup[0]['OFFSET'] == 256
    assert losetup[0]['AUTOCLEAR'] is False
    assert losetup[0]['RO'] is True
    assert losetup[0]['BACK-FILE'] == '/root/disk3.img'
    assert 'DIO' not in losetup[0]
    assert 'LOG-SEC' not in losetup[0]

    with pytest.raises(SkipException):
        LoSetup(context_wrap(LOSETUP_EMPTY))


def test_losetup_doc_examples():
    env = {'losetup': LoSetup(context_wrap(LOSETUP_DOCTEST))}
    failed, total = doctest.testmod(losetup, globs=env)
    assert failed == 0
