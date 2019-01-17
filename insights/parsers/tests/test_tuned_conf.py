import doctest

from insights.parsers import tuned_conf
from insights.tests import context_wrap

TUNED_CONF = """
#
# tuned configuration main service
#

[main]
# Interval for monitoring and tuning. Default is 10s.
# interval=10

#
# Disk monitoring section
#
[DiskMonitor]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
# enabled=False

#
# Disk tuning section
#
[DiskTuning]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
# enabled=False
#hdparm=False
alpm=False

#
# Net monitoring section
#
[NetMonitor]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
# enabled=False

#
# Net tuning section
#
[NetTuning]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
enabled=False

#
# CPU monitoring section
#
[CPUMonitor]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
enabled=False

#
# CPU tuning section
#
[CPUTuning]
# Enabled or disable the plugin. Default is True. Any other value
# disables it.
enabled=False
""".strip()


def test_documentation():
    env = {'tuned_obj': tuned_conf.TunedConfIni(context_wrap(TUNED_CONF))}
    failed_count, tests = doctest.testmod(tuned_conf, globs=env)
    assert failed_count == 0
