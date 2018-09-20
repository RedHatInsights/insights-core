# -*- coding: UTF-8 -*-

from insights.client.collection_rules import InsightsUploadConf
from insights.client.config import InsightsConfig
from pytest import fixture


@fixture
def insights_upload_conf():
    """
    Provides a function to instantiate InsightsUploadConf with a config created with given arguments.
    """
    def fixture(*args, **kwargs):
        """
        Instantiates InsightsUploadConf with a config created with given arguments.
        """
        config = InsightsConfig(*args, **kwargs)
        return InsightsUploadConf(config)
    return fixture
