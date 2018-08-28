# -*- coding: UTF-8 -*-

from .helpers import insights_upload_conf
from mock.mock import patch
from pytest import raises


collection_rules = {"version": "1.2.3"}
collection_rules_file = "/tmp/collection-rules"


@patch("insights.client.collection_rules.InsightsUploadConf.get_conf_file")
@patch("insights.client.collection_rules.InsightsUploadConf.get_collection_rules", return_value=None)
def test_load_from_file(get_collection_rules, get_conf_file):
    """
    Falls back to file if collection rules are not downloaded.
    """
    upload_conf = insights_upload_conf()
    result = upload_conf.get_conf_update()

    get_collection_rules.assert_called_once_with()
    get_conf_file.assert_called_once_with()
    assert result is get_conf_file.return_value


@patch("insights.client.collection_rules.InsightsUploadConf.get_conf_file")
@patch("insights.client.collection_rules.InsightsUploadConf.get_collection_rules", return_value={"some": "value"})
def test_no_version_error(get_collection_rules, get_conf_file):
    """
    Error is raised if there is no version in the collection rules loaded from URL.
    """
    upload_conf = insights_upload_conf()
    with raises(ValueError):
        upload_conf.get_conf_update()

    get_collection_rules.assert_called_once_with()
    get_conf_file.assert_not_called()


@patch("insights.client.collection_rules.constants.collection_rules_file", collection_rules_file)
@patch("insights.client.collection_rules.InsightsUploadConf.get_conf_file")
@patch("insights.client.collection_rules.InsightsUploadConf.get_collection_rules", return_value=collection_rules)
def test_load_from_url(get_collection_rules, get_conf_file):
    """
    Return collection rules loaded from URL with added file path.
    """
    upload_conf = insights_upload_conf()
    actual_result = upload_conf.get_conf_update()

    get_collection_rules.assert_called_once_with()
    get_conf_file.assert_not_called()

    expected_result = collection_rules.copy()
    expected_result["file"] = collection_rules_file

    assert actual_result == expected_result
