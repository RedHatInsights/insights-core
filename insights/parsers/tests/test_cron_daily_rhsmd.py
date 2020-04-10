import doctest

from insights.parsers import cron_daily_rhsmd
from insights.tests import context_wrap

RHSMD_1 = """
config=$(grep -E "^processTimeout" /etc/rhsm/rhsm.conf | grep -Po "[0-9]+")
rhsmd_timeout=$config
abc=$config
""".strip()


def test_docs():
    env = {
        'RHSMD_1': RHSMD_1
    }
    failed, total = doctest.testmod(cron_daily_rhsmd, globs=env)
    assert failed == 0


def test_parser():
    cron_daily_rhsmd.CronDailyRhsmd.collect('config_varialbe_lines', lambda n: n if "$config" in n else "")
    cron_daily_rhsmd.CronDailyRhsmd.any('rhsmd_timeout', lambda n: n if "rhsmd_timeout" in n else "")
    rhs = cron_daily_rhsmd.CronDailyRhsmd(context_wrap(RHSMD_1))
    assert rhs.rhsmd_timeout == 'rhsmd_timeout=$config'
    assert rhs.config_varialbe_lines == ['rhsmd_timeout=$config', 'abc=$config']
