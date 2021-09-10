from insights.client.config import InsightsConfig
from insights.contrib.soscleaner import SOSCleaner
from insights.client.data_collector import DataCollector
from insights.client.archive import CleanOptions
from mock.mock import patch, Mock


@patch('insights.client.data_collector.InsightsArchive')
def test_archive_returned(InsightsArchive):
    c = InsightsConfig()
    r = {}   # rm_conf
    a = InsightsArchive(c, r)
    d = DataCollector(c, a)
    ret = d.done()
    d.archive.create_tar_file.assert_called_once()
    assert ret == d.archive.create_tar_file.return_value


@patch('insights.client.data_collector.InsightsArchive')
def test_dir_returned(InsightsArchive):
    c = InsightsConfig(output_dir='test')
    r = {}   # rm_conf
    a = InsightsArchive(c, r)
    d = DataCollector(c, a)
    ret = d.done()
    d.archive.create_tar_file.assert_called_once()
    assert ret == d.archive.create_tar_file.return_value