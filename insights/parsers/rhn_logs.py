"""
RHN Logs -  Files /var/log/rhn/\*.log
=====================================

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
        There is a rule need to get the datetime of the last log, please DO NOT
        filter it in any other rules.

    Attributes:
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
    def parse_content(self, content):
        """
        Parse the logs as its super class LogFileOutput.
        And get the last log date from the last lines. If the last line is not
        complete, then get from its previous line.
        """
        super(TaskomaticDaemonLog, self).parse_content(content)
        self.last_log_date = None

        for l in reversed(self.lines):
            l_sp = l.split('|')
            if len(l_sp) >= 3:
                try:
                    self.last_log_date = datetime.strptime(
                            l_sp[2].strip(), '%Y/%m/%d %H:%M:%S')
                    break
                except Exception:
                    continue


@parser('rhn_server_xmlrpc.log')
class ServerXMLRPCLog(LogFileOutput):
    """Class for parsing the ``rhn_server_xmlrpc.log`` file.

    Typical line of rhn_server_xmlrpc.log:
        2016/04/11 05:52:01 -04:00 23630 10.4.4.17: xmlrpc/registration.welcome_message('lang: None',)

    Attributes:
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

    LINE_STR = r"^(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} " + \
        r"[+-]?\d{2}:\d{2}) (?P<pid>\d+) (?P<client_ip>\S+): " + \
        r"(?P<module>\w+)/(?P<function>[\w.-]+)" + \
        r"(?:\((?:(?P<client_id>\d+), ?)?(?P<args>.*?),?\))?$"
    LINE_RE = re.compile(LINE_STR)
    GROUPS = ('timestamp', 'pid', 'client_ip', 'module', 'function',
              'client_id', 'args')

    def parse_content(self, content):
        """
        Parse the logs as its super class LogFileOutput.
        And get the last complete log. If the last line is not complete,
        then get from its previous line.
        """
        super(ServerXMLRPCLog, self).parse_content(content)
        self.last = None

        msg_info = {}
        for l in reversed(self.lines[-2:]):
            msg_info = self.parse_line(l)
            # assume parse is successful if we got an IP address
            if 'client_ip' in msg_info:
                break
        # Get the last one even if it didn't parse.
        self.last = msg_info
        return msg_info

    def parse_line(self, line):
        """
        Parse a log line using the XMLRPC regular expression into a dict.
        All data will be in fields, and the raw log line is stored in 'raw_log'.
        """
        msg_info = dict()
        msg_info['raw_log'] = line

        match = self.LINE_RE.search(line)
        if match:
            for group in self.GROUPS:
                msg_info[group] = match.group(group)
            # Try converting the time stamp but move on if it fails
            try:
                stamp = match.group('timestamp')
                # Cannot guess time zone from e.g. '+01:00', so strip timezone
                msg_info['datetime'] = datetime.strptime(
                    stamp[0:19], "%Y/%m/%d %H:%M:%S")
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
    """Class for parsing the ``/var/log/rhn/search/rhn_search_daemon.log``."""
    pass
