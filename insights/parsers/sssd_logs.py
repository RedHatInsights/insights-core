"""
SSSDLog - files matching ``/var/log/sssd/*.log``
================================================

"""

from .. import parser, LogFileOutput
from datetime import datetime
from insights.specs import Specs


def strip_surrounds(s):
    # Or s{([\[\(]+)(.*)\1:?}{\2} except matching brace style
    start = 0
    end = len(s) - 1
    if s[end] == ':':
        end -= 1
    # print "strip '{s}' from {start} to {end}".format(s=s, start=start, end=end)
    while (s[start] == '[' and s[end] == ']') or \
      (s[start] == '(' and s[end] == ')'):
        start += 1
        end -= 1
    return s[start:(end + 1)]


@parser(Specs.sssd_logs)
class SSSDLog(LogFileOutput):
    """
    Parser class for reading SSSD log files.  The main work is done by the
    LogFileOutput super-class.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Sample input::

        (Tue Feb 14 09:45:02 2017) [sssd] [sbus_remove_timeout] (0x2000): 0x7f5aceb6a970
        (Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): dbus conn: 0x7f5aceb5cff0
        (Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): Dispatching.
        (Tue Feb 14 09:45:02 2017) [sssd] [sbus_remove_timeout] (0x2000): 0x7f5aceb63eb0
        (Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): dbus conn: 0x7f5aceb578b0
        (Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): Dispatching.
        (Tue Feb 14 09:45:02 2017) [sssd] [sbus_remove_timeout] (0x2000): 0x7f5aceb60f30
        (Tue Feb 14 09:45:02 2017) [sssd] [sbus_dispatch] (0x4000): dbus conn: 0x7f5aceb58360
        (Tue Feb 14 09:45:06 2015) [sssd] [monitor_hup] (0x0020): Received SIGHUP.
        (Tue Feb 14 09:45:07 2015) [sssd] [te_server_hup] (0x0020): Received SIGHUP. Rotating logfiles.

    Each line is parsed into a dictionary with the following keys:

        * **timestamp** - the date of the log line (as a string)
        * **datetime** - the date as a datetime object (if conversion is possible)
        * **module** - the module logging the message
        * **function** - the function within the module
        * **level** - the debug level (as a string)
        * **message** - the body of the message
        * **raw_message** - the raw message before being split.

    Examples:

        >>> logs = shared[SSSDLog]

        >>> hups = logs.get("SIGHUP")
        >>> print len(hups)
        2
        >>> hups[0]['module']
        'monitor_hup'

    """
    time_format = '%b %d %H:%M:%S %Y'

    def _parse_line(self, line):
        fields = line.split()
        parsed_line = {
            'timestamp': strip_surrounds(' '.join(fields[0:5])),
            'module': strip_surrounds(fields[5]),
            'function': strip_surrounds(fields[6]),
            'level': strip_surrounds(fields[7]),
            'message': ' '.join(fields[8:]),
            'raw_message': line
        }
        # Try to convert the datetime if possible
        try:
            parsed_line['datetime'] = datetime.strptime(
                parsed_line['timestamp'],
                '%a %b %d %H:%M:%S %Y'
            )
        except:
            pass
        return parsed_line
