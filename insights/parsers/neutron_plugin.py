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

'''
NeutronPlugin - file ``/etc/neutron/plugin.ini``
================================================

The ``NeutronPlugin`` class parses the Neutron plugin configuration file.
See the ``IniConfigFile`` class for more usage information.
'''

from .. import parser, LegacyItemAccess, IniConfigFile
from insights.specs import Specs


@parser(Specs.neutron_plugin_ini)
class NeutronPlugin(LegacyItemAccess, IniConfigFile):
    """
    Parse the ``/etc/neutron/plugin.ini`` configuration file.

    Sample configuration file::

        [ml2]
        type_drivers = local,flat,vlan,gre,vxlan
        tenant_network_types = local,flat,vlan,gre,vxlan
        mechanism_drivers =openvswitch,linuxbridge
        extension_drivers =

        [ml2_type_flat]
        flat_networks =*
        # Example:flat_networks = physnet1,physnet2
        # Example:flat_networks = *

        [ml2_type_vlan]
        network_vlan_ranges =physnet1:1000:2999
        # Example: network_vlan_ranges = physnet1:1000:2999,physnet2

        [ml2_type_gre]
        tunnel_id_ranges =20:100

        [ml2_type_vxlan]
        vni_ranges =10:100
        vxlan_group =224.0.0.1

        [ml2_type_geneve]
        # (ListOpt) Comma-separated list of <vni_min>:<vni_max> tuples enumerating
        # ranges of Geneve VNI IDs that are available for tenant network allocation.
        #
        # vni_ranges =

        [securitygroup]
        enable_security_group = True

    Examples:

        >>> nconf = shared[NeutronPlugin]
        >>> 'ml2' in nconf
        True
        >>> nconf.has_option('ml2', 'type_drivers')
        True
        >>> nconf.get("ml2_type_flat", "flat_networks")
        "*"
        >>> nconf.items('ml2_type_vxlan')
        {'vni_ranges': '10:100',
         'vxlan_group': '224.0.0.1'}
    """
    pass
