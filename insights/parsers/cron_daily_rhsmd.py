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

    .. note::
        Please refer to its super-class :py:class:`insights.core.Scannable`
        for full usage.

    Examples:

        >>> # CronDailyRhsmd.collect('config_lines', lambda n: n if "$config" in n else "")
        >>> # CronDailyRhsmd.any('one_config_line', lambda n: n if "$config" in n else "")
        >>> rhsmd.config_lines
        ['rhsmd_timeout=$config', 'abc=$config']
        >>> rhsmd.one_config_line
        'rhsmd_timeout=$config'
    """
    pass
