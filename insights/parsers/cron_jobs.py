"""
Cron jobs - files ``/etc/cron.d/*``
===================================

This module contains the following parsers:

CronForeman - file ``/etc/cron.d/foreman``
------------------------------------------
"""
from insights.core import Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsers import get_active_lines, keyword_search
from insights.specs import Specs


class CronFile(Parser):
    """
    It parses the file at ``/etc/cron.d/*```.

    Each row of the file is converted into a dictionary with keys for each field.
    And also the whole line is saved for use to the "raw" key.
    For example one row would look like::

        {
          'minute': '*',
          'hour': '*',
          'day_of_month': '*',
          'month': '*',
          'day_of_week': '*',
          'username': 'test',
          'command': '/usr/bin/keystone-manage token_flush > /dev/null 2>&1',
          'raw': '* * * * * * test /usr/bin/keystone-manage token_flush > /dev/null 2>&1'
        }

    It parses the line in the same way that cron(1) does.  Lines that
    are blank or start with a comment are ignored.  Environment lines of the
    form 'KEY = value' (with optional spacing around the equals sign) are
    stored in the `environment` dictionary. Lines containing a valid
    cron job, with five recogniseable time fields, username, a command,
    are stored in the `jobs` property and accessed through the pseudo-list
    interface and the `search` method. All other lines are stored in the
    `invalid_lines` property.

    It also recognises the extension of time signature 'nicknames', which
    take place of the first five parts of a standard crontab line:

        * `@reboot` : Run once after reboot.
        * `@yearly` : Run once a year, ie.  "0 0 1 1 \*".
        * `@annually` : Run once a year, ie.  "0 0 1 1 \*".
        * `@monthly` : Run once a month, ie. "0 0 1 \* \*".
        * `@weekly` : Run once a week, ie.  "0 0 \* \* 0".
        * `@daily` : Run once a day, ie.   "0 0 \* \* \*".
        * `@hourly` : Run once an hour, ie. "0 \* \* \* \*".

    In the case of the '@reboot' nickname, the row will not contain the 'minute',
    'hour', 'day_of_month', 'month', or 'day_of_week' keys, and instead will
    contain the key 'time' with the value '@reboot' (as well as the usual
    'username' and 'command' key). All other nicknames are translated directly
    into their five-part equivalent and parsed as a normal crontab line.

    Sample input::

        SHELL=/bin/sh
        TEST_HOME=/usr/share/test

        15 23 * * *     test    /usr/sbin/testaa 2>&1 >> /var/log/test.log
        0 7 * * *       test    /usr/sbin/testbb 2>&1 >> /var/log/test.log

    Attributes:
        jobs(list): A list of valid jobs info.
        environment(dict): The environment variables.
        invalid_lines(list): A list of lines which are neither in cron format nor in env variable format.

    Raises:
        ParseException: When a line starts with '@', but the nickname is unknown.

    Examples:
        >>> type(cron_obj)
        <class 'insights.parsers.cron_jobs.CronFile'>
        >>> len(cron_obj.environment)
        2
        >>> 'TEST_HOME' in cron_obj.environment
        True
        >>> cron_obj.environment['TEST_HOME']
        '/usr/share/test'
        >>> len(cron_obj.jobs)
        2
        >>> cron_obj.jobs[0].get('minute')
        '15'
        >>> cron_obj.jobs[0].get('hour')
        '23'
        >>> cron_obj.jobs[0].get('username')
        'test'
        >>> '/usr/sbin/testaa' in cron_obj.jobs[0].get('command')
        True
    """
    def parse_content(self, content):
        self.jobs = []
        self.environment = {}
        self.invalid_lines = []
        # 'nicknames' can be used for common event frequencies:
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
                    self.jobs.append({'time': '@reboot', 'username': parts[1], 'command': parts[2], 'raw': line})
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
                self.jobs.append({
                    'minute': items[0],
                    'hour': items[1],
                    'day_of_month': items[2],
                    'month': items[3],
                    'day_of_week': items[4],
                    'username': items[5],
                    'command': items[6],
                    'raw': line
                })
            else:
                parts = line.split('=')
                if len(parts) == 2:
                    self.environment[parts[0].strip()] = parts[1].strip()
                else:
                    self.invalid_lines.append(line)

    def search(self, **kwargs):
        """
        Return a list of dict for lines that matches the kwargs.

        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details. If no search
        parameters are given, a empty list is returned.
        """
        return keyword_search(self.jobs, **kwargs)


@parser(Specs.cron_foreman)
class CronForeman(CronFile):
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

    Examples:
        >>> type(foreman_jobs)
        <class 'insights.parsers.cron_jobs.CronForeman'>
        >>> len(foreman_jobs.environment)
        4
        >>> 'FOREMAN_HOME' in foreman_jobs.environment
        True
        >>> foreman_jobs.environment['FOREMAN_HOME']
        '/usr/share/foreman'
        >>> len(foreman_jobs.jobs)
        3
        >>> foreman_jobs.jobs[0].get('minute')
        '15'
        >>> foreman_jobs.jobs[0].get('hour')
        '23'
        >>> foreman_jobs.jobs[0].get('username')
        'foreman'
        >>> 'db:sessions:clear' in foreman_jobs.jobs[0].get('command')
        True
    """
    pass
