from insights.parsers import catalina_log
from insights.parsers.catalina_log import CatalinaServerLog, CatalinaOut
from insights.tests import context_wrap
from datetime import datetime
import doctest

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


def test_catalina_server_log():
    ser_log = CatalinaServerLog(context_wrap(SERVER_LOG))
    test_1 = ser_log.get('-Djava')
    assert 3 == len(test_1)
    test_2 = ser_log.get('Failed to initialize')
    assert 1 == len(test_2)
    assert test_2[0]['raw_message'] == 'SEVERE: Failed to initialize end point associated with ProtocolHandler ["http-bio-18080"]'
    assert len(list(ser_log.get_after(datetime(2017, 11, 28, 14, 11, 21)))) == 4
    assert "/var/cache/tomcat/temp" in ser_log


CATALINA_OUT1 = """
Nov 10, 2015 8:52:38 AM org.apache.jk.common.MsgAjp processHeader
SEVERE: BAD packet signature 18245
Nov 10, 2015 8:52:38 AM org.apache.jk.common.ChannelSocket processConnection
SEVERE: Error, processing connection
SEVERE: BAD packet signature 18245
Nov 10, 2015 8:52:38 AM org.apache.jk.common.ChannelSocket processConnection
SEVERE: Error, processing connection
INFO: Pausing Coyote HTTP/1.1 on http-8080
Nov 10, 2015 4:55:48 PM org.apache.coyote.http11.Http11Protocol pause
INFO: Pausing Coyote HTTP/1.1 on http-8443
Nov 10, 2015 4:55:49 PM org.apache.catalina.core.StandardService stop
INFO: Stopping service Catalina
INFO: Initializing Coyote HTTP/1.1 on http-8080
Nov 10, 2015 6:09:39 PM org.apache.coyote.http11.Http11Protocol init
INFO: Initializing Coyote HTTP/1.1 on http-8443
Nov 10, 2015 6:09:39 PM org.apache.catalina.startup.Catalina load
INFO: Initialization processed in 514 ms
Nov 10, 2015 6:09:39 PM org.apache.catalina.core.StandardService start
INFO: Starting service Catalina
Nov 10, 2015 6:09:39 PM org.apache.catalina.core.StandardEngine start
INFO: Starting Servlet Engine: Apache Tomcat/6.0.24
Nov 10, 2015 6:09:39 PM org.apache.catalina.startup.HostConfig deployDescriptor
INFO: Deploying configuration descriptor candlepin.xml
Nov 10, 2015 6:09:39 PM org.apache.catalina.loader.WebappClassLoader validateJarFile
INFO: validateJarFile(/usr/share/tomcat6/webapps/candlepin/WEB-INF/lib/servlet.jar) - jar not loaded. See Servlet Spec 2.3, section 9.7.2. Offending class: javax/servlet/Servlet.class
Nov 10, 2015 6:09:40 PM com.google.inject.internal.ProxyFactory <init>
WARNING: Method [protected org.candlepin.model.AbstractHibernateObject org.candlepin.resource.ConsumerContentOverrideResource.findParentById(java.lang.String)] is synthetic and is being intercepted by [org.candlepin.guice.CandlepinResourceTxnInterceptor@3b967594]. This could indicate a bug.  The method may be intercepted twice, or may not be intercepted at all.
Nov 10, 2015 6:09:40 PM com.google.inject.internal.ProxyFactory <init>
WARNING: Method [protected org.candlepin.model.AbstractHibernateObject org.candlepin.resource.ActivationKeyContentOverrideResource.findParentById(java.lang.String)] is synthetic and is being intercepted by [org.candlepin.guice.CandlepinResourceTxnInterceptor@3b967594]. This could indicate a bug.  The method may be intercepted twice, or may not be intercepted at all.
Nov 10, 2015 6:09:42 PM com.mchange.v2.log.MLog <clinit>
INFO: MLog clients using java 1.4+ standard logging.
Nov 10, 2015 6:09:42 PM com.mchange.v2.c3p0.C3P0Registry banner
INFO: Initializing c3p0-0.9.1.2 [built 31-March-2011 15:45:28; debug? false; trace: 5]
Nov 10, 2015 6:09:42 PM com.mchange.v2.c3p0.impl.AbstractPoolBackedDataSource getPoolManager
INFO: Initializing c3p0 pool... com.mchange.v2.c3p0.PoolBackedDataSource@64caac34 [ connectionPoolDataSource -> com.mchange.v2.c3p0.WrapperConnectionPoolDataSource@423e8640 [ acquireIncrement -> 3, acquireRetryAttempts -> 30, acquireRetryDelay -> 1000, autoCommitOnClose -> false, automaticTestTable -> null, breakAfterAcquireFailure -> false, checkoutTimeout -> 0, connectionCustomizerClassName -> null, connectionTesterClassName -> com.mchange.v2.c3p0.impl.DefaultConnectionTester, debugUnreturnedConnectionStackTraces -> false, factoryClassLocation -> null, forceIgnoreUnresolvedTransactions -> false, identityToken -> 2sonpk9c1vlvek918mzet6|3f7eb8ff, idleConnectionTestPeriod -> 300, initialPoolSize -> 5, maxAdministrativeTaskTime -> 0, maxConnectionAge -> 0, maxIdleTime -> 300, maxIdleTimeExcessConnections -> 0, maxPoolSize -> 20, maxStatements -> 0, maxStatementsPerConnection -> 0, minPoolSize -> 5, nestedDataSource -> com.mchange.v2.c3p0.DriverManagerDataSource@b4aff57d [ description -> null, driverClass -> null, factoryClassLocation -> null, identityToken -> 2sonpk9c1vlvek918mzet6|7a35d387, jdbcUrl -> jdbc:postgresql://localhost:5432/candlepin, properties -> {user=******, password=******, autocommit=true, release_mode=auto} ], preferredTestQuery -> null, propertyCycle -> 0, testConnectionOnCheckin -> false, testConnectionOnCheckout -> false, unreturnedConnectionTimeout -> 0, usesTraditionalReflectiveProxies -> false; userOverrides: {} ], dataSourceName -> null, factoryClassLocation -> null, identityToken -> 2sonpk9c1vlvek918mzet6|2764e21d, numHelperThreads -> 3 ]
WARN [UUIDHexGenerator] - HHH000409: Using org.hibernate.id.UUIDHexGenerator which does not generate IETF RFC 4122 compliant UUID values; consider using org.hibernate.id.UUIDGenerator instead
Nov 10, 2015 6:09:45 PM org.apache.catalina.startup.HostConfig deployDescriptor
INFO: Deploying configuration descriptor gutterball.xml
Nov 10, 2015 6:09:45 PM org.apache.catalina.loader.WebappClassLoader validateJarFile
INFO: validateJarFile(/usr/share/tomcat6/webapps/gutterball/WEB-INF/lib/servlet.jar) - jar not loaded. See Servlet Spec 2.3, section 9.7.2. Offending class: javax/servlet/Servlet.class
WARN [ConnectionProviderInitiator] - HHH000208: org.hibernate.connection.C3P0ConnectionProvider has been deprecated in favor of org.hibernate.service.jdbc.connections.internal.C3P0ConnectionProvider; that provider will be used instead.
Nov 10, 2015 6:09:46 PM com.mchange.v2.log.MLog <clinit>
INFO: MLog clients using java 1.4+ standard logging.
Nov 10, 2015 6:09:46 PM com.mchange.v2.c3p0.C3P0Registry banner
INFO: Initializing c3p0-0.9.1.2 [built 31-March-2011 15:45:28; debug? false; trace: 5]
Nov 10, 2015 6:09:46 PM com.mchange.v2.c3p0.management.ActiveManagementCoordinator attemptManageC3P0Registry
WARNING: A C3P0Registry mbean is already registered. This probably means that an application using c3p0 was undeployed, but not all PooledDataSources were closed prior to undeployment. This may lead to resource leaks over time. Please take care to close all PooledDataSources.
Nov 10, 2015 6:09:46 PM com.mchange.v2.c3p0.impl.AbstractPoolBackedDataSource getPoolManager
INFO: Initializing c3p0 pool... com.mchange.v2.c3p0.PoolBackedDataSource@daaa54fa [ connectionPoolDataSource -> com.mchange.v2.c3p0.WrapperConnectionPoolDataSource@813e3887 [ acquireIncrement -> 3, acquireRetryAttempts -> 30, acquireRetryDelay -> 1000, autoCommitOnClose -> false, automaticTestTable -> null, breakAfterAcquireFailure -> false, checkoutTimeout -> 0, connectionCustomizerClassName -> null, connectionTesterClassName -> com.mchange.v2.c3p0.impl.DefaultConnectionTester, debugUnreturnedConnectionStackTraces -> false, factoryClassLocation -> null, forceIgnoreUnresolvedTransactions -> false, identityToken -> 2sonpk9c1vlvhv6yu2uxw|5adff1b7, idleConnectionTestPeriod -> 300, initialPoolSize -> 5, maxAdministrativeTaskTime -> 0, maxConnectionAge -> 0, maxIdleTime -> 300, maxIdleTimeExcessConnections -> 0, maxPoolSize -> 20, maxStatements -> 0, maxStatementsPerConnection -> 0, minPoolSize -> 5, nestedDataSource -> com.mchange.v2.c3p0.DriverManagerDataSource@a5e5a991 [ description -> null, driverClass -> null, factoryClassLocation -> null, identityToken -> 2sonpk9c1vlvhv6yu2uxw|4d06026b, jdbcUrl -> jdbc:postgresql:gutterball, properties -> {user=******, password=******, autocommit=true, release_mode=auto} ], preferredTestQuery -> null, propertyCycle -> 0, testConnectionOnCheckin -> false, testConnectionOnCheckout -> false, unreturnedConnectionTimeout -> 0, usesTraditionalReflectiveProxies -> false; userOverrides: {} ], dataSourceName -> null, factoryClassLocation -> null, identityToken -> 2sonpk9c1vlvhv6yu2uxw|7efd82a6, numHelperThreads -> 3 ]
WARN [UUIDHexGenerator] - HHH000409: Using org.hibernate.id.UUIDHexGenerator which does not generate IETF RFC 4122 compliant UUID values; consider using org.hibernate.id.UUIDGenerator instead
Nov 10, 2015 6:09:47 PM org.apache.coyote.http11.Http11Protocol start
INFO: Starting Coyote HTTP/1.1 on http-8080
Nov 10, 2015 6:09:47 PM org.apache.coyote.http11.Http11Protocol start
INFO: Starting Coyote HTTP/1.1 on http-8443
Nov 10, 2015 6:09:47 PM org.apache.jk.common.ChannelSocket init
INFO: JK: ajp13 listening on /0.0.0.0:8009
Nov 10, 2015 6:09:47 PM org.apache.jk.server.JkMain start
INFO: Jk running ID=0 time=0/15  config=null
Nov 10, 2015 6:09:47 PM org.apache.catalina.startup.Catalina start
INFO: Server startup in 8434 ms
Nov 10, 2015 6:36:08 PM org.apache.coyote.http11.Http11Protocol pause
INFO: Pausing Coyote HTTP/1.1 on http-8080
Nov 10, 2015 6:36:08 PM org.apache.coyote.http11.Http11Protocol pause
INFO: Pausing Coyote HTTP/1.1 on http-8443
Nov 10, 2015 6:36:09 PM org.apache.catalina.core.StandardService stop
INFO: Stopping service Catalina
WARN [client] - HQ212037: Connection failure has been detected: HQ119015: The connection was disconnected because of server shutdown [code=DISCONNECTED]
WARN [client] - HQ212037: Connection failure has been detected: HQ119015: The connection was disconnected because of server shutdown [code=DISCONNECTED]
WARN [client] - HQ212037: Connection failure has been detected: HQ119015: The connection was disconnected because of server shutdown [code=DISCONNECTED]
WARN [server] - HQ222113: On ManagementService stop, there are 1 unexpected registered MBeans: [core.acceptor.2175e4c3-8800-11e5-9ba9-3f3f219d3ca7]
Nov 10, 2015 6:37:58 PM org.apache.catalina.core.AprLifecycleListener init
INFO: The APR based Apache Tomcat Native library which allows optimal performance in production environments was not found on the java.library.path: /usr/java/packages/lib/amd64:/usr/lib64:/lib64:/lib:/usr/lib
Nov 10, 2015 6:37:59 PM org.apache.coyote.http11.Http11Protocol init
INFO: Initializing Coyote HTTP/1.1 on http-8080
Nov 10, 2015 6:38:00 PM org.apache.coyote.http11.Http11Protocol init
INFO: Initializing Coyote HTTP/1.1 on http-8443
Nov 10, 2015 6:38:00 PM org.apache.catalina.startup.Catalina load
INFO: Initialization processed in 2278 ms
Nov 10, 2015 6:38:00 PM org.apache.catalina.core.StandardService start
INFO: Starting service Catalina
Nov 10, 2015 6:38:00 PM org.apache.catalina.core.StandardEngine start
INFO: Starting Servlet Engine: Apache Tomcat/6.0.24
Nov 10, 2015 6:38:00 PM org.apache.catalina.startup.HostConfig deployDescriptor
INFO: Deploying configuration descriptor candlepin.xml
Nov 10, 2015 6:38:01 PM org.apache.catalina.loader.WebappClassLoader validateJarFile
INFO: validateJarFile(/usr/share/tomcat6/webapps/candlepin/WEB-INF/lib/servlet.jar) - jar not loaded. See Servlet Spec 2.3, section 9.7.2. Offending class: javax/servlet/Servlet.class
Nov 10, 2015 6:38:26 PM com.mchange.v2.c3p0.management.ActiveManagementCoordinator attemptManageC3P0Registry
WARNING: A C3P0Registry mbean is already registered. This probably means that an application using c3p0 was undeployed, but not all PooledDataSources were closed prior to undeployment. This may lead to resource leaks over time. Please take care to close all PooledDataSources.
Nov 10, 2015 6:38:26 PM com.mchange.v2.c3p0.impl.AbstractPoolBackedDataSource getPoolManager
INFO: Initializing c3p0 pool... com.mchange.v2.c3p0.PoolBackedDataSource@86244320 [ connectionPoolDataSource -> com.mchange.v2.c3p0.WrapperConnectionPoolDataSource@d2a45c5e [ acquireIncrement -> 3, acquireRetryAttempts -> 30, acquireRetryDelay -> 1000, autoCommitOnClose -> false, automaticTestTable -> null, breakAfterAcquireFailure -> false, checkoutTimeout -> 0, connectionCustomizerClassName -> null, connectionTesterClassName -> com.mchange.v2.c3p0.impl.DefaultConnectionTester, debugUnreturnedConnectionStackTraces -> false, factoryClassLocation -> null, forceIgnoreUnresolvedTransactions -> false, identityToken -> 2sonpk9c1vmwckfzb7843|3ee3c109, idleConnectionTestPeriod -> 300, initialPoolSize -> 5, maxAdministrativeTaskTime -> 0, maxConnectionAge -> 0, maxIdleTime -> 300, maxIdleTimeExcessConnections -> 0, maxPoolSize -> 20, maxStatements -> 0, maxStatementsPerConnection -> 0, minPoolSize -> 5, nestedDataSource -> com.mchange.v2.c3p0.DriverManagerDataSource@4d38de29 [ description -> null, driverClass -> null, factoryClassLocation -> null, identityToken -> 2sonpk9c1vmwckfzb7843|34039dfc, jdbcUrl -> jdbc:postgresql:gutterball, properties -> {user=******, password=******, autocommit=true, release_mode=auto} ], preferredTestQuery -> null, propertyCycle -> 0, testConnectionOnCheckin -> false, testConnectionOnCheckout -> false, unreturnedConnectionTimeout -> 0, usesTraditionalReflectiveProxies -> false; userOverrides: {} ], dataSourceName -> null, factoryClassLocation -> null, identityToken -> 2sonpk9c1vmwckfzb7843|73f90cb5, numHelperThreads -> 3 ]
WARN [UUIDHexGenerator] - HHH000409: Using org.hibernate.id.UUIDHexGenerator which does not generate IETF RFC 4122 compliant UUID values; consider using org.hibernate.id.UUIDGenerator instead
Nov 10, 2015 6:38:26 PM org.apache.coyote.http11.Http11Protocol start
INFO: Starting Coyote HTTP/1.1 on http-8080
Nov 10, 2015 6:38:26 PM org.apache.coyote.http11.Http11Protocol start
INFO: Starting Coyote HTTP/1.1 on http-8443
Nov 10, 2015 6:38:27 PM org.apache.jk.common.ChannelSocket init
INFO: JK: ajp13 listening on /0.0.0.0:8009
Nov 10, 2015 6:38:27 PM org.apache.jk.server.JkMain start
INFO: Jk running ID=0 time=0/107  config=null
Nov 10, 2015 6:38:27 PM org.apache.catalina.startup.Catalina start
INFO: Server startup in 27028 ms
""".strip()


