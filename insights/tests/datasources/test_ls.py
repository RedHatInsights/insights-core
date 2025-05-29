import pytest

from collections import defaultdict

try:
    from unittest.mock import patch
except Exception:
    from mock import patch

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.parsers.blkid import BlockIDInfo
from insights.parsers.fstab import FSTab
from insights.parsers.lvm import Pvs
from insights.specs import Specs
from insights.specs.datasources.ls import (
    list_files_with_lH,
    list_with_la,
    list_with_la_filtered,
    list_with_lan,
    list_with_lan_filtered,
    list_with_lanL,
    list_with_lanR,
    list_with_lanRL,
    list_with_laRZ,
    list_with_laZ,
)
from insights.tests import context_wrap


FSTAB_CONTEXT = """
/dev/mapper/rhel_rhel8-root /                       xfs     defaults        0 0
/dev/vda1 /boot                   xfs     defaults        0 0
/dev/mapper/rhel_rhel8-swap none                    swap    defaults        0 0
/dev/mapper/rhel_rhel7-hana1 /hana/data/rhel7-hana1                       xfs     defaults        0 0
/dev/mapper/rhel_rhel7-hana2 /hana/data/rhel7-hana2                       xfs     defaults        0 0
/dev/mapper/rhel_rhel7-hana3 /hana/data/rhel7-hana3                       xfs     defaults        0 0
""".strip()

FSTAB_DATA = """
/dev/sdb2                                 /var                       ext3    defaults        1 1
/dev/mapper/rhel-root                     /                          ext4    defaults        1 1
UUID=9c4f1e8e-60c8-46ef-b70b-111111111111 /home                      xfs     defaults        0 0
LABEL=new-label         /var                    ext3    defaults        1 2
/dev/archive_data           /data/ac/archive none    bind                    0 0
""".strip()

BLKID_DATA = """
/dev/sda1: LABEL="TestHome" TYPE="ext4"
/dev/sdb1: LABEL="" UUID="c7c45f2d-1d1b-4cf0-9d51-e2b0046682f8" TYPE="ext4"
/dev/sdb2: LABEL="" UUID="UVTk76-UWOc-vk7s-galL-dxIP-4UXO-0jG4MH" TYPE="ext4"
/dev/mapper/rhel-home: LABEL="" UUID="9c4f1e8e-60c8-46ef-b70b-111111111111" TYPE="ext4"
/dev/mapper/rhel-var: LABEL="new-label" UUID="9c4f1e8e-60c8-46ef-b70b-5a7ae1fa3b7f" TYPE="xfs"
""".strip()

PVS_DATA = """
  WARNING: locking_type (0) is deprecated, using --nolocking.
  WARNING: File locking is disabled.
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='1.00g'|LVM2_PV_NAME='/dev/vda1'|LVM2_PV_MAJOR='252'|LVM2_PV_MINOR='1'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_PV_DEVICE_ID=''|LVM2_PV_DEVICE_ID_TYPE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='D0bk3H-NASe-ncYz-L3T0-mPSH-QbzT-xlPTrh'|LVM2_DEV_SIZE='<127.00g'|LVM2_PV_NAME='/dev/vda2'|LVM2_PV_MAJOR='252'|LVM2_PV_MINOR='2'|LVM2_PV_MDA_FREE='507.50k'|LVM2_PV_MDA_SIZE='1020.00k'|LVM2_PV_EXT_VSN='2'|LVM2_PE_START='1.00m'|LVM2_PV_SIZE='<127.00g'|LVM2_PV_FREE='<54.94g'|LVM2_PV_USED='<72.06g'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='32511'|LVM2_PV_PE_ALLOC_COUNT='18447'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE='used'|LVM2_PV_DUPLICATE=''|LVM2_PV_DEVICE_ID=''|LVM2_PV_DEVICE_ID_TYPE=''|LVM2_VG_NAME='rhel_rhel8'
""".strip()


