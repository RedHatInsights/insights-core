import doctest
from datetime import datetime

from insights.parsers import ovirt_engine_log
from insights.tests import context_wrap


SERVER_LOG = """
2018-01-17 01:46:15,022+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-1) WFLYSRV0027: Starting deployment of "restapi.war" (runtime-name: "restapi.war")
2018-01-17 01:46:15,022+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-5) WFLYSRV0027: Starting deployment of "rhev.ear" (runtime-name: "rhev.ear")
2018-01-17 01:46:15,022+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-6) WFLYSRV0027: Starting deployment of "apidoc.war" (runtime-name: "apidoc.war")
2018-01-17 01:46:15,022+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-4) WFLYSRV0027: Starting deployment of "engine.ear" (runtime-name: "engine.ear")
2018-01-17 01:46:15,022+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-3) WFLYSRV0027: Starting deployment of "ovirt-web-ui.war" (runtime-name: "ovirt-web-ui.war")
2018-01-17 01:46:15,035+05 INFO  [org.jboss.as.remoting] (MSC service thread 1-8) WFLYRMT0001: Listening on 127.0.0.1:8707
2018-01-17 01:46:15,064+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-6) WFLYSRV0207: Starting subdeployment (runtime-name: "rhev.war")
2018-01-17 01:46:15,532+05 INFO  [org.wildfly.security] (MSC service thread 1-3) ELY00001: WildFly Elytron version 1.1.7.Final-redhat-1
2018-01-17 01:46:15,823+05 INFO  [org.wildfly.extension.undertow] (ServerService Thread Pool -- 47) WFLYUT0021: Registered web context: '/ovirt-engine/web-ui' for server 'default-server'
2018-01-17 01:46:15,823+05 INFO  [org.wildfly.extension.undertow] (ServerService Thread Pool -- 45) WFLYUT0021: Registered web context: '/ovirt-engine/rhev' for server 'default-server'
2018-01-17 01:46:15,823+05 INFO  [org.wildfly.extension.undertow] (ServerService Thread Pool -- 43) WFLYUT0021: Registered web context: '/ovirt-engine/apidoc' for server 'default-server'
2018-01-17 01:46:15,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-5) WFLYSRV0207: Starting subdeployment (runtime-name: "bll.jar")
2018-01-17 01:46:15,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-3) WFLYSRV0207: Starting subdeployment (runtime-name: "userportal.war")
2018-01-17 01:46:15,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-5) WFLYSRV0207: Starting subdeployment (runtime-name: "enginesso.war")
2018-01-17 01:46:15,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-4) WFLYSRV0207: Starting subdeployment (runtime-name: "welcome.war")
2018-01-17 01:46:15,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-8) WFLYSRV0207: Starting subdeployment (runtime-name: "docs.war")
2018-01-17 01:46:15,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-7) WFLYSRV0207: Starting subdeployment (runtime-name: "root.war")
2018-01-17 01:46:15,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-6) WFLYSRV0207: Starting subdeployment (runtime-name: "services.war")
2018-01-17 01:46:16,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-1) WFLYSRV0207: Starting subdeployment (runtime-name: "webadmin.war")
2018-01-17 01:46:17,739+05 WARN  [org.jboss.as.dependency.unsupported] (MSC service thread 1-7) WFLYSRV0019: Deployment "deployment.engine.ear" is using an unsupported module ("org.dom4j") which may be changed or removed in future versions without notice.
""".strip()

UI_LOG = """
2018-01-24 05:31:26,243+05 ERROR [org.ovirt.engine.ui.frontend.server.gwt.OvirtRemoteLoggingService] (default task-134) [] Permutation name: C068E8B2E40A504D3054A1BDCF2A72BB
2018-01-24 05:32:26,243+05 ERROR [org.ovirt.engine.ui.frontend.server.gwt.OvirtRemoteLoggingService] (default task-134) [] Uncaught exception: com.google.gwt.core.client.JavaScriptException: (TypeError)
""".strip()

