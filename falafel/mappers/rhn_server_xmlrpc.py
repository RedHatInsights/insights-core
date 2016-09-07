from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed

import re

"""
2016/06/21 14:01:07 +01:00 29079 172.16.41.79: rhnServer/server_certificate.valid('Server id ID-1000014665 not found in database',)
"""

line_re = re.compile(r"^(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} [+-]?\d{2}:\d{2}) (?P<pid>\d+) (?P<client_ip>\S+): (?P<module>\w+)/(?P<function>[\w.-]+)(?:\((?:(?P<client_id>\d+), ?)?(?P<args>.*?),?\))?$")
GROUPS =('timestamp', 'pid', 'client_ip', 'module', 'function', 'client_id', 'args')

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
        print "got to get() in rhn_server_xmlrpc.LogLineList"
        r = list()
        for l in self.data:
            msg_info['raw_log'] = l
            if s in l:
                msg_info = dict()

                match = line_re.search(l)
                if match:
                    for group in GROUPS:
                        msg_info[group] = match.group(group)
                r.append(msg_info)
        return r

    @computed
    def last(self):
        """
        Returns the last complete log line
        If the last line is not complete, then return the second last line
        """
        msg_info = dict()
        # Only check the last 2 lines
        for l in self.data[-2:]:
            l_sp = [i.strip() for i in l.split('|', 3)]
            if len(l_sp) >= 3:
                # If the line is a complete log line
                msg_info = dict()
                msg_info['raw_log'] = l
                for i, c in enumerate(l_sp):
                    msg_info[LOG_COLUMN[i]] = l_sp[i]
        # Return the last one
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
