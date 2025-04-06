import pytest

from mock.mock import patch, mock_open
from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.host_key_files import host_key_files

VAR_LOGS = """
Mar 16 19:30:54 host sshd[10644]: error: Could not load host key: /etc/ssh/ssh_host_dsa_key
Mar 16 19:30:54 host sshd[10645]: error: Could not load host key: /etc/ssh_host_dsa_key
""".strip()

RELATIVE_PATH = "insights_datasources/host_key_files"
EXPECTED_RESULT = """
/etc/ssh/ssh_host_dsa_key   1
/etc/ssh_host_dsa_key   0
""".strip()


@patch(
    'insights.specs.datasources.host_key_files.open', new_callable=mock_open, read_data=VAR_LOGS
)
@patch('os.path.exists')
def test_host_key_files(mock_exists, mock_ds_open):
    files_dict = {
        '/etc/ssh/ssh_host_dsa_key': True,
        '/etc/ssh_host_dsa_key': False,
    }
    mock_exists.side_effect = lambda path: files_dict.get(path, False)

    broker = {}
    result = host_key_files(broker)
    assert result is not None

    expected = DatasourceProvider(content=EXPECTED_RESULT, relative_path=RELATIVE_PATH)
    assert len(result.content) == len(expected.content) == 2


@patch(
    'insights.specs.datasources.host_key_files.open', new_callable=mock_open, read_data=""
)
@patch('os.path.exists')
def test_host_key_files_empty_log(mock_exists, mock_ds_open):
    broker = {}
    with pytest.raises(SkipComponent) as e:
        host_key_files(broker)
    assert 'SkipComponent' in str(e)
