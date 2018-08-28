# -*- coding: UTF-8 -*-

from insights.client.collection_rules import InsightsUploadConf
from insights.client.config import InsightsConfig


def insights_upload_conf(*args, **kwargs):
    """
    Instantiates InsightsUploadConf with a config created with given arguments.
    """
    config = InsightsConfig(*args, **kwargs)
    return InsightsUploadConf(config)