# We cannot test this at the moment as LogFileOutput cannot read continuation multi line. Please see open issue#1256
CONSOLE_LOG = """
2018-08-01 09:15:14
Full thread dump OpenJDK 64-Bit Server VM (25.181-b13 mixed mode):

"ServerService Thread Pool -- 61" #118 prio=5 os_prio=0 tid=0x0000000007f1d000 nid=0x68c waiting on condition [0x00007f716d6bc000]
   java.lang.Thread.State: TIMED_WAITING (parking)
        at sun.misc.Unsafe.park(Native Method)
        - parking to wait for  <0x00000006c7fc5480> (a java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject)
        at java.util.concurrent.locks.LockSupport.parkNanos(LockSupport.java:215)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.awaitNanos(AbstractQueuedSynchronizer.java:2078)
        at java.util.concurrent.ScheduledThreadPoolExecutor$DelayedWorkQueue.take(ScheduledThreadPoolExecutor.java:1093)
        at java.util.concurrent.ScheduledThreadPoolExecutor$DelayedWorkQueue.take(ScheduledThreadPoolExecutor.java:809)
        at java.util.concurrent.ThreadPoolExecutor.getTask(ThreadPoolExecutor.java:1074)
        at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1134)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
        at java.lang.Thread.run(Thread.java:748)
        at org.jboss.threads.JBossThread.run(JBossThread.java:320)

"ServerService Thread Pool -- 60" #117 prio=5 os_prio=0 tid=0x000000000604c800 nid=0x689 waiting on condition [0x00007f716d7bd000]
   java.lang.Thread.State: WAITING (parking)
        at sun.misc.Unsafe.park(Native Method)
        - parking to wait for  <0x00000006c7fc5480> (a java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject)
        at java.util.concurrent.locks.LockSupport.park(LockSupport.java:175)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.await(AbstractQueuedSynchronizer.java:2039)
        at java.util.concurrent.ScheduledThreadPoolExecutor$DelayedWorkQueue.take(ScheduledThreadPoolExecutor.java:1088)
        at java.util.concurrent.ScheduledThreadPoolExecutor$DelayedWorkQueue.take(ScheduledThreadPoolExecutor.java:809)
        at java.util.concurrent.ThreadPoolExecutor.getTask(ThreadPoolExecutor.java:1074)
        at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1134)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
        at java.lang.Thread.run(Thread.java:748)
        at org.jboss.threads.JBossThread.run(JBossThread.java:320)

"xnio-file-watcher[Watcher for /usr/share/ovirt-engine/branding/rhv-2.brand/applications/rhv.ear/rhv.war/]-0" #98 daemon prio=5 os_prio=0 tid=0x00000000064a9000 nid=0x66d waiting on condition [0x00007f716e4a2000]
   java.lang.Thread.State: WAITING (parking)
        at sun.misc.Unsafe.park(Native Method)
        - parking to wait for  <0x00000006c8bf3c28> (a java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject)
        at java.util.concurrent.locks.LockSupport.park(LockSupport.java:175)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.await(AbstractQueuedSynchronizer.java:2039)
        at java.util.concurrent.LinkedBlockingDeque.takeFirst(LinkedBlockingDeque.java:492)
        at java.util.concurrent.LinkedBlockingDeque.take(LinkedBlockingDeque.java:680)
        at sun.nio.fs.AbstractWatchService.take(AbstractWatchService.java:118)
        at org.xnio.nio.WatchServiceFileSystemWatcher.run(WatchServiceFileSystemWatcher.java:86)
        at java.lang.Thread.run(Thread.java:748)

"Thread-61" #97 daemon prio=5 os_prio=0 tid=0x00000000064a8800 nid=0x66b runnable [0x00007f716e5a3000]
   java.lang.Thread.State: RUNNABLE
        at sun.nio.fs.LinuxWatchService.poll(Native Method)
        at sun.nio.fs.LinuxWatchService.access$600(LinuxWatchService.java:47)
        at sun.nio.fs.LinuxWatchService$Poller.run(LinuxWatchService.java:314)
        at java.lang.Thread.run(Thread.java:748)

"xnio-file-watcher[Watcher for /usr/share/ovirt-web-ui/ovirt-web-ui.war/]-0" #96 daemon prio=5 os_prio=0 tid=0x000000000639c800 nid=0x66a waiting on condition [0x00007f716e6a4000]
   java.lang.Thread.State: WAITING (parking)
        at sun.misc.Unsafe.park(Native Method)
        - parking to wait for  <0x00000006c8bc5850> (a java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject)
        at java.util.concurrent.locks.LockSupport.park(LockSupport.java:175)
        at java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.await(AbstractQueuedSynchronizer.java:2039)
        at java.util.concurrent.LinkedBlockingDeque.takeFirst(LinkedBlockingDeque.java:492)
        at java.util.concurrent.LinkedBlockingDeque.take(LinkedBlockingDeque.java:680)
        at sun.nio.fs.AbstractWatchService.take(AbstractWatchService.java:118)
        at org.xnio.nio.WatchServiceFileSystemWatcher.run(WatchServiceFileSystemWatcher.java:86)
        at java.lang.Thread.run(Thread.java:748)

"Thread-62" #95 daemon prio=5 os_prio=0 tid=0x0000000005933800 nid=0x669 runnable [0x00007f716e7a5000]
   java.lang.Thread.State: RUNNABLE
        at sun.nio.fs.LinuxWatchService.poll(Native Method)
        at sun.nio.fs.LinuxWatchService.access$600(LinuxWatchService.java:47)
        at sun.nio.fs.LinuxWatchService$Poller.run(LinuxWatchService.java:314)
        at java.lang.Thread.run(Thread.java:748)
""".strip()

