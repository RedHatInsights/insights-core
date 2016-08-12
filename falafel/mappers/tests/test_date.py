from falafel.mappers import date
from falafel.tests import context_wrap

DATE_OUTPUT1 = "Mon May 30 10:49:14 %s 2016"
DATE_OUTPUT2 = "Thu Oct 22 12:59:28 %s 2015"


class TestDate():
    def test_get_date1(self):
        DATE = DATE_OUTPUT1 % ('CST')
        date_info = date.get_date(context_wrap(DATE))
        assert date_info.data  == DATE
        assert date_info.datetime is not None
        assert date_info.timezone == 'CST'

    def test_get_date2(self):
        DATE = DATE_OUTPUT2 % ('EDT')
        date_info = date.get_date(context_wrap(DATE))
        assert date_info.data == DATE
        assert date_info.datetime is not None
        assert date_info.timezone == 'EDT'