def setup_function(func):
    if func is test_la_empty:
        pass
    if func is test_la:
        filters.add_filter(Specs.ls_la_dirs, ["/"])
    if func is test_la_filterd:
        filters.add_filter(Specs.ls_la_filtered_dirs, ["/", '/boot'])
    if func is test_lan:
        filters.add_filter(Specs.ls_lan_dirs, ["/", '/boot'])
    if func is test_lan_filterd:
        filters.add_filter(Specs.ls_lan_filtered_dirs, ["/"])
    if func is test_lanL:
        filters.add_filter(Specs.ls_lanL_dirs, ["/", '/boot'])
    if func is test_lanR:
        filters.add_filter(Specs.ls_lanR_dirs, ["/"])
    if func is test_lanRL:
        filters.add_filter(Specs.ls_lanRL_dirs, ["/", '/boot'])
    if func is test_lanRZ:
        filters.add_filter(Specs.ls_laRZ_dirs, ['/boot'])
    if func is test_lanZ:
        filters.add_filter(Specs.ls_laZ_dirs, ["/", '/mnt'])
    if func is test_lan_with_fstab_mounted_filter:
        filters.add_filter(Specs.ls_lan_dirs, ["/", '/boot', 'fstab_mounted.dirs'])
    if func is test_lH_files:
        filters.add_filter(Specs.ls_lH_files, ["/etc/redhat-release", '/var/log/messages'])
    if func is test_lH_files_pvs:
        filters.add_filter(Specs.ls_lH_files, ["/etc/redhat-release", '/var/log/messages', 'pvs.devices'])
    if func is test_lH_files_fstab_blkid:
        filters.add_filter(Specs.ls_lH_files, ["/etc/redhat-release", '/var/log/messages', 'fstab_mounted.devices'])


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)


def test_la_empty():
    with pytest.raises(SkipComponent):
        list_with_la({})


def test_la():
    ret = list_with_la({})
    assert ret == '/ _non_existing_'


def test_la_filterd():
    ret = list_with_la_filtered({})
    assert ret == '/ /boot'


def test_lan():
    ret = list_with_lan({})
    assert ret == '/ /boot'


def test_lan_filterd():
    ret = list_with_lan_filtered({})
    assert ret == '/ _non_existing_'


def test_lanL():
    ret = list_with_lanL({})
    assert ret == '/ /boot'


def test_lanR():
    ret = list_with_lanR({})
    assert '/' == ret


def test_lanRL():
    ret = list_with_lanRL({})
    assert ret == '/ /boot'


def test_lanRZ():
    ret = list_with_laRZ({})
    assert ret == '/boot'


def test_lanZ():
    ret = list_with_laZ({})
    assert ret == '/ /mnt'


def test_lan_with_fstab_mounted_filter():
    fstab = FSTab(context_wrap(FSTAB_CONTEXT))
    broker = {FSTab: fstab}
    ret = list_with_lan(broker)
    assert ret == '/ /boot /hana/data'


@patch("os.path.isdir", return_value=False)
def test_lH_files(_):
    ret = list_files_with_lH({})
    assert ret == '/etc/redhat-release /var/log/messages'


@patch("os.path.isdir", return_value=False)
def test_lH_files_pvs(_):
    pvs_info = Pvs(context_wrap(PVS_DATA))
    broker = {Pvs: pvs_info}
    ret = list_files_with_lH(broker)
    assert ret == '/dev/vda1 /dev/vda2 /etc/redhat-release /var/log/messages'


@patch("os.path.isdir", return_value=False)
def test_lH_files_fstab_blkid(_):
    fstab_info = FSTab(context_wrap(FSTAB_DATA))
    blkid_info = BlockIDInfo(context_wrap(BLKID_DATA))
    broker = {FSTab: fstab_info, BlockIDInfo: blkid_info}
    ret = list_files_with_lH(broker)
    assert ret == '/dev/mapper/rhel-home /dev/mapper/rhel-root /dev/mapper/rhel-var /dev/sdb2 /etc/redhat-release /var/log/messages'
