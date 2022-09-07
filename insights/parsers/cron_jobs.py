"""
Cron job files under /etc/cron* but not users crontab
=====================================================

This module contains the following parsers:

CronForeman - file ``/etc/cron.d/foreman``
------------------------------------------
"""

from insights.core import Scannable
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.cron_foreman)
class CronForeman(Scannable):
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
        30 7 * * *      foreman    /usr/sbin/foreman-rake reports:expire 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log

    Examples:

        >>> # CronForeman.collect('test_reports_expire', lambda n: n if "foreman-rake reports:expire" in n else "")
        >>> len(foreman_cron.test_reports_expire) == 1
        True
        >>> '/var/log/foreman/cron.log' in foreman_cron.test_reports_expire[0]
        True
    """
    pass
