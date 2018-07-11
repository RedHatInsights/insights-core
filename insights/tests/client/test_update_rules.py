# -*- coding: UTF-8 -*-

from insights.client.config import InsightsConfig
from insights.client.client import update_rules
from mock.mock import call, Mock, patch
from pytest import raises


collection_rules_file = "/tmp/collection_rules"
collection_fallback_file = "/tmp/fallback"


def update_rules_args(*insights_config_args, **insights_config_custom_kwargs):
    """
    Instantiates InsightsConfig with a default logging_file argument.
    """
    insights_config_all_kwargs = {"logging_file": "/tmp/insights.log"}
    insights_config_all_kwargs.update(insights_config_custom_kwargs)
    return InsightsConfig(*insights_config_args, **insights_config_all_kwargs), Mock()


def patch_get_collection_rules(collection_rules):
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.InsightsUploadConf.get_collection_rules",
                        return_value=collection_rules)
        return patcher(old_function)
    return decorator


def patch_get_connection():
    def decorator(old_function):
        patcher = patch("insights.client.client.get_connection", return_value=None)
        return patcher(old_function)
    return decorator


def patch_collection_rules_file():
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.constants.collection_rules_file", collection_rules_file)
        return patcher(old_function)
    return decorator


def patch_collection_fallback_file():
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.constants.collection_fallback_file", collection_fallback_file)
        return patcher(old_function)
    return decorator


def patch_try_disk(disk_confs):
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.InsightsUploadConf.try_disk", side_effect=disk_confs)
        return patcher(old_function)
    return decorator


@patch_get_collection_rules({"version": "1.2.3"})
@patch_get_connection()
def test_no_connection_error(get_connection, get_collection_rules):
    config, pconn = update_rules_args()
    with raises(ValueError):
        update_rules(config, None)


@patch_get_collection_rules({"version": "1.2.3"})
def test_get_collection_rules(get_collection_rules):
    config, pconn = update_rules_args()
    update_rules(config, pconn)
    get_collection_rules.assert_called_once_with()


@patch_get_collection_rules({"version": None})
def test_dyn_conf_no_version_error(get_collection_rules):
    config, pconn = update_rules_args()
    with raises(ValueError):
        update_rules(config, pconn)


@patch_try_disk([{"version": "1.2.3"}])
@patch_collection_rules_file()
@patch_get_collection_rules(None)
def test_collection_rules_file_conf_try_disk(get_collection_rules, try_disk):
    gpg = "perhaps"
    config, pconn = update_rules_args(gpg=gpg)
    update_rules(config, pconn)
    try_disk.assert_called_once_with(collection_rules_file, gpg)


@patch_try_disk([{"version": None}])
@patch_get_collection_rules({"version": None})
def test_collection_rules_file_conf_no_version_error(get_collection_rules, try_disk):
    config, pconn = update_rules_args()
    with raises(ValueError):
        update_rules(config, pconn)


@patch_try_disk([None, {"version": "1.2.3"}])
@patch_collection_fallback_file()
@patch_collection_rules_file()
@patch_get_collection_rules(None)
def test_fallback_file_conf_try_disk(get_collection_rules, try_disk):
    gpg = "perhaps"
    config, pconn = update_rules_args(gpg=gpg)
    update_rules(config, pconn)
    calls = [call(collection_rules_file, gpg), call(collection_fallback_file, gpg)]
    try_disk.assert_has_calls(calls)
    assert try_disk.call_count == len(calls)


@patch_try_disk([None, {"version": None}])
@patch_get_collection_rules(None)
def test_fallback_file_conf_no_version_error(get_collection_rules, try_disk):
    config, pconn = update_rules_args()
    with raises(ValueError):
        update_rules(config, pconn)


@patch_try_disk([None, None])
@patch_get_collection_rules(None)
def test_no_file_conf_error(get_collection_rules, try_disk):
    config, pconn = update_rules_args()
    with raises(ValueError):
        update_rules(config, pconn)
