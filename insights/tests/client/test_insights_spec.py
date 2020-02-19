from insights.client.data_collector import DataCollector
from insights.client.insights_spec import InsightsCommand
from insights.client.insights_spec import InsightsFile
from insights.client.insights_spec import InsightsSpec
from mock.mock import patch, MagicMock, ANY
import mock


@patch('insights.client.data_collector.read_pidfile')
def test_read_pidfile_called(read_pidfile):
    '''
    Pidfile is read when collection starts
    '''
    dc = DataCollector(MagicMock(display_name=None))
    dc.run_collection({'commands': [], 'files': []}, None, None)
    read_pidfile.assert_called_once()


@patch('insights.client.insights_spec.systemd_notify')
@patch('insights.client.insights_spec.Popen')
def test_systemd_notify_called_cmd(Popen, systemd_notify):
    '''
    Systemd_notify is called before a command is run or
    a file is collected
    '''
    process_mock = mock.Mock()
    attrs = {'communicate.return_value': (b'output', b'error')}
    process_mock.configure_mock(**attrs)
    Popen.return_value = process_mock
    cs = InsightsCommand(MagicMock(), {'command': '', 'pattern': [], 'symbolic_name': ''}, None, '/', parent_pid='420')
    cs.get_output()
    systemd_notify.assert_called_with('420')


@patch('insights.client.insights_spec.systemd_notify')
@patch('insights.client.insights_spec.Popen')
def test_systemd_notify_called_file(Popen, systemd_notify):
    '''
    Systemd_notify is called before a command is run or
    a file is collected
    '''
    process_mock = mock.Mock()
    attrs = {'communicate.return_value': (b'output', b'error')}
    process_mock.configure_mock(**attrs)
    Popen.return_value = process_mock
    fs = InsightsFile({'file': '', 'pattern': [], 'symbolic_name': ''}, None, '/', parent_pid='420')
    fs.get_output()
    systemd_notify.assert_called_with('420')


def test_string_pattern_init():
    '''
    Assert spec is loaded in string mode when a list of strings is present
    in the "patterns" section
    (legacy remove conf + new style w/ list only)
    '''
    spec = InsightsSpec(MagicMock(), {'command': '', 'pattern': [], 'symbolic_name': ''}, ['test'])
    assert not spec.regex


def test_regex_pattern_init():
    '''
    Assert spec is loaded in regex mode when a dict is present with the "wegex"
    key with a list of strings as its value in the "patterns" section
    '''
    spec = InsightsSpec(MagicMock(), {'command': '', 'pattern': [], 'symbolic_name': ''}, {'regex': ['test']})
    assert spec.regex


@patch('insights.client.insights_spec.systemd_notify')
@patch('insights.client.insights_spec.Popen')
@patch('insights.client.insights_spec.os.path.isfile', return_value=True)
def test_string_pattern_called(isfile, Popen, systemd_notify):
    '''
    '''
    process_mock = mock.Mock()
    attrs = {'communicate.return_value': (b'output', b'error')}
    process_mock.configure_mock(**attrs)
    Popen.return_value = process_mock
    fs = InsightsFile({'file': '', 'pattern': [], 'symbolic_name': ''}, ['test'], '/')
    fs.get_output()
    Popen.assert_any_call(['grep', '-F', '-v', '-f', ANY], stdin=ANY, stdout=ANY)


@patch('insights.client.insights_spec.systemd_notify')
@patch('insights.client.insights_spec.Popen')
@patch('insights.client.insights_spec.os.path.isfile', return_value=True)
def test_regex_pattern_called(isfile, Popen, systemd_notify):
    '''
    '''
    process_mock = mock.Mock()
    attrs = {'communicate.return_value': (b'output', b'error')}
    process_mock.configure_mock(**attrs)
    Popen.return_value = process_mock
    fs = InsightsFile({'file': '', 'pattern': [], 'symbolic_name': ''}, {'regex': ['test']}, '/')
    fs.get_output()
    Popen.assert_any_call(['grep', '-E', '-v', '-f', ANY], stdin=ANY, stdout=ANY)
