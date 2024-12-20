import os

from insights.client import InsightsClient
from insights.client.constants import InsightsConstants
from mock.mock import call
from mock.mock import patch


@patch("insights.client.atexit.register")
@patch("insights.client.write_to_disk")
@patch("insights.client.get_parent_process")
def test_write_pidfile(get_parent_process, write_to_disk, register):
    '''
    Test writing of the pidfile when InsightsClient
    is called initially (when from_phase=False)
    '''
    InsightsClient(from_phase=False)
    write_to_disk.assert_has_calls((
        call(InsightsConstants.pidfile, content=str(os.getpid())),
        call(InsightsConstants.ppidfile, content=get_parent_process.return_value)
    ))


@patch("insights.client.atexit.register")
@patch("insights.client.write_to_disk")
def test_atexit_delete_pidfile(write_to_disk, register):
    '''
    Test delete of the pidfile is registered when InsightsClient
    is called initially (when from_phase=False)
    '''
    InsightsClient(from_phase=False)
    register.assert_has_calls((
        call(write_to_disk, InsightsConstants.pidfile, delete=True),
        call(write_to_disk, InsightsConstants.ppidfile, delete=True)
    ))


@patch("insights.client.write_to_disk")
@patch("insights.client.get_parent_process")
def test_write_pidfile_not_called(get_parent_process, write_to_disk):
    '''
    Test that the pidfile is not written when
    called from a phase (from-phase=True)
    '''
    InsightsClient(from_phase=True)
    get_parent_process.assert_not_called()
    write_to_disk.assert_not_called()


@patch("insights.client.atexit.register")
def test_atexit_delete_pidfile_not_called(register):
    '''
    Test that delete of the pidfile is not registered when
    called from a phase (from_phase=True)
    '''
    InsightsClient(from_phase=True)
    register.assert_not_called()
