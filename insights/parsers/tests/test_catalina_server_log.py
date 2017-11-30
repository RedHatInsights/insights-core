from insights import add_filter
from insights.parsers.catalina_server_log import CatalinaServerlog
from insights.tests import context_wrap
from datetime import datetime

SERVER_LOG = """
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
""".strip()

add_filter("tomcat_server_log", [
    "Failed to initialize",
    "catalina",
    "-Djava"
])


def test_catalina_server_log():
    ser_log = CatalinaServerlog(context_wrap(SERVER_LOG))
    test_1 = ser_log.get('-Djava')
    assert 3 == len(test_1)
    test_2 = ser_log.get('Failed to initialize')
    assert 1 == len(test_2)
    assert test_2[0]['raw_message'] == 'SEVERE: Failed to initialize end point associated with ProtocolHandler ["http-bio-18080"]'
    assert len(list(ser_log.get_after(datetime(2017, 11, 28, 14, 11, 21)))) == 4
    assert "/var/cache/tomcat/temp" in ser_log
