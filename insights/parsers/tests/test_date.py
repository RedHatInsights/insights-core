from insights.parsers.date import Date, DateUTC, DateParseException
from insights.tests import context_wrap

import unittest

DATE_OUTPUT1 = "Mon May 30 10:49:14 %s 2016"
DATE_OUTPUT2 = "Thu Oct 22 12:59:28 %s 2015"
DATE_OUTPUT_TRUNCATED = "Thu Oct 22"
DATE_OUTPUT_INVALID = "Fon Pla 34 27:63:89 CST 20-1"


class TestDate(unittest.TestCase):
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

    def test_get_date_truncated(self):
        with self.assertRaisesRegexp(DateParseException, 'Expected six date parts.  Got '):
            date_info = Date(context_wrap(DATE_OUTPUT_TRUNCATED))
            self.assertIsNone(date_info)

    def test_get_date_invalid(self):
        with self.assertRaisesRegexp(DateParseException, DATE_OUTPUT_INVALID):
            date_info = Date(context_wrap(DATE_OUTPUT_INVALID))
            self.assertIsNone(date_info)


class TestDateUTC():
    def test_get_date1(self):
        DATE = DATE_OUTPUT1 % ('UTC')
        date_info = DateUTC(context_wrap(DATE))
        assert date_info.data == DATE
        assert date_info.datetime is not None
        assert date_info.timezone == 'UTC'
