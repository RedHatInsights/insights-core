"""
Module responsible for scheduling Insights data collection
"""
import os
import logging

from config import CONFIG as config
from constants import InsightsConstants as constants

CRON_DAILY = '/etc/cron.daily/'
CRON_WEEKLY = '/etc/cron.weekly/'
APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


class InsightsSchedule(object):

    """
    Set the cron schedule
    """
    def __init__(self, set_cron=True):
        if set_cron and not self.already_linked(CRON_WEEKLY + APP_NAME) and not self.already_linked(CRON_DAILY + APP_NAME):
            self.set_schedule(CRON_DAILY + APP_NAME)

    def already_linked(self, cronfile):
        """
        Determine if we are already scheduled
        """
        if os.path.isfile(cronfile):
            logger.debug('Found %s' % cronfile)
            return True
        else:
            return False

    def set_schedule(self, cronfile):
        """
        Set cron task to daily
        """
        logger.debug('Setting schedule to daily')
        try:
            os.remove(CRON_WEEKLY + APP_NAME)
        except OSError:
            logger.debug('Could not remove cron.weekly')

        try:
            os.symlink('/etc/' + APP_NAME + '/' + APP_NAME + (
                       '-container' if config['container_mode'] else ''
                       ), cronfile)
        except OSError:
            logger.debug('Could not link cron.daily')

        if os.path.islink(cronfile):
            return True

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
