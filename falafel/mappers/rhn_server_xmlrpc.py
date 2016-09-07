from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed

import re

"""
2016/06/21 14:01:07 +01:00 29079 172.16.41.79: rhnServer/server_certificate.valid('Server id ID-1000014665 not found in database',)
"""

line_re = re.compile(r"^(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} [+-]?\d{2}:\d{2}) (?P<pid>\d+) (?P<client_ip>\S+): (?P<module>\w+)/(?P<function>[\w.-]+)(?:\((?:(?P<client_id>\d+), ?)?(?P<args>.*?),?\))?$")
GROUPS =('timestamp', 'pid', 'client_ip', 'module', 'function', 'client_id', 'args')

def parse_line(line):
    """
        Parse a log line using the XMLRPC regular expression into a dict.  
        All data will be in fields, and the raw log line is stored in
        'raw_log'.
    """
    msg_info = dict()
    msg_info['raw_log'] = line

    match = line_re.search(line)
    if match:
        for group in GROUPS:
            msg_info[group] = match.group(group)

    return msg_info

class LogLineList(MapperOutput):

    def __contains__(self, s):
        """
        Check if the specified string 's' is contained in one line
        """
        return any(s in l for l in self.data)

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them in a list
        """
        return [parse_line(l) for l in self.data if s in l]

    @computed
    def last(self):
        """
        Returns the last complete log line
        If the last line is not complete, then return the second last line
        """
        msg_info = dict()
        # Only check the last 2 lines, in that order
        for l in reversed(self.data[-2:]):
            msg_info = parse_line(l)
            # assume parse is successful if we got an IP address
            if msg_info['client_ip']:
                return msg_info
        # Return the last one even if it didn't parse.
        return msg_info


@mapper('rhn_server_xmlrpc.log')
def server_xmlrpc_log(context):
    """
    Returns an object in type of LogLineList which provide 3 APIs:
    - Usage:
      in:
        log = shared.get(taskomatic_daemon_log)
        if "Abort command issued" in log:
            ...
      get:
        err_lines = log.get('Wrapper')
        for line in err_lines:
            assert line.get('stat') == 'INFO'
            assert line.get('log') ..
            assert line.get('proc') ..
            assert line.get('time') ..
            assert line.get('raw_log') ..
            ...
     last:
        last_line_stat = log.last.get('time')

    -----------

    """
    print "got to server_xmlrpc_log"
    return LogLineList(context.content)
