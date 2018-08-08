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

This is a standard log parser based on the LogFileOutput class.


Sample input from ``/var/log/ovirt-engine/server.log``::

    2018-01-17 01:46:15,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-6) WFLYSRV0207: Starting subdeployment (runtime-name: "services.war")
    2018-01-17 01:46:16,834+05 INFO  [org.jboss.as.server.deployment] (MSC service thread 1-1) WFLYSRV0207: Starting subdeployment (runtime-name: "webadmin.war")
    2018-01-17 01:46:17,739+05 WARN  [org.jboss.as.dependency.unsupported] (MSC service thread 1-7) WFLYSRV0019: Deployment "deployment.engine.ear" is using an unsupported module ("org.dom4j") which may be changed or removed in future versions without notice.


Examples:

    >>> 'is using an unsupported module' in server_log
    True
    >>> from datetime import datetime
    >>> len(list(server_log.get_after(datetime(2018, 1, 17, 1, 46, 16, 0)))) == 2
    True
    >>> matched_line = '2018-01-17 01:46:17,739+05 WARN  [org.jboss.as.dependency.unsupported] (MSC service thread 1-7) WFLYSRV0019: Deployment "deployment.engine.ear" is using an unsupported module ("org.dom4j") which may be changed or removed in future versions without notice.'
    >>> server_log.get('WARN')[-1].get('raw_message') == matched_line
    True
"""

from insights import LogFileOutput, parser
from insights.specs import Specs


class OvirtEngineLog(LogFileOutput):
    pass


@parser(Specs.ovirt_engine_boot_log)
class BootLog(OvirtEngineLog):
    pass


@parser(Specs.ovirt_engine_console_log)
class ConsoleLog(OvirtEngineLog):
    pass


@parser(Specs.ovirt_engine_log)
class EngineLog(OvirtEngineLog):
    pass


@parser(Specs.ovirt_engine_server_log)
class ServerLog(OvirtEngineLog):
    pass


@parser(Specs.ovirt_engine_ui_log)
class UILog(OvirtEngineLog):
    pass
