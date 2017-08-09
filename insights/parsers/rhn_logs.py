"""
RHN Logs -  Files ``/var/log/rhn/*.log``
========================================

Modules for parsing the content of log files under ``/rhn-logs/rhn`` directory
in spacewalk-debug or sosreport archives of Satellite 5.x.
"""
from datetime import datetime
from .. import parser, LogFileOutput
import re


@parser('rhn_taskomatic_daemon.log')
class TaskomaticDaemonLog(LogFileOutput):
    """Class for parsing the ``rhn_taskomatic_daemon.log`` file.

    Note:
        Because of the need to get the datetime of the last log, please DO NOT
        filter it.

    Attributes:
        lines (list): All lines captured in this file.
        last_log_date (datetime): The last log datetime get from the last line.

    Examples:
        >>> td_log = shared[TaskomaticDaemonLog]
        >>> td_log.file_path
        'var/log/rhn/rhn_taskomatic_daemon.log'
        >>> td_log.get('two')
        ['Log file line two']
        >>> 'three' in td_log
        True
        >>> td_log.last_log_date
        2016-05-18 15:13:40
    """
    time_format = '%Y/%m/%d %H:%M:%S'

    def parse_content(self, content):
        """
        Once the logs are parsed, retrieve the last log date from the last
        line which has a complete timestamp in the third field.
        """
        super(TaskomaticDaemonLog, self).parse_content(content)
        self.last_log_date = None

        for l in reversed(self.lines):
            l_sp = l.split('|')
            if len(l_sp) >= 3:
                try:
                    self.last_log_date = datetime.strptime(
                            l_sp[2].strip(), self.time_format)
                    break
                except Exception:
                    continue


@parser('rhn_server_xmlrpc.log')
class ServerXMLRPCLog(LogFileOutput):
    """Class for parsing the ``rhn_server_xmlrpc.log`` file.

    Sample log line::

        2016/04/11 05:52:01 -04:00 23630 10.4.4.17: xmlrpc/registration.welcome_message('lang: None',)

    Attributes:
        lines (list): All lines captured in this file.
        last (dict): Dict of the last log line.

    Examples:
        >>> log = shared[ServerXMLRPCLog]
        >>> log.file_path
        'var/log/rhn/rhn_server_xmlrpc.log'
        >>> log.get('two')
        [{'timestamp':'2016/04/11 05:52:01 -04:00',
          'datetime': datetime(2016, 04, 11, 05, 52, 01),
          'pid': '23630',
          'client_ip': '10.4.4.17',
          'module': 'xmlrpc',
          'function': 'registration.welcome_message',
          'client_id': None,
          'args': "'lang: None'",
          'raw_log': "..."}]
        >>> log.last
        [{'timestamp':'2016/04/11 05:52:01 -04:00',
          'datetime': datetime(2016, 04, 11, 05, 52, 01),
          'pid': '23630',
          'client_ip': '10.4.4.17',
          'module': 'xmlrpc',
          'function': 'registration.welcome_message',
          'client_id': None,
          'args': "'lang: None'",
          'raw_log': "..."}]
    """
    time_format = '%Y/%m/%d %H:%M:%S'

    _LINE_STR = r"^(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} " + \
        r"[+-]?\d{2}:\d{2}) (?P<pid>\d+) (?P<client_ip>\S+): " + \
        r"(?P<module>\w+)/(?P<function>[\w.-]+)" + \
        r"(?:\((?:(?P<client_id>\d+), ?)?(?P<args>.*?),?\))?$"
    _LINE_RE = re.compile(_LINE_STR)

    def parse_content(self, content):
        """
        Parse the logs as its super class LogFileOutput.
        And get the last complete log. If the last line is not complete,
        then get from its previous line.
        """
        super(ServerXMLRPCLog, self).parse_content(content)
        self.last = None

        msg_info = {}
        for l in reversed(self.lines):
            msg_info = self.parse_line(l)
            # assume parse is successful if we got an IP address
            if 'client_ip' in msg_info:
                break
        # Get the last one even if it didn't parse.
        self.last = msg_info

    def parse_line(self, line):
        """
        Parse a log line using the XMLRPC regular expression into a dict.
        All data will be in fields, and the raw log line is stored in 'raw_log'.
        """
        msg_info = dict()
        msg_info['raw_log'] = line

        match = self._LINE_RE.search(line)
        if match:
            msg_info.update(match.groupdict())
            # Try converting the time stamp but move on if it fails
            try:
                stamp = match.group('timestamp')
                # Cannot guess time zone from e.g. '+01:00', so strip timezone
                msg_info['datetime'] = datetime.strptime(
                    stamp[0:19], self.time_format)
            except ValueError:
                pass

        return msg_info

    def get(self, s):
        """
        Returns all lines that contain 's', parse them and wrap them in a list
        """
        return [self.parse_line(l) for l in self.lines if s in l]


