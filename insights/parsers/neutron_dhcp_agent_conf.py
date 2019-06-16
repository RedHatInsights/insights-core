#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
NeutronDhcpAgentIni - file ``/etc/neutron/dhcp_agent.ini``
==========================================================

The ``NeutronDhcpAgentIni`` class parses the dhcp-agent configuration file.
See the ``IniConfigFile`` class for more usage information.
"""

from insights import parser, IniConfigFile
from insights.core.filters import add_filter
from insights.specs import Specs

add_filter(Specs.neutron_dhcp_agent_ini, ["["])


@parser(Specs.neutron_dhcp_agent_ini)
class NeutronDhcpAgentIni(IniConfigFile):
    """
    Parse the ``/etc/neutron/dhcp_agent.ini`` configuration file.

    Sample configuration::

        [DEFAULT]

        ovs_integration_bridge = br-int
        ovs_use_veth = false
        interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
        ovs_vsctl_timeout = 10
        resync_interval = 30
        dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
        enable_isolated_metadata = True
        force_metadata = False
        enable_metadata_network = False
        root_helper=sudo neutron-rootwrap /etc/neutron/rootwrap.conf
        state_path=/var/lib/neutron

        [AGENT]

        report_interval = 30
        log_agent_heartbeats = false
        availability_zone = nova


    Examples:

        >>> data.has_option("AGENT", "log_agent_heartbeats")
        True
        >>> data.get("DEFAULT", "force_metadata") == "True"
        True
        >>> data.getint("DEFAULT", "resync_interval")
        30

    """
    pass
