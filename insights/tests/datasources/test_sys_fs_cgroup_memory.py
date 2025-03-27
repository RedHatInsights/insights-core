import pytest
from mock.mock import patch, mock_open, Mock
from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.sys_fs_cgroup_memory import (
    LocalSpecs,
    tasks_number,
    uniq_memory_swappiness,
)

RELATIVE_PATH_1 = 'insights_datasources/sys_fs_cgroup_uniq_memory_swappiness'
EXPECTED_RESULT_1 = "60  3"
EXPECTED_RESULT_2 = """
60   1
10   2
""".strip()

SYS_FS_CGROUP_MEMORY_TASKS = """
/sys/fs/cgroup/memory/user.slice/tasks
/sys/fs/cgroup/memory/system.slice/rh-nginx120-nginx.service/tasks
/sys/fs/cgroup/memory/system.slice/named.service/tasks
/sys/fs/cgroup/memory/system.slice/rhel-push-plugin.service/tasks
/sys/fs/cgroup/memory/system.slice/docker.service/tasks
/sys/fs/cgroup/memory/system.slice/var-lib-docker-overlay2.mount/tasks
/sys/fs/cgroup/memory/system.slice/var-lib-docker-containers.mount/tasks
/sys/fs/cgroup/memory/system.slice/sys-kernel-debug.mount/tasks
/sys/fs/cgroup/memory/system.slice/systemd-update-utmp.service/tasks
/sys/fs/cgroup/memory/system.slice/sshd.service/tasks
/sys/fs/cgroup/memory/system.slice/rhsmcertd.service/tasks
""".strip()

SYS_FS_CGROUP_MEMORY_TASKS_NO_FILE = """"""

NG_COMMAND_1 = """
/usr/bin/find: '/sys/fs/cgroup/memory': No such file or directory
""".strip()

NG_COMMAND_2 = """
-bash: /usr/bin/find: No such file or directory
""".strip()

SYS_FS_CGROUP_MEMORY_TASKS_RESULT = """
11
""".strip()

SYS_FS_CGROUP_MEMORY_TASKS_RESULT_NO_FILE = """
0
""".strip()

RELATIVE_PATH_2 = 'insights_datasources/sys_fs_cgroup_memory_tasks_number'


@patch(
    'insights.specs.datasources.sys_fs_cgroup_memory.open', new_callable=mock_open, read_data='60'
)
@patch('insights.specs.datasources.sys_fs_cgroup_memory.os.walk')
def test_sys_fs_cgroup_uniq_memory_swappiness_single_line(mock_walk, mock_ds_open):
    mock_walk.return_value = [
        (
            "/sys/fs/cgroup/memory",
            (),
            (
                "memory.swappiness",
                "test",
            ),
        ),
        (
            "/sys/fs/cgroup/memory/test_1",
            (),
            (
                "memory.swappiness",
                "test",
            ),
        ),
        (
            "/sys/fs/cgroup/memory/test_2",
            (),
            (
                "memory.swappiness",
                "test",
            ),
        ),
    ]

    broker = {}
    result = uniq_memory_swappiness(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=EXPECTED_RESULT_1, relative_path=RELATIVE_PATH_1)
    assert len(result.content) == len(expected.content) == 1
    assert result.content[0].split() == expected.content[0].split()
    assert result.relative_path == expected.relative_path


@patch(
    'insights.specs.datasources.sys_fs_cgroup_memory.open', new_callable=mock_open, read_data='60'
)
@patch('insights.specs.datasources.sys_fs_cgroup_memory.os.walk')
def test_sys_fs_cgroup_uniq_memory_swappiness_multi_lines(mock_walk, mock_ds_open):
    mock_walk.return_value = [
        (
            "/sys/fs/cgroup/memory",
            (),
            (
                "memory.swappiness",
                "test",
            ),
        ),
        (
            "/sys/fs/cgroup/memory/test_1",
            (),
            (
                "memory.swappiness",
                "test",
            ),
        ),
        (
            "/sys/fs/cgroup/memory/test_2",
            (),
            (
                "memory.swappiness",
                "test",
            ),
        ),
    ]

    mock_ds_open.side_effect = (
        mock_ds_open.return_value,
        mock_open(read_data="10").return_value,
        mock_open(read_data="10").return_value,
    )

    broker = {}
    result = uniq_memory_swappiness(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=EXPECTED_RESULT_2, relative_path=RELATIVE_PATH_1)
    assert len(result.content) == len(expected.content) == 2
    assert result.content[1].split() == expected.content[1].split()
    assert result.relative_path == expected.relative_path


