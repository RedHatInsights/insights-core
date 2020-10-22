from insights.client import InsightsClient
from insights.client.constants import InsightsConstants
from mock.mock import call
from mock.mock import patch


@patch("insights.client.write_to_disk")
@patch("insights.client.os.getpid")
@patch("insights.client.get_parent_process")
def test_write_pidfile(get_parent_process, getpid, write_to_disk):
    '''
    Test writing of the pidfile when InsightsClient
    is called initially (when setup_logging=False)
    '''
    InsightsClient(from_phase=False)
    getpid.assert_called_once()
    write_to_disk.assert_has_calls((
        call(InsightsConstants.pidfile, content=str(getpid.return_value)),
        call(InsightsConstants.ppidfile, content=get_parent_process.return_value)
    ))


@patch("insights.client.write_to_disk")
@patch("insights.client.os.getpid")
def test_write_pidfile_not_called(getpid, write_to_disk):
    '''
    Test that the pidfile is not written when
    called from a phase (setup_logging=True)
    '''
    InsightsClient(from_phase=True)
    getpid.assert_not_called()
    write_to_disk.assert_not_called()
