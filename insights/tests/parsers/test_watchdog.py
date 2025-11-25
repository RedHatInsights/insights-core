import doctest
import pytest

from insights.parsers import watchdog, SkipComponent
from insights.parsers.watchdog import WatchDogConf, WatchDogLog
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

WATCHDOG_LOG = """
DEBUG:root:0

INFO:root:Executing: /usr/bin/sg_persist -n -i -k -d /dev/mapper/mpathb

DEBUG:root:0   PR generation=0xc2, 4 registered reservation keys follow:
    0xfdfe0001
    0xfdfe0001
    0xfdfe0000
    0xfdfe0000
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


def test_watchdog_log():
    WatchDogLog.last_scan('register_line', 'registered reservation keys')
    watch_log = WatchDogLog(context_wrap(WATCHDOG_LOG))
    assert watch_log.register_line is not None
    assert watch_log.register_line.get('raw_message') == 'DEBUG:root:0   PR generation=0xc2, 4 registered reservation keys follow:'


def test_watchdog_log_exception():
    watch_log = WatchDogLog(context_wrap(WATCHDOG_LOG))
    with pytest.raises(RuntimeError):
        list(watch_log.get_after('2013-1-1'))


def test_doc():
    env = {
        "watchdog_conf_obj": WatchDogConf(context_wrap(WATCHDOG_CONF))
    }
    failed_count, _ = doctest.testmod(watchdog, globs=env)
    assert failed_count == 0
