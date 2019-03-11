"""
VDSMLog - file ``/var/log/vdsm/vdsm.log`` and ``/var/log/vdsm/import/import-*.log``
===================================================================================
"""

import re
from insights import LogFileOutput, parser
from datetime import datetime
from insights.specs import Specs


@parser(Specs.vdsm_log)
class VDSMLog(LogFileOutput):
    """Logs from the Virtual Desktop and Server Manager.

    Uses ``LogFileOutput`` as the base class - see its documentation for  more specific usage details.

    Sample logs from VDSM version 3::

        Thread-60::DEBUG::2015-05-08 18:01:03,071::blockSD::600::Storage.Misc.excCmd::(getReadDelay) '/bin/dd if=/dev/5a30691d-4fae-4023-ae96-50704f6b253c/metadata iflag=direct of=/dev/null bs=4096 count=1' (cwd None)
        Thread-60::DEBUG::2015-05-08 18:01:03,090::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\\n1+0 records out\\n4096 bytes (4.1 kB) copied, 0.00038933 s, 10.5 MB/s\\n'; <rc> = 0
        Thread-65::DEBUG::2015-05-08 18:01:04,835::blockSD::600::Storage.Misc.excCmd::(getReadDelay) '/bin/dd if=/dev/e70cce65-0d02-4da4-8781-6aeeef5c86ff/metadata iflag=direct of=/dev/null bs=4096 count=1' (cwd None)
        Thread-65::DEBUG::2015-05-08 18:01:04,857::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\\n1+0 records out\\n4096 bytes (4.1 kB) copied, 0.000157193 s, 26.1 MB/s\\n'; <rc> = 0
        Thread-4662::DEBUG::2015-05-08 18:01:05,560::task::595::TaskManager.Task::(_updateState) Task=`9a7948f6-b6d9-42c2-b91f-7e0346dfc1d6`::moving from state init -> state preparing

    Example:
        >>> from insights.parsers.vdsm_log import VDSMLog
        >>> from insights.tests import context_wrap
        >>> vdsm_log = VDSMLog(context_wrap(VDSM_LOG))
        >>> vdsm_log.get('TaskManager')
        'Thread-4662::DEBUG::2015-05-08 18:01:05,560::task::595::TaskManager.Task::(_updateState) Task=`9a7948f6-b6d9-42c2-b91f-7e0346dfc1d6`::moving from state init -> state preparing'
        >>> list(vdsm_log.parse_lines(vdsm_log.get('TaskManager')))[0]  # from generator to list to subscript
        {'thread': 'Thread-4662',
         'level': 'DEBUG',
         'asctime': datetime(2015, 5, 8, 18, 1, 5, 56000),
         'module': 'task',
         'line': '595',
         'logname': 'TaskManager.Task',
         'message': 'Task=`9a7948f6-b6d9-42c2-b91f-7e0346dfc1d6`::moving from state init -> state preparing'
        }


    Note: VDSM version 4 has different logs format than version 3.
    VDSM version 4 logs parser is designed to closely match log format
    as referred in ``/etc/vdsm/logger.conf`` which is as below::

        format: %(asctime)s %(levelname)-5s (%(threadName)s) [%(name)s] %(message)s (%(module)s:%(lineno)d)

    Sample logs from VDSM version 4::

        2017-04-18 14:00:00,000+0200 INFO  (jsonrpc/2) [jsonrpc.JsonRpcServer] RPC call Host.getStats succeeded in 0.02 seconds (__init__:515)
        2017-04-18 14:00:01,807+0200 INFO  (Reactor thread) [ProtocolDetector.AcceptorImpl] Accepted connection from ::ffff:10.34.60.219:49213 (protocoldetector:72)
        2017-04-18 14:00:01,808+0200 ERROR (Reactor thread) [ProtocolDetector.SSLHandshakeDispatcher] Error during handshake: unexpected eof (m2cutils:304)
        2017-04-18 14:00:03,304+0200 INFO  (jsonrpc/6) [jsonrpc.JsonRpcServer] RPC call Host.getAllVmStats succeeded in 0.00 seconds (__init__:515)
        2017-04-18 14:00:05,870+0200 INFO  (jsonrpc/7) [dispatcher] Run and protect: getSpmStatus(spUUID=u'00000002-0002-0002-0002-00000000024f', options=None) (logUtils:51)

    Example:
        >>> from insights.parsers.vdsm_log import VDSMLog
        >>> from insights.tests import context_wrap
        >>> vdsm_log = VDSMLog(context_wrap(VDSM_LOG))
        >>> lines_with_error = vdsm_log.get('ERROR')
        >>> list(vdsm_log.parse_lines(lines_with_error))[0]
        {'asctime': datetime(2017, 4, 18, 14, 0, 1, 808000),
         'levelname': 'ERROR',
         'thread_name': 'Reactor thread',
         'name': 'ProtocolDetector.SSLHandshakeDispatcher',
         'message': 'Error during handshake: unexpected eof',
         'module': 'm2cutils',
         'lineno': '304'
        }
    """
    def parse_lines(self, lines):
        """Parse log lines to be used with keep_scan or get

        Parameters:
            lines(list): Lines to be parsed

        Yields:
            Dictionary with following keys

            * **asctime(datetime)** - date and time as datetime object
            * **level(str)** - log level. Can me INFO, ERROR, WARN or DEBUG
            * **thread(str)** - thread name
            * **logname(str)** - filter name
            * **message(str)** - the body of the message
            * **module(str)** - module name
            * **lineno(str)** - line number which triggered the log

        This will NOT parse Python Traceback. Any unparsed line(s) will be yield as a list
        """
        time_format = '%Y-%m-%d %H:%M:%S,%f'

        # Parse data & time including milisecond at the begining of
        # line. Will ignore TZ hours difference.
        # Example: "2017-04-18 13:56:28,096+0200"
        #          2017    -   04  -   18  " "     13:56:28    ,  096     +0200
        #         \d{4}    - \d{2} - \d{2} \s+  [\d{2}:]+\d{2} , \d{3}  (ignored)     # noqa
        re_datetime_obj = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+[\d{2}:]+\d{2},\d{3})")  # noqa

        # Parse object name
        # Example: "[virt.vm]"
        #          [  virt.vm  ]
        #         \[  (\w.+)  \]
        re_name_obj = re.compile(r"\[(\w.+)\]")

        # In VDSM version 4 logs, three elements fall inside '()'.
        # Below pattern will catch anything that is in '()
        re_thread_and_module = re.compile(r"\((.*?)\)")

        # Capture anythin that falls between '[]' and '()'. '()' is
        # also at the end of line.
        # Example: "[virt.vm] The vm start process failed (vm:617)"
        #           \[\w.+\]           (.*?)              \(\w+\:\w+\)$
        re_message_obj = re.compile(r"\[\w.+\](.*?)\(\w+\:\w+\)$")

        # Capture INFO, ERROR, DEBUG and, WARN
        re_level_obj = re.compile(r"INFO|ERROR|DEBUG|WARN")

        for line in lines:
            # import pdb; pdb.set_trace()
            if isinstance(line, dict):
                line = line['raw_message']
            if re_datetime_obj.match(line):
                # VDSM version 4 log parser
                fields = dict()
                thread_and_module = re_thread_and_module.findall(line)
                timestamp = re_datetime_obj.search(line).group()
                fields['level'] = re_level_obj.search(line).group()
                fields['thread'] = thread_and_module[0]
                fields['logname'] = re_name_obj.findall(line)[0]
                fields['message'] = re_message_obj.findall(line)[0].strip()
                fields['module'], fields['lineno'] = thread_and_module[-1].split(':')  # noqa
                fields['asctime'] = datetime.strptime(timestamp, time_format)
                yield fields
            else:
                # VDSM version 3 log parser
                #
                # (psachin): I tried to keep the code unchanged as possible.
                #
                # If the line is too short, for some reason, then as many
                # fields as possible are pulled from the line.
                fieldnames = ('thread', 'level', 'timestamp', 'module', 'line', 'logname')
                fields = dict()
                parts = line.split('::', 6)
                fields.update(dict((k, v) for (k, v) in zip(fieldnames, filter(None, parts))))
                if len(parts) == 7:
                    func, msg = parts[6].split(' ', 1)
                    fields['message'] = msg
                # Did we get a timestamp in there?
                if 'timestamp' in fields:
                    # Try to convert the datetime if possible
                    try:
                        fields['asctime'] = datetime.strptime(
                            fields['timestamp'], time_format)
                        del fields['timestamp']
                    except:
                        pass
                yield fields


