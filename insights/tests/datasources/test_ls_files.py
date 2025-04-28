import pytest

from mock.mock import patch
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.parsers.fstab import FSTab
from insights.parsers.lvm import Pvs
from insights.parsers.blkid import BlockIDInfo
from insights.specs.datasources.ls_files import check_ls_files
from insights.tests import context_wrap


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

RELATIVE_PATH = 'insights_datasources/ls_files'

EXPECTED_RESULT = ['{"/dev/sdb2": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test", "/dev/mapper/rhel-root": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test", "/dev/mapper/rhel-home": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test", "/dev/mapper/rhel-var": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test", "/dev/vda1": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test", "/dev/vda2": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test"}']

EXPECTED_RESULT_ONLY_PVS = ['{"/dev/vda1": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test", "/dev/vda2": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test"}']

EXPECTED_RESULT_ONLY_FSTAB = ['{"/dev/sdb2": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test", "/dev/mapper/rhel-root": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test", "/dev/mapper/rhel-home": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test", "/dev/mapper/rhel-var": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test"}']


@patch("os.path.exists", return_value=True)
@patch('os.popen')
def test_ls_files(m_popen, m_exists):
    m_popen().read.return_value = "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test"
    fstab_info = FSTab(context_wrap(FSTAB_DATA))
    blkid_info = BlockIDInfo(context_wrap(BLKID_DATA))
    pvs_info = Pvs(context_wrap(PVS_DATA))
    broker = {FSTab: fstab_info, BlockIDInfo: blkid_info, Pvs: pvs_info}
    result = check_ls_files(broker)
    expected = DatasourceProvider(content=EXPECTED_RESULT, relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


@patch("os.path.exists", return_value=True)
@patch('os.popen')
def test_ls_files_no_fstab(m_popen, m_exists):
    m_popen().read.return_value = "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test"
    pvs_info = Pvs(context_wrap(PVS_DATA))
    broker = {Pvs: pvs_info}
    result = check_ls_files(broker)
    expected = DatasourceProvider(content=EXPECTED_RESULT_ONLY_PVS, relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


@patch("os.path.exists", return_value=True)
@patch('os.popen')
def test_ls_files_no_pvs(m_popen, m_exists):
    m_popen().read.return_value = "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test"
    fstab_info = FSTab(context_wrap(FSTAB_DATA))
    blkid_info = BlockIDInfo(context_wrap(BLKID_DATA))
    broker = {FSTab: fstab_info, BlockIDInfo: blkid_info}
    result = check_ls_files(broker)
    expected = DatasourceProvider(content=EXPECTED_RESULT_ONLY_FSTAB, relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


@patch("os.path.exists", return_value=False)
@patch('os.popen')
def test_ls_files_no_existing(m_popen, m_exists):
    m_popen().read.return_value = "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/test"
    fstab_info = FSTab(context_wrap(FSTAB_DATA))
    blkid_info = BlockIDInfo(context_wrap(BLKID_DATA))
    pvs_info = Pvs(context_wrap(PVS_DATA))
    broker = {FSTab: fstab_info, BlockIDInfo: blkid_info, Pvs: pvs_info}
    with pytest.raises(SkipComponent) as e:
        check_ls_files(broker)
    assert 'SkipComponent' in str(e)


@patch("os.path.exists", return_value=True)
def test_httpd_cmds_no_output(m_exists):
    fstab_info = FSTab(context_wrap(FSTAB_DATA))
    blkid_info = BlockIDInfo(context_wrap(BLKID_DATA))
    pvs_info = Pvs(context_wrap(PVS_DATA))
    broker = {FSTab: fstab_info, BlockIDInfo: blkid_info, Pvs: pvs_info}
    with pytest.raises(SkipComponent) as e:
        check_ls_files(broker)
    assert 'SkipComponent' in str(e)
