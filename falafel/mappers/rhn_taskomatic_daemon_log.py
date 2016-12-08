"""Will be deprecated, do not use"""
from .. import Mapper, mapper

LOG_COLUMN = ('stat', 'proc', 'time', 'log')


class LogLineList(Mapper):

    def parse_content(self, content):
        self.data = content

    def __contains__(self, s):
        """
        Check if the specified string 's' is contained in one line
        """
        return any(s in l for l in self.data)

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them in a list
        """
        r = list()
        for l in self.data:
            if s in l:
                l_sp = [i.strip() for i in l.split('|', 3)]
                msg_info = dict()
                msg_info['raw_log'] = l
                if l_sp:
                    for i, c in enumerate(l_sp):
                        msg_info[LOG_COLUMN[i]] = l_sp[i]
                r.append(msg_info)
        return r

    @property
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


@mapper('rhn_taskomatic_daemon.log')
def taskomatic_daemon_log(context):
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
    return LogLineList(context)
