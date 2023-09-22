import pytest

from mock.mock import Mock

from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.sys_fs_cgroup_memory_tasks_number import LocalSpecs, sys_fs_cgroup_memory_tasks_number_data_datasource


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

RELATIVE_PATH = 'insights_commands/sys_fs_cgroup_memory_tasks_number'


def test_sys_fs_cgroup_memory_tasks_number_data_datasource():
    sys_fs_cgroup_memory_tasks_number_data = Mock()
    sys_fs_cgroup_memory_tasks_number_data.content = SYS_FS_CGROUP_MEMORY_TASKS.splitlines()
    broker = {LocalSpecs.sys_fs_cgroup_memory_tasks_raw: sys_fs_cgroup_memory_tasks_number_data}
    result = sys_fs_cgroup_memory_tasks_number_data_datasource(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=SYS_FS_CGROUP_MEMORY_TASKS_RESULT, relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_sys_fs_cgroup_memory_tasks_number_data_datasource_no_file():
    sys_fs_cgroup_memory_tasks_number_data = Mock()
    sys_fs_cgroup_memory_tasks_number_data.content = SYS_FS_CGROUP_MEMORY_TASKS_NO_FILE.splitlines()
    broker = {LocalSpecs.sys_fs_cgroup_memory_tasks_raw: sys_fs_cgroup_memory_tasks_number_data}
    result = sys_fs_cgroup_memory_tasks_number_data_datasource(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=SYS_FS_CGROUP_MEMORY_TASKS_RESULT_NO_FILE, relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_sys_fs_cgroup_memory_tasks_number_data_datasource_NG_1_output():
    sys_fs_cgroup_memory_tasks_number_data = Mock()
    sys_fs_cgroup_memory_tasks_number_data.content = NG_COMMAND_1.splitlines()
    broker = {LocalSpecs.sys_fs_cgroup_memory_tasks_raw: sys_fs_cgroup_memory_tasks_number_data}
    with pytest.raises(SkipComponent) as e:
        sys_fs_cgroup_memory_tasks_number_data_datasource(broker)
    assert 'SkipComponent' in str(e)


def test_sys_fs_cgroup_memory_tasks_number_data_datasource_NG_2_output():
    sys_fs_cgroup_memory_tasks_number_data = Mock()
    sys_fs_cgroup_memory_tasks_number_data.content = NG_COMMAND_2.splitlines()
    broker = {LocalSpecs.sys_fs_cgroup_memory_tasks_raw: sys_fs_cgroup_memory_tasks_number_data}
    with pytest.raises(SkipComponent) as e:
        sys_fs_cgroup_memory_tasks_number_data_datasource(broker)
    assert 'SkipComponent' in str(e)
