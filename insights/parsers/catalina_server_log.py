"""
CatalinaServerlog - ``catalina*.log`` files for Tomcat
======================================================
.. warning::
    Deprecated parser, please use
    :class:`insights.parsers.catalina_log.CatalinaServerLog` instead.

.. note::
    On RHEL6, the default tomcat server log file is under /var/log/tomcat6/.
    On RHEL7, the default tomcat server log file is under /var/log/tomcat/.

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

    CatalinaServerlog.filters.append('initializing ProtocolHandler')
    CatalinaServerlog.keep_scan('init_pro', 'initializing ProtocolHandler')

Examples:
    >>> CatalinaServerlog.filters.append('Failed to initialize')
    >>> log = shared[CatalinaServerlog]
    >>> log.file_path
    '/var/log/tomcat/catalina.2017-11-28.log'
    >>> catalina.file_name
    'catalina.2017-11-28.log'
    >>> error_msgs = log.get('Failed to initialize')
    >>> error_msgs[0]['raw_message']
    'SEVERE: Failed to initialize end point associated with ProtocolHandler ["http-bio-18080"]'
    >>> '/var/cache/tomcat/temp' in log
    True
    >>> from datetime import datetime
    >>> log.get_after(datetime(2017, 11, 28, 14, 11, 21))[0]['raw_message']
    'Nov 28, 2017 2:11:22 PM org.apache.coyote.AbstractProtocol init'
"""

from .. import LogFileOutput, parser
from insights.util import deprecated


@parser("catalina_server_log")
class CatalinaServerlog(LogFileOutput):
    """
    Read the default tomcat server log file.
    """
    def __init__(self, *args, **kwargs):
        deprecated(CatalinaServerlog, "Use the `CatalinaServerLog` parser in the `catalina_log` module")
        super(CatalinaServerlog, self).__init__(*args, **kwargs)

    time_format = '%b %d, %Y %I:%M:%S %p'
