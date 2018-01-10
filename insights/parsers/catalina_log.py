"""
catalina_log - Log files for Tomcat
===================================

.. note::
    The tomcat log files are gotten from the directory specified in the java
    commands.
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.catalina_server_log)
class CatalinaServerLog(LogFileOutput):
    """
    Read the tomcat server log file.

    Note that the standard format of Catalina log lines spreads the information
    over two lines::

        INFO: Command line argument: -Djava.io.tmpdir=/var/cache/tomcat/temp
        Nov 28, 2017 2:11:20 PM org.apache.catalina.startup.VersionLoggerListener log
        INFO: Command line argument: -Djava.util.logging.config.file=/usr/share/tomcat/conf/logging.properties
        Nov 28, 2017 2:11:20 PM org.apache.catalina.startup.VersionLoggerListener log
        INFO: Command line argument: -Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager
        Nov 28, 2017 2:11:20 PM org.apache.catalina.core.AprLifecycleListener lifecycleEvent
        INFO: The APR based Apache Tomcat Native library which allows optimal performance in production environments was not found on the java.library.path: /usr/java/packages/lib/amd64:/usr/lib64:/lib64:/lib:/usr/lib
        Nov 28, 2017 2:11:22 PM org.apache.coyote.AbstractProtocol init
        INFO: Initializing ProtocolHandler ["http-bio-18080"]
        Nov 28, 2017 2:11:23 PM org.apache.coyote.AbstractProtocol init
        SEVERE: Failed to initialize end point associated with ProtocolHandler ["http-bio-18080"]

    However, this parser only recognises single lines.
    Please refer to its super-class :class:`insights.core.LogFileOutput`.

    When using this parser, consider using a filter or a scan method, e.g.::

        CatalinaServerLog.filters.append('initializing ProtocolHandler')
        CatalinaServerLog.keep_scan('init_pro', 'initializing ProtocolHandler')

    Examples:
        >>> type(log)
        <class 'insights.parsers.catalina_log.CatalinaServerLog'>
        >>> log.file_path
        '/var/log/tomcat/catalina.2017-11-28.log'
        >>> log.file_name
        'catalina.2017-11-28.log'
        >>> log.get('Failed to initialize')[0]['raw_message']
        'SEVERE: Failed to initialize end point associated with ProtocolHandler ["http-bio-18080"]'
        >>> '/var/cache/tomcat/temp' in log
        True
        >>> from datetime import datetime
        >>> list(log.get_after(datetime(2017, 11, 28, 14, 11, 21)))[0]['raw_message']
        'Nov 28, 2017 2:11:22 PM org.apache.coyote.AbstractProtocol init'
    """
    time_format = '%b %d, %Y %I:%M:%S %p'


@parser(Specs.catalina_out)
class CatalinaOut(LogFileOutput):
    """
    This parser reads all ``catalina.out`` files in the ``/var/log/tomcat*``
    directories.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Note that the standard format of Catalina log lines spreads the information
    over two lines::

        Nov 10, 2015 8:52:38 AM org.apache.jk.common.MsgAjp processHeader
        SEVERE: BAD packet signature 18245
        Nov 10, 2015 8:52:38 AM org.apache.jk.common.ChannelSocket processConnection
        SEVERE: Error, processing connection
        SEVERE: BAD packet signature 18245
        Nov 10, 2015 8:52:38 AM org.apache.jk.common.ChannelSocket processConnection
        SEVERE: Error, processing connection
        Nov 10, 2015 4:55:48 PM org.apache.coyote.http11.Http11Protocol pause
        INFO: Pausing Coyote HTTP/1.1 on http-8080

    However, this parser only recognises single lines.

    When using this parser, consider using a filter or a scan method, e.g.::

        CatalinaOut.filters.append('BAD packet signature')
        CatalinaOut.keep_scan('bad_signatures', 'BAD packet signature')

    Example:
        >>> type(out)
        <class 'insights.parsers.catalina_log.CatalinaOut'>
        >>> out.file_path
        '/var/log/tomcat/catalina.out'
        >>> out.file_name
        'catalina.out'
        >>> len(out.get('SEVERE'))
        4
        >>> 'Http11Protocol pause' in out
        True
        >>> out.lines[0]
        'Nov 10, 2015 8:52:38 AM org.apache.jk.common.MsgAjp processHeader'
        >>> from datetime import datetime
        >>> list(out.get_after(datetime(2015, 11, 10, 12, 00, 00)))[0]['raw_message']
        'Nov 10, 2015 4:55:48 PM org.apache.coyote.http11.Http11Protocol pause'
    """
    time_format = '%b %d, %Y %I:%M:%S %p'
