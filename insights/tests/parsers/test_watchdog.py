import doctest
import pytest

from insights.parsers import watchdog, SkipComponent
from insights.parsers.watchdog import WatchDogConf
from insights.tests import context_wrap

WATCHDOG_CONF = """
# The retry-timeout and repair limit are used to handle errors in a
# more robust manner. Errors must persist for longer than this to
# action a repair or reboot, and if repair-maximum attempts are
# made without the test passing a reboot is initiated anyway.

retry-timeout          = 60
repair-maximum         = 1
realtime               = yes
priority               = 1
""".strip()


def test_watchdog_conf():
    watchdog_conf = WatchDogConf(context_wrap(WATCHDOG_CONF))
    assert len(watchdog_conf) == 4
    assert watchdog_conf.get('retry-timeout') == '60'
    assert watchdog_conf.get('repair-maximum') == '1'
    assert watchdog_conf.get('realtime') == 'yes'
    assert watchdog_conf.get('priority') == '1'


def test_watchdog_skip():
    with pytest.raises(SkipComponent):
        WatchDogConf(context_wrap(''))


def test_doc():
    env = {
        "watchdog_conf_obj": WatchDogConf(context_wrap(WATCHDOG_CONF))
    }
    failed_count, _ = doctest.testmod(watchdog, globs=env)
    assert failed_count == 0
