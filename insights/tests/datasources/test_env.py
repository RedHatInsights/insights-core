import pytest
from mock.mock import patch, mock_open
from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.env import ld_library_path_global_conf

ENV_FILE_1 = """
LD_LIBRARY_PATH="/path/to/test"
export LD_LIBRARY_PATH
""".strip()

ENV_FILE_2 = """
export  LD_LIBRARY_PATH="/path/to/test"
""".strip()

ENV_FILE_3 = """
export LD_LIBRARY_PATH="/path/to/test" TEST="test"
""".strip()

ENV_CONFIG = {
    "/etc/environment": {"content": ENV_FILE_1, "isfile": True, "isdir": False},
    "/etc/env.d": {"content": "# export LD_LIBRARY_PATH", "isfile": False, "isdir": True},
    "/etc/env.d/test.conf": {"content": ENV_FILE_2, "isfile": True, "isdir": False},
    "/etc/profile": {
        "content": "export TEST=/test\n unset LD_LIBRARY_PATH",
        "isfile": True,
        "isdir": False,
    },
    "/etc/profile.d": {"content": "export TEST # LD_LIBRARY_PATH", "isfile": False, "isdir": True},
    "/etc/profile.d/test.conf": {"content": "", "isfile": True, "isdir": False},
    "/etc/bashrc": {"content": "", "isfile": True, "isdir": False},
    "/etc/bash.bashrc": {"content": "", "isfile": True, "isdir": False},
    "/root/.bash_profile": {"content": ENV_FILE_3, "isfile": True, "isdir": False},
    "/root/.bashrc": {"content": "", "isfile": True, "isdir": False},
    "/root/.profile": {"content": "LD_LIBRARY_PATH=/path/to/test", "isfile": True, "isdir": False},
    "/root/.cshrc": {"content": "", "isfile": True, "isdir": False},
    "/root/.zshrc": {"content": "", "isfile": True, "isdir": False},
    "/root/.tcshrc": {"content": "", "isfile": True, "isdir": False},
}

RELATIVE_PATH = 'insights_datasources/ld_library_path_global_conf'

EXPECTED_RESULT = """
{"export_files": ["/etc/environment", "/etc/env.d/test.conf", "/root/.bash_profile"], "unset_files": ["/etc/profile"]}
""".strip()


def _open_side_effect(name, mode):
    return mock_open(read_data=ENV_CONFIG.get(name, {}).get("content", ""))()


def _isfile_side_effect(name):
    return ENV_CONFIG.get(name, {}).get("isfile", False)


def _isdir_return_value(name):
    return ENV_CONFIG.get(name, {}).get("isdir", False)


@patch('insights.specs.datasources.env.open', side_effect=_open_side_effect)
@patch('os.path.exists', return_value=True)
@patch('os.path.isfile', side_effect=_isfile_side_effect)
@patch('os.path.isdir', return_value=_isdir_return_value)
@patch('os.listdir')
def test_ld_library_path_global_conf(
    mock_listdir, mock_isdir, mock_isfile, mock_exists, mock_ds_open
):
    mock_listdir.return_value = ["test.conf"]

    broker = {}
    result = ld_library_path_global_conf(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=EXPECTED_RESULT, relative_path=RELATIVE_PATH)
    assert result.relative_path == expected.relative_path
    assert result.content == expected.content


@patch('os.path.exists', return_value=False)
def test_ld_library_path_global_conf_without_env_files(mock_exists):
    broker = {}
    with pytest.raises(SkipComponent) as e:
        ld_library_path_global_conf(broker)
    assert 'SkipComponent' in str(e)


@patch('insights.specs.datasources.env.open', read_data="")
@patch('os.path.exists', return_value=True)
@patch('os.path.isfile', side_effect=_isfile_side_effect)
@patch('os.path.isdir', return_value=_isdir_return_value)
@patch('os.listdir')
def test_ld_library_path_global_conf_all_env_files_are_empty(
    mock_listdir, mock_isdir, mock_isfile, mock_exists, mock_ds_open
):
    mock_listdir.return_value = ["test.conf"]

    broker = {}
    with pytest.raises(SkipComponent) as e:
        ld_library_path_global_conf(broker)
    assert 'SkipComponent' in str(e)
