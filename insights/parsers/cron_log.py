"""
CronLog - file ``/var/log/cron``
================================
"""

from insights import parser, Syslog
from insights.specs import Specs


@parser(Specs.cron_logs)
class CronLog(Syslog):
    """
    Class for parsing ``/var/log/cron`` file.

    Provide access to cron log using the
    :class:`insights.core.Syslog` parser class.

    Sample log content::

      Feb 20 18:59:01 hostname CROND[14468]: (root) CMD (/usr/sbin/logrotate /etc/logrotate.d/redcloaklogs.conf)
      Feb 20 19:00:01 hostname crond[14532]: (root) PAM ERROR (Authentication token is no longer valid; new one required)
      Feb 20 19:00:01 hostname crond[14532]: (root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)
      Feb 20 19:01:01 hostname crond[14597]: (root) PAM ERROR (Authentication token is no longer valid; new one required)
      Feb 20 19:01:01 hostname crond[14597]: (root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)
      Feb 20 19:01:01 hostname crond[14598]: (root) PAM ERROR (Authentication token is no longer valid; new one required)
      Feb 20 19:01:01 hostname crond[14598]: (root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)
      Feb 20 19:02:01 hostname crond[14661]: (root) PAM ERROR (Authentication token is no longer valid; new one required)
      Feb 20 19:02:01 hostname crond[14661]: (root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)

    Examples:

      >>> cron_log = cron_log_msg.get("FAILED")
      >>> len(cron_log)
      4
      >>> cron_log[0].get("procname")
      'crond[14532]'
      >>> cron_log[0].get("message")
      '(root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)'
    """
    pass