ENGINE_LOG = """
2018-08-06 04:06:33,229+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'engine' is using 0 threads out of 500, 8 threads waiting for tasks and 0 tasks in queue.
2018-08-06 04:06:33,229+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'engineScheduled' is using 0 threads out of 100, 100 threads waiting for tasks.
2018-08-06 04:06:33,229+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'engineThreadMonitoring' is using 1 threads out of 1, 0 threads waiting for tasks.
2018-08-06 04:06:33,229+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'hostUpdatesChecker' is using 0 threads out of 5, 5 threads waiting for tasks.
2018-08-06 04:16:33,231+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'commandCoordinator' is using 0 threads out of 10, 2 threads waiting for tasks.
2018-08-06 04:16:33,231+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'default' is using 0 threads out of 1, 5 threads waiting for tasks.
2018-08-06 04:16:33,231+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'engine' is using 0 threads out of 500, 8 threads waiting for tasks and 0 tasks in queue.
2018-08-06 04:16:33,231+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'engineScheduled' is using 0 threads out of 100, 100 threads waiting for tasks.
2018-08-06 04:16:33,231+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'engineThreadMonitoring' is using 1 threads out of 1, 0 threads waiting for tasks.
2018-08-06 04:16:33,231+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'hostUpdatesChecker' is using 0 threads out of 5, 5 threads waiting for tasks.
2018-08-06 04:26:33,233+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'commandCoordinator' is using 0 threads out of 10, 2 threads waiting for tasks.
2018-08-06 04:26:33,233+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'default' is using 0 threads out of 1, 5 threads waiting for tasks.
2018-08-06 04:26:33,233+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'engine' is using 0 threads out of 500, 8 threads waiting for tasks and 0 tasks in queue.
2018-08-22 00:16:14,357+05 INFO  [org.ovirt.engine.core.vdsbroker.vdsbroker.HotUnplugLeaseVDSCommand] (default task-133) [e3bc976c-bc3e-4b41-807f-3a518169ad18] START, HotUnplugLeaseVDSCommand(HostName = example.com, LeaseVDSParameters:{hostId='bfa308ab-5add-4ad7-8f1c-389cb8dcf703', vmId='789489a3-be62-40e4-b13e-beb34ba5ff93'}), log id: 7a634963
""".strip()

BOOT_LOG = """
03:46:17,790 INFO  [org.jboss.modules] JBoss Modules version 1.6.4.Final-redhat-1
03:46:18,067 INFO  [org.jboss.msc] JBoss MSC version 1.2.7.SP1-redhat-1
03:46:18,181 INFO  [org.jboss.as] WFLYSRV0049: JBoss EAP 7.1.3.GA (WildFly Core 3.0.16.Final-redhat-1) starting
03:46:19,126 INFO  [org.jboss.as.controller.management-deprecated] WFLYCTL0028: Attribute 'security-realm' in the resource at address '/core-service=management/management-interface=native-interface' is deprecated, and may be removed in future version. See the attribute description in the output of the read-resource-description operation to learn more about the deprecation.
03:46:19,128 INFO  [org.jboss.as.controller.management-deprecated] WFLYCTL0028: Attribute 'security-realm' in the resource at address '/core-service=management/management-interface=http-interface' is deprecated, and may be removed in future version. See the attribute description in the output of the read-resource-description operation to learn more about the deprecation.
03:46:19,208 INFO  [org.jboss.as.server.deployment.scanner] WFLYDS0004: Found restapi.war in deployment directory. To trigger deployment create a file called restapi.war.dodeploy
03:46:19,208 INFO  [org.jboss.as.server.deployment.scanner] WFLYDS0004: Found engine.ear in deployment directory. To trigger deployment create a file called engine.ear.dodeploy
03:46:19,208 INFO  [org.jboss.as.server.deployment.scanner] WFLYDS0004: Found ovirt-web-ui.war in deployment directory. To trigger deployment create a file called ovirt-web-ui.war.dodeploy
03:46:19,208 INFO  [org.jboss.as.server.deployment.scanner] WFLYDS0004: Found apidoc.war in deployment directory. To trigger deployment create a file called apidoc.war.dodeploy
03:46:19,208 INFO  [org.jboss.as.server.deployment.scanner] WFLYDS0004: Found rhv.ear in deployment directory. To trigger deployment create a file called rhv.ear.dodeploy
03:46:19,238 INFO  [org.jboss.as.server] WFLYSRV0039: Creating http management service using socket-binding (management)
03:46:19,242 INFO  [org.xnio] XNIO version 3.5.5.Final-redhat-1
03:46:19,250 INFO  [org.xnio.nio] XNIO NIO Implementation Version 3.5.5.Final-redhat-1
""".strip()


