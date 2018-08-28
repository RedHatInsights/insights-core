# -*- coding: UTF-8 -*-

from .helpers import insights_upload_conf
from mock.mock import call, patch
from pytest import raises


collection_rules_file = "/tmp/collection_rules"
collection_fallback_file = "/tmp/collection_fallback"


def patch_collection_rules_file():
    """
    Makes collection_rules_file contain a fixed path.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.constants.collection_rules_file", collection_rules_file)
        return patcher(old_function)
    return decorator


def patch_collection_fallback_file():
    """
    Makes collection_fallback_file contain a fixed path.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.constants.collection_fallback_file", collection_fallback_file)
        return patcher(old_function)
    return decorator


def patch_try_disk(return_values):
    """
    Makes try_disk sequentially return the passed contents.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.InsightsUploadConf.try_disk", side_effect=return_values)
        return patcher(old_function)
    return decorator


@patch_try_disk([{"version": "1.2.3"}])
@patch_collection_rules_file()
def test_collection_rules_file_try_disk(try_disk):
    """
    Collection rules are loaded from the default file while performing signature validation.
    """
    gpg = "perhaps"
    upload_conf = insights_upload_conf(gpg=gpg)
    upload_conf.get_conf_file()

    try_disk.assert_called_once_with(collection_rules_file, gpg)


@patch_try_disk([{"version": None}])
def test_collection_rules_file_no_version_error(try_disk):
    """
    Collection rules from the default file are rejected if they don't specify version.
    """
    upload_conf = insights_upload_conf()

    with raises(ValueError):
        upload_conf.get_conf_file()


@patch_try_disk([{"version": "1.2.3"}])
@patch_collection_rules_file()
def test_return_collection_rules(try_disk):
    """
    Collection rules from the default file are returned with the filename appended to the data.
    """
    upload_conf = insights_upload_conf()

    assert upload_conf.get_conf_file() == {"version": "1.2.3", "file": collection_rules_file}


@patch_try_disk([None, {"version": "1.2.3"}])
@patch_collection_fallback_file()
@patch_collection_rules_file()
def test_fallback_file_try_disk(try_disk):
    """
    If there are no collection rules in the default file, they are loaded from the fallback file while performing
    signature validation.
    """
    gpg = "perhaps"
    upload_conf = insights_upload_conf(gpg=gpg)

    upload_conf.get_conf_file()

    calls = [call(collection_rules_file, gpg), call(collection_fallback_file, gpg)]
    try_disk.assert_has_calls(calls)


@patch_try_disk([None, {"version": None}])
def test_fallback_file_no_version_error(try_disk):
    """
    Collection rules from the fallback file are rejected if they don't specify version.
    """
    upload_conf = insights_upload_conf()

    with raises(ValueError):
        upload_conf.get_conf_file()


@patch_try_disk([None, {"version": "1.2.3"}])
@patch_collection_fallback_file()
def test_return_collection_fallback(try_disk):
    """
    Collection rules from the fallback file are returned with the filename appended to the data.
    """
    upload_conf = insights_upload_conf()

    assert upload_conf.get_conf_file() == {"version": "1.2.3", "file": collection_fallback_file}


@patch_try_disk([None, None])
def test_no_file_error(try_disk):
    """
    An error is raised if there are no collection rules neither in the default nor the fallback file.
    """
    upload_conf = insights_upload_conf()

    with raises(ValueError):
        upload_conf.get_conf_file()
