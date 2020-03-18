"""
Octavia - file ``octavia.conf``
===============================

Provides a parser arser for file
``/var/lib/config-data/puppet-generated/octavia/etc/octavia/octavia.conf``.  Filters
have been added to this parser to ensure that the necessary data will be collected.

Sample input data::

    [DEFAULT]
    # Print debugging output (set logging level to DEBUG instead of default WARNING level).
    debug = False

    # Plugin options are hot_plug_plugin (Hot-pluggable controller plugin)
    # octavia_plugins = hot_plug_plugin

    # Hostname to be used by the host machine for services running on it.
    # The default value is the hostname of the host machine.
    # host =

    # AMQP Transport URL
    # For Single Host, specify one full transport URL:
    #   transport_url = rabbit://<user>:<pass>@127.0.0.1:5672/<vhost>
    # For HA, specify queue nodes in cluster, comma delimited:
    #   transport_url = rabbit://<user>:<pass>@server01,<user>:<pass>@server02/<vhost>
    # transport_url =

    # How long in seconds to wait for octavia worker to exit before killing them.
    # graceful_shutdown_timeout = 60

    [api_settings]
    bind_host = 127.0.0.1
    bind_port = 9876

    # How should authentication be handled (keystone, noauth)
    # auth_strategy = keystone

    # allow_pagination = True
    # allow_sorting = True
    # pagination_max_limit = 1000
    # Base URI for the API for use in pagination links.
    # This will be autodetected from the request if not overridden here.
    # Example:
    #   api_base_uri = http://localhost:9876
    # api_base_uri =

    # Enable/disable ability for users to create TLS Terminated listeners
    # allow_tls_terminated_listeners = True

    # Enable/disable ability for users to create PING type Health Monitors
    # allow_ping_health_monitors = True

    # Dictionary of enabled provider driver names and descriptions
    # A comma separated list of dictionaries of the enabled provider driver names
    # and descriptions.
    # enabled_provider_drivers = amphora:The Octavia Amphora driver.,octavia: \
    #                            Deprecated alias of the Octavia Amphora driver.

    # Default provider driver
    default_provider_driver = amphora

    # The minimum health monitor delay interval for UDP-CONNECT Health Monitor type
    udp_connect_min_interval_health_monitor = 3

Examples:
    >>> type(octavia_conf)
    <class 'insights.parsers.octavia.OctaviaConf'>
    >>> octavia_conf.defaults()['debug'] == 'False'
    True
    >>> octavia_conf.get('api_settings', 'bind_port') == '9876'
    True
    >>> octavia_conf.has_option('api_settings', 'missing_key')
    False
"""
from insights import IniConfigFile, parser
from insights.core.filters import add_filter
from insights.specs import Specs

VALID_KEYS = [
    '[',
    'active_connection_max_retries',
    'active_connection_rety_interval',
    'admin_log_targets',
    'administrative_log_facility',
    'agent_request_read_timeout',
    'agent_server_ca',
    'agent_server_cert',
    'agent_server_network_dir',
    'agent_server_network_file',
    'agent_tls_protocol',
    'allow_pagination',
    'allow_ping_health_monitors',
    'allow_sorting',
    'allow_tls_terminated_listeners',
    'allow_vip_network_id',
    'allow_vip_port_id',
    'allow_vip_subnet_id',
    'amp_active_retries',
    'amp_active_wait_sec',
    'amp_boot_network_list',
    'amp_flavor_id',
    'amp_image_id',
    'amp_image_owner_id',
    'amp_image_tag',
    'amp_secgroup_list',
    'amp_ssh_access_allowed',
    'amphora_driver',
    'amphora_expiry_age',
    'amphora_udp_driver',
    'anti_affinity_policy',
    'api_base_uri',
    'audit_map_file',
    'auth_strategy',
    'auth_type',
    'availability_zone',
    'base_cert_dir',
    'base_path',
    'bind_host',
    'bind_ip',
    'bind_port',
    'build_active_retries',
    'build_rate_limit',
    'build_retry_interval',
    'ca_certificates_file',
    'cafile',
    'cert_generator',
    'cert_manager',
    'cert_validity_time',
    'cleanup_interval',
    'client_ca',
    'client_cert',
    'compute_driver',
    'connection_logging',
    'connection_max_retries',
    'connection_retry_interval',
    'controller_ip_port_list',
    'debug',
    'default_health_monitor_quota',
    'default_listener_quota',
    'default_load_balancer_quota',
    'default_member_quota',
    'default_pool_quota',
    'default_provider_driver',
    'disable_local_log_storage',
    'disable_revert',
    'distributor_driver',
    'driver',
    'enable_anti_affinity',
    'enable_proxy_headers_parsing',
    'enabled',
    'enabled_provider_agents',
    'enabled_provider_drivers',
    'endpoint_type',
    'engine',
    'failover_threads',
    'forward_all_logs',
    'get_socket_path',
    'graceful_shutdown_timeout',
    'haproxy_cmd',
    'haproxy_stick_size',
    'haproxy_template',
    'health_check_interval',
    'health_update_driver',
    'health_update_threads',
    'heartbeat_interval',
    'heartbeat_timeout',
    'ignore_req_list',
    'insecure',
    'lb_network_interface',
    'load_balancer_expiry_age',
    'loadbalancer_topology',
    'log_dir',
    'log_file',
    'log_protocol',
    'log_queue_size',
    'log_retry_count',
    'log_retry_interval',
    'logging_template_override',
    'max_process_warning_percent',
    'max_retries',
    'max_workers',
    'memcached_servers',
    'network_driver',
    'octavia_plugins',
    'pagination_max_limit',
    'policy_file',
    'port_detach_timeout',
    'provider_agent_shutdown_timeout',
    'random_amphora_name_length',
    'region_name',
    'respawn_count',
    'respawn_interval',
    'rest_request_conn_timeout',
    'rest_request_read_timeout',
    'retry_interval',
    'rpc_thread_pool_size',
    'server_ca',
    'service_name',
    'signing_digest',
    'sock_rlimit',
    'spare_amphora_pool_size',
    'spare_check_interval',
    'stats_max_processes',
    'stats_request_timeout',
    'stats_socket_path',
    'stats_update_driver',
    'stats_update_threads',
    'status_max_processes',
    'status_request_timeout',
    'status_socket_path',
    'status_update_threads',
    'storage_path',
    'tenant_log_targets',
    'topic',
    'topics',
    'udp_connect_min_interval_health_monitor',
    'use_oslo_messaging',
    'use_upstart',
    'user_data_config_drive',
    'user_log_facility',
    'user_log_format',
    'volume_create_max_retries',
    'volume_create_retry_interval',
    'volume_create_timeout',
    'volume_driver',
    'volume_size',
    'volume_type',
    'vrrp_advert_int',
    'vrrp_check_interval',
    'vrrp_fail_count',
    'vrrp_garp_refresh_count',
    'vrrp_garp_refresh_interval',
    'vrrp_success_count',
    'workers'
]

add_filter(Specs.octavia_conf, VALID_KEYS)


@parser(Specs.octavia_conf)
class OctaviaConf(IniConfigFile):
    """
    Parser for file ``/var/lib/config-data/puppet-generated/octavia/etc/octavia/octavia.conf``
    """
    pass
