# -*- coding: UTF-8 -*-

from insights.client.client import collect
from insights.client.config import InsightsConfig
from json import dump as json_dump
from mock.mock import Mock, patch, PropertyMock
from tempfile import TemporaryFile


stdin_payload = {"uploader.json": "some JSON", "sig": "some signature"}


def collect_args(*insights_config_args, **insights_config_custom_kwargs):
    """
    Instantiates InsightsConfig with a default logging_file argument.
    """
    insights_config_all_kwargs = {"logging_file": "/tmp/insights.log"}
    insights_config_all_kwargs.update(insights_config_custom_kwargs)
    return InsightsConfig(*insights_config_args, **insights_config_all_kwargs), Mock()


def patch_get_branch_info(old_function):
    """
    Sets a static response to get_branch_info method.
    """
    patcher = patch("insights.client.client.get_branch_info")
    return patcher(old_function)


def patch_stdin(old_function):
    """
    Sets a static JSON data to stdin.
    """
    stdin = TemporaryFile("w+t")
    json_dump(stdin_payload, stdin)
    stdin.seek(0)

    patcher = patch("insights.client.client.sys.stdin", new_callable=PropertyMock(return_value=stdin))
    return patcher(old_function)


def patch_get_conf_stdin(old_function):
    """
    Mocks InsightsUploadConf.get_conf_stdin.
    """
    patcher = patch("insights.client.client.InsightsUploadConf.get_conf_stdin")
    return patcher(old_function)


def patch_get_conf_file(old_function):
    """
    Mocks InsightsUploadConf.get_conf_file so it returns a fixed configuration.
    """
    patcher = patch("insights.client.client.InsightsUploadConf.get_conf_file")
    return patcher(old_function)


def patch_get_rm_conf(old_function):
    """
    Mocks InsightsUploadConf.get_rm_conf so it returns a fixed configuration.
    """
    patcher = patch("insights.client.client.InsightsUploadConf.get_rm_conf")
    return patcher(old_function)


def patch_data_collector(old_function):
    """
    Replaces DataCollector with a dummy mock.
    """
    patcher = patch("insights.client.client.DataCollector")
    return patcher(old_function)


@patch_data_collector
@patch_get_conf_file
@patch_get_conf_stdin
@patch_get_branch_info
def test_get_conf_file(get_branch_info, get_conf_stdin, get_conf_file, data_collector):
    """
    If there is no config passed via stdin, it is loaded from a file instead.
    """
    config, pconn = collect_args()
    collect(config, pconn)

    get_conf_stdin.assert_not_called()
    get_conf_file.assert_called_once_with()


@patch_data_collector
@patch_get_conf_file
@patch_get_conf_stdin
@patch_stdin
@patch_get_branch_info
def test_get_conf_stdin(get_branch_info, stdin, get_conf_stdin, get_conf_file, data_collector):
    """
    If there is config passed via stdin, use it and do not look for it in files.
    """
    config, pconn = collect_args(from_stdin=True)
    collect(config, pconn)

    get_conf_stdin.assert_called_once_with(stdin_payload)
    get_conf_file.assert_not_called()


@patch_data_collector
@patch_get_rm_conf
@patch_get_conf_stdin
@patch_stdin
@patch_get_branch_info
def test_get_rm_conf_stdin(get_branch_info, stdin, get_conf_stdin, get_rm_conf, data_collector):
    """
    Load configuration of files removed from collection when collection rules are loaded from stdin.
    """
    config, pconn = collect_args(from_stdin=True)
    collect(config, pconn)

    get_rm_conf.assert_called_once_with()


@patch_data_collector
@patch_get_rm_conf
@patch_get_conf_file
@patch_get_branch_info
def test_get_rm_conf_file(get_branch_info, get_conf_file, get_rm_conf, data_collector):
    """
    Load configuration of files removed from collection when collection rules are loaded from a file.
    """
    config, pconn = collect_args(from_stdin=False)
    collect(config, pconn)

    get_rm_conf.assert_called_once_with()


@patch_data_collector
@patch_get_rm_conf
@patch_get_conf_stdin
@patch_stdin
@patch_get_branch_info
def test_data_collector_stdin(get_branch_info, stdin, get_conf_stdin, get_rm_conf, data_collector):
    """
    Configuration from stdin is passed to the DataCollector along with removed files configuration.
    """
    config, pconn = collect_args(from_stdin=True)
    collect(config, pconn)

    collection_rules = get_conf_stdin.return_value
    rm_conf = get_rm_conf.return_value
    branch_info = get_branch_info.return_value
    data_collector.return_value.run_collection.assert_called_once_with(collection_rules, rm_conf, branch_info)
    data_collector.return_value.done.assert_called_once_with(collection_rules, rm_conf)


@patch_data_collector
@patch_get_rm_conf
@patch_get_conf_file
@patch_get_branch_info
def test_data_collector_file(get_branch_info, get_conf_file, get_rm_conf, data_collector):
    """
    Configuration from a file is passed to the DataCollector along with removed files configuration.
    """
    config, pconn = collect_args(from_stdin=False)
    collect(config, pconn)

    collection_rules = get_conf_file.return_value
    rm_conf = get_rm_conf.return_value
    branch_info = get_branch_info.return_value
    data_collector.return_value.run_collection.assert_called_once_with(collection_rules, rm_conf, branch_info)
    data_collector.return_value.done.assert_called_once_with(collection_rules, rm_conf)
