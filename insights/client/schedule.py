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
    extension = '-container' if config.analyze_container else ''
    return '/etc/%s/%s%s.cron' % (APP_NAME, APP_NAME, extension)


class InsightsSchedulerCron(object):

    def __init__(self, config, source=None, target='/etc/cron.daily/' + APP_NAME):
        self.target = target
        self.source = source if source else cron_source(config)

    @property
    def active(self):
        if os.path.exists(self.source):
            return os.path.isfile(self.target)
        return False

    def set_daily(self):
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

    @property
    def active(self):
        try:
            systemctl_status = run_command_get_output('systemctl is-enabled insights-client.timer')
            return systemctl_status['status'] == 0
        except OSError:
            logger.exception('Could not get systemd status')
            return False

    def set_daily(self):
        logger.debug('Starting systemd timer')
        try:
            # Start timers in the case of rhel 7 running systemd
            systemctl_timer = run_command_get_output('systemctl start insights-client.timer')
            systemctl_timer = run_command_get_output('systemctl enable insights-client.timer')
            logger.debug("Starting Insights Client systemd timer.")
            logger.debug("Status: %s", systemctl_timer['status'])
            logger.debug("Output: %s", systemctl_timer['output'])
            return self.active
        except OSError:
            logger.exception('Could not start systemd timer')
            return False

    def remove_scheduling(self):
        logger.debug('Stopping all systemd timers')
        try:
            # Stop timers in the case of rhel 7 running systemd
            systemctl_timer = run_command_get_output('systemctl disable insights-client.timer')
            systemctl_timer = run_command_get_output('systemctl stop insights-client.timer')
            logger.debug("Stopping Insights Client systemd timer.")
            logger.debug("Status: %s", systemctl_timer['status'])
            logger.debug("Output: %s", systemctl_timer['output'])
            return not self.active
        except OSError:
            logger.exception('Could not stop systemd timer')
            return False


def get_scheduler(config, source=None, target='/etc/cron.daily/' + APP_NAME):
    source = source if source else cron_source(config)
    if os.path.exists(source):
        return InsightsSchedulerCron(config, source, target)
    else:
        return InsightsSchedulerSystemd()
