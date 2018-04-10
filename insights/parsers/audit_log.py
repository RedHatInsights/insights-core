"""
audit_log - File ``/var/log/audit/audit.log``
=============================================
"""

import shlex
from datetime import date
from .. import LogFileOutput, parser, add_filter
from insights.specs import Specs

# Currently, only selinux related(AVC type) audit logs are interested.
# Add this filter in parser directly to filter out too many other types logs.
# Also, filters can be changed to meet any further requirments.
filter_list = [
    'type=AVC',
]
add_filter(Specs.audit_log, filter_list)


@parser(Specs.audit_log)
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
        [{
            'is_valid': True,
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
        }]
        >>> assert len(list(log.get_after(timestamp=date.fromtimestamp(1506047401.407)))) == 3
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
            * Note, if a line isn't parseable by the above steps, return dict with items 'raw_message' and 'is_valid' only.

        Parameters:
            line(string): Log line to parse

        Yields:
            Dictionary corresponding to the data in line split into
            functional elements:

            * **raw_message** - the original unparsed line
            * **is_valid** - true if the line is parseable, else false
            * **type** - the log type
            * **timestamp** - the timestamp of the log line (as a string)
            * **msg_ID** - the serial number behind the timestamp
            * **unparsed** - the unparsed part in log, may or maynot exist

            If the line is not regular, for some reason, then as many fields as
            possible are pulled from the line.
        """
        info = {'raw_message': line, 'is_valid': False}
        linesp = shlex.split(line)

        if (len(linesp) < 2 or
                not (linesp[0] and linesp[0].startswith('type=')) or
                not (linesp[1] and linesp[1].startswith('msg=audit('))):
            return info

        timestamp_id = linesp[1].lstrip('msg=audit(').rstrip('):')
        timestamp_id_sp = timestamp_id.split(':')
        if len(timestamp_id_sp) != 2:
            return info

        info['type'] = linesp[0].lstrip('type=')
        info['timestamp'] = timestamp_id_sp[0]
        info['msg_ID'] = timestamp_id_sp[1]

        for index in range(len(linesp) - 1, 1, -1):
            itemsp = linesp[index].split('=', 1)
            if len(itemsp) < 2:
                unparsed1 = (line.rsplit(linesp[index + 1])[0]
                             if index + 1 < len(linesp)
                             else line)
                unparsed2 = unparsed1.split(linesp[1])[-1]
                info["unparsed"] = unparsed2.strip()
                break
            info[itemsp[0]] = itemsp[1]

        info['is_valid'] = True
        return info

    def get_after(self, timestamp, s=None):
        """
        Find all the (available) logs that are after the given time stamp.
        Override this function in class LogFileOutput.

        Parameters:

            timestamp(datetime.datetime): lines before this time are ignored.
            s(str or list): one or more strings to search for.
                If not supplied, all available lines are searched.

        Yields:
            (dict): the parsed data of lines with timestamps after this date in the
            same format they were supplied.
        """
        search_by_expression = self._valid_search(s)
        for line in self.lines:
            # If `s` is not None, keywords must be found in the line
            if s and not search_by_expression(line):
                continue
            info = self._parse_line(line)
            try:
                logtime = date.fromtimestamp(float(info.get('timestamp', 0)))
                if logtime > timestamp:
                    yield info
            except:
                pass
