import six
import mock
from insights.client.constants import InsightsConstants as constants
from insights.client.config import InsightsConfig
from insights.client.core_collector import CoreCollector
from mock.mock import call
from mock.mock import patch


@patch('insights.client.core_collector.os.remove')
@patch('insights.client.core_collector.InsightsArchive')
def test_egg_release_file_read_and_written(archive, remove):
    '''
    Verify the egg release file is read from file and
    written to the archive
    '''
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True) as mock_open:
        mock_open.side_effect = [mock.mock_open(read_data='/testvalue').return_value]
        c = InsightsConfig()
        d = CoreCollector(c)
        d._write_egg_release()
        remove.assert_called_once_with(constants.egg_release_file)
        d.archive.add_metadata_to_archive.assert_called_once_with('/testvalue', '/egg_release')


@patch('insights.client.core_collector.os.remove')
@patch('insights.client.core_collector.InsightsArchive')
def test_egg_release_file_read_and_written_no_delete(archive, remove):
    '''
    Verify the egg release file is read from file and
    written to the archive, even if the file cannot be deleted
    '''
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    remove.side_effect = OSError('test')

    with patch(open_name, create=True) as mock_open:
        mock_open.side_effect = [mock.mock_open(read_data='/testvalue').return_value]
        c = InsightsConfig()
        d = CoreCollector(c)
        d._write_egg_release()
        remove.assert_called_once_with(constants.egg_release_file)
        d.archive.add_metadata_to_archive.assert_called_once_with('/testvalue', '/egg_release')


@patch('insights.client.core_collector.os.remove')
@patch('insights.client.core_collector.InsightsArchive')
def test_egg_release_file_read_and_written_no_read(archive, remove):
    '''
    Verify that when the egg release file cannot be read,
    a blank string is written to the archive
    '''
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    remove.side_effect = OSError('test')

    with patch(open_name, create=True) as mock_open:
        mock_open.side_effect = IOError('test')
        c = InsightsConfig()
        d = CoreCollector(c)
        d._write_egg_release()
        remove.assert_called_once_with(constants.egg_release_file)
        d.archive.add_metadata_to_archive.assert_called_once_with('', '/egg_release')


@patch('insights.client.core_collector.os.remove')
@patch('insights.client.core_collector.InsightsArchive')
def test_egg_release_file_read_memory_error(archive, remove):
    '''
    Verify that a memory error on the egg release file read is not
    fatal.
    '''
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True) as mock_open:
        file_mock = mock.mock_open().return_value
        file_mock.read.side_effect = MemoryError()
        mock_open.side_effect = [file_mock]
        c = InsightsConfig()
        d = CoreCollector(c)
        d._write_egg_release()
        remove.assert_called_once_with(constants.egg_release_file)
        d.archive.add_metadata_to_archive.assert_called_once_with('', '/egg_release')


@patch('insights.client.core_collector.os.remove')
@patch(
    'insights.client.core_collector.InsightsArchive',
    **{'return_value.add_metadata_to_archive.side_effect': [OSError('[Errno 28] No space left on device'), None]})
def test_egg_release_file_write_os_error(archive, remove):
    '''
    Verify that an OS Error (e.g. no space left) on the egg release file
    write is not fatal - an empty file is written instead.
    '''
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True) as mock_open:
        mock_open.side_effect = [mock.mock_open(read_data='/testvalue').return_value]
        c = InsightsConfig()
        d = CoreCollector(c)
        d._write_egg_release()
        remove.assert_called_once_with(constants.egg_release_file)
        failed_call = call('/testvalue', '/egg_release')
        rescue_call = call('', '/egg_release')
        expected_calls = [failed_call, rescue_call]
        d.archive.add_metadata_to_archive.assert_has_calls(expected_calls)
