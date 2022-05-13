import doctest
import insights.parsers.octavia as octavia_module
from insights.parsers.octavia import OctaviaConf, VALID_KEYS
from insights.tests import context_wrap

CONF_FILE = """
[DEFAULT]
# Print debugging output (set logging level to DEBUG instead of default WARNING level).
debug = False

# Plugin options are hot_plug_plugin (Hot-pluggable controller plugin)
octavia_plugins = hot_plug_plugin

# Hostname to be used by the host machine for services running on it.
# The default value is the hostname of the host machine.
host = some_hostname.some_domain.com

# AMQP Transport URL
# For Single Host, specify one full transport URL:
#   transport_url = rabbit://<user>:<pass>@127.0.0.1:5672/<vhost>
# For HA, specify queue nodes in cluster, comma delimited:
#   transport_url = rabbit://<user>:<pass>@server01,<user>:<pass>@server02/<vhost>
transport_url =

# How long in seconds to wait for octavia worker to exit before killing them.
graceful_shutdown_timeout = 60

log_file = some_file
log_dir = some_dir
policy_file = some_policy_file

[api_settings]
bind_host = 127.0.0.1
bind_port = 9876

# How should authentication be handled (keystone, noauth)
auth_strategy = keystone

allow_pagination = True
allow_sorting = True
pagination_max_limit = 1000
# Base URI for the API for use in pagination links.
# This will be autodetected from the request if not overridden here.
# Example:
#   api_base_uri = http://localhost:9876
api_base_uri = http://localhost:9876

# Enable/disable ability for users to create TLS Terminated listeners
allow_tls_terminated_listeners = True

# Enable/disable ability for users to create PING type Health Monitors
allow_ping_health_monitors = True

# Dictionary of enabled provider driver names and descriptions
# A comma separated list of dictionaries of the enabled provider driver names
# and descriptions.
enabled_provider_drivers = amphora:The Octavia Amphora driver.,octavia: \\
                           Deprecated alias of the Octavia Amphora driver.

# Default provider driver
default_provider_driver = amphora

# The minimum health monitor delay interval for UDP-CONNECT Health Monitor type
udp_connect_min_interval_health_monitor = 3

[database]
# This line MUST be changed to actually run the plugin.
# Example:
# connection = mysql+pymysql://root:pass@127.0.0.1:3306/octavia
# Replace 127.0.0.1 above with the IP address of the database used by the
# main octavia server. (Leave it as is if the database runs on this host.)

connection = mysql+pymysql://

# NOTE: In deployment the [database] section and its connection attribute may
# be set in the corresponding core plugin '.ini' file. However, it is suggested
# to put the [database] section and its connection attribute in this
# configuration file.

[health_manager]
bind_ip = 127.0.0.1
bind_port = 5555
# controller_ip_port_list example: 127.0.0.1:5555, 127.0.0.1:5555
controller_ip_port_list = 127.0.0.1:5555, 127.0.0.1:5555
failover_threads = 10
# status_update_threads will default to the number of processors on the host.
# This setting is deprecated and if you specify health_update_threads and
# stats_update_threads, they override this parameter.
status_update_threads = 10
# health_update_threads will default to the number of processors on the host
health_update_threads = 10
# stats_update_threads will default to the number of processors on the host
stats_update_threads = 10
heartbeat_interval = 10
# Symmetric encrpytion key
heartbeat_key =
heartbeat_timeout = 60
health_check_interval = 3
sock_rlimit = 0

# Health/StatsUpdate options are
#                           *_db
#                           *_logger
health_update_driver = health_db
stats_update_driver = stats_db

[keystone_authtoken]
# This group of config options are imported from keystone middleware. Thus the
# option names should match the names declared in the middleware.
# The www_authenticate_uri is the public endpoint and is returned in headers on a 401
# www_authenticate_uri = https://localhost:5000/v3
# The auth_url is the admin endpoint actually used for validating tokens
auth_url = https://localhost:5000/v3
username = octavia
password = password
project_name = service

# Domain names must be set, these are *not* default but work for most clouds
# project_domain_name = Default
user_domain_name = Default

insecure = False
cafile =

[certificates]
# Certificate Generator options are local_cert_generator
cert_generator = local_cert_generator

# For local certificate signing:
ca_certificate = /etc/ssl/certs/ssl-cert-snakeoil.pem
ca_private_key = /etc/ssl/private/ssl-cert-snakeoil.key
ca_private_key_passphrase =
server_certs_key_passphrase = do-not-use-this-key
signing_digest = sha256
cert_validity_time = 2592000  # 30 days = 30d * 24h * 60m * 60s = 2592000s
storage_path = /var/lib/octavia/certificates/

# For the TLS management
# Certificate Manager options are local_cert_manager
#                                 barbican_cert_manager
#                                 castellan_cert_manager
cert_manager = barbican_cert_manager
# For Barbican authentication (if using any Barbican based cert class)
barbican_auth = barbican_acl_auth
#
# Region in Identity service catalog to use for communication with the Barbican service.
region_name = some_region
#
# Endpoint type to use for communication with the Barbican service.
endpoint_type = publicURL

[networking]
# The maximum attempts to retry an action with the networking service.
max_retries = 15
# Seconds to wait before retrying an action with the networking service.
retry_interval = 1
# The maximum time to wait, in seconds, for a port to detach from an amphora
port_detach_timeout = 300
# Allow/disallow specific network object types when creating VIPs.
allow_vip_network_id = True
allow_vip_subnet_id = True
allow_vip_port_id = True
# List of network_ids that are valid for VIP creation.
# If this field empty, no validation is performed.
valid_vip_networks =
# List of reserved IP addresses that cannot be used for member addresses
# The default is the nova metadata service address
reserved_ips = ['169.254.169.254']

[haproxy_amphora]
base_path = /var/lib/octavia
base_cert_dir = /var/lib/octavia/certs
# Absolute path to a custom HAProxy template file
haproxy_template = /some/path
connection_logging = True
connection_max_retries = 120
connection_retry_interval = 5
build_rate_limit = -1
build_active_retries = 120
build_retry_interval = 5

# Maximum number of entries that can fit in the stick table.
# The size supports "k", "m", "g" suffixes.
haproxy_stick_size = 10k

# REST Driver specific
bind_host = 0.0.0.0
bind_port = 9443
#
# This setting is only needed with IPv6 link-local addresses (fe80::/64) are
# used for communication between Octavia and its Amphora, if IPv4 or other IPv6
# addresses are used it can be ignored.
lb_network_interface = o-hm0
#
haproxy_cmd = /usr/sbin/haproxy
respawn_count = 2
respawn_interval = 2
client_cert = /etc/octavia/certs/client.pem
server_ca = /etc/octavia/certs/server_ca.pem
#
# This setting is deprecated. It is now automatically discovered.
use_upstart = True
#
rest_request_conn_timeout = 10
rest_request_read_timeout = 60
#
# These "active" timeouts are used once the amphora should already
# be fully up and active. These values are lower than the other values to
# facilitate "fail fast" scenarios like failovers
active_connection_max_retries = 15
active_connection_rety_interval = 2

# The user flow log format for HAProxy.
# {{ project_id }} and {{ lb_id }} will be automatically substituted by the
# controller when configuring HAProxy if they are present in the string.
user_log_format = '{{ project_id }} {{ lb_id }} %f %ci %cp %t %{+Q}r %ST %B %U %[ssl_c_verify] %{+Q}[ssl_c_s_dn] %b %s %Tt %tsc'

[controller_worker]
workers = 1
amp_active_retries = 30
amp_active_wait_sec = 10
# Glance parameters to extract image ID to use for amphora. Only one of
# parameters is needed. Using tags is the recommended way to refer to images.
amp_image_id =
amp_image_tag =
# Optional owner ID used to restrict glance images to one owner ID.
# This is a recommended security setting.
amp_image_owner_id =
# Nova parameters to use when booting amphora
amp_flavor_id =
# Upload the ssh key as the service_auth user described elsewhere in this config.
# Leaving this variable blank will install no ssh key on the amphora.
amp_ssh_key_name =

amp_ssh_access_allowed = True

# Networks to attach to the Amphorae examples:
#  - One primary network
#  - - amp_boot_network_list = 22222222-3333-4444-5555-666666666666
#  - Multiple networks
#  - - amp_boot_network_list = 11111111-2222-33333-4444-555555555555, 22222222-3333-4444-5555-666666666666
#  - All networks defined in the list will be attached to each amphora
amp_boot_network_list =

amp_secgroup_list =
client_ca = /etc/octavia/certs/ca_01.pem

# Amphora driver options are amphora_noop_driver,
#                            amphora_haproxy_rest_driver
#
amphora_driver = amphora_noop_driver
#
# Compute driver options are compute_noop_driver
#                            compute_nova_driver
#
compute_driver = compute_noop_driver
#
# Network driver options are network_noop_driver
#                            allowed_address_pairs_driver
#
network_driver = network_noop_driver
# Volume driver options are volume_noop_driver
#                           volume_cinder_driver
#
volume_driver = volume_noop_driver
#
# Distributor driver options are distributor_noop_driver
#                                single_VIP_amphora
#
distributor_driver = distributor_noop_driver
#
# Load balancer topology options are SINGLE, ACTIVE_STANDBY
loadbalancer_topology = SINGLE
user_data_config_drive = False

[task_flow]
# TaskFlow engine options are:
#   - serial:   Runs all tasks on a single thread.
#   - parallel: Schedules tasks onto different threads to allow
#               for running non-dependent tasks simultaneously
#
engine = parallel
max_workers = 5
#
# This setting prevents the controller worker from reverting taskflow flows.
# This will leave resources in an inconsistent state and should only be used
# for debugging purposes.
disable_revert = False

[oslo_messaging]
# Queue Consumer Thread Pool Size
rpc_thread_pool_size = 2

# Topic (i.e. Queue) Name
topic = octavia_prov

[oslo_middleware]
# HTTPProxyToWSGI middleware enabled
enable_proxy_headers_parsing = False

[house_keeping]
# Interval in seconds to initiate spare amphora checks
spare_check_interval = 30
spare_amphora_pool_size = 0

# Cleanup interval for Deleted amphora
cleanup_interval = 30
# Amphora expiry age in seconds. Default is 1 week
amphora_expiry_age = 604800

# Load balancer expiry age in seconds. Default is 1 week
load_balancer_expiry_age = 604800

[amphora_agent]
agent_server_ca = /etc/octavia/certs/client_ca.pem
agent_server_cert = /etc/octavia/certs/server.pem

# Defaults for agent_server_network_dir when not specified here are:
# Ubuntu: /etc/netns/amphora-haproxy/network/interfaces.d/
# Centos/fedora/rhel: /etc/netns/amphora-haproxy/sysconfig/network-scripts/
#
agent_server_network_dir =

agent_server_network_file =
agent_request_read_timeout = 180

# Minimum TLS protocol, eg: TLS, TLSv1.1, TLSv1.2, TLSv1.3 (if available)
agent_tls_protocol = TLSv1.2

# Amphora default UDP driver is keepalived_lvs
#
amphora_udp_driver = keepalived_lvs

##### Log offloading
#
# Note: The admin and tenant logs can point to the same endpoints.
#
# List of log server ip and port pairs for Administrative logs.
# Additional hosts are backup to the primary server. If none are
# specified, remote logging is disabled.
# Example 192.0.2.1:10514, 2001:db8:1::10:10514'
#
admin_log_targets =
#
# List of log server ip and port pairs for tenant traffic logs.
# Additional hosts are backup to the primary server. If none are
# specified, remote logging is disabled.
# Example 192.0.2.1:10514, 2001:db8:2::15:10514'
#
tenant_log_targets =

# Sets the syslog LOG_LOCAL[0-7] facility number for amphora log offloading.
# user_log_facility will receive the traffic flow logs.
# administrative_log_facility will receive the amphora processes logs.
# Note: Some processes only support LOG_LOCAL, so we are restricted to the
#       LOG_LOCAL facilities.
#
user_log_facility = 0
administrative_log_facility = 1

# The log forwarding protocol to use. One of TCP or UDP.
log_protocol = UDP

# The maximum attempts to retry connecting to the logging host.
log_retry_count = 5

# The time, in seconds, to wait between retries connecting to the logging host.
log_retry_interval = 2

# The queue size (messages) to buffer log messages.
log_queue_size = 10000

# Controller local path to a custom logging configuration template.
# Currently this is an rsyslog configuration file template.
logging_template_override =

# When True, the amphora will forward all of the system logs (except tenant
# traffice logs) to the admin log target(s). When False, only amphora specific
# admin logs will be forwarded.
forward_all_logs = False

# When True, no logs will be written to the amphora filesystem. When False,
# log files will be written to the local filesystem.
disable_local_log_storage = False

[keepalived_vrrp]
# Amphora Role/Priority advertisement interval in seconds
vrrp_advert_int = 1

# Service health check interval and success/fail count
vrrp_check_interval = 5
vrrp_fail_count = 2
vrrp_success_count = 2

# Amphora MASTER gratuitous ARP refresh settings
vrrp_garp_refresh_interval = 5
vrrp_garp_refresh_count = 2

[service_auth]
memcached_servers =
cafile = /opt/stack/data/ca-bundle.pem
project_domain_name = Default
project_name = admin
user_domain_name = Default
password = password
username = admin
auth_type = password
auth_url = http://localhost:5555/

[nova]
# The name of the nova service in the keystone catalog
service_name =
# Custom nova endpoint if override is necessary
endpoint =

# Region in Identity service catalog to use for communication with the
# OpenStack services.
region_name =

# Endpoint type in Identity service catalog to use for communication with
# the OpenStack services.
endpoint_type = publicURL

# CA certificates file to verify neutron connections when TLS is enabled
ca_certificates_file =

# Disable certificate validation on SSL connections
insecure = False

# If non-zero, generate a random name of the length provided for each amphora,
# in the format "a[A-Z0-9]*".
# Otherwise, the default name format will be used: "amphora-{UUID}".
random_amphora_name_length = 0
#
# Availability zone to use for creating Amphorae
availability_zone =

# Enable anti-affinity in nova
enable_anti_affinity = False
# Set the anti-affinity policy to what is suitable.
# Nova supports: anti-affinity and soft-anti-affinity
anti_affinity_policy = anti-affinity

[cinder]
# The name of the cinder service in the keystone catalog
service_name =
# Custom cinder endpoint if override is necessary
endpoint =

# Region in Identity service catalog to use for communication with the
# OpenStack services.
region_name =

# Endpoint type in Identity service catalog to use for communication with
# the OpenStack services.
endpoint_type = publicURL

# Availability zone to use for creating Volume
availability_zone =

# CA certificates file to verify cinder connections when TLS is enabled
insecure = False
ca_certificates_file =

# Size of root volume in GB for Amphora Instance when use Cinder
# In some storage backends such as ScaleIO, the size of volume is multiple of 8
volume_size = 16

# Volume type to be used for Amphora Instance root disk
# If not specified, default_volume_type from cinder.conf will be used
volume_type =

# Interval time to wait until volume becomes available
volume_create_retry_interval = 5

# Timeout to wait for volume creation success
volume_create_timeout = 300

# Maximum number of retries to create volume
volume_create_max_retries = 5

[glance]
# The name of the glance service in the keystone catalog
service_name =
# Custom glance endpoint if override is necessary
endpoint =

# Region in Identity service catalog to use for communication with the
# OpenStack services.
region_name =

# Endpoint type in Identity service catalog to use for communication with
# the OpenStack services.
endpoint_type = publicURL

# CA certificates file to verify neutron connections when TLS is enabled
insecure = False
ca_certificates_file =

[neutron]
# The name of the neutron service in the keystone catalog
service_name =
# Custom neutron endpoint if override is necessary
endpoint =

# Region in Identity service catalog to use for communication with the
# OpenStack services.
region_name =

# Endpoint type in Identity service catalog to use for communication with
# the OpenStack services.
endpoint_type = publicURL

# CA certificates file to verify neutron connections when TLS is enabled
insecure = False
ca_certificates_file =

[quotas]
default_load_balancer_quota = -1
default_listener_quota = -1
default_member_quota = -1
default_pool_quota = -1
default_health_monitor_quota = -1

[audit]
# Enable auditing of API requests.
enabled = False

# Path to audit map file for octavia-api service. Used only
# when API audit is enabled.
audit_map_file = /etc/octavia/octavia_api_audit_map.conf

# Comma separated list of REST API HTTP methods to be
# ignored during audit. For example: auditing will not be done
# on any GET or POST requests if this is set to "GET,POST". It
# is used only when API audit is enabled.
ignore_req_list =

[audit_middleware_notifications]
# Note: This section comes from openstack/keystonemiddleware
# It is included here for documentation convenience and may be out of date

# Indicate whether to use oslo_messaging as the notifier. If set to False,
# the local logger will be used as the notifier. If set to True, the
# oslo_messaging package must also be present. Otherwise, the local will be
# used instead.
use_oslo_messaging = True

# The Driver to handle sending notifications. Possible values are messaging,
# messagingv2, routing, log, test, noop. If not specified, then value from
# oslo_messaging_notifications conf section is used.
driver =

# List of AMQP topics used for OpenStack notifications. If not specified,
# then value from oslo_messaging_notifications conf section is used.
topics =

# A URL representing messaging driver to use for notification. If not
# specified, we fall back to the same configuration used for RPC.
transport_url =

[driver_agent]
status_socket_path = /var/run/octavia/status.sock
stats_socket_path = /var/run/octavia/stats.sock
get_socket_path = /var/run/octavia/get.sock

# Maximum time to wait for a status message before checking for shutdown
status_request_timeout = 5

# Maximum number of status processes per driver-agent
status_max_processes = 50

# Maximum time to wait for a stats message before checking for shutdown
stats_request_timeout = 5

# Maximum number of stats processes per driver-agent
stats_max_processes = 50

# Percentage of max_processes (both status and stats) in use to start
# logging warning messages about an overloaded driver-agent.
max_process_warning_percent = .75

# How long in seconds to wait for provider agents to exit before killing them.
provider_agent_shutdown_timeout = 60

# List of enabled provider agents.
enabled_provider_agents =
"""

