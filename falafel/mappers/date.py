import sys
from datetime import datetime

from .. import MapperOutput, mapper, get_active_lines


class DateParseException(Exception):
    pass


@mapper("date")
class Date(MapperOutput):
    """Parses the output of the ``date`` command.

    Sample: Fri Jun 24 09:13:34 CST 2016

    Attributes
    ----------
    datetime: datetime.datetime
        A native datetime.datetime of the parsed date string
    timezone: str
        The string portion of the date string containing the timezone
    """
    def __init__(self, data, path=None):
        super(Date, self).__init__(data, path)
        self.datetime, self.timezone = self.parse(data)

    @classmethod
    def parse_content(cls, content):
        return get_active_lines(content, comment_char="COMMAND>")[0]

    @staticmethod
    def parse(data):
        parts = data.split()
        if not len(parts) == 6:
            msg = "Expected six date parts.  Got [%s]"
            raise DateParseException(msg % data)
        try:
            tz = parts[4]
            no_tz = ' '.join(parts[:4]) + ' ' + parts[-1]
            dt = datetime.strptime(no_tz, '%a %b %d %H:%M:%S %Y')
            return dt, tz
        except:
            raise DateParseException(data), None, sys.exc_info()[2]
