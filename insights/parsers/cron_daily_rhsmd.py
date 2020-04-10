"""
CronDailyRhsmd - file ``/etc/cron.daily/rhsmd``
===============================================
"""

from insights.core import Scannable
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.cron_daily_rhsmd)
class CronDailyRhsmd(Scannable):
    """
    Parse the ``/etc/cron.daily/rhsmd`` file.

    Sample input::

        config=$(grep -E "^processTimeout" /etc/rhsm/rhsm.conf | grep -Po "[0-9]+")
        rhsmd_timeout=$config
        abc=$config

    Examples::

        >>> from insights.tests import context_wrap
        >>> from insights.parsers.cron_daily_rhsmd import CronDailyRhsmd
        >>> CronDailyRhsmd.collect('config_lines', lambda n: n if "$config" in n else "")
        >>> CronDailyRhsmd.any('one_config_line', lambda n: n if "$config" in n else "")
        >>> rhsmd=CronDailyRhsmd(context_wrap(RHSMD_1))
        >>> rhsmd.config_lines
        ['rhsmd_timeout=$config', 'abc=$config']
        >>> rhsmd.one_config_line
        'rhsmd_timeout=$config'
    """
    pass
