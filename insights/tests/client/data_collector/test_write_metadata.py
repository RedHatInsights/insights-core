import six
import mock
from insights.client.constants import InsightsConstants as constants
from insights.client.config import InsightsConfig
from insights.client.data_collector import DataCollector
from mock.mock import patch


@patch('insights.client.data_collector.os.remove')
@patch('insights.client.data_collector.InsightsArchive')
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
        d = DataCollector(c)
        d._write_egg_release()
        remove.assert_called_once_with(constants.egg_release_file)
        d.archive.add_metadata_to_archive.assert_called_once_with('/testvalue', '/egg_release')


@patch('insights.client.data_collector.os.remove')
@patch('insights.client.data_collector.InsightsArchive')
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
        d = DataCollector(c)
        d._write_egg_release()
        remove.assert_called_once_with(constants.egg_release_file)
        d.archive.add_metadata_to_archive.assert_called_once_with('/testvalue', '/egg_release')


@patch('insights.client.data_collector.os.remove')
@patch('insights.client.data_collector.InsightsArchive')
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
        d = DataCollector(c)
        d._write_egg_release()
        remove.assert_called_once_with(constants.egg_release_file)
        d.archive.add_metadata_to_archive.assert_called_once_with('', '/egg_release')