@parser('rhn_search_daemon.log')
class SearchDaemonLog(LogFileOutput):
    """
    Class for parsing the ``/var/log/rhn/search/rhn_search_daemon.log`` file.

    Sample log contents::

        STATUS | wrapper  | 2013/01/28 14:41:58 | --> Wrapper Started as Daemon
        STATUS | wrapper  | 2013/01/28 14:41:58 | Launching a JVM...
        INFO   | jvm 1    | 2013/01/28 14:41:59 | Wrapper (Version 3.2.1) http://wrapper.tanukisoftware.org
        STATUS | wrapper  | 2013/01/29 17:04:25 | TERM trapped.  Shutting down.

    Attributes:
        lines (list): All lines captured in this file.

    Examples:
        >>> log = shared[SearchDaemonLog]
        >>> log.file_path
        'var/log/rhn/search/rhn_search_daemon.log'
        >>> log.get('Launching a JVM')
        ['STATUS | wrapper  | 2013/01/28 14:41:58 | Launching a JVM...']
        >>> list(log.get_after(datetime(2013, 1, 29, 0, 0, 0)))
        ['STATUS | wrapper  | 2013/01/29 17:04:25 | TERM trapped.  Shutting down.']
    """
    time_format = '%Y/%m/%d %H:%M:%S'


@parser('rhn_server_satellite.log')
class SatelliteServerLog(LogFileOutput):
    """
    Class for parsing the ``var/log/rhn/rhn_server_satellite.log`` file

    Sample log contents::

        2016/11/19 01:13:35 -04:00 Downloading errata data complete
        2016/11/19 01:13:35 -04:00 Downloading kickstartable trees metadata
        2016/11/19 01:13:35 -04:00    Retrieving / parsing kickstart tree files: rhel-x86_64-server-optional-6-debuginfo (NONE RELEVANT)
        2016/11/19 01:13:39 -04:00    debug/output level: 1
        2016/11/19 01:13:39 -04:00    db:  rhnsat/<password>@rhnsat
        2016/11/19 01:13:39 -04:00
        2016/11/19 01:13:39 -04:00 Retrieving / parsing channel-families data
        2016/11/19 01:13:44 -04:00 channel-families data complete
        2016/11/19 01:13:44 -04:00
        2016/11/19 01:13:44 -04:00 RHN Entitlement Certificate sync

    Examples:
        >>> log = shared[SatelliteServerLog]
        >>> log.get('Downloading')
        ['2016/11/19 01:13:35 -04:00 Downloading errata data complete', '2016/11/19 01:13:35 -04:00 Downloading kickstartable trees metadata']

        >>> log.get_after(datetime(2016, 11, 19, 1, 13, 44))
        ['2016/11/19 01:13:44 -04:00 channel-families data complete', '2016/11/19 01:13:44 -04:00 ', '2016/11/19 01:13:44 -04:00 RHN Entitlement Certificate sync']
    """
    time_format = '%Y/%m/%d %H:%M:%S'
