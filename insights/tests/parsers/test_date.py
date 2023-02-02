import doctest
import pytest

from datetime import datetime

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import date
from insights.parsers.date import Date, DateUTC, DateParseException, TimeDateCtlStatus
from insights.tests import context_wrap


DATE_OUTPUT1 = "Mon May 30 10:49:14 %s 2016"
DATE_OUTPUT2 = "Thu Oct 22 12:59:28 %s 2015"
DATE_OUTPUT_TRUNCATED = "Thu Oct 22"
DATE_OUTPUT_INVALID = "Fon Pla 34 27:63:89 CST 20-1"

TIMEDATECTL_CONTENT1 = """
               Local time: Mon 2022-11-14 22:37:01 EST
           Universal time: Tue 2022-11-15 03:37:01 UTC
                 RTC time: Tue 2022-11-15 03:37:40
                Time zone: America/New_York (EST, -0500)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
"""

TIMEDATECTL_CONTENT2 = """
               Local time: Mon 2022-11-14 23:04:06 PST
           Universal time: Tue 2022-11-15 07:04:06 UTC
                 RTC time: Tue 2022-11-15 07:04:05
                Time zone: US/Pacific (PST, -0800)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: yes

Warning: The system is configured to read the RTC time in the local time zone.
         This mode cannot be fully supported. It will create various problems
         with time zone changes and daylight saving time adjustments. The RTC
         time is never updated, it relies on external facilities to maintain it.
         If at all possible, use RTC in UTC by calling
         'timedatectl set-local-rtc 0'.
"""

TIMEDATECTL_CONTENT3 = """
      Local time: Mon 2022-11-14 02:33:36 EST
  Universal time: Mon 2022-11-14 07:33:36 UTC
        RTC time: Mon 2022-11-14 07:33:34
       Time zone: America/New_York (EST, -0500)
     NTP enabled: yes
NTP synchronized: yes
 RTC in local TZ: no
      DST active: no
 Last DST change: DST ended at
                  Sun 2022-11-06 01:59:59 EDT
                  Sun 2022-11-06 01:00:00 EST
 Next DST change: DST begins (the clock jumps one hour forward) at
                  Sun 2023-03-12 01:59:59 EST
                  Sun 2023-03-12 03:00:00 EDT
"""

TIMEDATECTL_CONTENT_WRONG_DATE_FORMAT = """
      Local time: Mon 2022-11-14 02:33:36 EST
  Universal time: Mon 2022-11-14 07:33:36 UTC
        RTC time: 2022-11-14 07:33:34
       Time zone: America/New_York (EST, -0500)
     NTP enabled: yes
NTP synchronized: yes
 RTC in local TZ: no
      DST active: no
 Last DST change: DST ended at
                  Sun 2022-11-06 01:59:59 EDT
                  Sun 2022-11-06 01:00:00 EST
 Next DST change: DST begins (the clock jumps one hour forward) at
                  Sun 2023-03-12 01:59:59 EST
                  Sun 2023-03-12 03:00:00 EDT
"""

TIMEDATECTL_CONTENT_NOT_COLON_ALIGNED = """
      Local time: Mon 2022-11-14 02:33:36 EST
  Universal time  : Mon 2022-11-14 07:33:36 UTC
        RTC time: 2022-11-14 07:33:34
       Time zone: America/New_York (EST, -0500)
     NTP enabled: yes
NTP synchronized: yes
 RTC in local TZ: no
      DST active: no
 Last DST change: DST ended at
                  Sun 2022-11-06 01:59:59 EDT
                  Sun 2022-11-06 01:00:00 EST
 Next DST change: DST begins (the clock jumps one hour forward) at
                  Sun 2023-03-12 01:59:59 EST
                  Sun 2023-03-12 03:00:00 EDT
"""

TIMEDATECTL_CONTENT4_WITHOUT_INFO = """"""

TIMEDATECTL_CONTENT4_WITHOUT_COLON_OUTPUT = """
this is just test
""".strip()


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


def test_timedatectl():
    timectl1 = TimeDateCtlStatus(context_wrap(TIMEDATECTL_CONTENT1, strip=False))
    assert timectl1 is not None
    assert 'local_time' in timectl1
    local_time_val = datetime.strptime('2022-11-14 22:37:01', '%Y-%m-%d %H:%M:%S')
    assert timectl1['local_time'] == local_time_val
    assert 'universal_time' in timectl1
    universal_time_val = datetime.strptime('2022-11-15 03:37:01', '%Y-%m-%d %H:%M:%S')
    assert timectl1['universal_time'] == universal_time_val
    assert 'rtc_time' in timectl1
    rtc_time_val = datetime.strptime('2022-11-15 03:37:40', '%Y-%m-%d %H:%M:%S')
    assert timectl1['rtc_time'] == rtc_time_val
    assert timectl1['system_clock_synchronized'] == 'yes'
    assert timectl1['rtc_in_local_tz'] == 'no'
    assert timectl1['ntp_service'] == 'active'

    timectl2 = TimeDateCtlStatus(context_wrap(TIMEDATECTL_CONTENT2, strip=False))
    assert 'warning' in timectl2
    assert 'timedatectl set-local-rtc 0' in timectl2['warning']

    timectl3 = TimeDateCtlStatus(context_wrap(TIMEDATECTL_CONTENT3, strip=False))
    assert 'last_dst_change' in timectl3
    assert timectl3['system_clock_synchronized'] == 'yes'
    assert 'DST ended at Sun 2022-11-06 01:59:59 EDT Sun 2022-11-06 01:00:00 EST' in timectl3['last_dst_change']
    assert 'DST begins (the clock jumps one hour forward) at Sun 2023-03-12 01:59:59 EST Sun 2023-03-12 03:00:00 EDT' in timectl3['next_dst_change']


def test_timedatectl_except():
    with pytest.raises(SkipComponent):
        TimeDateCtlStatus(context_wrap(TIMEDATECTL_CONTENT4_WITHOUT_INFO, strip=False))
    with pytest.raises(ParseException):
        TimeDateCtlStatus(context_wrap(TIMEDATECTL_CONTENT4_WITHOUT_COLON_OUTPUT, strip=False))
    with pytest.raises(DateParseException):
        TimeDateCtlStatus(context_wrap(TIMEDATECTL_CONTENT_WRONG_DATE_FORMAT, strip=False))
    with pytest.raises(ParseException):
        TimeDateCtlStatus(context_wrap(TIMEDATECTL_CONTENT_NOT_COLON_ALIGNED, strip=False))


def test_doc():
    failed_count, _ = doctest.testmod(
        date, globs={'ctl_info': TimeDateCtlStatus(context_wrap(TIMEDATECTL_CONTENT2, strip=False))}
    )
    assert failed_count == 0