@patch(
    'insights.specs.datasources.sys_fs_cgroup_memory.open', new_callable=mock_open, read_data='60'
)
@patch('insights.specs.datasources.sys_fs_cgroup_memory.os.walk')
def test_sys_fs_cgroup_uniq_memory_swappiness_without_swappiness_file(mock_walk, mock_ds_open):
    mock_walk.return_value = [
        (
            "/sys/fs/cgroup/memory",
            (),
            (
                "cpu",
                "test",
            ),
        ),
        (
            "/sys/fs/cgroup/memory/test_1",
            (),
            (
                "cpu",
                "test",
            ),
        ),
        (
            "/sys/fs/cgroup/memory/test_2",
            (),
            (
                "cpu",
                "test",
            ),
        ),
    ]

    broker = {}
    with pytest.raises(SkipComponent) as e:
        uniq_memory_swappiness(broker)
    assert 'SkipComponent' in str(e)


@patch(
    'insights.specs.datasources.sys_fs_cgroup_memory.open', new_callable=mock_open, read_data='60'
)
@patch('insights.specs.datasources.sys_fs_cgroup_memory.os.walk')
def test_sys_fs_cgroup_uniq_memory_swappiness_without_memory_dir(mock_walk, mock_ds_open):
    mock_walk.return_value = []

    broker = {}
    with pytest.raises(SkipComponent) as e:
        uniq_memory_swappiness(broker)
    assert 'SkipComponent' in str(e)


def test_tasks_number():
    sys_fs_cgroup_memory_tasks_number_data = Mock()
    sys_fs_cgroup_memory_tasks_number_data.content = SYS_FS_CGROUP_MEMORY_TASKS.splitlines()
    broker = {LocalSpecs.sys_fs_cgroup_memory_tasks_raw: sys_fs_cgroup_memory_tasks_number_data}
    result = tasks_number(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(
        content=SYS_FS_CGROUP_MEMORY_TASKS_RESULT, relative_path=RELATIVE_PATH_2
    )
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_tasks_number_no_file():
    sys_fs_cgroup_memory_tasks_number_data = Mock()
    sys_fs_cgroup_memory_tasks_number_data.content = SYS_FS_CGROUP_MEMORY_TASKS_NO_FILE.splitlines()
    broker = {LocalSpecs.sys_fs_cgroup_memory_tasks_raw: sys_fs_cgroup_memory_tasks_number_data}
    result = tasks_number(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(
        content=SYS_FS_CGROUP_MEMORY_TASKS_RESULT_NO_FILE, relative_path=RELATIVE_PATH_2
    )
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_tasks_number_NG_1_output():
    sys_fs_cgroup_memory_tasks_number_data = Mock()
    sys_fs_cgroup_memory_tasks_number_data.content = NG_COMMAND_1.splitlines()
    broker = {LocalSpecs.sys_fs_cgroup_memory_tasks_raw: sys_fs_cgroup_memory_tasks_number_data}
    with pytest.raises(SkipComponent) as e:
        tasks_number(broker)
    assert 'SkipComponent' in str(e)


def test_tasks_number_NG_2_output():
    sys_fs_cgroup_memory_tasks_number_data = Mock()
    sys_fs_cgroup_memory_tasks_number_data.content = NG_COMMAND_2.splitlines()
    broker = {LocalSpecs.sys_fs_cgroup_memory_tasks_raw: sys_fs_cgroup_memory_tasks_number_data}
    with pytest.raises(SkipComponent) as e:
        tasks_number(broker)
    assert 'SkipComponent' in str(e)
