import pytest

from insights.parsers.watchdog_logs import WatchDogLog
from insights.tests import context_wrap

WATCHDOG_LOG = """
DEBUG:root:0

INFO:root:Executing: /usr/bin/sg_persist -n -i -k -d /dev/mapper/mpathb

DEBUG:root:0   PR generation=0xc2, 4 registered reservation keys follow:
    0xfdfe0001
    0xfdfe0001
    0xfdfe0000
    0xfdfe0000
""".strip()


def test_watchdog():
    WatchDogLog.last_scan('register_line', 'registered reservation keys')
    watch_log = WatchDogLog(context_wrap(WATCHDOG_LOG))
    assert watch_log.register_line is not None
    assert watch_log.register_line.get('raw_message') == 'DEBUG:root:0   PR generation=0xc2, 4 registered reservation keys follow:'


def test_exception():
    watch_log = WatchDogLog(context_wrap(WATCHDOG_LOG))
    with pytest.raises(RuntimeError):
        list(watch_log.get_after('2013-1-1'))
