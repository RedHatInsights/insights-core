"""
NeutronSriovAgent - file ``/etc/neutron/plugins/ml2/sriov_agent.ini``
=====================================================================

This class provides parsing for the files:
    ``/etc/neutron/plugins/ml2/sriov_agent.ini``
    ``/var/lib/config-data/puppet-generated/neutron/etc/neutron/plugins/ml2/sriov_agent.ini``

Sample input data is in the format::

    [DEFAULT]
    debug = false

    [sriov_nic]
    physical_device_mappings=datacentre:enp2s0f6

    [agent]
    polling_interval=2

    [securitygroup]
    firewall_driver=noop
    report_interval = 60

    [keystone_authtoken]
    auth_port = 35357

See the ``IniConfigFile`` class for examples.
"""
from .. import IniConfigFile, parser, add_filter
from insights.specs import Specs

FILTERS = [
    "debug",
    "[",
    "physical_device_mappings",
    "exclude_devices",
    "extensions"
]
add_filter(Specs.neutron_sriov_agent, FILTERS)


@parser(Specs.neutron_sriov_agent)
class NeutronSriovAgent(IniConfigFile):
    """Class to parse file ``sriov_agent.ini``."""
    pass
