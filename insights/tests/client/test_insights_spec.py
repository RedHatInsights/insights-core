from insights.client.data_collector import DataCollector
from insights.client.insights_spec import InsightsCommand
from insights.client.insights_spec import InsightsFile
from mock.mock import patch, MagicMock
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
