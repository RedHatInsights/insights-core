from insights.tests import context_wrap
from insights.parsers import jboss_domain_log
from insights.parsers.jboss_domain_log import JbossDomainServerLog, JbossStandaloneServerLog
from datetime import time
import doctest

OUT1 = """
16:22:57,476 INFO  [org.xnio] (MSC service thread 1-12) XNIO Version 3.0.14.GA-redhat-1
16:22:57,480 INFO  [org.xnio.nio] (MSC service thread 1-12) XNIO NIO Implementation Version 3.0.14.GA-redhat-1
16:22:57,495 INFO  [org.jboss.remoting] (MSC service thread 1-12) JBoss Remoting version 3.3.5.Final-redhat-1
16:23:03,881 INFO  [org.jboss.as.controller.management-deprecated] (ServerService Thread Pool -- 23) JBAS014627: Attribute 'enabled' in the resource at address '/subsystem=datasources/data-source=ExampleDS' is deprecated, and may be removed in future version. See the attribute description in the output of the read-resource-description operation to learn more about the deprecation.
16:23:03,958 INFO  [org.jboss.as.security] (ServerService Thread Pool -- 37) JBAS013371: Activating Security Subsystem
16:23:03,960 INFO  [org.jboss.as.webservices] (ServerService Thread Pool -- 33) JBAS015537: Activating WebServices Extension
16:23:03,957 WARN  [org.jboss.as.txn] (ServerService Thread Pool -- 35) JBAS010153: Node identifier property is set to the default value. Please make sure it is unique.
16:23:03,962 INFO  [org.jboss.as.security] (MSC service thread 1-11) JBAS013370: Current PicketBox version=4.1.1.Final-redhat-1
16:23:03,974 INFO  [org.jboss.as.naming] (ServerService Thread Pool -- 42) JBAS011800: Activating Naming Subsystem
16:23:04,024 INFO  [org.jboss.as.clustering.infinispan] (ServerService Thread Pool -- 54) JBAS010280: Activating Infinispan subsystem.
16:23:04,049 INFO  [org.jboss.as.naming] (MSC service thread 1-8) JBAS011802: Starting Naming Service
16:23:04,058 INFO  [org.jboss.as.jacorb] (ServerService Thread Pool -- 53) JBAS016300: Activating JacORB Subsystem
16:23:04,066 INFO  [org.jboss.as.configadmin] (ServerService Thread Pool -- 58) JBAS016200: Activating ConfigAdmin Subsystem
16:23:04,077 INFO  [org.jboss.as.connector.logging] (MSC service thread 1-6) JBAS010408: Starting JCA Subsystem (IronJacamar 1.0.32.Final-redhat-1)
16:23:04,079 INFO  [org.jboss.as.connector.subsystems.datasources] (ServerService Thread Pool -- 57) JBAS010403: Deploying JDBC-compliant driver class org.h2.Driver (version 1.3)
16:23:04,080 INFO  [org.jboss.as.jsf] (ServerService Thread Pool -- 46) JBAS012615: Activated the following JSF Implementations: [main, 1.2]
16:23:04,267 INFO  [org.jboss.as.mail.extension] (MSC service thread 1-14) JBAS015400: Bound mail session [java:jboss/mail/Default]
16:23:04,366 INFO  [org.jboss.jaxr] (MSC service thread 1-16) JBAS014000: Started JAXR subsystem, binding JAXR connection factory into JNDI as: java:jboss/jaxr/ConnectionFactory
16:23:04,726 INFO  [org.apache.coyote.http11.Http11Protocol] (MSC service thread 1-4) JBWEB003001: Coyote HTTP/1.1 initializing on : http-/192.168.199.175:8080
16:23:04,745 INFO  [org.apache.coyote.http11.Http11Protocol] (MSC service thread 1-4) JBWEB003000: Coyote HTTP/1.1 starting on: http-/192.168.199.175:8080
16:23:04,801 INFO  [org.hornetq.core.server] (ServerService Thread Pool -- 60) HQ221000: live server is starting with configuration HornetQ Configuration (clustered=false,backup=false,sharedStore=true,journalDirectory=/home/test/jboss/machine2/domain/servers/server-one/data/messagingjournal,bindingsDirectory=/home/test/jboss/machine2/domain/servers/server-one/data/messagingbindings,largeMessagesDirectory=/home/test/jboss/machine2/domain/servers/server-one/data/messaginglargemessages,pagingDirectory=/home/test/jboss/machine2/domain/servers/server-one/data/messagingpaging)
16:23:04,809 INFO  [org.hornetq.core.server] (ServerService Thread Pool -- 60) HQ221006: Waiting to obtain live lock
16:23:04,969 INFO  [org.hornetq.core.server] (ServerService Thread Pool -- 60) HQ221013: Using NIO Journal
ectory=/home/test/jboss/machine2/domain/servers/server-one/data/messagingjournal,bindingsDirectory=/home/test/jboss/machine2/domain/servers/server-one/data/messagingbindings,largeMessagesDirectory=/home/test/jboss/machine2/domain/servers/server-one/data/messaginglargemessages,pagingDirectory=/home/test/jboss/machine2/domain/servers/server-one/data/messagingpaging)
16:23:05,018 INFO  [org.jboss.as.remoting] (MSC service thread 1-7) JBAS017100: Listening on 192.168.199.175:444
""".strip()


