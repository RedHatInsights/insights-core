"""
Rules for data collection
"""
from __future__ import absolute_import
import logging
import six
import os
from six.moves import configparser as ConfigParser

from .constants import InsightsConstants as constants

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


# TODO remove and move rm.conf parsing elsewhere
class InsightsUploadConf(object):
    """
    Insights spec configuration from uploader.json
    """

    def __init__(self, config, conn=None):
        """
        Load config from parent
        """
        self.config = config
        self.remove_file = config.remove_file

    def get_rm_conf(self):
        """
        Get excluded files config from remove_file.
        """
        if not os.path.isfile(self.remove_file):
            return None

        # Convert config object into dict
        parsedconfig = ConfigParser.RawConfigParser()
        parsedconfig.read(self.remove_file)
        rm_conf = {}

        try:
            for item, value in parsedconfig.items('remove'):
                if six.PY3:
                    rm_conf[item] = value.strip().encode('utf-8').decode('unicode-escape').split(',')
                else:
                    rm_conf[item] = value.strip().decode('string-escape').split(',')
            return rm_conf
        except ConfigParser.NoSectionError:
            raise RuntimeError("[remove] heading missing in remove.conf")


if __name__ == '__main__':
    from .config import InsightsConfig
    print(InsightsUploadConf(InsightsConfig().load_all()))