@parser(Specs.vdsm_import_log)
class VDSMImportLog(LogFileOutput):
    """Parser for the log file detailing virtual machine imports.

    Sample log file::

        [    0.2] preparing for copy
        [    0.2] Copying disk 1/1 to /rhev/data-center/958ca292-9126/f524d2ba-155a/images/502f5598-335d-/d4b140c8-9cd5
        [    0.0] >>> source, dest, and storage-type have different lengths

    Example:

        >>> log = vdsm_import_logs.get('preparing for copy')
        >>> len(log)
        1
        >>> log[0].get('raw_message', None)
        '[    0.2] preparing for copy'
        >>> vdsm_import_logs.vm_uuid              # file: import-1f9efdf5-2584-4a2a-8f85-c3b6f5dac4e0-20180130T154807.log
        '1f9efdf5-2584-4a2a-8f85-c3b6f5dac4e0'
        >>> vdsm_import_logs.file_datetime
        datetime.datetime(2018, 1, 30, 15, 48, 07)

    Attributes:
        vm_uuid (str): UUID of imported VM
        file_datetime (datetime): Date and time that import began.
    """
    _line_re = re.compile(r'^(?:\[\s+(?P<timestamp>\d+\.\d+)\]\s+)?(?P<message>.*)$')

    def parse_content(self, content):
        """Parse ``import-@UUID-@datetime.log`` log file."""
        super(VDSMImportLog, self).parse_content(content)
        splited_file_name = self.file_name.split('-')
        self.vm_uuid = '-'.join(splited_file_name[1:-1])
        _datetime = splited_file_name[-1].replace('.log', '')

        try:
            self.file_datetime = datetime.strptime(_datetime, '%Y%m%dT%H%M%S')
        except:
            self.file_datetime = None

    def get_after(self, timestamp, s=None):
        """Find all the (available) logs that are after the given time stamp.

        If `s` is not supplied, then all lines are used.  Otherwise, only the
        lines contain the `s` are used.  `s` can be either a single string or a
        strings list. For list, all keywords in the list must be found in the
        line.

        Parameters:
            timestamp(float): log lines after this time are returned.
            s(str or list): one or more strings to search for.
                If not supplied, all available lines are searched.
        Yields:
            Log lines with time stamps after the given time.
        Raises:
            TypeError: The ``timestamp`` should be in `float` type, otherwise a
                `TypeError` will be raised.
        """
        if not isinstance(timestamp, float):
            raise TypeError(
                        "get_after needs a float type timestamp, but get '{c}'".format(
                            c=timestamp)
            )

        including_lines = False
        search_by_expression = self._valid_search(s)
        for line in self.lines:
            # If `s` is not None, keywords must be found in the line
            if s and not search_by_expression(line):
                continue
            # Otherwise, search all lines
            match = self._line_re.search(line)
            if match and match.group('timestamp'):
                # Get logtimestamp and compare to given timestamp
                logstamp = float(match.group('timestamp'))
                if logstamp >= timestamp:
                    including_lines = True
                    yield self._parse_line(line)
                else:
                    including_lines = False
            else:
                # If we're including lines, add this continuation line
                if including_lines:
                    yield self._parse_line(line)
