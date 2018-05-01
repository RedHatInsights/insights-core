from __future__ import print_function
from insights.core.context import OSP
from insights.parsers import nova_conf
from insights.tests import context_wrap

nova_content = """

[DEFAULT]
notification_driver =
#this is comment

notification_topics=notifications

rpc_backend=rabbit
use_ipv6=True
notify_on_state_change=vm_and_task_state
notify_api_faults=False
state_path=/var/lib/nova
report_interval = 10
osapi_compute_listen=fd00:4888:1000:f901::c1
osapi_compute_workers=32
metadata_listen=fd00:4888:1000:f901::c1
metadata_workers=32
service_down_time=60
rootwrap_config=/etc/nova/rootwrap.conf
auth_strategy=keystone
use_forwarded_for=False
novncproxy_host=fd00:4888:1000:f901::c1
novncproxy_port=6080
network_api_class=nova.network.neutronv2.api.API
dhcp_domain=
security_group_api=neutron
debug=False
verbose=False
log_dir=/var/log/nova
use_syslog=False
scheduler_host_manager=nova.scheduler.host_manager.HostManager
scheduler_host_subset_size=1
cpu_allocation_ratio=16.0
disk_allocation_ratio=1.0
max_io_ops_per_host=8
max_instances_per_host=50
ram_allocation_ratio=1.0
scheduler_available_filters=nova.scheduler.filters.all_filters
scheduler_default_filters=RetryFilter,AvailabilityZoneFilter,RamFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,NUMATopologyFilter,PciPassthroughFilter
scheduler_weight_classes=nova.scheduler.weights.all_weighers
scheduler_max_attempts=3
vif_plugging_is_fatal=True
vif_plugging_timeout=300
firewall_driver=nova.virt.firewall.NoopFirewallDriver
novncproxy_base_url=http://[fd00:4888:1000:f901::c1]:6080/vnc_auto.html
volume_api_class=nova.volume.cinder.API
memcached_servers=inet6:[fd00:4888:1000:f901::c0]:11211,inet6:[fd00:4888:1000:f901::c1]:11211,inet6:[fd00:4888:1000:f901::c2]:11211
[ephemeral_storage_encryption]
[glance]
api_servers=http://[fd00:4888:1000:f901::a000]:9292
[keystone_authtoken]
auth_uri=http://[fd00:4888:1000:f901::a000]:5000/v2.0
identity_uri=http://192.168.1.107:35357
admin_user=nova
admin_password=*********
admin_tenant_name=service
service_metadata_proxy=True
ovs_bridge=br-int
extension_sync_interval=600
rabbit_hosts=fd00:4888:1000:f901::c0,fd00:4888:1000:f901::c1,fd00:4888:1000:f901::c2
rabbit_use_ssl=False
rabbit_userid=guest
rabbit_password=*********
rabbit_virtual_host  =  /
rabbit_ha_queues=True
heartbeat_timeout_threshold=60
heartbeat_rate=2
"""

osp = OSP()
osp.role = "Compute"


def test_nova_conf():
    result = nova_conf.NovaConf(context_wrap(nova_content, osp=osp))
    print(result)
    assert result.get("DEFAULT", "notification_driver") == ""
    assert result.get("DEFAULT", "report_interval") == "10"
    assert result.get("DEFAULT", "novncproxy_host") == "fd00:4888:1000:f901::c1"

    assert result.get("keystone_authtoken", "auth_uri") == "http://[fd00:4888:1000:f901::a000]:5000/v2.0"
    assert result.get("keystone_authtoken", "service_metadata_proxy") == "True"
    assert result.get("keystone_authtoken", "rabbit_hosts")\
        == "fd00:4888:1000:f901::c0,fd00:4888:1000:f901::c1,fd00:4888:1000:f901::c2"
