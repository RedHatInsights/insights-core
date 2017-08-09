import pytest
from insights.parsers.date import Date, DateUTC, DateParseException
from insights.tests import context_wrap

DATE_OUTPUT1 = "Mon May 30 10:49:14 %s 2016"
DATE_OUTPUT2 = "Thu Oct 22 12:59:28 %s 2015"
DATE_OUTPUT_TRUNCATED = "Thu Oct 22"
DATE_OUTPUT_INVALID = "Fon Pla 34 27:63:89 CST 20-1"


def test_get_date1():
    DATE = DATE_OUTPUT1 % ('CST')
    date_info = Date(context_wrap(DATE))
    assert date_info.data == DATE
    assert date_info.datetime is not None
    assert date_info.timezone == 'CST'


def test_get_date2():
    DATE = DATE_OUTPUT2 % ('EDT')
    date_info = Date(context_wrap(DATE))
    assert date_info.data == DATE
    assert date_info.datetime is not None
    assert date_info.timezone == 'EDT'


def test_get_date_truncated():
    with pytest.raises(DateParseException) as e_info:
        Date(context_wrap(DATE_OUTPUT_TRUNCATED))
    assert 'Expected six date parts.  Got ' in str(e_info.value)


def test_get_date_invalid():
    with pytest.raises(DateParseException) as e_info:
        Date(context_wrap(DATE_OUTPUT_INVALID))
    assert DATE_OUTPUT_INVALID in str(e_info.value)


def test_get_date3():
    DATE = DATE_OUTPUT1 % ('UTC')
    date_info = DateUTC(context_wrap(DATE))
    assert date_info.data == DATE
    assert date_info.datetime is not None
    assert date_info.timezone == 'UTC'
