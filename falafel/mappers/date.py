import sys
from datetime import datetime

from falafel.core import MapperOutput
from falafel.core.plugins import mapper


class DateParseException(Exception): pass


class Date(MapperOutput):

    def __init__(self, data, path=None):
        super(Date, self).__init__(data, path)
        self.datetime, self.timezone = self.parse(data)

    @classmethod
    def parse_content(cls, content):
        return list(content)[0]

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


@mapper('date')
def get_date(context):
    """
    Sample: Fri Jun 24 09:13:34 CST 2016

    Returns a dict which contains:
     'date': the output of the date
     'datetime': the datetime object translated from 'date'
     'tzstr': the timezone string get from date's output, e.g. CST
    """
    return Date(Date.parse_content(context.content))
