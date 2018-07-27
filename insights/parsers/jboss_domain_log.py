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


@parser(Specs.jboss_standalone_server_log)
class JbossStandaloneServerLog(JbossDomainLog):
    """
    Read JBoss standalone server log file.

    Sample input::


        2018-07-17 10:58:44,606 INFO  [org.jboss.modules] (main) JBoss Modules version 1.6.0.Final-redhat-1
        2018-07-17 10:58:44,911 INFO  [org.jboss.msc] (main) JBoss MSC version 1.2.7.SP1-redhat-1
        2018-07-17 10:58:45,032 INFO  [org.jboss.as] (MSC service thread 1-7) WFLYSRV0049: JBoss EAP 7.1.0.GA (WildFly Core 3.0.10.Final-redhat-1) starting
        2018-07-17 10:58:45,033 DEBUG [org.jboss.as.config] (MSC service thread 1-7) Configured system properties:
            [Standalone] =
            awt.toolkit = sun.awt.X11.XToolkit
            file.encoding = UTF-8
            file.encoding.pkg = sun.io
            file.separator = /
            java.awt.graphicsenv = sun.awt.X11GraphicsEnvironment
            java.awt.headless = true
            java.awt.printerjob = sun.print.PSPrinterJob
            java.class.path = /opt/jboss-eap-7.1/jboss-modules.jar
            java.class.version = 52.0
            java.endorsed.dirs = /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/endorsed
            java.ext.dirs = /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/ext:/usr/java/packages/lib/ext
            java.home = /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre
            java.io.tmpdir = /tmp
            java.library.path = /usr/java/packages/lib/amd64:/usr/lib64:/lib64:/lib:/usr/lib
            java.net.preferIPv4Stack = true
            java.runtime.name = OpenJDK Runtime Environment
            java.runtime.version = 1.8.0_111-b16
            java.specification.name = Java Platform API Specification
            java.specification.vendor = Oracle Corporation
            java.specification.version = 1.8
            java.util.logging.manager = org.jboss.logmanager.LogManager
            java.vendor = Oracle Corporation
            java.vendor.url = http://java.oracle.com/
            java.vendor.url.bug = http://bugreport.sun.com/bugreport/
            java.version = 1.8.0_111
            java.vm.info = mixed mode
            java.vm.name = OpenJDK 64-Bit Server VM
            java.vm.specification.name = Java Virtual Machine Specification
            java.vm.specification.vendor = Oracle Corporation
            java.vm.specification.version = 1.8
            java.vm.vendor = Oracle Corporation
            java.vm.version = 25.111-b16
            javax.management.builder.initial = org.jboss.as.jmx.PluggableMBeanServerBuilder
            javax.xml.datatype.DatatypeFactory = __redirected.__DatatypeFactory
            javax.xml.parsers.DocumentBuilderFactory = __redirected.__DocumentBuilderFactory
            javax.xml.parsers.SAXParserFactory = __redirected.__SAXParserFactory
            javax.xml.stream.XMLEventFactory = __redirected.__XMLEventFactory
            javax.xml.stream.XMLInputFactory = __redirected.__XMLInputFactory
            javax.xml.stream.XMLOutputFactory = __redirected.__XMLOutputFactory
            javax.xml.transform.TransformerFactory = __redirected.__TransformerFactory
            javax.xml.validation.SchemaFactory:http://www.w3.org/2001/XMLSchema = __redirected.__SchemaFactory
            javax.xml.xpath.XPathFactory:http://java.sun.com/jaxp/xpath/dom = __redirected.__XPathFactory
            jboss.home.dir = /opt/jboss-eap-7.1
            jboss.host.name = mylinux
            jboss.modules.dir = /opt/jboss-eap-7.1/modules
            jboss.modules.system.pkgs = org.jboss.byteman
            jboss.node.name = mylinux
            jboss.qualified.host.name = mylinux
            jboss.server.base.dir = /opt/jboss-eap-7.1/standalone
            jboss.server.config.dir = /opt/jboss-eap-7.1/standalone/configuration
            jboss.server.data.dir = /opt/jboss-eap-7.1/standalone/data
            jboss.server.deploy.dir = /opt/jboss-eap-7.1/standalone/data/content
            jboss.server.log.dir = /opt/jboss-eap-7.1/standalone/log
            jboss.server.name = mylinux
            jboss.server.persist.config = true
            jboss.server.temp.dir = /opt/jboss-eap-7.1/standalone/tmp
            line.separator =

            logging.configuration = file:/opt/jboss-eap-7.1/standalone/configuration/logging.properties
            module.path = /opt/jboss-eap-7.1/modules
            org.jboss.boot.log.file = /opt/jboss-eap-7.1/standalone/log/server.log
            org.jboss.resolver.warning = true
            org.xml.sax.driver = __redirected.__XMLReaderFactory
            os.arch = amd64
            os.name = Linux
            os.version = 4.8.13-100.fc23.x86_64
            path.separator = :
            sun.arch.data.model = 64
            sun.boot.class.path = /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/resources.jar:/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/rt.jar:/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/sunrsasign.jar:/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/jsse.jar:/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/jce.jar:/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/charsets.jar:/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/jfr.jar:/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/classes
            sun.boot.library.path = /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b16.fc23.x86_64/jre/lib/amd64
            sun.cpu.endian = little
            sun.cpu.isalist =
            sun.desktop = gnome
            sun.io.unicode.encoding = UnicodeLittle
            sun.java.command = /opt/jboss-eap-7.1/jboss-modules.jar -mp /opt/jboss-eap-7.1/modules org.jboss.as.standalone -Djboss.home.dir=/opt/jboss-eap-7.1 -Djboss.server.base.dir=/opt/jboss-eap-7.1/standalone --server-config=standalone-ha.xml
            sun.java.launcher = SUN_STANDARD

    Examples:
        >>> type(standalone_log)
        <class 'insights.parsers.jboss_domain_log.JbossStandaloneServerLog'>
        >>> standalone_log.file_path
        '/JBOSS_HOME/standalone/log/server.log'
        >>> standalone_log.file_name
        'server.log'
        >>> len(standalone_log.get("sun.java.command ="))
        1
    """
    pass
