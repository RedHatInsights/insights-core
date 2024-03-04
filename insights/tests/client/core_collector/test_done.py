from mock.mock import patch

from insights.client.config import InsightsConfig
from insights.client.core_collector import CoreCollector


@patch('insights.client.core_collector.InsightsArchive')
def test_archive_returned(_):
    c = InsightsConfig()
    d = CoreCollector(c)
    ret = d.done()
    d.archive.create_tar_file.assert_called_once()
    assert ret == d.archive.create_tar_file.return_value


@patch('insights.client.core_collector.InsightsArchive')
def test_dir_returned(_):
    c = InsightsConfig(output_dir='test')
    d = CoreCollector(c)
    ret = d.done()
    d.archive.create_tar_file.assert_not_called()
    assert ret == d.archive.archive_dir
