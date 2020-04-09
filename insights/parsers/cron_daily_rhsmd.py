"""
CronDailyRhsmd - file ``/etc/cron.daily/rhsmd``
===============================================
"""

from insights.core import LogFileOutput
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.cron_daily_rhsmd)
class CronDailyRhsmd(LogFileOutput):
    """
    Parse the ``/etc/cron.daily/rhsmd`` file.
    """
    pass
