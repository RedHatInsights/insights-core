from falafel.core.plugins import mapper
from falafel.core import MapperOutput

LOG_COLUMN = ('stat', 'proc', 'time', 'log')


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

    def last(self):
        """
        Returns the last complete log line
        If the last line is not complete, then return the second last line
        """
        msg_info = dict()
        for l in self.data[-2:]:
            l_sp = [i.strip() for i in l.split('|', 3)]
            if len(l_sp) >= 3:
                msg_info = dict()
                msg_info['raw_log'] = l
                for i, c in enumerate(l_sp):
                    msg_info[LOG_COLUMN[i]] = l_sp[i]
        # Return the last one
        return msg_info


@mapper('rhn_taskomatic_daemon.log')
def taskomatic_daemon_log(context):
    """
    Returns an object in type of LogLineList which provide two methods:
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
        last_line_stat = log.last().get('stat') if log.last()

    -----------

    """
    # for line in context.content:
    return LogLineList(context.content)
