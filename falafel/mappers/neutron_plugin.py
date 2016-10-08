from .. import Mapper, mapper, LegacyItemAccess


@mapper("neutron_plugin.ini")
class NeutronPlugin(LegacyItemAccess, Mapper):
    """
    parsing plugin.ini and return dict.
    :return: a dict(dict)   Example:
    {
        "ml2": {
            "extension_drivers": "",
            "mechanism_drivers": "openvswitch,linuxbridge",
            "path_mtu": "0",
            "tenant_network_types": "local,flat,vlan,gre,vxlan",
            "type_drivers": "local,flat,vlan,gre,vxlan"
        },
        "ml2_type_flat": {
            "flat_networks": "*"
        },
        "ml2_type_geneve": {},
        "ml2_type_gre": {
            "tunnel_id_ranges": "20:100"
        },
        "ml2_type_vlan": {
            "network_vlan_ranges": "physnet1:1000:2999"
        },
        "ml2_type_vxlan": {
            "vni_ranges": "10:100",
            "vxlan_group": "224.0.0.1"
        },
        "securitygroup": {
            "enable_security_group": "True"
        }
    }
    """

    def parse_content(self, content):
        neutron_dict = {}
        section_dict = {}
        for line in content:
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            if line.startswith("["):
                # new section beginning
                section_dict = {}
                neutron_dict[line[1:-1]] = section_dict
            elif '=' in line:
                key, value = line.split("=", 1)
                section_dict[key.strip()] = value.strip()
        self.data = neutron_dict
