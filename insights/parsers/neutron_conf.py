"""
NeutronConf - file ``/etc/neutron/neutron.conf``
================================================

This class provides parsing for the file ``/etc/neutron/neutron.conf``.

Sample input data is in the format::

    [DEFAULT]
    # debug = False
    debug = False
    # verbose = True
    verbose = False
    core_plugin =neutron.plugins.openvswitch.ovs_neutron_plugin.OVSNeutronPluginV2

    [quotas]
    default_quota = -1
    quota_network = 10
    [agent]
    report_interval = 60

    [keystone_authtoken]
    auth_host = ost-controller-lb-del.om-l.dsn.inet
    auth_port = 35357

See the ``IniConfigFile`` class for examples.
"""
from .. import IniConfigFile, parser, add_filter
from insights.specs import Specs

add_filter(Specs.neutron_conf, ["["])

ADDITIONAL_FILTERS = [
    "service_plugins",
    "allow_automatic_dhcp_failover",
    "rpc_workers",
    "api_workers",
    "ipam_driver",
    "agent_down_time",
    "agent_report_interval",
    "router_distributed"
]
add_filter(Specs.neutron_conf, ADDITIONAL_FILTERS)


@parser(Specs.neutron_conf)
class NeutronConf(IniConfigFile):
    """Class to parse file ``neutron.conf``."""
    pass