def test_server_log():
    server_log = ovirt_engine_log.ServerLog(context_wrap(SERVER_LOG))
    assert 'is using an unsupported module' in server_log
    assert len(list(server_log.get_after(datetime(2018, 1, 17, 1, 46, 16, 0)))) == 2

    matched_line = '2018-01-17 01:46:17,739+05 WARN  [org.jboss.as.dependency.unsupported] (MSC service thread 1-7) WFLYSRV0019: Deployment "deployment.engine.ear" is using an unsupported module ("org.dom4j") which may be changed or removed in future versions without notice.'
    assert server_log.get('WARN')[-1].get('raw_message') == matched_line

    sec_lines = server_log.get('org.wildfly.security')
    assert len(sec_lines) == 1
    assert sec_lines[0]['level'] == 'INFO'


def test_ui_log():
    ui_log = ovirt_engine_log.UILog(context_wrap(UI_LOG))
    assert 'Permutation name' in ui_log
    assert len(list(ui_log.get_after(datetime(2018, 1, 24, 5, 31, 26, 0)))) == 2

    exception_lines = ui_log.get('Uncaught exception')
    assert len(exception_lines) == 1
    assert exception_lines[0].get('procname') == 'org.ovirt.engine.ui.frontend.server.gwt.OvirtRemoteLoggingService'
    assert exception_lines[0].get('level') == 'ERROR'


def test_engine_log():
    engine_log = ovirt_engine_log.EngineLog(context_wrap(ENGINE_LOG))
    assert "Thread pool 'engine'" in engine_log
    assert len(list(engine_log.get_after(datetime(2018, 8, 6, 4, 16, 33, 0)))) == 10

    matched_line = "2018-08-06 04:16:33,231+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'hostUpdatesChecker' is using 0 threads out of 5, 5 threads waiting for tasks."
    assert engine_log.get('hostUpdatesChecker')[-1].get('raw_message') == matched_line
    assert engine_log.get('vdsbroker')[-1].get('procname') == 'org.ovirt.engine.core.vdsbroker.vdsbroker.HotUnplugLeaseVDSCommand'


def test_boot_log():
    boot_log = ovirt_engine_log.BootLog(context_wrap(BOOT_LOG))
    assert "Creating http management service using socket-binding" in boot_log
    xnio_lines = boot_log.get('xnio.nio')
    assert len(xnio_lines) == 1
    assert xnio_lines[0].get('procname') == 'org.xnio.nio'
    assert xnio_lines[0].get('level') == 'INFO'
    assert xnio_lines[0].get('message') == 'XNIO NIO Implementation Version 3.5.5.Final-redhat-1'

    log_line = '2018-01-17 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-1) WFLYSRV0027: Starting deployment of "restapi.war" (runtime-name: "restapi.war")'
    boot_log = ovirt_engine_log.BootLog(context_wrap(log_line))
    assert "restapi" in boot_log
    assert boot_log.get('restapi')[0]['raw_message'] == log_line


def test_documentation():
    failed_count, tests = doctest.testmod(
        ovirt_engine_log,
        globs={'server_log': ovirt_engine_log.ServerLog(context_wrap(SERVER_LOG)),
               'boot_log': ovirt_engine_log.BootLog(context_wrap(BOOT_LOG)),
               'engine_log': ovirt_engine_log.EngineLog(context_wrap(ENGINE_LOG)),
               'ui_log': ovirt_engine_log.UILog(context_wrap(UI_LOG))}
    )
    assert failed_count == 0
