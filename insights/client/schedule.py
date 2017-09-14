"""
Module responsible for scheduling Insights data collection in cron
"""
import os
import logging

from config import CONFIG as config
from constants import InsightsConstants as constants

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


class InsightsSchedule(object):

    def __init__(self, source=None, target='/etc/cron.daily/' + APP_NAME):
        self.target = target
        if source:
            self.source = source
        else:
            extension = '-container' if config['container_mode'] else ''
            self.source = '/etc/%s/%s%s.cron' % (APP_NAME, APP_NAME, extension)

    @property
    def active(self):
        return os.path.isfile(self.target)

    def set_daily(self):
        logger.debug('Setting schedule to daily')
        try:
            if not os.path.exists(self.target):
                os.symlink(self.source, self.target)
                return True
        except OSError:
            logger.exception('Could not link cron.daily')

    def remove_scheduling(self):
        logger.debug('Removing all cron tasks')
        try:
            if os.path.exists(self.target):
                os.remove(self.target)
                return True
        except OSError:
            logger.exception('Could not remove cron.daily')
