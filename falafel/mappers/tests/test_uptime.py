from falafel.mappers import uptime
from falafel.tests import context_wrap
import datetime

UPTIME1 = " 14:28:24 up  5:55,  4 users,  load average: 0.04, 0.03, 0.05"
UPTIME2 = " 10:55:22 up 40 days, 21:17,  1 user,  load average: 0.49, 0.12, 0.04"
UPTIME3 = " 10:55:22 up 40 days, 3 min,  1 user,  load average: 0.49, 0.12, 0.04"
UPTIME4 = " 10:55:22 up 30 min,  1 user,  load average: 0.49, 0.12, 0.04"


class TestUptime():
    def test_get_uptime1(self):
        data = uptime.get_uptime(context_wrap(UPTIME1))
        assert len(data) == 6
        assert data.get('currtime') == '14:28:24'
        assert data.get('updays') == ""
        assert data.get('uphhmm') == '5:55'
        assert data.get('users') == '4'
        assert data.get('loadavg') == ['0.04', '0.03', '0.05']
        c = datetime.timedelta(days=0, hours=5, minutes=55)
        assert data.get('uptime').total_seconds() == c.total_seconds()

    def test_get_uptime2(self):
        data = uptime.get_uptime(context_wrap(UPTIME2))
        assert len(data) == 6
        assert data.get('currtime') == '10:55:22'
        assert data.get('updays') == '40'
        assert data.get('uphhmm') == '21:17'
        assert data.get('users') == '1'
        assert data.get('loadavg') == ['0.49', '0.12', '0.04']
        c = datetime.timedelta(days=40, hours=21, minutes=17)
        assert data.get('uptime').total_seconds() == c.total_seconds()

    def test_get_uptime3(self):
        data = uptime.get_uptime(context_wrap(UPTIME3))
        assert len(data) == 6
        assert data.get('currtime') == '10:55:22'
        assert data.get('updays') == '40'
        assert data.get('uphhmm') == '00:03'
        assert data.get('users') == '1'
        assert data.get('loadavg') == ['0.49', '0.12', '0.04']
        c = datetime.timedelta(days=40, hours=0, minutes=3)
        assert data.get('uptime').total_seconds() == c.total_seconds()

    def test_get_uptime4(self):
        data = uptime.get_uptime(context_wrap(UPTIME4))
        assert len(data) == 6
        assert data.get('currtime') == '10:55:22'
        assert data.get('updays') == ""
        assert data.get('uphhmm') == '00:30'
        assert data.get('users') == '1'
        assert data.get('loadavg') == ['0.49', '0.12', '0.04']
        c = datetime.timedelta(days=0, hours=0, minutes=30)
        assert data.get('uptime').total_seconds() == c.total_seconds()
