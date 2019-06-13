import doctest

from insights.parsers import neutron_ml2_conf
from insights.parsers.neutron_ml2_conf import NeutronMl2Conf
from insights.tests import context_wrap

neutron_ml2_content = """
[DEFAULT]
verbose=True
debug=False
[ml2]
type_drivers=vxlan,vlan,flat,gre
tenant_network_types=vxlan
mechanism_drivers=openvswitch
extension_drivers=qos,port_security
path_mtu=0
overlay_ip_version=4
[ml2_type_flat]
flat_networks=datacentre
[ml2_type_geneve]
[ml2_type_gre]
tunnel_id_ranges=1:4094
[ml2_type_vlan]
network_vlan_ranges=datacentre:1:1000
[ml2_type_vxlan]
vni_ranges=1:4094
vxlan_group=224.0.0.1
[securitygroup]
firewall_driver=iptables_hybrid
"""


def test_neutron_ml2_conf():
    result = NeutronMl2Conf(context_wrap(neutron_ml2_content))
    assert result.get("ml2_type_flat", "flat_networks") == "datacentre"
    assert result.get("ml2", "tenant_network_types") == "vxlan"
    assert result.get("ml2", "mechanism_drivers") == "openvswitch"
    assert result.get("securitygroup", "firewall_driver") == "iptables_hybrid"


def test_neutron_ml2_conf_docs():
    failed, total = doctest.testmod(
        neutron_ml2_conf,
        globs={
            'neutron_ml2_conf': NeutronMl2Conf(context_wrap(neutron_ml2_content)),
        }
    )
    assert failed == 0
