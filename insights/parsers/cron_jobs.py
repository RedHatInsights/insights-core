"""
Cron job files under /etc/cron.d/*
==================================

This module contains the following parsers:

CronForeman - file ``/etc/cron.d/foreman``
------------------------------------------
"""

from insights.core import Parser
from insights.parsers import get_active_lines, ParseException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.cron_foreman)
class CronForeman(Parser, list):
    """
    Parse the ``/etc/cron.d/foreman`` file.

    Sample input::

        SHELL=/bin/sh
        PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

        RAILS_ENV=production
        FOREMAN_HOME=/usr/share/foreman

        # Clean up the session entries in the database
        15 23 * * *     foreman    /usr/sbin/foreman-rake db:sessions:clear 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log

        # Send out recurring notifications
        0 7 * * *       foreman    /usr/sbin/foreman-rake reports:daily 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log
        0 5 * * 0       foreman    /usr/sbin/foreman-rake reports:weekly 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log
        0 3 1 * *       foreman    /usr/sbin/foreman-rake reports:monthly 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log

        # Expire old reports
        30 7 * * *      foreman    /usr/sbin/foreman-rake reports:expire 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log
        30 7 * * *      foreman    /usr/sbin/foreman-rake reports:expire days=3 report_type=ForemanOpenscap::ArfReport 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log

        # Expire old audits
        0 1 * * *      foreman    /usr/sbin/foreman-rake audits:expire 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/audit.log

    Attributes:
        environment(dict): The environment variables.
        invalid_lines(list): A list of lines which are not in expected format.

    Raises:
        ParseException: When a line starts with '@', but the nickname is unknown.

    Examples:
        >>> type(foreman_jobs)
        <class 'insights.parsers.cron_jobs.CronForeman'>
        >>> len(foreman_jobs.environment)
        4
        >>> 'FOREMAN_HOME' in foreman_jobs.environment
        True
        >>> foreman_jobs.environment['FOREMAN_HOME']
        '/usr/share/foreman'
        >>> len(foreman_jobs)
        7
        >>> foreman_jobs[0].get('minute')
        '15'
        >>> foreman_jobs[0].get('hour')
        '23'
        >>> foreman_jobs[0].get('username')
        'foreman'
        >>> 'db:sessions:clear' in foreman_jobs[0].get('command')
        True
    """
    def parse_content(self, content):
        self.environment = {}
        self.invalid_lines = []
        # It can use 'nicknames' for common event frequencies:
        nicknames = {
            '@yearly': '0 0 1 1 *',
            '@annually': '0 0 1 1 *',
            '@monthly': '0 0 1 * *',
            '@weekly': '0 0 * * 0',
            '@daily': '0 0 * * *',
            '@hourly': '0 * * * *',
        }
        for line in get_active_lines(content):
            if line.startswith('@'):
                # Reboot is 'special':
                if line.startswith('@reboot'):
                    parts = line.split(None, 2)
                    self.append({'time': '@reboot', 'username': parts[1], 'command': parts[2]})
                    continue
                else:
                    parts = line.split(None, 2)
                    if parts[0] not in nicknames:
                        raise ParseException(
                            "{n} not recognised as a time specification 'nickname'".format(n=parts[0])
                        )
                    # Otherwise, put the time spec nickname translation into
                    # the line
                    line = line.replace(parts[0], nicknames[parts[0]])
            items = line.split(None, 6)
            if len(items) == 7:
                self.append({
                    'minute': items[0],
                    'hour': items[1],
                    'day_of_month': items[2],
                    'month': items[3],
                    'day_of_week': items[4],
                    'username': items[5],
                    'command': items[6]
                })
            else:
                parts = line.split('=')
                if len(parts) == 2:
                    self.environment[parts[0].strip()] = parts[1].strip()
                else:
                    self.invalid_lines.append(line)

    def search(self, filter_str):
        """Return a list of dict for lines that have `filter_str` in the command."""
        return [r for r in self if filter_str in r['command']]
