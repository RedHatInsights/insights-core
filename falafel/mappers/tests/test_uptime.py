from falafel.mappers.uptime import Uptime
from falafel.tests import context_wrap
import datetime

UPTIME1 = " 14:28:24 up  5:55,  4 users,  load average: 0.04, 0.03, 0.05"
UPTIME2 = " 10:55:22 up 40 days, 21:17,  1 user,  load average: 0.49, 0.12, 0.04"
UPTIME3 = " 10:55:22 up 40 days, 3 min,  1 user,  load average: 0.49, 0.12, 0.04"
UPTIME4 = " 10:55:22 up 30 min,  1 user,  load average: 0.49, 0.12, 0.04"


class TestUptime():
    def test_get_uptime1(self):
        uptime = Uptime(context_wrap(UPTIME1))
        assert len(uptime.data) == 6
        assert uptime.currtime == '14:28:24'
        assert uptime.updays == ""
        assert uptime.uphhmm == '5:55'
        assert uptime.users == '4'
        assert uptime.loadavg == ['0.04', '0.03', '0.05']
        c = datetime.timedelta(days=0, hours=5, minutes=55)
        assert uptime.uptime.total_seconds() == c.total_seconds()

    def test_get_uptime2(self):
        uptime = Uptime(context_wrap(UPTIME2))
        assert len(uptime.data) == 6
        assert uptime.currtime == '10:55:22'
        assert uptime.updays == '40'
        assert uptime.uphhmm == '21:17'
        assert uptime.users == '1'
        assert uptime.loadavg == ['0.49', '0.12', '0.04']
        c = datetime.timedelta(days=40, hours=21, minutes=17)
        assert uptime.uptime.total_seconds() == c.total_seconds()

    def test_get_uptime3(self):
        uptime = Uptime(context_wrap(UPTIME3))
        assert len(uptime.data) == 6
        assert uptime.currtime == '10:55:22'
        assert uptime.updays == '40'
        assert uptime.uphhmm == '00:03'
        assert uptime.users == '1'
        assert uptime.loadavg == ['0.49', '0.12', '0.04']
        c = datetime.timedelta(days=40, hours=0, minutes=3)
        assert uptime.uptime.total_seconds() == c.total_seconds()

    def test_get_uptime4(self):
        uptime = Uptime(context_wrap(UPTIME4))
        assert len(uptime.data) == 6
        assert uptime.currtime == '10:55:22'
        assert uptime.updays == ""
        assert uptime.uphhmm == '00:30'
        assert uptime.users == '1'
        assert uptime.loadavg == ['0.49', '0.12', '0.04']
        c = datetime.timedelta(days=0, hours=0, minutes=30)
        assert uptime.uptime.total_seconds() == c.total_seconds()
