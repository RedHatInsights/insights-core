from insights.parsers.cron_daily_rhsmd import CronDailyRhsmd
from insights.tests import context_wrap

RHSMD_1 = """
config=$(grep -E "^processTimeout" /etc/rhsm/rhsm.conf | grep -Po "[0-9]+")
if [ -n $config ]; then
  rhsmd_timeout=$config
else
  rhsmd_timeout=300
fi
""".strip()


def test_rhcms():
    rhsmd = CronDailyRhsmd(context_wrap(RHSMD_1))
    assert any("$config" in line for line in rhsmd.lines)
