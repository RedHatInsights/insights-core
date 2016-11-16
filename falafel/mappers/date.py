import sys
from datetime import datetime

from .. import Mapper, mapper, get_active_lines


class DateParseException(Exception):
    pass


@mapper("date")
class Date(Mapper):
    """Parses the output of the ``date`` command.

    Sample: Fri Jun 24 09:13:34 CST 2016

    Attributes
    ----------
    datetime: datetime.datetime
        A native datetime.datetime of the parsed date string
    timezone: str
        The string portion of the date string containing the timezone
    """
    def parse_content(self, content):
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
            raise DateParseException(self.data), None, sys.exc_info()[2]


@mapper("date_utc")
class DateUTC(Mapper):
    """Parses the output of the ``date --utc`` command.

    Sample: Fri Jun 24 09:13:34 UTC 2016

    Attributes
    ----------
    datetime: datetime.datetime
        A native datetime.datetime of the parsed date string
    timezone: str
        The string portion of the date string containing the timezone
    """
    def parse_content(self, content):
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
            raise DateParseException(self.data), None, sys.exc_info()[2]
