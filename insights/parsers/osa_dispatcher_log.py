"""
OSADispatcherLog - file ``/var/log/rhn/osa-dispatcher.log``
===========================================================
"""
from insights.core.plugins import parser
from insights.core import LogFileOutput

from datetime import datetime
import re
from insights.specs import Specs


@parser(Specs.osa_dispatcher_log)
class OSADispatcherLog(LogFileOutput):
    """
    Reads the OSA dispatcher log.  Based on the ``LogFileOutput`` class.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`


    Works a bit like the XMLRPC log but the IP address always seems to be
    ``0.0.0.0`` and the module is always 'osad' - it's more like what
    produced the log.

    Sample log data::

        2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.__init__
        2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.setup_connection('Connected to jabber server', u'example.com')
        2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/osa_dispatcher.fix_connection('Upstream notification server started on port', 1290)
        2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.process_forever
        2015/12/27 22:48:50 -04:00 28307 0.0.0.0: osad/jabber_lib.main('ERROR', 'Error caught:')
        2015/12/27 22:48:50 -04:00 28307 0.0.0.0: osad/jabber_lib.main('ERROR', 'Traceback (most recent call last)')

    Example:
        >>> osa = shared[OSADispatcherLog]
        >>> osa.get('__init__')
        [{'raw_message': '2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.__init__',
         'timestamp': '2015/12/23 04:40:58 -04:00',
         'datetime': datetime.datetime(2015, 12, 23, 4, 40, 58),
         'pid': '28307', 'client_ip': '0.0.0.0', 'module': 'osad',
         'function': 'jabber_lib.__init__', 'info': None}
        ]
        >>> osa.last()
        {'raw_message': "2015/12/27 22:48:50 -04:00 28307 0.0.0.0: osad/jabber_lib.main('ERROR', 'Traceback (most recent call last)')",
         'timestamp': '2015/12/27 22:48:50 -04:00',
         'datetime': datetime.datetime(2015, 12, 27, 22, 48, 50), 'pid': '28307',
         'client_ip': '0.0.0.0', 'module': 'osad', 'function': 'jabber_lib.main',
         'info': "'ERROR', 'Traceback (most recent call last)'"}
        >>> from datetime import datetime
        >>> len(list(osa.get_after(datetime(2015, 12, 27, 22, 48, 0))))
        2
    """
    time_format = '%Y/%m/%d %H:%M:%S'

    _LINE_STR = r"^(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} " + \
        r"[+-]?\d{2}:\d{2}) (?P<pid>\d+) (?P<client_ip>\S+): " + \
        r"(?P<module>\w+)/(?P<function>[\w_.-]+)(?:\((?P<info>.*)\))?$"
    _LINE_RE = re.compile(_LINE_STR)

    def _parse_line(self, line):
        """
        Parse a log line using the XMLRPC regular expression into a dict.
        All data will be in fields, and the raw log line is stored in
        'raw_message'.

        This also attempts to convert the timestamp given into a datetime
        object; if it can't convert it, then you don't get a 'datetime'
        key in the line's dict.
        """
        msg_info = dict()
        msg_info['raw_message'] = line

        match = self._LINE_RE.search(line)
        if match:
            msg_info.update(match.groupdict())
            try:
                stamp = match.group('timestamp')
                # Must remove : from timezone for strptime %z
                msg_info['datetime'] = datetime.strptime(
                    stamp[0:23] + stamp[24:26], self.time_format + ' %z')
            except:
                pass

        return msg_info

    def last(self):
        """
        Finds the last complete log line in the file.  It looks for a line with
        a client IP address and parses the line to a dictionary.

        Returns:
            (dict) the last complete log line parsed to a dictionary.
        """
        msg_info = dict()
        for l in reversed(self.lines):
            msg_info = self._parse_line(l)
            # assume parse is successful if we got an IP address
            if 'client_ip' in msg_info:
                return msg_info
        # Return the last one even if it didn't parse.
        return msg_info
