import doctest

from insights.parsers import neutron_plugin
from insights.tests import context_wrap

neutron_plugin_content = """
[ml2]
# (ListOpt) List of network type driver entrypoints to be loaded from
# the neutron.ml2.type_drivers namespace.
#
# type_drivers = local,flat,vlan,gre,vxlan,geneve
type_drivers = local,flat,vlan,gre,vxlan
# Example: type_drivers = flat,vlan,gre,vxlan,geneve

# (ListOpt) Ordered list of network_types to allocate as tenant
# networks. The default value 'local' is useful for single-box testing
# but provides no connectivity between hosts.
#
# tenant_network_types = local
tenant_network_types = local,flat,vlan,gre,vxlan
# Example: tenant_network_types = vlan,gre,vxlan,geneve


# (ListOpt) Ordered list of networking mechanism driver entrypoints
# to be loaded from the neutron.ml2.mechanism_drivers namespace.
# mechanism_drivers =
mechanism_drivers =openvswitch,linuxbridge
# Example: mechanism_drivers = openvswitch,mlnx
# Example: mechanism_drivers = arista
# Example: mechanism_drivers = openvswitch,cisco_nexus,logger
# Example: mechanism_drivers = openvswitch,brocade
# Example: mechanism_drivers = linuxbridge,brocade

# (ListOpt) Ordered list of extension driver entrypoints
# to be loaded from the neutron.ml2.extension_drivers namespace.
# extension_drivers =
extension_drivers =
# Example: extension_drivers = anewextensiondriver

# =========== items for MTU selection and advertisement =============
# (IntOpt) Path MTU.  The maximum permissible size of an unfragmented
# packet travelling from and to addresses where encapsulated Neutron
# traffic is sent.  Drivers calculate maximum viable MTU for
# validating tenant requests based on this value (typically,
# path_mtu - max encap header size).  If <=0, the path MTU is
# indeterminate and no calculation takes place.
# path_mtu = 0
path_mtu = 0

# (IntOpt) Segment MTU.  The maximum permissible size of an
# unfragmented packet travelling a L2 network segment.  If <=0,
# the segment MTU is indeterminate and no calculation takes place.
# segment_mtu = 0
# (ListOpt) Physical network MTUs.  List of mappings of physical
# network to MTU value.  The format of the mapping is
# <physnet>:<mtu val>.  This mapping allows specifying a
# physical network MTU value that differs from the default
# segment_mtu value.
# physical_network_mtus =
# Example: physical_network_mtus = physnet1:1550, physnet2:1500
# ======== end of items for MTU selection and advertisement =========

# (StrOpt) Default network type for external networks when no provider
# attributes are specified. By default it is None, which means that if
# provider attributes are not specified while creating external networks
# then they will have the same type as tenant networks.
# Allowed values for external_network_type config option depend on the
# network type values configured in type_drivers config option.
# external_network_type =
# Example: external_network_type = local

[ml2_type_flat]
# (ListOpt) List of physical_network names with which flat networks
# can be created. Use * to allow flat networks with arbitrary
# physical_network names.
#
# flat_networks =
flat_networks =*
# Example:flat_networks = physnet1,physnet2
# Example:flat_networks = *

[ml2_type_vlan]
# (ListOpt) List of <physical_network>[:<vlan_min>:<vlan_max>] tuples
# specifying physical_network names usable for VLAN provider and
# tenant networks, as well as ranges of VLAN tags on each
# physical_network available for allocation as tenant networks.
#
# network_vlan_ranges =
network_vlan_ranges =physnet1:1000:2999
# Example: network_vlan_ranges = physnet1:1000:2999,physnet2

[ml2_type_gre]
# (ListOpt) Comma-separated list of <tun_min>:<tun_max> tuples enumerating ranges of GRE tunnel IDs that are available for tenant network allocation
# tunnel_id_ranges =
tunnel_id_ranges =20:100
[ml2_type_vxlan]
# (ListOpt) Comma-separated list of <vni_min>:<vni_max> tuples enumerating
# ranges of VXLAN VNI IDs that are available for tenant network allocation.
#
# vni_ranges =
vni_ranges =10:100

# (StrOpt) Multicast group for the VXLAN interface. When configured, will
# enable sending all broadcast traffic to this multicast group. When left
# unconfigured, will disable multicast VXLAN mode.
#
# vxlan_group =
vxlan_group =224.0.0.1
# Example: vxlan_group = 239.1.1.1

[ml2_type_geneve]
# (ListOpt) Comma-separated list of <vni_min>:<vni_max> tuples enumerating
# ranges of Geneve VNI IDs that are available for tenant network allocation.
#
# vni_ranges =

# (IntOpt) Geneve encapsulation header size is dynamic, this
# value is used to calculate the maximum MTU for the driver.
# this is the sum of the sizes of the outer ETH+IP+UDP+GENEVE
# header sizes.
# The default size for this field is 50, which is the size of the
# Geneve header without any additional option headers
#
# max_header_size =
# Example: max_header_size = 50 (Geneve headers with no additional options)

[securitygroup]
# Controls if neutron security group is enabled or not.
# It should be false when you use nova security group.
# enable_security_group = True
enable_security_group = True

# Use ipset to speed-up the iptables security groups. Enabling ipset support
# requires that ipset is installed on L2 agent node.
# enable_ipset = True
"""


def test_doc_examples():
    failed_count, tests = doctest.testmod(
        neutron_plugin,
        globs={'conf': neutron_plugin.NeutronPlugin(context_wrap(neutron_plugin_content))}
    )
    assert failed_count == 0


def test_neutron_ini():
    result = neutron_plugin.NeutronPlugin(context_wrap(neutron_plugin_content))
    assert result.get("ml2_type_flat", "flat_networks") == "*"
    assert result.get("securitygroup", "enable_security_group") == "True"
    assert result.get("ml2_type_gre", "tunnel_id_ranges") == "20:100"
    assert result.get("ml2_type_vxlan", "vni_ranges") == "10:100"
