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
    ALL_TIMERS = ("insights-client", "insights-client-checkin")

    def __init__(self):
        """
        Looks for loaded timers using `systemctl show`, stores their names in self.loaded_timers. No loaded timers
        produce (). If an error occurs, self.loaded_timers becomes None and all methods (schedule, remove_scheduling,
        active) then return None.
        """
        results = self._run_systemctl_commands(self.ALL_TIMERS, "show", "--property", "LoadState")
        if not results:
            self.loaded_timers = None  # Command failed.
        else:
            self.loaded_timers = tuple(
                timer
                for timer, result in results.items()
                if result["status"] == 0 and result["output"] == "LoadState=loaded\n"
            )
            if not self.loaded_timers:
                logger.warning("No loaded timers found")

    @staticmethod
    def _run_systemctl_command(*args):
        cmd_args = " ".join(args)
        command = "systemctl %s" % cmd_args
        logger.debug("Running command %s", command)
        try:
            result = run_command_get_output(command)
        except OSError:
            logger.exception("Could not run %s", command)
            return None
        else:
            logger.debug("Status: %s", result["status"])
            logger.debug("Output: %s", result["output"])
            return result

    @classmethod
    def _run_systemctl_commands(cls, timers, *args):
        if timers is None:
            return None  # Could not list loaded timers on init.

        results = {}

        for timer in timers:
            unit = "%s.timer" % timer
            command_args = args + (unit,)
            result = cls._run_systemctl_command(*command_args)
            if not result:
                return None  # Command failed.
            results[timer] = result

        return results

    @property
    def active(self):
        """
        Runs systemctl is-enabled for each loaded timers. Returns True if all loaded timers are enabled, None if any
        systemctl command fails - here or in init.
        """
        results = self._run_systemctl_commands(self.loaded_timers, "is-enabled")
        return results and all(result["status"] == 0 for result in results.values())

    def schedule(self):
        """
        Runs systemctl enable --now for each loaded timers. Returns True if all loaded timers are successfully enabled,
        False if any of them remains inactive. If no timer is loaded, returns {}, if any systemctl command fails - here
        or in init - returns None. Both falsey as nothing has been actually enabled.
        """
        logger.debug("Starting systemd timers")
        results = self._run_systemctl_commands(self.loaded_timers, "enable", "--now")
        return results and self.active

    def remove_scheduling(self):
        """
        Runs systemctl disable --now for each loaded timers. Returns True if all loaded timers are successfully
        disabled, False if any of them remains active. If no timer is loaded, returns {}, if any systemctl command
        fails - here or in init - returns None. Both falsey as nothing has been actually disabled.
        """
        logger.debug("Stopping all systemd timers")
        results = self._run_systemctl_commands(self.loaded_timers, "disable", "--now")

        if results:
            active = self.active
            return None if active is None else not active
        else:
            return results


def get_scheduler(config, source=None, target='/etc/cron.daily/' + APP_NAME):
    source = source if source else cron_source(config)
    if os.path.exists(source):
        return InsightsSchedulerCron(config, source, target)
    else:
        return InsightsSchedulerSystemd()
