"""
Cron file ``/var/log/cron``
===========================
"""

from .. import Syslog, parser
from insights.specs import Specs


@parser(Specs.cron_log)
class CronLog(Syslog):
    """Class for parsing the ``/var/log/cron`` file.

    Sample log text::

        Feb  9 03:19:03 dev7u7 run-parts(/etc/cron.daily)[351]: finished rhsmd
        Feb  9 03:19:03 dev7u7 anacron[30728]: Job `cron.daily' terminated
        Feb  9 03:19:03 dev7u7 anacron[30728]: Normal exit (1 job run)
        Feb  9 03:20:01 dev7u7 CROND[486]: (root) CMD (/usr/lib64/sa/sa1 1 1)

    .. note::
        Please refer to its super-class :class:`insights.core.Syslog`

    .. note::
        Because timestamps in the cron log by default have no year,
        the year of the logs will be affered from the year in your
        timestamp. This will also work around December/January crossover.

    Examples:
        >>> cronlog = shared[CronLog]
        >>> cronlog.get('Normal exit')
        [{'timestamp':'Feb  9 03:19:03',
          'hostname':'dev7u7',
          'procname': 'anacron[30728]',
          'message': 'Normal exit (1 job run)',
          'raw_message': 'Feb  9 03:19:03 dev7u7 anacron[30728]: Normal exit (1 job run)'
        }]
    """
    pass