DEFAULT_OPTIONS = set([
    'debug', 'octavia_plugins', 'graceful_shutdown_timeout',
    'log_file', 'log_dir', 'policy_file'
])


def test_full_conf():
    # Simulate filtering to allow testing filtered data
    filtered_content = []
    for line in CONF_FILE.strip().splitlines():
        if any([f in line for f in VALID_KEYS]):
            filtered_content.append(line)
    octavia_conf = OctaviaConf(context_wrap('\n'.join(filtered_content)))
    assert octavia_conf is not None
    assert set(octavia_conf.defaults().keys()) == DEFAULT_OPTIONS
    assert octavia_conf.defaults()['debug'] == 'False'
    assert octavia_conf.defaults()['octavia_plugins'] == 'hot_plug_plugin'

    assert 'api_settings' in octavia_conf
    assert set(octavia_conf.items('api_settings').keys()) == set([
        'bind_host', 'bind_port', 'auth_strategy', 'allow_pagination', 'allow_sorting',
        'pagination_max_limit', 'api_base_uri', 'allow_tls_terminated_listeners',
        'allow_ping_health_monitors', 'enabled_provider_drivers', 'default_provider_driver',
        'udp_connect_min_interval_health_monitor'
    ]) | DEFAULT_OPTIONS

    assert 'database' in octavia_conf
    assert set(octavia_conf.items('database').keys()) == DEFAULT_OPTIONS

    assert 'health_manager' in octavia_conf
    assert set(octavia_conf.items('health_manager').keys()) == set([
        'bind_ip', 'bind_port', 'controller_ip_port_list', 'failover_threads',
        'status_update_threads', 'health_update_threads', 'stats_update_threads',
        'heartbeat_interval', 'heartbeat_timeout', 'health_check_interval',
        'sock_rlimit', 'health_update_driver', 'stats_update_driver'
    ]) | DEFAULT_OPTIONS

    assert 'keystone_authtoken' in octavia_conf
    assert set(octavia_conf.items('keystone_authtoken').keys()) == set(['insecure', 'cafile']) | DEFAULT_OPTIONS

    assert 'certificates' in octavia_conf
    assert set(octavia_conf.items('certificates').keys()) == set([
        'cert_generator', 'signing_digest', 'cert_validity_time', 'storage_path',
        'cert_manager', 'region_name', 'endpoint_type'
    ]) | DEFAULT_OPTIONS

    assert 'networking' in octavia_conf
    assert set(octavia_conf.items('networking').keys()) == set([
        'max_retries', 'retry_interval', 'port_detach_timeout', 'allow_vip_network_id',
        'allow_vip_subnet_id', 'allow_vip_port_id', 'reserved_ips'
    ]) | DEFAULT_OPTIONS

    assert 'haproxy_amphora' in octavia_conf
    assert set(octavia_conf.items('haproxy_amphora').keys()) == set([
        'base_path',
        'base_cert_dir',
        'haproxy_template',
        'connection_logging',
        'connection_max_retries',
        'connection_retry_interval',
        'build_rate_limit',
        'build_active_retries',
        'build_retry_interval',
        'haproxy_stick_size',
        'bind_host',
        'bind_port',
        'lb_network_interface',
        'haproxy_cmd',
        'respawn_count',
        'respawn_interval',
        'client_cert',
        'server_ca',
        'use_upstart',
        'rest_request_conn_timeout',
        'rest_request_read_timeout',
        'active_connection_max_retries',
        'active_connection_rety_interval',
        'user_log_format',
    ]) | DEFAULT_OPTIONS

    assert 'controller_worker' in octavia_conf
    assert set(octavia_conf.items('controller_worker').keys()) == set([
        'workers',
        'amp_active_retries',
        'amp_active_wait_sec',
        'amp_image_id',
        'amp_image_tag',
        'amp_image_owner_id',
        'amp_flavor_id',
        'amp_boot_network_list',
        'amp_secgroup_list',
        'amp_ssh_access_allowed',
        'client_ca',
        'amphora_driver',
        'compute_driver',
        'network_driver',
        'volume_driver',
        'distributor_driver',
        'loadbalancer_topology',
        'user_data_config_drive',
    ]) | DEFAULT_OPTIONS

    assert 'task_flow' in octavia_conf
    assert set(octavia_conf.items('task_flow').keys()) == set([
        'engine',
        'max_workers',
        'disable_revert',
    ]) | DEFAULT_OPTIONS

    assert 'oslo_messaging' in octavia_conf
    assert set(octavia_conf.items('oslo_messaging').keys()) == set([
        'rpc_thread_pool_size',
        'topic',
    ]) | DEFAULT_OPTIONS

    assert 'oslo_middleware' in octavia_conf
    assert set(octavia_conf.items('oslo_middleware').keys()) == set([
        'enable_proxy_headers_parsing',
    ]) | DEFAULT_OPTIONS

    assert 'house_keeping' in octavia_conf
    assert set(octavia_conf.items('house_keeping').keys()) == set([
        'spare_check_interval',
        'spare_amphora_pool_size',
        'cleanup_interval',
        'amphora_expiry_age',
        'load_balancer_expiry_age',
    ]) | DEFAULT_OPTIONS

    assert 'amphora_agent' in octavia_conf
    assert set(octavia_conf.items('amphora_agent').keys()) == set([
        'agent_server_ca',
        'agent_server_cert',
        'agent_server_network_dir',
        'agent_server_network_file',
        'agent_request_read_timeout',
        'agent_tls_protocol',
        'amphora_udp_driver',
        'admin_log_targets',
        'tenant_log_targets',
        'user_log_facility',
        'administrative_log_facility',
        'log_protocol',
        'log_retry_count',
        'log_retry_interval',
        'log_queue_size',
        'logging_template_override',
        'forward_all_logs',
        'disable_local_log_storage',
    ]) | DEFAULT_OPTIONS

    assert 'keepalived_vrrp' in octavia_conf
    assert set(octavia_conf.items('keepalived_vrrp').keys()) == set([
        'vrrp_advert_int',
        'vrrp_check_interval',
        'vrrp_fail_count',
        'vrrp_success_count',
        'vrrp_garp_refresh_interval',
        'vrrp_garp_refresh_count',
    ]) | DEFAULT_OPTIONS

    assert 'service_auth' in octavia_conf
    assert set(octavia_conf.items('service_auth').keys()) == set([
        'memcached_servers',
        'cafile',
        'auth_type',
    ]) | DEFAULT_OPTIONS

    assert 'nova' in octavia_conf
    assert set(octavia_conf.items('nova').keys()) == set([
        'service_name',
        'region_name',
        'endpoint_type',
        'ca_certificates_file',
        'insecure',
        'random_amphora_name_length',
        'availability_zone',
        'enable_anti_affinity',
        'anti_affinity_policy',
    ]) | DEFAULT_OPTIONS

    assert 'cinder' in octavia_conf
    assert set(octavia_conf.items('cinder').keys()) == set([
        'service_name',
        'region_name',
        'endpoint_type',
        'availability_zone',
        'insecure',
        'ca_certificates_file',
        'volume_size',
        'volume_type',
        'volume_create_retry_interval',
        'volume_create_timeout',
        'volume_create_max_retries',
    ]) | DEFAULT_OPTIONS

    assert 'glance' in octavia_conf
    assert set(octavia_conf.items('glance').keys()) == set([
        'service_name',
        'region_name',
        'endpoint_type',
        'insecure',
        'ca_certificates_file',
    ]) | DEFAULT_OPTIONS

    assert 'neutron' in octavia_conf
    assert set(octavia_conf.items('neutron').keys()) == set([
        'service_name',
        'region_name',
        'endpoint_type',
        'insecure',
        'ca_certificates_file',
    ]) | DEFAULT_OPTIONS

    assert 'quotas' in octavia_conf
    assert set(octavia_conf.items('quotas').keys()) == set([
        'default_load_balancer_quota',
        'default_listener_quota',
        'default_member_quota',
        'default_pool_quota',
        'default_health_monitor_quota',
    ]) | DEFAULT_OPTIONS

    assert 'audit' in octavia_conf
    assert set(octavia_conf.items('audit').keys()) == set([
        'enabled',
        'audit_map_file',
        'ignore_req_list',
    ]) | DEFAULT_OPTIONS

    assert 'audit_middleware_notifications' in octavia_conf
    assert set(octavia_conf.items('audit_middleware_notifications').keys()) == set([
        'use_oslo_messaging',
        'driver',
        'topics',
    ]) | DEFAULT_OPTIONS

    assert 'driver_agent' in octavia_conf
    assert set(octavia_conf.items('driver_agent').keys()) == set([
        'status_socket_path',
        'stats_socket_path',
        'get_socket_path',
        'status_request_timeout',
        'status_max_processes',
        'stats_request_timeout',
        'stats_max_processes',
        'max_process_warning_percent',
        'provider_agent_shutdown_timeout',
        'enabled_provider_agents',
    ]) | DEFAULT_OPTIONS


def test_doc_examples():
    env = {
        'octavia_conf': OctaviaConf(context_wrap(CONF_FILE)),
    }
    failed, total = doctest.testmod(octavia_module, globs=env)
    assert failed == 0
