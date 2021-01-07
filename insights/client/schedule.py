"""
Module responsible for scheduling Insights data collection in cron
"""
from __future__ import absolute_import
import os
import logging

from .constants import InsightsConstants as constants
from .utilities import run_command_get_output

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


def cron_source(config):
    return '/etc/%s/%s%s.cron' % (APP_NAME, APP_NAME, '')


class InsightsSchedulerCron(object):

    def __init__(self, config, source=None, target='/etc/cron.daily/' + APP_NAME):
        self.target = target
        self.source = source if source else cron_source(config)

    @property
    def active(self):
        if os.path.exists(self.source):
            return os.path.isfile(self.target)
        return False

    def schedule(self):
        logger.debug('Scheduling cron.daily')
        try:
            if not os.path.exists(self.target):
                os.symlink(self.source, self.target)
            return True
        except OSError:
            logger.exception('Could not link cron.daily')
            return False

    def remove_scheduling(self):
        logger.debug('Removing all cron tasks')
        try:
            # Remove symlinks in the case of rhel 6 running cron jobs
            if os.path.exists(self.target):
                os.remove(self.target)
            return True
        except OSError:
            logger.exception('Could not remove cron.daily')
            return False


class InsightsSchedulerSystemd(object):
    SYSTEMD_TIMERS = ("insights-client", "insights-client-checkin")

    @staticmethod
    def _run_systemctl_command(args):
        command = 'systemctl %s' % args
        logger.debug('Running command %s', command)
        try:
            result = run_command_get_output(command)
        except OSError:
            logger.exception('Could not run %s', command)
            return None
        else:
            logger.debug("Status: %s", result['status'])
            logger.debug("Output: %s", result['output'])
            return result

    @classmethod
    def _run_systemctl_commands(cls, args):
        results = {}

        for timer in cls.SYSTEMD_TIMERS:
            unit = '%s.timer' % timer
            command = '%s %s' % (args, unit)
            result = cls._run_systemctl_command(command)
            if not result:
                return None
            results[timer] = result

        return results

    @property
    def active(self):
        results = self._run_systemctl_commands('is-enabled')
        return results and all(result['status'] == 0 for result in results.values())

    def schedule(self):
        logger.debug('Starting systemd timers')
        results = self._run_systemctl_commands('enable --now')
        return results and self.active is True

    def remove_scheduling(self):
        logger.debug('Stopping all systemd timers')
        results = self._run_systemctl_commands('disable --now')
        return results and self.active is False


def get_scheduler(config, source=None, target='/etc/cron.daily/' + APP_NAME):
    source = source if source else cron_source(config)
    if os.path.exists(source):
        return InsightsSchedulerCron(config, source, target)
    else:
        return InsightsSchedulerSystemd()
