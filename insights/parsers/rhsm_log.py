from datetime import datetime

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.rhsm_log)
class RhsmLog(LogFileOutput):
    """
    Class for parsing the log file: ``/var/log/rhsm/rhsm.log``.

    Sample input::
        2016-07-31 04:06:41,215 [DEBUG] rhsmcertd-worker:24440 @identity.py:131 - Loading consumer info from identity certificates.
        2016-07-31 04:06:41,221 [DEBUG] rhsmcertd-worker:24440 @connection.py:475 - Loaded CA certificates from /etc/rhsm/ca/: redhat-uep.pem
        2016-07-31 04:06:41,221 [DEBUG] rhsmcertd-worker:24440 @connection.py:523 - Making request: GET /subscription/consumers/a808d48e-36bf-4071-a00a-0efacc511b2b/certificates/serials
        2016-07-31 04:07:21,245 [ERROR] rhsmcertd-worker:24440 @entcertlib.py:121 - [Errno -2] Name or service not known

    Examples:
        >>> log = rhsm_log.get('Name or service not known')[0]
        >>> log.get('raw_message')
        '2016-07-31 04:07:21,245 [ERROR] rhsmcertd-worker:24440 @entcertlib.py:121 - [Errno -2] Name or service not known'
        >>> log.get('message')
        '[ERROR] rhsmcertd-worker:24440 @entcertlib.py:121 - [Errno -2] Name or service not known'
        >>> log.get("timestamp")
        datetime.datetime(2016, 7, 31, 4, 7, 21, 245000)
    """
    time_format = '%Y-%m-%d %H:%M:%S,%f'

    def _parse_line(self, line):
        """
        Parse log line to valid components
        """
        msg_info = {'raw_message': line}
        line_split = line.split(None, 2)
        try:
            msg_info['timestamp'] = datetime.strptime(' '.join(line_split[:2]), self.time_format)
            msg_info['message'] = line_split[2]
        except (ValueError, IndexError):
            pass
        return msg_info
