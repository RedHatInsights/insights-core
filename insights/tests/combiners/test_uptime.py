import datetime
from insights.parsers.uptime import Uptime
from insights.combiners.uptime import uptime
from insights.tests import context_wrap

UPTIME1 = " 14:28:24 up  5:55,  4 users,  load average: 0.04, 0.03, 0.05"
UPTIME2 = " 10:55:22 up 40 days, 3 min,  1 user,  load average: 0.49, 0.12, 0.04"


def total_seconds(time_delta):
    return (time_delta.days * 24 * 60 * 60) + time_delta.seconds


def test_get_uptime_uptime1():
    ut = Uptime(context_wrap(UPTIME1))
    upt = uptime(ut)
    assert upt.currtime == '14:28:24'
    assert upt.updays == ""
    assert upt.uphhmm == '5:55'
    assert upt.users == '4'
    assert upt.loadavg == ['0.04', '0.03', '0.05']
    c = datetime.timedelta(days=0, hours=5, minutes=55)
    assert total_seconds(upt.uptime) == total_seconds(c)


def test_get_uptime_uptime2():
    ut = Uptime(context_wrap(UPTIME2))
    upt = uptime(ut)
    assert upt.currtime == '10:55:22'
    assert upt.updays == '40'
    assert upt.uphhmm == '00:03'
    assert upt.users == '1'
    assert upt.loadavg == ['0.49', '0.12', '0.04']
    c = datetime.timedelta(days=40, hours=0, minutes=3)
    assert total_seconds(upt.uptime) == total_seconds(c)


def test_get_both_uptime():
    ut = Uptime(context_wrap(UPTIME2))
    upt = uptime(ut)
    assert upt.currtime == '10:55:22'
    assert upt.updays == '40'
    assert upt.uphhmm == '00:03'
    assert upt.users == '1'
    assert upt.loadavg == ['0.49', '0.12', '0.04']
    c = datetime.timedelta(days=40, hours=0, minutes=3)
    assert total_seconds(upt.uptime) == total_seconds(c)
