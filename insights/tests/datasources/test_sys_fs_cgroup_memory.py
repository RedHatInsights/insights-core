import pytest
from mock.mock import patch, mock_open
from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.sys_fs_cgroup_memory import sys_fs_cgroup_uniq_memory_swappiness

RELATIVE_PATH = 'insights_commands/sys_fs_cgroup_uniq_memory_swappiness'
EXPECTED_RESULT_1 = "60  3"
EXPECTED_RESULT_2 = """
60   1
10   2
""".strip()


@patch('insights.specs.datasources.sys_fs_cgroup_memory.open', new_callable=mock_open, read_data='60')
@patch('insights.specs.datasources.sys_fs_cgroup_memory.os.walk')
def test_sys_fs_cgroup_uniq_memory_swappiness_single_line(mock_walk, mock_ds_open):
    mock_walk.return_value = [
        ("/sys/fs/cgroup/memory", (), ("memory.swappiness", "test",)),
        ("/sys/fs/cgroup/memory/test_1", (), ("memory.swappiness", "test",)),
        ("/sys/fs/cgroup/memory/test_2", (), ("memory.swappiness", "test",)),
    ]

    broker = {}
    result = sys_fs_cgroup_uniq_memory_swappiness(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=EXPECTED_RESULT_1, relative_path=RELATIVE_PATH)
    assert len(result.content) == len(expected.content) == 1
    assert result.content[0].split() == expected.content[0].split()
    assert result.relative_path == expected.relative_path


@patch('insights.specs.datasources.sys_fs_cgroup_memory.open', new_callable=mock_open, read_data='60')
@patch('insights.specs.datasources.sys_fs_cgroup_memory.os.walk')
def test_sys_fs_cgroup_uniq_memory_swappiness_multi_lines(mock_walk, mock_ds_open):
    mock_walk.return_value = [
        ("/sys/fs/cgroup/memory", (), ("memory.swappiness", "test",)),
        ("/sys/fs/cgroup/memory/test_1", (), ("memory.swappiness", "test",)),
        ("/sys/fs/cgroup/memory/test_2", (), ("memory.swappiness", "test",)),
    ]

    mock_ds_open.side_effect = (mock_ds_open.return_value, mock_open(read_data="10").return_value, mock_open(read_data="10").return_value,)

    broker = {}
    result = sys_fs_cgroup_uniq_memory_swappiness(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=EXPECTED_RESULT_2, relative_path=RELATIVE_PATH)
    assert len(result.content) == len(expected.content) == 2
    assert result.content[1].split() == expected.content[1].split()
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
