from falafel.tests import context_wrap
from falafel.mappers.rhn_taskomatic_daemon_log import taskomatic_daemon_log

daemon_log = """
STATUS | wrapper  | 2016/05/18 15:13:36 | --> Wrapper Started as Daemon
STATUS | wrapper  | 2016/05/18 15:13:36 | Launching a JVM...
INFO   | jvm 1    | 2016/05/18 15:13:36 | Wrapper (Version 3.2.3) http://wrapper.tanukisoftware.org
INFO   | jvm 1    | 2016/05/18 15:13:36 |   Copyright 1999-2006 Tanuki Software, Inc.  All Rights Reserved.
INFO   | jvm 1    | 2016/05/18 15:13:39 | May 18, 2016 3:13:39 PM com.mchange.v2.log.MLog <clinit>
INFO   | jvm 1    | 2016/05/18 15:13:39 | INFO: MLog clients using java 1.4+ standard logging.
INFO   | jvm 1    | 2016/05/18 15:13:39 | May 18, 2016 3:13:39 PM com.mchange.v2.c3p0.C3P0Registry banner
INFO   | jvm 1    | 2016/05/18 15:13:39 | INFO: Initializing c3p0-0.9.1.2 [built 31-March-2011 15:45:28; debug? false; trace: 5]
INFO   | jvm 1    | 2016/05/18 15:13:39 | May 18, 2016 3:13:39 PM com.mchange.v2.c3p0.impl.AbstractPoolBackedDataSource getPoolManager
INFO   | jvm 1    | 2016/05/10 15:13:39 | INFO: Initializing c3p0 pool... com.mchange.v2.c3p0.PoolBackedDataSource@ea9d5b40 [ connectionPoolDataSource -> com.mchange.v2.c3p0.WrapperConnectionPoolDataSource@d1b21349 [ acquireIncrement -> 3, acquireRetryAttempts -> 30, acquireRetryDelay -> 1000, autoCommitOnClose -> false, automaticTestTable -> null, breakAfterAcquireFailure -> false, checkoutTimeout -> 0, connectionCustomizerClassName -> com.redhat.rhn.common.db.RhnConnectionCustomizer, connectionTesterClassName -> com.mchange.v2.c3p0.impl.DefaultConnectionTester, debugUnreturnedConnectionStackTraces -> false, factoryClassLocation -> null, forceIgnoreUnresolvedTransactions -> false, identityToken -> z8kflt9g1i0xjsv13mnjcq|1d434058, idleConnectionTestPeriod -> 300, initialPoolSize -> 5, maxAdministrativeTaskTime -> 0, maxConnectionAge -> 0, maxIdleTime -> 300, maxIdleTimeExcessConnections -> 0, maxPoolSize -> 20, maxStatements -> 0, maxStatementsPerConnection -> 0, minPoolSize -> 5, nestedDataSource -> com.mchange.v2.c3p0.DriverManagerDataSource@47193081 [ description -> null, driverClass -> null, factoryClassLocation -> null, identityToken -> z8kflt9g1i0xjsv13mnjcq|2978124d, jdbcUrl -> jdbc:postgresql:rhnschema, properties -> {user=******, password=******, driver_proto=jdbc:postgresql} ], preferredTestQuery -> select 'c3p0 ping' from dual, propertyCycle -> 0, testConnectionOnCheckin -> false, testConnectionOnCheckout -> true, unreturnedConnectionTimeout -> 0, usesTraditionalReflectiveProxies -> false; userOverrides: {} ], dataSourceName -> null, factoryClassLocation -> null, identityToken -> z8kflt9g1i0xjsv13mnjcq|51cdf94, numHelperThreads -> 3 ]
""".strip()


def test_rhn_taskomatic_daemon_log():
    out_log = taskomatic_daemon_log(context_wrap(daemon_log))
    assert "Wrapper Started as Daemon" in out_log
    assert len(out_log.get("jvm")) == 8
    assert out_log.get("jvm")[0].get('stat') == 'INFO'
    assert out_log.last.get('time') == '2016/05/10 15:13:39'