def test_catalina_out():
    out_log = CatalinaOut(context_wrap(CATALINA_OUT1))
    assert "IETF RFC 4122 compliant UUID" in out_log
    assert len(out_log.get("SEVERE")) == 4
    assert len(list(out_log.get_after(datetime(2015, 11, 10, 18, 38, 10)))) == 15


CATALINA_OUT2 = """
Nov 10, 2015 8:52:38 AM org.apache.jk.common.MsgAjp processHeader
SEVERE: BAD packet signature 18245
Nov 10, 2015 8:52:38 AM org.apache.jk.common.ChannelSocket processConnection
SEVERE: Error, processing connection
SEVERE: BAD packet signature 18245
Nov 10, 2015 8:52:38 AM org.apache.jk.common.ChannelSocket processConnection
SEVERE: Error, processing connection
Nov 10, 2015 4:55:48 PM org.apache.coyote.http11.Http11Protocol pause
INFO: Pausing Coyote HTTP/1.1 on http-8080
""".strip()


def test_catalina_log_doc_examples():
    env = {
            'CatalinaOut': CatalinaOut,
            'out': CatalinaOut(context_wrap(CATALINA_OUT2, path='/var/log/tomcat/catalina.out')),
            'log': CatalinaServerLog(context_wrap(SERVER_LOG, path='/var/log/tomcat/catalina.2017-11-28.log'))
          }
    failed, total = doctest.testmod(catalina_log, globs=env)
    assert failed == 0
