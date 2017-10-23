"""
SSSDLog - files matching ``/var/log/sssd/*.log``
================================================

"""

from .. import parser, LogFileOutput
from datetime import datetime


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


@parser('sssd_logs')
class SSSDLog(LogFileOutput):
    """
    Parser class for reading SSSD log files.  The main work is done by the
    LogFileOutput superclass.

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

    Examples:

        >>> logs = shared[SSSDLog]

        >>> hups = logs.get("SIGHUP")
        >>> print len(hups)
        2
        >>> SSSDLog.parse_lines(hups)[0]['module']
        'monitor_hup'

    """
    time_format = '%b %d %H:%M:%S %Y'

    @staticmethod
    def parse_lines(lines):
        """
        This helper method takes a set of lines provided e.g. by get, and
        breaks them up into a list of dictionaries that can be used to
        interpret the line.   The first five columns are taken as the date,
        then the module, function, debug level and message.

        Parameters:
            lines (list): A list of log lines to parse, e.g. as saved by
                ``keep_scan``

        Returns:
            list[dict]:

                A list of dictionaries corresponding to the data in
                each line split into functional elements:

                * **timestamp** - the date of the log line (as a string)
                * **datetime** - the date as a datetime object (if conversion is possible)
                * **module** - the module logging the message
                * **function** - the function within the module
                * **level** - the debug level (as a string)
                * **message** - the body of the message
        """

        messages = []
        for line in lines:
            fields = line.split()
            messages.append({
                'timestamp': strip_surrounds(' '.join(fields[0:5])),
                'module': strip_surrounds(fields[5]),
                'function': strip_surrounds(fields[6]),
                'level': strip_surrounds(fields[7]),
                'message': ' '.join(fields[8:]),
            })
            # Try to convert the datetime if possible
            try:
                messages[-1]['datetime'] = datetime.strptime(
                    messages[-1]['timestamp'],
                    '%a %b %d %H:%M:%S %Y'
                )
            except:
                pass
        return messages
