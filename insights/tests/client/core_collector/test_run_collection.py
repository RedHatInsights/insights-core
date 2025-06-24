from mock.mock import patch

from insights.client.config import InsightsConfig
from insights.client.core_collector import CoreCollector


@patch('insights.client.core_collector.logger')
@patch('insights.client.core_collector.systemd_notify_init_thread', return_value=None)
@patch('insights.client.core_collector.InsightsArchive.create_archive_dir', return_value=None)
@patch('insights.client.core_collector.collect', return_value=None)
def test_run_collection(collect, create_archive_dir, systemd_notify_init_thread, logger):
    conf = InsightsConfig()
    cc = CoreCollector(conf)
    cc.run_collection({})
    systemd_notify_init_thread.assert_called_once()
    create_archive_dir.assert_called_once()
    collect.collect.assert_called_once()
    logger.debug.assert_called_with('Core collection finished.')
