"""
Ovirt Engine logs
=================

This module contains the following parsers:

ServerLog - file ``/var/log/ovirt-engine/server.log``
-----------------------------------------------------
UILog - file ``/var/log/ovirt-engine/ui.log``
---------------------------------------------
EngineLog - file ``/var/log/ovirt-engine/engine.log``
-----------------------------------------------------
BootLog - file ``/var/log/ovirt-engine/boot.log``
-------------------------------------------------
ConsoleLog - file ``/var/log/ovirt-engine/console.log``
-------------------------------------------------------
"""
from time import strptime

from insights import LogFileOutput, Syslog, parser
from insights.specs import Specs


@parser(Specs.ovirt_engine_boot_log)
class BootLog(Syslog):
    '''Provide access to ``/var/log/ovirt-engine/boot.log`` using the Syslog parser class.

    Sample input::

        03:46:19,238 INFO  [org.jboss.as.server] WFLYSRV0039: Creating http management service using socket-binding (management)
        03:46:19,242 INFO  [org.xnio] XNIO version 3.5.5.Final-redhat-1
        03:46:19,250 INFO  [org.xnio.nio] XNIO NIO Implementation Version 3.5.5.Final-redhat-1

    Examples:

        >>> xnio_lines = boot_log.get('xnio.nio')
        >>> len(xnio_lines)
        1
        >>> xnio_lines[0].get('procname')
        'org.xnio.nio'
        >>> xnio_lines[0].get('level')
        'INFO'
        >>> xnio_lines[0].get('message')
        'XNIO NIO Implementation Version 3.5.5.Final-redhat-1'
    '''
    time_format = '%H:%M:%S,%f'

    def _parse_line(self, line):
        msg_info = {'raw_message': line}
        line_splits = line.split()
        try:
            if strptime(line_splits[0], self.time_format):
                msg_info['timestamp'] = line_splits[0]
                msg_info['level'] = line_splits[1]
                msg_info['procname'] = line_splits[2].strip('[]')
                msg_info['message'] = ' '.join(line_splits[3:])
        except ValueError:
            pass
        return msg_info


@parser(Specs.ovirt_engine_console_log)
class ConsoleLog(LogFileOutput):
    '''Provide access to ``/var/log/ovirt-engine/console.log`` using the LogFileoutput parser class.'''
    pass


# Using existing engine_log specs
@parser(Specs.engine_log)
class EngineLog(LogFileOutput):
    '''Provide access to ``/var/log/ovirt-engine/engine.log`` using the LogFileoutput parser class.

    Sample input::

        2018-08-06 04:06:33,229+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'engine' is using 0 threads out of 500, 8 threads waiting for tasks and 0 tasks in queue.
        2018-08-06 04:06:33,229+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'engineScheduled' is using 0 threads out of 100, 100 threads waiting for tasks.

    Examples:

        >>> from datetime import datetime
        >>> "Thread pool 'engine'" in engine_log
        True
        >>> len(list(engine_log.get_after(datetime(2018, 8, 6, 4, 16, 33, 0))))
        9
        >>> matched_line = "2018-08-06 04:16:33,231+05 INFO  [org.ovirt.engine.core.bll.utils.ThreadPoolMonitoringService] (EE-ManagedThreadFactory-engineThreadMonitoring-Thread-1) [] Thread pool 'hostUpdatesChecker' is using 0 threads out of 5, 5 threads waiting for tasks."
        >>> engine_log.get('hostUpdatesChecker')[-1].get('raw_message') == matched_line
        True
    '''
    pass


@parser(Specs.ovirt_engine_server_log)
class ServerLog(LogFileOutput):
    '''Provide access to ``/var/log/ovirt-engine/server.log`` using the LogFileoutput parser class.

    Sample input::

        2018-01-17 01:46:15,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-6) WFLYSRV0207: Starting subdeployment (runtime-name: "services.war")
        2018-01-17 01:46:16,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-1) WFLYSRV0207: Starting subdeployment (runtime-name: "webadmin.war")
        2018-01-17 01:46:17,739+05 WARN  [org.jboss.as.dependency.unsupported] (MSC service thread 1-7) WFLYSRV0019: Deployment "deployment.engine.ear" is using an unsupported module ("org.dom4j") which may be changed or removed in future versions without notice.


    Examples:

        >>> 'is using an unsupported module' in server_log
        True
        >>> from datetime import datetime
        >>> len(list(server_log.get_after(datetime(2018, 1, 17, 1, 46, 16, 0))))
        2
        >>> matched_line = '2018-01-17 01:46:17,739+05 WARN  [org.jboss.as.dependency.unsupported] (MSC service thread 1-7) WFLYSRV0019: Deployment "deployment.engine.ear" is using an unsupported module ("org.dom4j") which may be changed or removed in future versions without notice.'
        >>> server_log.get('WARN')[-1].get('raw_message') == matched_line
        True
    '''
    pass


@parser(Specs.ovirt_engine_ui_log)
class UILog(LogFileOutput):
    '''Provide access to ``/var/log/ovirt-engine/ui.log`` using the LogFileoutput parser class.

    Sample input::

        2018-01-24 05:31:26,243+05 ERROR [org.ovirt.engine.ui.frontend.server.gwt.OvirtRemoteLoggingService] (default task-134) [] Permutation name: C068E8B2E40A504D3054A1BDCF2A72BB
        2018-01-24 05:32:26,243+05 ERROR [org.ovirt.engine.ui.frontend.server.gwt.OvirtRemoteLoggingService] (default task-134) [] Uncaught exception: com.google.gwt.core.client.JavaScriptException: (TypeError)

    Examples:

        >>> 'Permutation name' in ui_log
        True
        >>> from datetime import datetime
        >>> len(list(ui_log.get_after(datetime(2018, 1, 24, 5, 31, 26, 0))))
        2
    '''
    pass
