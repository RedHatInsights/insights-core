import pytest
from mock.mock import Mock, patch

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.mdadm import raid_devices

MOCK_OS_STAT_ST_MODE = {
    "b": 25008,
    "d": 16877,
    "-": 33188,
}

GLOB_DEV_MD_1 = "/dev/md1 /dev/md2 /dev/md3".split()
GLOB_DEV_MD_2 = "/dev/md".split()
GLOB_DEV_MD_3 = "/dev/mdxyz".split()
GLOB_DEV_MD_4 = "".split()

mock_os_stat_return_1 = Mock(st_mode=MOCK_OS_STAT_ST_MODE["b"])
mock_os_stat_return_2 = Mock(st_mode=MOCK_OS_STAT_ST_MODE["d"])
mock_os_stat_return_3 = Mock(st_mode=MOCK_OS_STAT_ST_MODE["-"])


@patch("os.stat", return_value=mock_os_stat_return_1)
@patch("glob.glob", return_value=GLOB_DEV_MD_1)
def test_raid_devices(m_glob, m_stst):
    result = raid_devices({})
    assert result is not None
    assert isinstance(result, str)
    assert result == "/dev/md1 /dev/md2 /dev/md3"


@patch("os.stat", return_value=mock_os_stat_return_2)
@patch("glob.glob", return_value=GLOB_DEV_MD_2)
def test_raid_devices_bad_2(m_glob, m_stst):
    with pytest.raises(SkipComponent) as e:
        raid_devices({})
    assert "Skipping raid_devices: No /dev/md* raid devices found" in str(e)


@patch("os.stat", return_value=mock_os_stat_return_3)
@patch("glob.glob", return_value=GLOB_DEV_MD_3)
def test_raid_devices_bad_3(m_glob, m_stst):
    with pytest.raises(SkipComponent) as e:
        raid_devices({})
    assert "Skipping raid_devices: No /dev/md* raid devices found" in str(e)


@patch("os.stat", return_value=mock_os_stat_return_1)
@patch("glob.glob", return_value=GLOB_DEV_MD_4)
def test_raid_devices_bad_4(m_glob, m_stst):
    with pytest.raises(SkipComponent) as e:
        raid_devices({})
    assert "Skipping raid_devices: No /dev/md* raid devices found" in str(e)
