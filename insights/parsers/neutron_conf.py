"""
NeutronConf - file ``/etc/neutron/neutron.conf``
================================================
"""
from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.plugins import parser
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
    """
    This class provides parsing for the file ``/etc/neutron/neutron.conf``.

    Sample input data is in the format::

        [DEFAULT]
        debug = False
        verbose = False
        core_plugin = neutron.plugins.openvswitch.ovs_neutron_plugin.OVSNeutronPluginV2

        [quotas]
        default_quota = -1
        quota_network = 10

        [agent]
        report_interval = 60

        [keystone_authtoken]
        auth_host = ost-controller-lb-del.example.com
        auth_port = 35357

        [database]
        connection = mysql://neutron:dSNneutron01@ost-mysql.example.com/neutron?ssl_ca=/etc/pki/CA/certs/ca.crt

        [service_providers]
        service_provider = LOADBALANCER:Haproxy:neutron.services.loadbalancer.drivers.haproxy.plugin_driver.HaproxyOnHostPluginDriver:default

    Examples:
        >>> type(conf)
        <class 'insights.parsers.neutron_conf.NeutronConf'>
        >>> conf.sections()
        ['quotas', 'agent', 'keystone_authtoken', 'database', 'service_providers']
        >>> conf.has_option('DEFAULT', 'debug')
        True
        >>> conf.get("DEFAULT", "verbose")
        'False'
        >>> conf.get("keystone_authtoken", "auth_host")
        'ost-controller-lb-del.example.com'
        >>> conf.getboolean("DEFAULT", "debug")
        False
        >>> conf.getint("agent", "report_interval")
        60
    """
    pass
