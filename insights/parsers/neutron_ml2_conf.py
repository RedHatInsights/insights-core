"""
NeutronMl2Conf - file ``/etc/neutron/plugins/ml2/ml2_conf.ini``
===============================================================
This class provides parsing for the file ``/etc/neutron/plugins/ml2/ml2_conf.ini``.
See the ``IniConfigFile`` class for more usage information.
"""


from .. import IniConfigFile, parser, add_filter
from insights.specs import Specs

add_filter(Specs.neutron_ml2_conf, ["["])


@parser(Specs.neutron_ml2_conf)
class NeutronMl2Conf(IniConfigFile):
    """
    Neutron ML2 configuration parser class, based on the ``IniConfigFile`` class.

    Sample input data is in the format::

        [DEFAULT]

        debug = false
        verbose = true
        use_syslog = false

        [ml2]

        type_drivers = local,flat,vlan,gre,vxlan,geneve
        mechanism_drivers = openvswitch

        [securitygroup]

        firewall_driver = iptables_hybrid
        enable_security_group = true


    Examples:

        >>> neutron_ml2_conf.has_option("ml2", "type_drivers")
        True
        >>> neutron_ml2_conf.get("ml2", "mechanism_drivers") == "openvswitch"
        True

    """
    pass
