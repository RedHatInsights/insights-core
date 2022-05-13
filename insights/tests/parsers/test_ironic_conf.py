import doctest

from insights.parsers import ironic_conf
from insights.parsers.ironic_conf import IronicConf
from insights.tests import context_wrap

ironic_content = """
[DEFAULT]
auth_strategy=keystone
default_resource_class=baremetal
enabled_hardware_types=idrac,ilo,ipmi,redfish
enabled_bios_interfaces=no-bios
enabled_boot_interfaces=ilo-pxe,pxe
enabled_console_interfaces=ipmitool-socat,ilo,no-console
enabled_deploy_interfaces=iscsi,direct,ansible
enabled_inspect_interfaces=inspector,no-inspect
default_inspect_interface=inspector
enabled_management_interfaces=fake,idrac,ilo,ipmitool,noop,redfish
enabled_network_interfaces=flat
default_network_interface=flat
enabled_power_interfaces=fake,idrac,ilo,ipmitool,redfish
enabled_raid_interfaces=idrac,no-raid
enabled_rescue_interfaces=no-rescue,agent
default_rescue_interface=agent
enabled_storage_interfaces=noop
enabled_vendor_interfaces=idrac,ipmitool,no-vendor
my_ip=192.168.24.1
debug=True
log_dir=/var/log/ironic
[agent]
deploy_logs_collect=always
deploy_logs_storage_backend=local
deploy_logs_local_path=/var/log/ironic/deploy/
[ansible]
[api]
[audit]
[cimc]
[cinder]
auth_type=password
password=Nzmsp57Yg94HXsv9x8Znc7tEI
project_domain_name=Default
project_name=service
user_domain_name=Default
username=ironic
[cisco_ucs]
[conductor]
force_power_state_during_sync=False
automated_clean=False
max_time_interval=120
[console]
[cors]
allowed_origin=*
expose_headers=Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma
max_age=3600
allow_methods=GET,POST,PUT,DELETE,OPTIONS,PATCH
allow_headers=Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma,X-Auth-Token
[database]
[deploy]
http_root=/var/lib/ironic/httpboot
erase_devices_priority=0
erase_devices_metadata_priority=10
"""


def test_ironic_conf():
    result = IronicConf(context_wrap(ironic_content))
    assert result.get("DEFAULT", "auth_strategy") == "keystone"
    assert result.get("DEFAULT", "default_resource_class") == "baremetal"
    assert result.get("DEFAULT", "default_rescue_interface") == "agent"
    assert result.get("agent", "deploy_logs_collect") == "always"
    assert result.get("conductor", "force_power_state_during_sync") == "False"


def test_ironic_conf_docs():
    failed, total = doctest.testmod(
        ironic_conf,
        globs={
            'ironic_conf': IronicConf(context_wrap(ironic_content)),
        }
    )
    assert failed == 0
