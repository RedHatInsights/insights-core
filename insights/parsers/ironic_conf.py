"""
IronicConf - file ``/etc/ironic/ironic.conf``
=============================================
This class provides parsing for the file ``/etc/ironic/ironic.conf``.
See the ``IniConfigFile`` class for more usage information.
"""
from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

add_filter(Specs.ironic_conf, ["["])


@parser(Specs.ironic_conf)
class IronicConf(IniConfigFile):
    """
    Ironic configuration parser class, based on the ``IniConfigFile`` class.

    Sample input data is in the format::

        [DEFAULT]
        auth_strategy=keystone
        default_resource_class=baremetal
        enabled_hardware_types=idrac,ilo,ipmi,redfish
        enabled_bios_interfaces=no-bios
        enabled_boot_interfaces=ilo-pxe,pxe
        enabled_console_interfaces=ipmitool-socat,ilo,no-console
        force_raw_images = True

        [agent]
        deploy_logs_collect=always
        deploy_logs_storage_backend=local
        deploy_logs_local_path=/var/log/ironic/deploy/

        [cinder]
        auth_url=http://1.1.1.1:5000
        project_domain_name=Default
        project_name=service
        user_domain_name=Default

    Examples:
        >>> type(ironic_conf)
        <class 'insights.parsers.ironic_conf.IronicConf'>
        >>> ironic_conf.has_option("agent", "deploy_logs_collect")
        True
        >>> ironic_conf.get("DEFAULT", "auth_strategy") == "keystone"
        True
    """
    pass
