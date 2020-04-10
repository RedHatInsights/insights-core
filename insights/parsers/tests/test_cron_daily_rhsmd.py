import doctest

from insights.parsers import cron_daily_rhsmd

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
