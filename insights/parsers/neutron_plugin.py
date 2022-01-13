"""
NeutronPlugin - file ``/etc/neutron/plugin.ini``
================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.neutron_plugin_ini)
class NeutronPlugin(IniConfigFile):
    """
    Parse the ``/etc/neutron/plugin.ini`` configuration file.

    Sample configuration file::

        [ml2]
        type_drivers = local,flat,vlan,gre,vxlan
        tenant_network_types = local,flat,vlan,gre,vxlan
        mechanism_drivers = openvswitch,linuxbridge
        extension_drivers =

        [ml2_type_flat]
        flat_networks = *

        [ml2_type_vlan]
        network_vlan_ranges = physnet1:1000:2999

        [ml2_type_gre]
        tunnel_id_ranges = 20:100

        [ml2_type_vxlan]
        vni_ranges = 10:100
        vxlan_group = 224.0.0.1

        [ml2_type_geneve]
        vni_ranges =

        [securitygroup]
        enable_security_group = True

    Examples:
        >>> type(conf)
        <class 'insights.parsers.neutron_plugin.NeutronPlugin'>
        >>> 'ml2' in conf
        True
        >>> conf.has_option('ml2', 'type_drivers')
        True
        >>> conf.get("ml2_type_flat", "flat_networks")
        '*'
    """
    pass
