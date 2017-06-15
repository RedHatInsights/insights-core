"""
Module responsible for scheduling Insights data collection
"""
import os
import logging
from client_config import InsightsClient
from constants import InsightsConstants as constants

CRON_DAILY = '/etc/cron.daily/'
CRON_WEEKLY = '/etc/cron.weekly/'
APP_NAME = constants.app_name
logger = logging.getLogger(APP_NAME)


class InsightsSchedule(object):
    """
    Set the cron schedule
    """
    def __init__(self, set_cron=True):
        if set_cron and not self.already_linked():
            self.set_daily()

    def already_linked(self):
        """
        Determine if we are already scheduled
        """
        if os.path.isfile(CRON_WEEKLY + APP_NAME):
            logger.debug('Found cron.weekly')
            return True
        elif os.path.isfile(CRON_DAILY + APP_NAME):
            logger.debug('Found cron.daily')
            return True
        else:
            return False

    def set_daily(self):
        """
        Set cron task to daily
        """
        logger.debug('Setting schedule to daily')
        try:
            os.remove(CRON_WEEKLY + APP_NAME)
        except OSError:
            logger.debug('Could not remove cron.weekly')

        try:
            os.symlink(
                '/etc/' + APP_NAME + '/' + APP_NAME + (
                    '-container' if InsightsClient.options.container_mode else ''
                ) + '.cron',
                CRON_DAILY + APP_NAME)
        except OSError:
            logger.debug('Could not link cron.daily')

    def remove_scheduling(self):
        '''
        Delete cron tasks
        '''
        logger.debug('Removing all cron tasks')
        try:
            os.remove(CRON_WEEKLY + APP_NAME)
        except OSError:
            logger.debug('Could not remove cron.weekly')
        try:
            os.remove(CRON_DAILY + APP_NAME)
        except OSError:
            logger.debug('Could not remove cron.daily')
