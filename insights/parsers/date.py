"""
Date parsers
============

This module contains the following parsers:

Date - command ``date``
-----------------------
DateUTC - command ``date --utc``
--------------------------------
TimeDateCtlStatus - command ``timedatectl status``
--------------------------------------------------
"""
import six
import sys

from datetime import datetime

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


class DateParseException(Exception):
    pass


class DateParser(CommandParser):
    """Base class implementing shared code."""

    def parse_content(self, content):
        """
        Parses the output of the ``date`` and ``date --utc`` command.

        Sample: Fri Jun 24 09:13:34 CST 2016
        Sample: Fri Jun 24 09:13:34 UTC 2016

        Attributes
        ----------
        datetime: datetime.datetime
            A native datetime.datetime of the parsed date string
        timezone: str
            The string portion of the date string containing the timezone

        Raises:
            DateParseException: Raised if any exception occurs parsing the
            content.
        """
        self.data = get_active_lines(content, comment_char="COMMAND>")[0]
        parts = self.data.split()
        if not len(parts) == 6:
            msg = "Expected six date parts.  Got [%s]"
            raise DateParseException(msg % self.data)
        try:
            self.timezone = parts[4]
            no_tz = ' '.join(parts[:4]) + ' ' + parts[-1]
            self.datetime = datetime.strptime(no_tz, '%a %b %d %H:%M:%S %Y')
        except:
            six.reraise(DateParseException, DateParseException(self.data), sys.exc_info()[2])


@parser(Specs.date)
class Date(DateParser):
    """
    Class to parse ``date`` command output.

    Sample in::

        Fri Jun 24 09:13:34 CST 2016

    Examples:
        >>> from insights.parsers.date import Date
        >>> from insights.tests import context_wrap
        >>> date_content = "Mon May 30 10:49:14 CST 2016"
        >>> shared = {Date: Date(context_wrap(date_content))}
        >>> date_info = shared[Date]
        >>> date_info.data
        'Mon May 30 10:49:14 CST 2016'
        >>> date_info.datetime is not None
        True
        >>> date_info.timezone
        'CST'
    """
    pass


@parser(Specs.date_utc)
class DateUTC(DateParser):
    """
    Class to parse ``date --utc`` command output.

    Sample in::

        Fri Jun 24 09:13:34 UTC 2016

    Examples:
        >>> from insights.parsers.date import DateUTC
        >>> from insights.tests import context_wrap
        >>> date_content = "Mon May 30 10:49:14 UTC 2016"
        >>> shared = {DateUTC: DateUTC(context_wrap(date_content))}
        >>> date_info = shared[DateUTC]
        >>> date_info.data
        'Mon May 30 10:49:14 UTC 2016'
        >>> date_info.datetime
        datetime.datetime(2016, 5, 30, 10, 49, 14)
        >>> date_info.timezone
        'UTC'
    """
    pass


@parser(Specs.timedatectl_status)
class TimeDateCtlStatus(CommandParser, dict):
    """
    Class to parse the ``timedatectl status`` command output.
    It saves the infomartion in each line into a dict.
    Since the colon in all the lines except warning is aligned, every line
    is splited by the same colon index. The key is the lowercase of the first
    part joined by underscore after splitting it by colon, and the value is
    the left part after the colon. If the next line is continue line,
    then append it to the previous key. And also it converts
    the value to datetime format for "Local time", "Universal time" and "RTC time".

    Sample in::

                       Local time: Mon 2022-11-14 23:04:06 PST
                   Universal time: Tue 2022-11-15 07:04:06 UTC
                         RTC time: Tue 2022-11-15 07:04:05
                        Time zone: US/Pacific (PST, -0800)
        System clock synchronized: yes
                      NTP service: active
                  RTC in local TZ: yes
                  Last DST change: DST ended at
                                   Sun 2022-11-06 01:59:59 EDT
                                   Sun 2022-11-06 01:00:00 EST
                  Next DST change: DST begins (the clock jumps one hour forward) at
                                   Sun 2023-03-12 01:59:59 EST
                                   Sun 2023-03-12 03:00:00 EDT

        Warning: The system is configured to read the RTC time in the local time zone.
                This mode cannot be fully supported. It will create various problems
                with time zone changes and daylight saving time adjustments. The RTC
                time is never updated, it relies on external facilities to maintain it.
                If at all possible, use RTC in UTC by calling
                'timedatectl set-local-rtc 0'.

    Raises:
        DateParseException: when the datetime in "Local time", "Universal time",
                            "RTC time" are not in expected format.
        ParseException: when the colon in each line except warning is not aligned.

    Examples:
        >>> ctl_info['ntp_service']
        'active'
        >>> ctl_info['system_clock_synchronized']
        'yes'
        >>> ctl_info['local_time']
        datetime.datetime(2022, 11, 14, 23, 4, 6)
    """
    date_format = '%a %Y-%m-%d %H:%M:%S'

    # unify the different names in rhel7 and rhel8
    key_mapping = {
        'ntp_synchronized': 'system_clock_synchronized'
    }

    def parse_content(self, content):
        dict_key = None
        warning_start = False
        non_blank_line = None
        for line in content:
            if line.strip():
                non_blank_line = line
                break
        if non_blank_line is None:
            raise SkipComponent('No data in the output.')
        try:
            colon_index = non_blank_line.index(':')
        except ValueError:
            raise ParseException('No colon found, the line %s is not in expected format.' % line)
        for line in content:
            if not line.strip():
                continue
            if line[colon_index] == ':':
                key = line[:colon_index].strip()
                value = line[colon_index + 1:].strip()
                dict_key = '_'.join(key.lower().split())
                if dict_key in ['local_time', 'universal_time', 'rtc_time']:
                    if dict_key == 'rtc_time':
                        final_val = value
                    else:
                        final_val = value.rsplit(None, 1)[0]  # remove tz info
                    try:
                        self[dict_key] = datetime.strptime(final_val, self.date_format)
                    except Exception:
                        six.reraise(DateParseException, DateParseException(value), sys.exc_info()[2])
                else:
                    if dict_key in self.key_mapping:
                        self[self.key_mapping[dict_key]] = value
                    else:
                        self[dict_key] = value
            elif not line[:colon_index].strip():
                # this line is also the content of the previous key
                self[dict_key] += ' ' + line.strip()
            elif line.lstrip().startswith('Warning:'):
                warning_start = True
                self['warning'] = line.split(':')[1].strip()
            else:
                if warning_start:
                    self['warning'] += ' ' + line.strip()
                else:
                    raise ParseException('Unexpected format of line %s.' % line)
