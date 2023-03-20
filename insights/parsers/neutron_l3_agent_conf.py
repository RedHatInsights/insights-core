"""
NeutronL3AgentIni - file ``/etc/neutron/l3_agent.ini``
======================================================
"""

from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

add_filter(Specs.neutron_l3_agent_ini, ["["])


@parser(Specs.neutron_l3_agent_ini)
class NeutronL3AgentIni(IniConfigFile):
    """
    Parse the ``/etc/neutron/l3_agent.ini`` configuration file.

    Sample configuration::

         [DEFAULT]
         ovs_integration_bridge = br-int
         ovs_use_veth = false
         ovs_vsctl_timeout = 10
         agent_mode = dvr
         metadata_port = 9697
         enable_metadata_proxy = true
         external_network_bridge =
         debug = False
         log_date_format = %Y-%m-%d %H:%M:%S

         [AGENT]
         report_interval = 30
         log_agent_heartbeats = false
         availability_zone = nova

    Examples:
        >>> type(l3_agent_ini)
        <class 'insights.parsers.neutron_l3_agent_conf.NeutronL3AgentIni'>
        >>> l3_agent_ini.has_option("AGENT", "log_agent_heartbeats")
        True
        >>> l3_agent_ini.get("DEFAULT", "agent_mode") == "dvr"
        True
        >>> l3_agent_ini.getint("DEFAULT", "metadata_port")
        9697
    """
    pass
