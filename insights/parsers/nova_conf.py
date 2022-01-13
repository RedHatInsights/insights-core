"""
Nova configuration - file ``/etc/nova/nova.conf``
=================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.nova_conf)
class NovaConf(IniConfigFile):
    """
    The Nova configuration file is a standard '.ini' file and this parser uses
    the ``IniConfigFile`` class to read it.

    Sample configuration::

    [DEFAULT]
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
    scheduler_weight_classes=nova.scheduler.weights.all_weighers
    scheduler_max_attempts=3
    vif_plugging_is_fatal=True
    vif_plugging_timeout=300
    firewall_driver=nova.virt.firewall.NoopFirewallDriver
    volume_api_class=nova.volume.cinder.API

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
    rabbit_use_ssl=False
    rabbit_userid=guest
    rabbit_password=*********
    rabbit_ha_queues=True
    heartbeat_timeout_threshold=60

    Examples:
        >>> type(conf)
        <class 'insights.parsers.nova_conf.NovaConf'>
        >>> conf.sections()
        ['ephemeral_storage_encryption', 'glance', 'keystone_authtoken']
        >>> conf.has_option('DEFAULT', 'use_ipv6')
        True
        >>> conf.get("DEFAULT", "log_dir")
        '/var/log/nova'
        >>> conf.get("DEFAULT", "debug")
        'False'
        >>> conf.getboolean("DEFAULT", "verbose")
        False
        >>> conf.getint("keystone_authtoken", "extension_sync_interval")
        600
    """
    pass
