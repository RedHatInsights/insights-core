from insights.parsers.uptime import Uptime
from insights.parsers import ParseException
from insights.tests import context_wrap
import datetime

import pytest

UPTIME_TEST_DATA = [
    {
        'test_data': " 14:28:24 up  5:55,  4 users,  load average: 0.04, 0.03, 0.05",
        'currtime': '14:28:24', 'updays': '', 'uphhmm': '5:55', 'users': '4',
        'loadavg': ['0.04', '0.03', '0.05'],
        'uptime': datetime.timedelta(days=0, hours=5, minutes=55)
    }, {
        'test_data': " 10:55:22 up 40 days, 21:17,  1 user,  load average: 0.49, 0.12, 0.04",
        'currtime': '10:55:22', 'updays': '40', 'uphhmm': '21:17', 'users': '1',
        'loadavg': ['0.49', '0.12', '0.04'],
        'uptime': datetime.timedelta(days=40, hours=21, minutes=17)
    }, {
        'test_data': " 10:55:22 up 40 days, 3 min,  1 user,  load average: 0.49, 0.12, 0.04",
        'currtime': '10:55:22', 'updays': '40', 'uphhmm': '00:03', 'users': '1',
        'loadavg': ['0.49', '0.12', '0.04'],
        'uptime': datetime.timedelta(days=40, hours=0, minutes=3)
    }, {
        'test_data': " 10:55:22 up 30 min,  1 user,  load average: 0.49, 0.12, 0.04",
        'currtime': '10:55:22', 'updays': '', 'uphhmm': '00:30', 'users': '1',
        'loadavg': ['0.49', '0.12', '0.04'],
        'uptime': datetime.timedelta(days=0, hours=0, minutes=30)
    }, {
        'test_data': " 16:33:40 up 2 days, 12 users,  load average: 9.32, 8.96, 8.87",
        'currtime': '16:33:40', 'updays': '2', 'uphhmm': '', 'users': '12',
        'loadavg': ['9.32', '8.96', '8.87'],
        'uptime': datetime.timedelta(days=2, hours=0, minutes=0)
    }
]
NOT_AN_UPTIME = "10:55:22 up 30 min"


def total_seconds(time_delta):
    return (time_delta.days * 24 * 60 * 60) + time_delta.seconds


def test_get_uptimes():
    for test_data in UPTIME_TEST_DATA:
        uptime = Uptime(context_wrap(test_data['test_data']))
        assert len(uptime.data) == 6
        assert uptime.currtime == test_data['currtime']
        assert uptime.updays == test_data['updays']
        assert uptime.uphhmm == test_data['uphhmm']
        assert uptime.users == test_data['users']
        assert uptime.loadavg == test_data['loadavg']
        assert total_seconds(uptime.uptime) == total_seconds(test_data['uptime'])


def test_get_no_uptime():
    with pytest.raises(ParseException) as exc:
        uptime = Uptime(context_wrap(NOT_AN_UPTIME))
        assert len(uptime.data) == 0
    assert 'No uptime data found on ' in str(exc)
