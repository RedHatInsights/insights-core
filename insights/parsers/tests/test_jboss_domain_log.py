from insights.tests import context_wrap
from insights.parsers import jboss_domain_log
from insights.parsers.jboss_domain_log import JbossDomainServerLog
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
        context_wrap(OUT1, path="/home/test/jboss/machine2/domain/servers/server-one/log/server.log"))
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


def test_jboss_domain_server_log_doc_examples():
    env = {
            'JbossDomainServerLog': JbossDomainServerLog,
            'log': JbossDomainServerLog(context_wrap(OUT2, path='/home/test/jboss/machine2/domain/servers/server-one/log/server.log')),
          }
    failed, total = doctest.testmod(jboss_domain_log, globs=env)
    assert failed == 0
