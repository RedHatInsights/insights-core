from falafel.mappers import date
from falafel.tests import context_wrap
from datetime import datetime

DATE_OUTPUT1 = "Mon May 30 10:49:14%s2016"
DATE_OUTPUT2 = "Thu Oct 22 12:59:28%s2015"

class TestDate():
    def test_get_date1(self):
        DATE = DATE_OUTPUT1% (' CST ')
        DATE_OBJECT = datetime.strptime(DATE_OUTPUT1 % ' ', '%a %b %d %H:%M:%S %Y')
        date_info = date.get_date(context_wrap(DATE))
        assert len(date_info) == 3
        assert date_info.get('date') == DATE
        assert date_info.get('datetime') == DATE_OBJECT
        assert date_info.get('tzstr') == 'CST'

    def test_get_date2(self):
        DATE = DATE_OUTPUT2% (' EDT ')
        DATE_OBJECT = datetime.strptime(DATE_OUTPUT2 % ' ', '%a %b %d %H:%M:%S %Y')
        date_info = date.get_date(context_wrap(DATE))
        assert len(date_info) == 3
        assert date_info.get('date') == DATE
        assert date_info.get('datetime') == DATE_OBJECT
        assert date_info.get('tzstr') == 'EDT'
