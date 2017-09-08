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
logger = logging.getLogger(APP_NAME)


class InsightsSchedule(object):
    """
    Set the cron schedule
    """
    def __init__(self):
        pass

    def already_linked(self, cronfile=None):
        """
        Determine if we are already scheduled
        """
        if cronfile is not None:
            if os.path.isfile(cronfile):
                logger.debug("Found linked file %s.", cronfile)
                return True
            else:
                logger.debug("Did not find linked file %s.", cronfile)
                return False
        else:
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
                    '-container' if config['container_mode'] else ''
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
