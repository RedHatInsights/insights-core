from insights.tests import context_wrap
from insights.parsers.timedatectl import Timedatectl

TIMEDATECTL_GENERAL = """
      Local time: Wed 2019-12-04 09:15:28 CST
  Universal time: Wed 2019-12-04 01:15:28 UTC
        RTC time: Wed 2019-12-04 01:15:27
       Time zone: Asia/Shanghai (CST, +0800)
     NTP enabled: yes
NTP synchronized: yes
 RTC in local TZ: no
      DST active: n/a
"""

TIMEDATECTL_DAYLIGHT_SAVING_TIME = """
      Local time: Tue 2019-12-03 20:28:52 EST
  Universal time: Wed 2019-12-04 01:28:52 UTC
        RTC time: Tue 2019-12-03 20:28:52
       Time zone: America/New_York (EST, -0500)
     NTP enabled: yes
NTP synchronized: yes
 RTC in local TZ: yes
      DST active: no
 Last DST change: DST ended at
                  Sun 2019-11-03 01:59:59 EDT
                  Sun 2019-11-03 01:00:00 EST
 Next DST change: DST begins (the clock jumps one hour forward) at
                  Sun 2020-03-08 01:59:59 EST
                  Sun 2020-03-08 03:00:00 EDT

Warning: The system is configured to read the RTC time in the local time zone.
         This mode can not be fully supported. It will create various problems
         with time zone changes and daylight saving time adjustments. The RTC
         time is never updated, it relies on external facilities to maintain it.
         If at all possible, use RTC in UTC by calling
"""


def test_general_timedatectl():
    timedate = Timedatectl(context_wrap(TIMEDATECTL_GENERAL))
    assert timedate is not None
    assert 'Local time' in timedate
    assert timedate['Local time'] == "Wed 2019-12-04 09:15:28 CST"
    assert 'Universal time' in timedate
    assert timedate['Universal time'] == "Wed 2019-12-04 01:15:28 UTC"
    assert 'RTC time' in timedate
    assert timedate['RTC time'] == "Wed 2019-12-04 01:15:27"
    assert 'Time zone' in timedate
    assert timedate['Time zone'] == "Asia/Shanghai (CST, +0800)"
    assert 'RTC in local TZ' in timedate
    assert timedate['RTC in local TZ'] == "no"
    assert 'DST active' in timedate
    assert timedate['DST active'] == "n/a"


def test_DST_timedatectl():
    timedate = Timedatectl(context_wrap(TIMEDATECTL_DAYLIGHT_SAVING_TIME))
    assert timedate is not None
    assert 'RTC in local TZ' in timedate
    assert timedate['RTC in local TZ'] == "yes"
    assert 'DST active' in timedate
    assert timedate['DST active'] == "no"
    assert 'Last DST change' in timedate
    assert "DST ended at" in timedate['Last DST change']
    assert "Sun 2019-11-03 01:59:59 EDT" in timedate['Last DST change']
    assert "Sun 2019-11-03 01:00:00 EST" in timedate['Last DST change']
    assert 'Next DST change' in timedate
    assert "DST begins (the clock jumps one hour forward) at" in timedate['Next DST change']
    assert "Sun 2020-03-08 01:59:59 EST" in timedate['Next DST change']
    assert "Sun 2020-03-08 03:00:00 EDT" in timedate['Next DST change']
    assert 'Warning' in timedate
    assert "The system is configured to read the RTC time in the local time zone." in timedate['Warning']
