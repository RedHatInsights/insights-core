"""
timedatectl - command ``/usr/bin/timedatectl``
==============================================

The ``timedatectl`` module provides parsing for the output
from the command ``/usr/bin/timedatectl``. The ``Timedatectl``
class implements the parsing and provides a ``dict`` that
contains Key-Vaule pairs in the output.

Sample content from command ``/usr/bin/timedatectl`` is::

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

Examples:
    >>> 'Local time' in timedatectl
    True
    >>> timedatectl['Local time']
    'Wed 2019-12-04 01:15:28 UTC'
    >>> 'DST active' in timedatectl
    True
    >>> timedatectl['DST active']
    'no'
    >>> 'Last DST change' in timedatectl
    True
    >>> "Sun 2019-11-03 01:59:59 EDT" in timedatectl['Last DST change']
    True
    >>> print(timedatectl['Last DST change'])
    DST ended at
    Sun 2019-11-03 01:59:59 EDT
    Sun 2019-11-03 01:00:00 EST
"""

from insights.specs import Specs
from insights.parsers import ParseException
from .. import parser, CommandParser


@parser(Specs.timedatectl)
class Timedatectl(CommandParser):
    """Parser class to parse the output of ``/usr/bin/timedatectl``."""
    def parse_content(self, content):
        data = {}
        delimiter = ': '
        previous_key = ''

        for line in content:
            line = line.strip()
            if not line:
                continue  # skip the empty line

            if delimiter in line:
                key, value = [l.strip() for l in line.split(delimiter, 1)]
                data[key] = value
                previous_key = key  # save it for the lines in the same section
            else:
                if previous_key:
                    # new val in dict  = old val in dict    +  CR  + new value
                    data[previous_key] = data[previous_key] + "\n" + line

        if not data:
            raise ParseException("No Data about Timedatectl")

        self.data = data

    def __str__(self):
        return str(self.data)

    def __contains__(self, key):
        return key in self.data

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key] if key in self.data else None
