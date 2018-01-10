"""
NeutronOVSAgentLog - file ``/var/log/neutron/openvswitch-agent.log``
====================================================================

Parser plugin for parsing the log file for Neutron OVS Agent

Typical content of ``openvswitch-agent.log`` file is::

    2016-11-09 14:39:25.343 3153 INFO neutron.common.config [-] Logging enabled!
    2016-11-09 14:39:25.343 3153 INFO neutron.common.config [-] /usr/bin/neutron-openvswitch-agent version 9.1.0
    2016-11-09 14:39:25.347 3153 WARNING oslo_config.cfg [-] Option "rabbit_hosts" from group "oslo_messaging_rabbit" is deprecated for removal.  Its value may be silently ignored in the future.
    2016-11-09 14:39:25.348 3153 WARNING oslo_config.cfg [-] Option "rabbit_password" from group "oslo_messaging_rabbit" is deprecated for removal.  Its value may be silently ignored in the future.
    2016-11-09 14:39:25.348 3153 WARNING oslo_config.cfg [-] Option "rabbit_userid" from group "oslo_messaging_rabbit" is deprecated for removal.  Its value may be silently ignored in the future.
    2016-11-09 14:39:25.352 3153 INFO ryu.base.app_manager [-] loading app neutron.plugins.ml2.drivers.openvswitch.agent.openflow.native.ovs_ryuapp
    2016-11-09 14:39:27.171 3153 INFO ryu.base.app_manager [-] loading app ryu.app.ofctl.service
    2016-11-09 14:39:27.190 3153 INFO ryu.base.app_manager [-] loading app ryu.controller.ofp_handler
    2016-11-09 14:39:27.209 3153 INFO ryu.base.app_manager [-] instantiating app neutron.plugins.ml2.drivers.openvswitch.agent.openflow.native.ovs_ryuapp of OVSNeutronAgentRyuApp
    2016-11-09 14:39:27.210 3153 INFO ryu.base.app_manager [-] instantiating app ryu.controller.ofp_handler of OFPHandler
    2016-11-09 14:39:27.210 3153 INFO ryu.base.app_manager [-] instantiating app ryu.app.ofctl.service of OfctlService
    2016-11-09 14:39:28.255 3153 INFO oslo_rootwrap.client [-] Spawned new rootwrap daemon process with pid=3925
    2016-11-09 14:39:29.376 3153 INFO neutron.plugins.ml2.drivers.openvswitch.agent.openflow.native.ovs_bridge [-] Bridge br-int has datapath-ID 0000c2670b638c45
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.neutron_ovs_agent_log)
class NeutronOVSAgentLog(LogFileOutput):
    """Class for parsing ``/var/log/neutron/openvswitch-agent.log`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass
