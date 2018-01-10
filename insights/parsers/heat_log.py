"""
Heat logs
=========

Module for parsing the log files for Heat.  Parsers included are:

HeatApiLog - file ``/var/log/heat/heat-api.log``
------------------------------------------------

HeatEngineLog - file ``/var/log/heat/heat-engine.log``
------------------------------------------------------

"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.heat_api_log)
class HeatApiLog(LogFileOutput):
    """Class for parsing ``/var/log/heat/heat-api.log`` file.

    Typical content of ``heat-api.log`` file is::

        2016-11-09 14:39:29.223 3844 WARNING oslo_config.cfg [-] Option "rpc_backend" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
        2016-11-09 14:39:30.612 3844 INFO heat.api [-] Starting Heat REST API on 172.16.2.12:8004
        2016-11-09 14:39:30.612 3844 WARNING oslo_reports.guru_meditation_report [-] Guru meditation now registers SIGUSR1 and SIGUSR2 by default for backward compatibility. SIGUSR1 will no longer be registered in a future release, so please use SIGUSR2 to generate reports.
        2016-11-09 14:39:30.615 3844 INFO heat.common.wsgi [-] Starting 0 workers
        2016-11-09 14:39:30.625 3844 INFO heat.common.wsgi [-] Started child 4136
        2016-11-09 14:39:30.641 3844 INFO heat.common.wsgi [-] Started child 4137
        2016-11-09 14:39:30.723 4137 INFO eventlet.wsgi.server [-] (4137) wsgi starting up on http://172.16.2.12:8004
        2016-11-09 14:39:30.728 3844 INFO heat.common.wsgi [-] Started child 4139
        2016-11-09 14:39:30.750 4140 INFO eventlet.wsgi.server [-] (4140) wsgi starting up on http://172.16.2.12:8004
        2016-11-09 14:39:30.732 3844 INFO heat.common.wsgi [-] Started child 4140
        2016-11-09 14:39:30.764 4139 INFO eventlet.wsgi.server [-] (4139) wsgi starting up on http://172.16.2.12:8004
        2016-11-09 14:39:30.782 4136 INFO eventlet.wsgi.server [-] (4136) wsgi starting up on http://172.16.2.12:8004

    .. note::
        Please refer to its super-class :py:class:`insights.core.LogFileOutput`
    """
    pass


@parser(Specs.heat_engine_log)
class HeatEngineLog(LogFileOutput):
    """Class for parsing ``/var/log/heat/heat-engine.log`` file.

    Typical content of ``heat-engine.log`` file is::

        2016-11-09 14:32:43.062 4392 WARNING oslo_config.cfg [-] Option "rpc_backend" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
        2016-11-09 14:32:43.371 4392 WARNING oslo_reports.guru_meditation_report [-] Guru meditation now registers SIGUSR1 and SIGUSR2 by default for backward compatibility. SIGUSR1 will no longer be registered in a future release, so please use SIGUSR2 to generate reports.
        2016-11-09 14:32:43.374 4392 WARNING heat.common.pluginutils [-] Encountered exception while loading heat.engine.clients.os.monasca: "No module named monascaclient". Not using monasca.
        2016-11-09 14:32:43.402 4392 WARNING heat.common.pluginutils [-] Encountered exception while loading heat.engine.clients.os.senlin: "No module named senlinclient". Not using senlin.
        2016-11-09 14:32:43.761 4392 WARNING heat.common.pluginutils [-] Encountered exception while loading heat.engine.clients.os.senlin: "No module named senlinclient". Not using senlin.cluster.
        2016-11-09 14:32:43.763 4392 WARNING heat.common.pluginutils [-] Encountered exception while loading heat.engine.clients.os.senlin: "No module named senlinclient". Not using senlin.profile.
        2016-11-09 14:32:43.763 4392 WARNING heat.common.pluginutils [-] Encountered exception while loading heat.engine.clients.os.monasca: "No module named monascaclient". Not using monasca.notification.
        2016-11-09 14:32:43.764 4392 WARNING heat.common.pluginutils [-] Encountered exception while loading heat.engine.clients.os.senlin: "No module named senlinclient". Not using senlin.profile_type.
        2016-11-09 14:32:43.765 4392 WARNING heat.common.pluginutils [-] Encountered exception while loading heat.engine.clients.os.senlin: "No module named senlinclient". Not using senlin.policy_type.
        2016-11-09 14:32:44.153 4392 WARNING heat.engine.environment [-] OS::Aodh::CombinationAlarm is DEPRECATED. The combination alarm is deprecated and disabled by default in Aodh.
        2016-11-09 14:32:44.154 4392 WARNING heat.engine.environment [-] OS::Heat::HARestarter is DEPRECATED. The HARestarter resource type is deprecated and will be removed in a future release of Heat, once it has support for auto-healing any type of resource. Note that HARestarter does *not* actually restart servers - it deletes and then recreates them. It also does the same to all dependent resources, and may therefore exhibit unexpected and undesirable behaviour. Instead, use the mark-unhealthy API to mark a resource as needing replacement, and then a stack update to perform the replacement while respecting  the dependencies and not deleting them unnecessarily.
        2016-11-09 14:32:44.154 4392 WARNING heat.engine.environment [-] OS::Heat::SoftwareDeployments is HIDDEN. Please use OS::Heat::SoftwareDeploymentGroup instead.
        2016-11-09 14:32:44.155 4392 WARNING heat.engine.environment [-] OS::Heat::StructuredDeployments is HIDDEN. Please use OS::Heat::StructuredDeploymentGroup instead.
        2016-11-09 14:32:44.156 4392 WARNING heat.engine.environment [-] OS::Neutron::ExtraRoute is UNSUPPORTED. Use this resource at your own risk.

    .. note::
        Please refer to its super-class :py:class:`insights.core.LogFileOutput`
    """
    pass
