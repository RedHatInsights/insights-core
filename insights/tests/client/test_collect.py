# -*- coding: UTF-8 -*-
from mock.mock import patch

from insights.client.client import collect
from insights.client.config import InsightsConfig

conf_remove_file = "/tmp/remove.conf"
conf_file_redaction_file = "/tmp/file-redaction.yaml"
conf_file_content_redaction_file = "/tmp/file-content-redaction.yaml"
removed_files = ["/etc/some_file", "/tmp/another_file"]


def collect_args(*insights_config_args, **insights_config_custom_kwargs):
    """
    Instantiates InsightsConfig with a default logging_file argument.
    """
    all_insights_config_kwargs = {
        "logging_file": "/tmp/insights.log",
        "remove_file": conf_remove_file,
        "redaction_file": conf_file_redaction_file,
        "content_redaction_file": conf_file_content_redaction_file,
    }
    all_insights_config_kwargs.update(insights_config_custom_kwargs)
    return InsightsConfig(*insights_config_args, **all_insights_config_kwargs)


def patch_get_rm_conf():
    """
    Mocks InsightsUploadConf.get_rm_conf so it returns a fixed configuration.
    """

    def decorator(old_function):
        patcher = patch("insights.client.client.InsightsUploadConf.get_rm_conf")
        return patcher(old_function)

    return decorator


def patch_core_collector():
    """
    Replaces CoreCollector with a dummy mock.
    """

    def decorator(old_function):
        patcher = patch("insights.client.client.CoreCollector")
        return patcher(old_function)

    return decorator


@patch_core_collector()
@patch_get_rm_conf()
def test_get_rm_conf_file(get_rm_conf, core_collector):
    """
    Load configuration of files removed from collection when collection rules are loaded from a file.
    """
    config = collect_args()
    collect(config)

    get_rm_conf.assert_called_once_with()


@patch_core_collector()
@patch_get_rm_conf()
def test_core_collector_file(get_rm_conf, core_collector):
    """
    Configuration from a file is passed to the CoreCollector along with removed files configuration.
    """
    config = collect_args()
    collect(config)

    rm_conf = get_rm_conf.return_value
    core_collector.return_value.run_collection.assert_called_once_with(rm_conf)
    core_collector.return_value.done.assert_called_once_with()


@patch("insights.client.client.CoreCollector")
@patch_get_rm_conf()
def test_correct_collector_loaded(get_rm_conf, core_collector):
    '''
    Verify that core collection is loaded
    '''
    config = collect_args()
    collect(config)

    core_collector.return_value.run_collection.assert_called()

    core_collector.return_value.run_collection.reset_mock()