def test_jboss_domain_server_log():
    out_log = JbossDomainServerLog(
        context_wrap(OUT1,
                     path="/home/test/jboss/machine2/domain/servers/server-one/log/server.log"))
    assert out_log.file_path == "/home/test/jboss/machine2/domain/servers/server-one/log/server.log"
    assert "XNIO Version 3.0.14.GA-redhat-1" in out_log
    assert len(out_log.get("GA-redhat-1")) == 2
    assert out_log.get("GA-redhat-1")[0].get(
        "raw_message") == "16:22:57,476 INFO  [org.xnio] (MSC service thread 1-12) XNIO Version 3.0.14.GA-redhat-1"
    assert "Listening on 192.168.199.175:444" in out_log
    assert len(list(out_log.get_after(time(16, 23, 0o4)))) == 16


OUT2 = """
16:22:57,476 INFO  [org.xnio] (MSC service thread 1-12) XNIO Version 3.0.14.GA-redhat-1
16:22:57,480 INFO  [org.xnio.nio] (MSC service thread 1-12) XNIO NIO Implementation Version 3.0.14.GA-redhat-1
16:22:57,495 INFO  [org.jboss.remoting] (MSC service thread 1-12) JBoss Remoting version 3.3.5.Final-redhat-1
16:23:03,881 INFO  [org.jboss.as.controller.management-deprecated] (ServerService Thread Pool -- 23) JBAS014627: Attribute 'enabled' in the resource at address '/subsystem=datasources/data-source=ExampleDS' is deprecated, and may be removed in future version. See the attribute description in the output of the read-resource-description operation to learn more about the deprecation.
16:23:03,958 INFO  [org.jboss.as.security] (ServerService Thread Pool -- 37) JBAS013371: Activating Security Subsystem
""".strip()

standalong_server_log = """
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
    sun.jnu.encoding = UTF-8
    sun.management.compiler = HotSpot 64-Bit Tiered Compilers
    sun.os.patch.level = unknown
    user.country = US
    user.dir = /opt/jboss-eap-7.1/bin
    user.home = /home/lizhong
    user.language = en
    user.name = lizhong
    user.timezone = Asia/Shanghai
2018-07-17 10:58:45,033 DEBUG [org.jboss.as.config] (MSC service thread 1-7) VM Arguments: -D[Standalone] -verbose:gc -Xloggc:/opt/jboss-eap-7.1/standalone/log/gc.log -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=5 -XX:GCLogFileSize=3M -XX:-TraceClassUnloading -Xms1303m -Xmx1303m -XX:MetaspaceSize=96M -XX:MaxMetaspaceSize=256m -Djava.net.preferIPv4Stack=true -Djboss.modules.system.pkgs=org.jboss.byteman -Djava.awt.headless=true -Dorg.jboss.boot.log.file=/opt/jboss-eap-7.1/standalone/log/server.log -Dlogging.configuration=file:/opt/jboss-eap-7.1/standalone/configuration/logging.properties
2018-07-17 10:58:46,021 INFO  [org.jboss.as.controller.management-deprecated] (Controller Boot Thread) WFLYCTL0028: Attribute 'security-realm' in the resource at address '/core-service=management/management-interface=http-interface' is deprecated, and may be removed in future version. See the attribute description in the output of the read-resource-description operation to learn more about the deprecation.
2018-07-17 10:58:46,033 INFO  [org.wildfly.security] (ServerService Thread Pool -- 30) ELY00001: WildFly Elytron version 1.1.7.Final-redhat-1
2018-07-17 10:58:46,036 INFO  [org.jboss.as.controller.management-deprecated] (ServerService Thread Pool -- 15) WFLYCTL0028: Attribute 'security-realm' in the resource at address '/subsystem=undertow/server=default-server/https-listener=https' is deprecated, and may be removed in future version. See the attribute description in the output of the read-resource-description operation to learn more about the deprecation.
2018-07-17 10:58:46,172 INFO  [org.jboss.as.server] (Controller Boot Thread) WFLYSRV0039: Creating http management service using socket-binding (management-http)
"""


def test_jboss_standalone_server_log():
    out_log = JbossStandaloneServerLog(
        context_wrap(standalong_server_log, path="JBOSS_HOME/standalone/log/server.log"))
    assert out_log.file_path == "/JBOSS_HOME/standalone/log/server.log"
    assert "sun.java.command =" in out_log
    assert len(out_log.get("sun.java.command =")) == 1
    assert out_log.get("java.specification.")[-1][
               "raw_message"].strip() == "java.specification.version = 1.8"


def test_jboss_domain_server_log_doc_examples():
    env = {
        'JbossDomainServerLog': JbossDomainServerLog,
        'log': JbossDomainServerLog(context_wrap(OUT2,
                                                 path='/home/test/jboss/machine2/domain/servers/server-one/log/server.log')),
        'JbossStandaloneServerLog': JbossStandaloneServerLog,
        'standalone_log': JbossStandaloneServerLog(context_wrap(standalong_server_log,
                                                                path="/JBOSS_HOME/standalone/log/server.log")),
    }
    failed, total = doctest.testmod(jboss_domain_log, globs=env)
    assert failed == 0
