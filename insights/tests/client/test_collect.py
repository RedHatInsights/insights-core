# -*- coding: UTF-8 -*-
from mock.mock import patch

from insights.client.client import collect
from insights.client.config import InsightsConfig


@patch("insights.client.client.InsightsUploadConf.create_report")
@patch("insights.client.client.CoreCollector")
@patch("insights.client.client.InsightsUploadConf.get_rm_conf")
@patch("insights.client.client.get_branch_info")
def test_collector_file(get_branch_info, get_rm_conf, collector, create_report):
    """
    CoreCollector is loaded and a None value for spec_conf
    """
    config = InsightsConfig()
    collect(config)

    get_branch_info.assert_called_once_with(config)
    get_rm_conf.assert_called_once_with()
    create_report.assert_called_once_with()

    rm_conf = get_rm_conf.return_value
    branch_info = get_branch_info.return_value
    blacklist_report = create_report.return_value

    collector.return_value.run_collection.assert_called_once_with(rm_conf, branch_info, blacklist_report)
    collector.return_value.done.assert_called_once_with()
