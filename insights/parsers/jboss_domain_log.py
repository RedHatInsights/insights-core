"""
JbossDomainServerLog - file ``$JBOSS_SERVER_LOG_DIR/server.log*``
=================================================================

Parser for the JBoss Domain Server Log File.
"""

from .. import LogFileOutput, parser
import re
from datetime import time
from insights.specs import Specs


class JbossDomainLog(LogFileOutput):
    """
    Read JBoss domain log file.
    """
    time_format = '%H:%M:%S'
    _line_re = re.compile(r'^(?P<timestamp>\d+:\d+:\d+)(,\d+)(?P<messages>.*)$')

    def get_after(self, timestamp, s=None):
        """
        Find all the (available) logs that are after the given time stamp.

        If `s` is not supplied, then all lines are used.  Otherwise, only the
        lines contain the `s` are used.  `s` can be either a single string or a
        strings list. For list, all keywords in the list must be found in the
        line.

        .. note::
            The time stamp is time type instead of usual datetime type. If
            a time stamp is not found on the line between square brackets, then
            it is treated as a continuation of the previous line and is only
            included if the previous line's timestamp is greater than the
            timestamp given.  Because continuation lines are only included if a
            previous line has matched, this means that searching in logs that do
            not have a time stamp produces no lines.

        Parameters:
            timestamp(time): log lines after this time are returned.
            s(str or list): one or more strings to search for.
                If not supplied, all available lines are searched.

        Yields:
            Log lines with time stamps after the given time.

        Raises:
            TypeError: The ``timestamp`` should be in `time` type, otherwise a
                `TypeError` will be raised.
        """
        if not isinstance(timestamp, time):
            raise TypeError(
                "get_after needs a time type timestamp, but get '{c}'".format(
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
                l_hh, l_mm, l_ss = match.group('timestamp').split(":")
                logstamp = time(int(l_hh), int(l_mm), int(l_ss))
                if logstamp >= timestamp:
                    including_lines = True
                    yield self._parse_line(line)
                else:
                    including_lines = False
            else:
                # If we're including lines, add this continuation line
                if including_lines:
                    yield self._parse_line(line)


@parser(Specs.jboss_domain_server_log)
class JbossDomainServerLog(JbossDomainLog):
    """
    Read JBoss domain server log file.

    Sample input::


        16:22:57,476 INFO  [org.xnio] (MSC service thread 1-12) XNIO Version 3.0.14.GA-redhat-1
        16:22:57,480 INFO  [org.xnio.nio] (MSC service thread 1-12) XNIO NIO Implementation Version 3.0.14.GA-redhat-1
        16:22:57,495 INFO  [org.jboss.remoting] (MSC service thread 1-12) JBoss Remoting version 3.3.5.Final-redhat-1
        16:23:03,881 INFO  [org.jboss.as.controller.management-deprecated] (ServerService Thread Pool -- 23) JBAS014627: Attribute 'enabled' in the resource at address '/subsystem=datasources/data-source=ExampleDS' is deprecated, and may be removed in future version. See the attribute description in the output of the read-resource-description operation to learn more about the deprecation.
        16:23:03,958 INFO  [org.jboss.as.security] (ServerService Thread Pool -- 37) JBAS013371: Activating Security Subsystem


    Examples:
        >>> type(log)
        <class 'insights.parsers.jboss_domain_log.JbossDomainServerLog'>
        >>> log.file_path
        '/home/test/jboss/machine2/domain/servers/server-one/log/server.log'
        >>> log.file_name
        'server.log'
        >>> error_msgs = log.get('3.0.14.GA-redhat-1')
        >>> error_msgs[0]['raw_message']
        '16:22:57,476 INFO  [org.xnio] (MSC service thread 1-12) XNIO Version 3.0.14.GA-redhat-1'
        >>> 'Activating Security Subsystem' in log
        True
        >>> from datetime import time
        >>> list(log.get_after(time(16, 23, 3)))[1]['raw_message']
        '16:23:03,958 INFO  [org.jboss.as.security] (ServerService Thread Pool -- 37) JBAS013371: Activating Security Subsystem'
    """
    pass
