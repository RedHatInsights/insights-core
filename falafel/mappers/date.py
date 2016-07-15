import logging
from falafel.core.plugins import mapper
from datetime import datetime

logger = logging.getLogger("rpm")


@mapper('date')
def get_date(context):
    """
    Sample: Fri Jun 24 09:13:34 CST 2016

    Returns a dict which contains:
     'date': the output of the date
     'datetime': the datetime object translated from 'date'
     'tzstr': the timezone string get from date's output, e.g. CST
    """
    sos_date = list(context.content)[0]
    # Convert to datetime object
    sos_date_obj = None
    tz_str = ''
    sos_date_split = sos_date.split()
    if len(sos_date_split) == 6:
        tz_str = sos_date_split[-2]
        # Remove the tzinfo for converting
        sos_date_notz = ' '.join(sos_date_split[0:4]) + ' ' + sos_date_split[-1]
        # Convert it
        try:
            sos_date_obj = datetime.strptime(sos_date_notz, '%a %b %d %H:%M:%S %Y')
        except (ValueError, UnicodeEncodeError):
            tz_str = ''
            logger.debug("Error parsing date %s" % sos_date_notz)

    return {'date': sos_date, 'datetime': sos_date_obj, 'tzstr': tz_str}
