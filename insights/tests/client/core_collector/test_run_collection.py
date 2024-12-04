from mock.mock import patch

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.client.core_collector import CoreCollector


@patch('insights.client.core_collector.logger')
@patch('insights.client.core_collector.CoreCollector._write_egg_release', return_value=None)
@patch('insights.client.core_collector.CoreCollector._write_blacklisted_specs', return_value=None)
@patch('insights.client.core_collector.CoreCollector._write_blacklist_report', return_value=None)
@patch('insights.client.core_collector.CoreCollector._write_tags', return_value=None)
@patch('insights.client.core_collector.CoreCollector._write_version_info', return_value=None)
@patch('insights.client.core_collector.CoreCollector._write_ansible_host', return_value=None)
@patch('insights.client.core_collector.CoreCollector._write_display_name', return_value=None)
@patch('insights.client.core_collector.CoreCollector._write_branch_info', return_value=None)
@patch('insights.client.core_collector.systemd_notify_init_thread', return_value=None)
@patch('insights.client.core_collector.InsightsArchive.create_archive_dir', return_value=None)
@patch('insights.client.core_collector.collect', return_value=None)
def test_run_collection(
        collect,
        create_archive_dir,
        systemd_notify_init_thread,
        _write_branch_info,
        _write_display_name,
        _write_ansible_host,
        _write_version_info,
        _write_tags,
        _write_blacklist_report,
        _write_blacklisted_specs,
        _write_egg_release,
        logger):
    conf = InsightsConfig()
    arch = InsightsArchive(conf)
    cc = CoreCollector(conf, arch)
    cc.run_collection({}, {}, {})
    create_archive_dir.assert_called_once()
    collect.collect.assert_called_once()
    logger.debug.assert_called_with('Metadata collection finished.')
