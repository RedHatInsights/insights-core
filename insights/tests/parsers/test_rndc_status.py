import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import rndc_status
from insights.parsers.rndc_status import RndcStatus
from insights.tests import context_wrap

RNDC_STATUS = """
version: BIND 9.11.4-P2-RedHat-9.11.4-9.P2.el7 (Extended Support Version) <id:7107deb>
running on rhel7: Linux x86_64 3.10.0-957.10.1.el7.x86_64 #1 SMP Thu Feb 7 07:12:53 UTC 2019
boot time: Mon, 26 Aug 2019 02:17:03 GMT
last configured: Mon, 26 Aug 2019 02:17:03 GMT
configuration file: /etc/named.conf
CPUs found: 4
worker threads: 4
UDP listeners per interface: 3
number of zones: 103 (97 automatic)
debug level: 0
xfers running: 0
xfers deferred: 0
soa queries in progress: 0
query logging is OFF
recursive clients: 0/900/1000
tcp clients: 1/150
server is up and running
""".strip()

RNDC_STATUS_INVALID = """
invalid
invalid
invalid
""".strip()

RNDC_STATUS_EMPTY = """
""".strip()


def test_rndc_status():
    rndc_status = RndcStatus(context_wrap(RNDC_STATUS))
    assert rndc_status['boot time'] == 'Mon, 26 Aug 2019 02:17:03 GMT'
    assert rndc_status['server'] == 'up and running'


def test_invalid():
    with pytest.raises(ParseException) as e:
        RndcStatus(context_wrap(RNDC_STATUS_INVALID))
    assert "invalid" in str(e)


def test_empty():
    with pytest.raises(SkipComponent) as e:
        RndcStatus(context_wrap(RNDC_STATUS_EMPTY))
    assert "Empty content" in str(e)


def test_rndc_status_doc_examples():
    env = {
        'rndc_status': RndcStatus(
            context_wrap(RNDC_STATUS)),
    }
    failed, total = doctest.testmod(rndc_status, globs=env)
    assert failed == 0
