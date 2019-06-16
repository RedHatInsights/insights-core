# -*- coding: UTF-8 -*-
#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
