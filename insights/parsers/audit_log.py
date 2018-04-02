"""
audit_log - File ``/var/log/audit/audit.log``
=============================================

"""

import shlex
from datetime import date
from .. import LogFileOutput, parser

# Currently, only selinux related(AVC type) audit logs are interested.
# Add this filter in parser directly to filter out too many other types logs.
# Also, filters can be changed to meet any further requirments.
filter_list = [
    'type=AVC',
]


@parser("audit_log", filter_list)
class AuditLog(LogFileOutput):
    """
    Class for parsing ``/var/log/audit/audit.log`` file.

    Sample log lines::

        type=CRYPTO_KEY_USER msg=audit(1506046832.641:53584): pid=16865 uid=0 auid=0 ses=7247 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=destroy kind=session fp=? direction=both spid=16865 suid=0 rport=59296 laddr=192.0.2.1 lport=22  exe="/usr/sbin/sshd" hostname=? addr=192.0.2.3 terminal=? res=success'
        type=LOGIN msg=audit(1506047401.407:53591): pid=482 uid=0 subj=system_u:system_r:crond_t:s0-s0:c0.c1023 old-auid=4294967295 auid=993 old-ses=4294967295 ses=7389 res=1
        type=AVC msg=audit(1506487181.009:32794): avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket

    Examples:
        >>> log = shared[AuditLog]
        >>> log.get('type=AVC')
        'type=AVC msg=audit(1506487181.009:32794): avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket'
        >>> avc_log_info = list(log.parse_lines(log.get('type=AVC')))[0]
        >>> avc_log_info
        {
            'timestamp': '1506487181.009',
            'unparsed': 'avc:  denied  { create } for',
            'msg_ID': '32794',
            'pid': '27960',
            'raw_message': 'type=AVC msg=audit(1506487181.009:32794): avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket',
            'comm': 'mongod',
            'scontext': 'system_u:system_r:mongod_t:s0',
            'tclass': 'unix_dgram_socket',
            'type': 'AVC',
            'tcontext': 'system_u:system_r:mongod_t:s0'
        }
        >>> assert avc_log_info == list(log.get_after(timestamp=date.fromtimestamp(1506047401.407)))[0]
    """
    def _parse_line(self, line):
        """
        Parse a log line into a info dictionary.

        Parsing logic:

            * First, use `shlex.split` to split by empty.
            * Next, assert the first two key-value pair is 'type' and 'msg'.
            * Next, parse the remained string reversly to get key-value pair data as more as possible.
            * The left unparsed string will be stored at "unparsed".
            * At last, wrap all key-value pairs into a dict called info.

        Parameters:
            line(string): Log line to parse

        Yields:
            Dictionary corresponding to the data in line split into
            functional elements:

            * **raw_message** - the original unparsed line
            * **type** - the log type
            * **timestamp** - the timestamp of the log line (as a string)
            * **msg_ID** - the serial number behind the timestamp
            * **unparsed** - the unparsed part in log, may or maynot exist

            If the line is not regular, for some reason, then as many fields as
            possible are pulled from the line.
        """
        info = {}
        linesp = shlex.split(line)

        if (len(linesp) < 2 or
                not (linesp[0] and linesp[0].startswith('type=')) or
                not (linesp[1] and linesp[1].startswith('msg=audit('))):
            return

        info['type'] = linesp[0].lstrip('type=')

        timestamp_id = linesp[1].lstrip('msg=audit(').rstrip('):')
        timestamp_id_sp = timestamp_id.split(':')
        if len(timestamp_id_sp) != 2:
            return
        info['timestamp'] = timestamp_id_sp[0]
        info['msg_ID'] = timestamp_id_sp[1]

        for index in xrange(len(linesp) - 1, 1, -1):
            itemsp = linesp[index].split('=', 1)
            if len(itemsp) < 2:
                unparsed1 = (line.rsplit(linesp[index + 1])[0]
                             if index + 1 < len(linesp)
                             else line)
                unparsed2 = unparsed1.split(linesp[1])[-1]
                info["unparsed"] = unparsed2.strip()
                break
            info[itemsp[0]] = itemsp[1]

        info['raw_message'] = line
        return info

    def get(self, keywords):
        """
        Parameters:
            keywords(str or list): one or more strings to find in the lines.

        Returns:
            ([dicts]): all lines that contain all the keywords given as a
            list of dictionaries

        Examples::

            [
             {'timestamp': '1506487181.009',
              'msg_ID': '32794',
              'type': 'AVC',
              'unparsed': 'avc:  denied  { create } for',
              'raw_message': '...: ...'
              ...
             }, ...
            ]
        """
        r = []
        for l in self.lines:
            if ((type(keywords) == list and all([s in l for s in keywords])) or
                    (type(keywords) == str and keywords in l)):
                info = self._parse_line(l)
                if info:
                    r.append(info)
        return r

    def get_after(self, timestamp, lines=None):
        """
        Find all the (available) logs that are after the given time stamp.
        Override this function in class LogFileOutput.

        Parameters:

            timestamp(datetime.datetime): lines before this time are ignored.
            lines(list): an optional list of lines from this parser to search.

        Yields:
            (dict): the parsed data of lines with timestamps after this date in the
            same format they were supplied.
        """
        if lines is None:
            lines = self.lines

        for line in lines:
            info = self._parse_line(line)
            if info:
                try:
                    logtime = date.fromtimestamp(float(info.get('timestamp', 0)))
                    if logtime > timestamp:
                        yield info
                except:
                    pass
