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

    def __init__(self, filename='/etc/cron.daily/' + APP_NAME):
        self.cron_daily = filename

    @property
    def active(self):
        return os.path.isfile(self.cron_daily)

    def set_daily(self):
        logger.debug('Setting schedule to daily')
        try:
            extension = '-container' if config['container_mode'] else ''
            filename = '/etc/%s/%s%s.cron' % (APP_NAME, APP_NAME, extension)
            if not os.path.exists(self.cron_daily):
                os.symlink(filename, self.cron_daily)
                return True
        except OSError:
            logger.exception('Could not link cron.daily')

    def remove_scheduling(self):
        logger.debug('Removing all cron tasks')
        try:
            os.remove(self.cron_daily)
        except OSError:
            logger.exception('Could not remove cron.daily')
