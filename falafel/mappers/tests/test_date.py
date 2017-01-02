from falafel.mappers.date import Date, DateUTC
from falafel.tests import context_wrap

DATE_OUTPUT1 = "Mon May 30 10:49:14 %s 2016"
DATE_OUTPUT2 = "Thu Oct 22 12:59:28 %s 2015"


class TestDate():
    def test_get_date1(self):
        DATE = DATE_OUTPUT1 % ('CST')
        date_info = Date(context_wrap(DATE))
        assert date_info.data == DATE
        assert date_info.datetime is not None
        assert date_info.timezone == 'CST'

    def test_get_date2(self):
        DATE = DATE_OUTPUT2 % ('EDT')
        date_info = Date(context_wrap(DATE))
        assert date_info.data == DATE
        assert date_info.datetime is not None
        assert date_info.timezone == 'EDT'


class TestDateUTC():
    def test_get_date1(self):
        DATE = DATE_OUTPUT1 % ('UTC')
        date_info = DateUTC(context_wrap(DATE))
        assert date_info.data == DATE
        assert date_info.datetime is not None
        assert date_info.timezone == 'UTC'
