"""
ZdumpV - command ``/usr/sbin/zdump -v /etc/localtime -c 2019,2039``
===================================================================

The ``/usr/sbin/zdump -v /etc/localtime -c 2019,2039`` command provides information about
'Daylight Saving Time' in file /etc/localtime from 2019 to 2039.

Sample content from command ``zdump -v /etc/localtime -c 2019,2039`` is::

    /etc/localtime  Sun Mar 10 06:59:59 2019 UTC = Sun Mar 10 01:59:59 2019 EST isdst=0 gmtoff=-18000
    /etc/localtime  Sun Mar 10 07:00:00 2019 UTC = Sun Mar 10 03:00:00 2019 EDT isdst=1 gmtoff=-14400
    /etc/localtime  Sun Nov  7 05:59:59 2038 UTC = Sun Nov  7 01:59:59 2038 EDT isdst=1 gmtoff=-14400
    /etc/localtime  Sun Nov  7 06:00:00 2038 UTC = Sun Nov  7 01:00:00 2038 EST isdst=0 gmtoff=-18000

Examples:
    >>> dst = zdump[0]
    >>> dst.get('utc_time')
    datetime.datetime(2019, 3, 10, 6, 59, 59)
    >>> dst.get('utc_time_raw')
    'Sun Mar 10 06:59:59 2019 UTC'
    >>> dst.get('local_time')
    datetime.datetime(2019, 3, 10, 1, 59, 59)
    >>> dst.get('local_time_raw')
    'Sun Mar 10 01:59:59 2019 EST'
    >>> dst.get('isdst')
    0
    >>> dst.get('gmtoff')
    -18000
"""
from datetime import datetime

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


def str2datetime(timestamp, tz=False):
    """
    This function translates the time stamp into a datetime object.

    Args:
        timestamp (str): the time stamp from command `zdump -v`
        tz (bool): True if it's UTC TimeZone.

    Returns:
        time (datetime): the datetime object about the time stamp
        time_string (str): the formatted time stamp
    """
    time, time_string = None, timestamp.strip()

    # Fixed the problem that the program running this python code doesn't
    # has the corresponding TimeZone where strptime will raise ValueError.
    # So, we skip the `TimeZone`
    time_s = time_string.rsplit(None, 1)[0]
    time_f = "%a %b %d %H:%M:%S %Y"

    if tz:
        # In some version, `zdump` prints 'UT' instead of 'UTC'
        # 'UC' is an invalid TimeZone for function `strptime`
        time_s = time_s + " UTC"
        time_f = "%a %b %d %H:%M:%S %Y %Z"

    try:
        time = datetime.strptime(time_s, time_f)
    except ValueError:
        pass

    return time, time_string


@parser(Specs.zdump_v)
class ZdumpV(CommandParser, list):
    """
    Parse the output from the ``/usr/sbin/zdump -v /etc/localtime -c 2019,2039`` command
    and store the 'Daylight Saving Time' information into a list.

    Raises:
        SkipComponent: When nothing is parsed.

    .. warning:: The value in key `local_time` doesn't include the TimeZone information
    """
    def parse_content(self, content):
        if not content:
            raise SkipComponent("No Data from command: /usr/sbin/zdump -v /etc/localtime -c 2019,2039")

        for line in content:
            dst = {}
            if 'isdst' not in line:
                # skip the line that does not include a time stamp
                continue

            utc_time, remains = line.strip('/etc/localtime').split(' = ')
            dst['utc_time'], dst['utc_time_raw'] = str2datetime(utc_time, True)
            if dst['utc_time'] is None:
                continue

            local_time, _ = remains.split("isdst")
            dst['local_time'], dst['local_time_raw'] = str2datetime(local_time)
            if dst['local_time'] is None:
                continue

            isdst = [s.split('=')[1] for s in remains.split() if 'isdst' in s and '=' in s]
            if isdst:
                dst['isdst'] = int(isdst[0])

            gmtoff = [s.split('=')[1] for s in remains.split() if 'gmtoff' in s and '=' in s]
            if gmtoff:
                dst['gmtoff'] = int(gmtoff[0])

            self.append(dst)
