import pytest
from mock.mock import patch, mock_open
from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.sys_fs_cgroup_memory import sys_fs_cgroup_uniq_memory_swappiness

RELATIVE_PATH = 'insights_commands/sys_fs_cgroup_uniq_memory_swappiness'
EXPECTED_RESULT = "60  3"


@patch('insights.specs.datasources.sys_fs_cgroup_memory.open', new_callable=mock_open, read_data='60')
@patch('insights.specs.datasources.sys_fs_cgroup_memory.os.walk')
def test_sys_fs_cgroup_uniq_memory_swappiness(mock_walk, mock_ds_open):
    mock_walk.return_value = [
        ("/sys/fs/cgroup/memory", (), ("memory.swappiness", "test",)),
        ("/sys/fs/cgroup/memory/test_1", (), ("memory.swappiness", "test",)),
        ("/sys/fs/cgroup/memory/test_2", (), ("memory.swappiness", "test",)),
    ]

    broker = {}
    result = sys_fs_cgroup_uniq_memory_swappiness(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=EXPECTED_RESULT, relative_path=RELATIVE_PATH)
    assert len(result.content) == len(expected.content) == 1
    assert result.content[0].split() == expected.content[0].split()
    assert result.relative_path == expected.relative_path


@patch('insights.specs.datasources.sys_fs_cgroup_memory.open', new_callable=mock_open, read_data='60')
@patch('insights.specs.datasources.sys_fs_cgroup_memory.os.walk')
def test_sys_fs_cgroup_uniq_memory_swappiness_without_swappiness_file(mock_walk, mock_ds_open):
    mock_walk.return_value = [
        ("/sys/fs/cgroup/memory", (), ("cpu", "test",)),
        ("/sys/fs/cgroup/memory/test_1", (), ("cpu", "test",)),
        ("/sys/fs/cgroup/memory/test_2", (), ("cpu", "test",)),
    ]

    broker = {}
    with pytest.raises(SkipComponent) as e:
        sys_fs_cgroup_uniq_memory_swappiness(broker)
    assert 'SkipComponent' in str(e)


@patch('insights.specs.datasources.sys_fs_cgroup_memory.open', new_callable=mock_open, read_data='60')
@patch('insights.specs.datasources.sys_fs_cgroup_memory.os.walk')
def test_sys_fs_cgroup_uniq_memory_swappiness_without_memory_dir(mock_walk, mock_ds_open):
    mock_walk.return_value = []

    broker = {}
    with pytest.raises(SkipComponent) as e:
        sys_fs_cgroup_uniq_memory_swappiness(broker)
    assert 'SkipComponent' in str(e)
