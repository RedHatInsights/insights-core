"""
cron_log - File ``/var/log/cron``
=================================
"""

from .. import Syslog, parser
from insights.specs import Specs


@parser(Specs.cron_log)
class CronLog(Syslog):
    """
    Read the ``/var/log/cron`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.Syslog` for more
        details.

    Sample input::

        Feb 19 03:49:01 smtcfc0247 CROND[899752]: (root) CMD (/etc/run /etc/cron/every15Minutes /var/venus/logs/cron/every15Minutes 5 4.4 >/dev/null 2>&1)
        Feb 19 03:49:01 smtcfc0247 CROND[899751]: (root) CMD (/etc/run /etc/cron/everyHour /var/venus/logs/cron/everyHour 5 65.8 >/dev/null 2>&1)
        Feb 19 03:49:01 smtcfc0247 CROND[899753]: (root) CMD (/etc/run /etc/cron/every5Minutes /var/venus/logs/cron/every5Minutes 5 43.0 >/dev/null 2>&1)
        Feb 19 03:49:01 smtcfc0247 CROND[908273]: (root) CMD (run-parts /etc/cron.hourly)

    Examples:
        >>> run_lines = cron_log.get('/etc/run')
        >>> len(run_lines)
        3
        >>> run_lines[0]['message'] = '(root) CMD (/etc/run /etc/cron/every15Minutes /var/venus/logs/cron/every15Minutes 5 4.4 >/dev/null 2>&1)'
        >>> run_lines[0]['procname'] = 'CROND[899752]'
        >>> run_lines[0]['timestamp'] = 'Feb 19 03:49:01'
    """
    pass
