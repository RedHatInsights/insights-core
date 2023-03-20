"""
NeutronMetadataAgentIni - file ``/etc/neutron/metadata_agent.ini``
==================================================================
"""
from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

add_filter(Specs.neutron_metadata_agent_ini, ["["])


@parser(Specs.neutron_metadata_agent_ini)
class NeutronMetadataAgentIni(IniConfigFile):
    """
    Parse the ``/etc/neutron/metadata_agent.ini`` configuration file.

    Sample configuration::

        [DEFAULT]
        debug = False
        auth_url = http://localhost:35357/v2.0
        auth_insecure = False
        admin_tenant_name = service
        admin_user = neutron
        nova_metadata_ip = 127.0.0.1
        nova_metadata_port = 8775
        nova_metadata_protocol = http
        metadata_workers =0
        metadata_backlog = 4096

        [AGENT]
        log_agent_heartbeats = False

    Examples:
        >>> type(metadata_agent_ini)
        <class 'insights.parsers.neutron_metadata_agent_conf.NeutronMetadataAgentIni'>
        >>> metadata_agent_ini.has_option('AGENT', 'log_agent_heartbeats')
        True
        >>> metadata_agent_ini.get("DEFAULT", "auth_url") == 'http://localhost:35357/v2.0'
        True
        >>> metadata_agent_ini.getint("DEFAULT", "metadata_backlog")
        4096
    """
    pass
