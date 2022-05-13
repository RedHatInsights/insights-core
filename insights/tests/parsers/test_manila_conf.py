import doctest

from insights.core.context import OSP
from insights.parsers import manila_conf
from insights.tests import context_wrap

MANILA_CONTENT = """
[DEFAULT]

#
# From manila
#

# The maximum number of items returned in a single response from a
# collection resource. (integer value)
#osapi_max_limit = 1000

# Base URL to be presented to users in links to the Share API (string
# value)
#osapi_share_base_URL = <None>

# Treat X-Forwarded-For as the canonical remote address. Only enable
# this if you have a sanitizing proxy. (boolean value)
#use_forwarded_for = false

# File name for the paste.deploy config for manila-api. (string value)
#api_paste_config = api-paste.ini

# Top-level directory for maintaining manila's state. (string value)
#state_path = /var/lib/manila

# IP address of this host. (string value)
#my_ip = 192.0.2.1

# The topic scheduler nodes listen on. (string value)
scheduler_topic = manila-scheduler

# The topic share nodes listen on. (string value)
share_topic = manila-share

# Deploy v1 of the Manila API. This option is deprecated, is not used,
# and will be removed in a future release. (boolean value)
#enable_v1_api = false

# Deploy v2 of the Manila API. This option is deprecated, is not used,
# and will be removed in a future release. (boolean value)
enable_v2_api = false

# Whether to rate limit the API. (boolean value)
#api_rate_limit = true

# Specify list of extensions to load when using osapi_share_extension
# option with manila.api.contrib.select_extensions. (list value)
#osapi_share_ext_list =

# The osapi share extension to load. (multi valued)
#osapi_share_extension = manila.api.contrib.standard_extensions

# The filename to use with sqlite. (string value)
#sqlite_db = manila.sqlite

# If passed, use synchronous mode for sqlite. (boolean value)
#sqlite_synchronous = true

# Timeout before idle SQL connections are reaped. (integer value)
#sql_idle_timeout = 3600

# Maximum database connection retries during startup. (setting -1
# implies an infinite retry count). (integer value)
#sql_max_retries = 10

# Interval between retries of opening a SQL connection. (integer
# value)
#sql_retry_interval = 10

# Full class name for the scheduler manager. (string value)
#scheduler_manager = manila.scheduler.manager.SchedulerManager

# Full class name for the share manager. (string value)
#share_manager = manila.share.manager.ShareManager

# Name of this node.  This can be an opaque identifier.  It is not
# necessarily a hostname, FQDN, or IP address. (string value)
#host = testhost

# Availability zone of this node. (string value)
#storage_availability_zone = nova

# Default share type to use. (string value)
#default_share_type = <None>

# Memcached servers or None for in process cache. (list value)
#memcached_servers = <None>

# Time period to generate share usages for.  Time period must be hour,
# day, month or year. (string value)
#share_usage_audit_period = month

# Deprecated: command to use for running commands as root. (string
# value)
#root_helper = sudo

# Path to the rootwrap configuration file to use for running commands
# as root. (string value)
#rootwrap_config = <None>

# Whether to log monkey patching. (boolean value)
#monkey_patch = false

# List of modules or decorators to monkey patch. (list value)
#monkey_patch_modules =

# Maximum time since last check-in for up service. (integer value)
#service_down_time = 60

# The full class name of the share API class to use. (string value)
#share_api_class = manila.share.api.API

# The strategy to use for auth. Supports noauth, keystone, and
# deprecated. (string value)
#auth_strategy = keystone

# A list of share backend names to use. These backend names should be
# backed by a unique [CONFIG] group with its options. (list value)
#enabled_share_backends = <None>

# Specify list of protocols to be allowed for share creation.
# Available values are '('NFS', 'CIFS', 'GLUSTERFS', 'HDFS')' (list
# value)
#enabled_share_protocols = NFS,CIFS

# The full class name of the Compute API class to use. (string value)
#compute_api_class = manila.compute.nova.API

# Info to match when looking for nova in the service catalog. Format
# is separated values of the form:
# <service_type>:<service_name>:<endpoint_type> (string value)
#nova_catalog_info = compute:nova:publicURL

# Same as nova_catalog_info, but for admin endpoint. (string value)
#nova_catalog_admin_info = compute:nova:adminURL

# Region name of this node. (string value)
#os_region_name = <None>

# Location of CA certificates file to use for nova client requests.
# (string value)
#nova_ca_certificates_file = <None>

# Allow to perform insecure SSL requests to nova. (boolean value)
#nova_api_insecure = false

# Nova admin username. (string value)
#nova_admin_username = nova

# Nova admin password. (string value)
#nova_admin_password = <None>

# Nova admin tenant name. (string value)
#nova_admin_tenant_name = service

# Identity service URL. (string value)
#nova_admin_auth_url = http://localhost:5000/v2.0

# Version of Nova API to be used. (string value)
#nova_api_microversion = 2.10

# The backend to use for database. (string value)
#db_backend = sqlalchemy

# Services to be added to the available pool on create. (boolean
# value)
#enable_new_services = true

# Template string to be used to generate share names. (string value)
#share_name_template = share-%s

# Template string to be used to generate share snapshot names. (string
# value)
#share_snapshot_name_template = share-snapshot-%s

# Driver to use for database access. (string value)
#db_driver = manila.db

# Whether to make exception message format errors fatal. (boolean
# value)
#fatal_exception_format_errors = false

# Name of Open vSwitch bridge to use. (string value)
#ovs_integration_bridge = br-int

# The full class name of the Networking API class to use. (string
# value)
# Deprecated group/name - [DEFAULT]/network_api_class
#network_api_class = manila.network.neutron.neutron_network_plugin.NeutronNetworkPlugin

# URL for connecting to neutron. (string value)
# Deprecated group/name - [DEFAULT]/neutron_url
#neutron_url = http://127.0.0.1:9696

# Timeout value for connecting to neutron in seconds. (integer value)
# Deprecated group/name - [DEFAULT]/neutron_url_timeout
#neutron_url_timeout = 30

# Username for connecting to neutron in admin context. (string value)
# Deprecated group/name - [DEFAULT]/neutron_admin_username
#neutron_admin_username = neutron

# Password for connecting to neutron in admin context. (string value)
# Deprecated group/name - [DEFAULT]/neutron_admin_password
#neutron_admin_password = <None>

# Project name for connecting to Neutron in admin context. (string
# value)
# Deprecated group/name - [DEFAULT]/neutron_admin_tenant_name
#neutron_admin_project_name = service

# Auth URL for connecting to neutron in admin context. (string value)
# Deprecated group/name - [DEFAULT]/neutron_admin_auth_url
#neutron_admin_auth_url = http://localhost:5000/v2.0

# If set, ignore any SSL validation issues. (boolean value)
# Deprecated group/name - [DEFAULT]/neutron_api_insecure
#neutron_api_insecure = false

# Auth strategy for connecting to neutron in admin context. (string
# value)
# Deprecated group/name - [DEFAULT]/neutron_auth_strategy
#neutron_auth_strategy = keystone

# Location of CA certificates file to use for neutron client requests.
# (string value)
# Deprecated group/name - [DEFAULT]/neutron_ca_certificates_file
#neutron_ca_certificates_file = <None>

# Default Neutron network that will be used for share server creation.
# This opt is used only with class 'NeutronSingleNetworkPlugin'.
# (string value)
# Deprecated group/name - [DEFAULT]/neutron_net_id
#neutron_net_id = <None>

# Default Neutron subnet that will be used for share server creation.
# Should be assigned to network defined in opt 'neutron_net_id'. This
# opt is used only with class 'NeutronSingleNetworkPlugin'. (string
# value)
# Deprecated group/name - [DEFAULT]/neutron_subnet_id
#neutron_subnet_id = <None>

# Default Nova network that will be used for share servers. This opt
# is used only with class 'NovaSingleNetworkPlugin'. (string value)
# Deprecated group/name - [DEFAULT]/nova_single_network_plugin_net_id
#nova_single_network_plugin_net_id = <None>

# Gateway IPv4 address that should be used. Required. (string value)
# Deprecated group/name - [DEFAULT]/standalone_network_plugin_gateway
#standalone_network_plugin_gateway = <None>

# Network mask that will be used. Can be either decimal like '24' or
# binary like '255.255.255.0'. Required. (string value)
# Deprecated group/name - [DEFAULT]/standalone_network_plugin_mask
#standalone_network_plugin_mask = <None>

# Set it if network has segmentation (VLAN, VXLAN, etc...). It will be
# assigned to share-network and share drivers will be able to use this
# for network interfaces within provisioned share servers. Optional.
# Example: 1001 (string value)
# Deprecated group/name - [DEFAULT]/standalone_network_plugin_segmentation_id
#standalone_network_plugin_segmentation_id = <None>

# Can be IP address, range of IP addresses or list of addresses or
# ranges. Contains addresses from IP network that are allowed to be
# used. If empty, then will be assumed that all host addresses from
# network can be used. Optional. Examples: 10.0.0.10 or
# 10.0.0.10-10.0.0.20 or
# 10.0.0.10-10.0.0.20,10.0.0.30-10.0.0.40,10.0.0.50 (list value)
# Deprecated group/name - [DEFAULT]/standalone_network_plugin_allowed_ip_ranges
#standalone_network_plugin_allowed_ip_ranges = <None>

# IP version of network. Optional.Allowed values are '4' and '6'.
# Default value is '4'. (integer value)
# Deprecated group/name - [DEFAULT]/standalone_network_plugin_ip_version
#standalone_network_plugin_ip_version = 4

# Number of shares allowed per project. (integer value)
#quota_shares = 50

# Number of share snapshots allowed per project. (integer value)
#quota_snapshots = 50

# Number of share gigabytes allowed per project. (integer value)
#quota_gigabytes = 1000

# Number of snapshot gigabytes allowed per project. (integer value)
#quota_snapshot_gigabytes = 1000

# Number of share-networks allowed per project. (integer value)
#quota_share_networks = 10

# Number of seconds until a reservation expires. (integer value)
#reservation_expire = 86400

# Count of reservations until usage is refreshed. (integer value)
#until_refresh = 0

# Number of seconds between subsequent usage refreshes. (integer
# value)
#max_age = 0

# Default driver to use for quota checks. (string value)
#quota_driver = manila.quota.DbQuotaDriver

# The scheduler host manager class to use. (string value)
#scheduler_host_manager = manila.scheduler.host_manager.HostManager

# Maximum number of attempts to schedule a share. (integer value)
#scheduler_max_attempts = 3

# Which filter class names to use for filtering hosts when not
# specified in the request. (list value)
#scheduler_default_filters = AvailabilityZoneFilter,CapacityFilter,CapabilitiesFilter,ConsistencyGroupFilter

# Which weigher class names to use for weighing hosts. (list value)
#scheduler_default_weighers = CapacityWeigher

# Default scheduler driver to use. (string value)
#scheduler_driver = manila.scheduler.filter_scheduler.FilterScheduler

# Absolute path to scheduler configuration JSON file. (string value)
#scheduler_json_config_location =

# Maximum number of volume gigabytes to allow per host. (integer
# value)
#max_gigabytes = 10000

# Multiplier used for weighing share capacity. Negative numbers mean
# to stack vs spread. (floating point value)
#capacity_weight_multiplier = 1.0

# Multiplier used for weighing pools which have existing share
# servers. Negative numbers mean to spread vs stack. (floating point
# value)
#pool_weight_multiplier = 1.0

# Seconds between nodes reporting state to datastore. (integer value)
#report_interval = 10

# Seconds between running periodic tasks. (integer value)
#periodic_interval = 60

# Range of seconds to randomly delay when starting the periodic task
# scheduler to reduce stampeding. (Disable by setting to 0) (integer
# value)
#periodic_fuzzy_delay = 60

# IP address for OpenStack Share API to listen on. (string value)
#osapi_share_listen = ::

# Port for OpenStack Share API to listen on. (integer value)
#osapi_share_listen_port = 8786

# Number of workers for OpenStack Share API service. (integer value)
#osapi_share_workers = 1

# If set to False, then share creation from snapshot will be performed
# on the same host. If set to True, then scheduling step will be used.
# (boolean value)
#use_scheduler_creating_share_from_snapshot = false

# Directory where Ganesha config files are stored. (string value)
#ganesha_config_dir = /etc/ganesha

# Path to main Ganesha config file. (string value)
#ganesha_config_path = $ganesha_config_dir/ganesha.conf

# Name of the ganesha nfs service. (string value)
#ganesha_service_name = ganesha.nfsd

# Location of Ganesha database file. (Ganesha module only.) (string
# value)
#ganesha_db_path = $state_path/manila-ganesha.db

# Path to directory containing Ganesha export configuration. (Ganesha
# module only.) (string value)
#ganesha_export_dir = $ganesha_config_dir/export.d

# Path to directory containing Ganesha export block templates.
# (Ganesha module only.) (string value)
#ganesha_export_template_dir = /etc/manila/ganesha-export-templ.d

# Number of times to attempt to run flakey shell commands. (integer
# value)
#num_shell_tries = 3

# The percentage of backend capacity reserved. (integer value)
#reserved_share_percentage = 0

# The backend name for a given driver implementation. (string value)
#share_backend_name = <None>

# Name of the configuration group in the Manila conf file to look for
# network config options.If not set, the share backend's config group
# will be used.If an option is not found within provided group,
# then'DEFAULT' group will be used for search of option. (string
# value)
#network_config_group = <None>

# There are two possible approaches for share drivers in Manila. First
# is when share driver is able to handle share-servers and second when
# not. Drivers can support either both or only one of these
# approaches. So, set this opt to True if share driver is able to
# handle share servers and it is desired mode else set False. It is
# set to None by default to make this choice intentional. (boolean
# value)
#driver_handles_share_servers = <None>

# Float representation of the over subscription ratio when thin
# provisioning is involved. Default ratio is 20.0, meaning provisioned
# capacity can be 20 times the total physical capacity. If the ratio
# is 10.5, it means provisioned capacity can be 10.5 times the total
# physical capacity. A ratio of 1.0 means provisioned capacity cannot
# exceed the total physical capacity. A ratio lower than 1.0 is
# invalid. (floating point value)
#max_over_subscription_ratio = 20.0

# Temporary path to create and mount shares during migration. (string
# value)
#migration_tmp_location = /tmp/

# List of files and folders to be ignored when migrating shares. Items
# should be names (not including any path). (list value)
#migration_ignore_files = lost+found

# Time to wait for access rules to be allowed/denied on backends when
# migrating shares using generic approach (seconds). (integer value)
#migration_wait_access_rules_timeout = 90

# Timeout for creating and deleting share instances when performing
# share migration (seconds). (integer value)
#migration_create_delete_share_timeout = 300

# Backend IP in admin network to use for mounting shares during
# migration. (string value)
#migration_mounting_backend_ip = <None>

# The IP of the node responsible for copying data during migration,
# such as the data copy service node, reachable by the backend.
# (string value)
#migration_data_copy_node_ip = <None>

# The command for mounting shares for this backend. Must specifythe
# executable and all necessary parameters for the protocol supported.
# It is advisable to separate protocols per backend. (string value)
#migration_protocol_mount_command = <None>

# Specify whether read only access mode is supported in thisbackend.
# (boolean value)
#migration_readonly_support = true

# Backend server SSH connection timeout. (integer value)
#ssh_conn_timeout = 60

# Minimum number of connections in the SSH pool. (integer value)
#ssh_min_pool_conn = 1

# Maximum number of connections in the SSH pool. (integer value)
#ssh_max_pool_conn = 10

# The full class name of the Private Data Driver class to use. (string
# value)
#drivers_private_storage_class = manila.share.drivers_private_data.SqlStorageDriver

# User name for the EMC server. (string value)
#emc_nas_login = <None>

# Password for the EMC server. (string value)
#emc_nas_password = <None>

# EMC server hostname or IP address. (string value)
#emc_nas_server = <None>

# Port number for the EMC server. (integer value)
#emc_nas_server_port = 8080

# Use secure connection to server. (boolean value)
#emc_nas_server_secure = true

# Share backend. (string value)
#emc_share_backend = <None>

# Container of share servers. (string value)
#emc_nas_server_container = server_2

# EMC pool name. (string value)
#emc_nas_pool_name = <None>

# The root directory where shares will be located. (string value)
#emc_nas_root_dir = <None>

# Path to smb config. (string value)
#smb_template_config_path = $state_path/smb.conf

# Volume name template. (string value)
#volume_name_template = manila-share-%s

# Volume snapshot name template. (string value)
#volume_snapshot_name_template = manila-snapshot-%s

# Parent path in service instance where shares will be mounted.
# (string value)
#share_mount_path = /shares

# Maximum time to wait for creating cinder volume. (integer value)
#max_time_to_create_volume = 180

# Maximum time to wait for extending cinder volume. (integer value)
#max_time_to_extend_volume = 180

# Maximum time to wait for attaching cinder volume. (integer value)
#max_time_to_attach = 120

# Path to SMB config in service instance. (string value)
#service_instance_smb_config_path = $share_mount_path/smb.conf

# Specify list of share export helpers. (list value)
#share_helpers = CIFS=manila.share.drivers.generic.CIFSHelper,NFS=manila.share.drivers.generic.NFSHelper

# Filesystem type of the share volume. (string value)
# Allowed values: ext4, ext3
#share_volume_fstype = ext4

# Name or id of cinder volume type which will be used for all volumes
# created by driver. (string value)
#cinder_volume_type = <None>

# Type of NFS server that mediate access to the Gluster volumes
# (Gluster or Ganesha). (string value)
#glusterfs_nfs_server_type = Gluster

# Remote Ganesha server node's IP address. (string value)
#glusterfs_ganesha_server_ip = <None>

# Remote Ganesha server node's username. (string value)
#glusterfs_ganesha_server_username = root

# Remote Ganesha server node's login password. This is not required if
# 'glusterfs_path_to_private_key' is configured. (string value)
#glusterfs_ganesha_server_password = <None>

# Specifies GlusterFS share layout, that is, the method of associating
# backing GlusterFS resources to shares. (string value)
#glusterfs_share_layout = <None>

# Specifies the GlusterFS volume to be mounted on the Manila host. It
# is of the form [remoteuser@]<volserver>:<volid>. (string value)
#glusterfs_target = <None>

# Base directory containing mount points for Gluster volumes. (string
# value)
#glusterfs_mount_point_base = $state_path/mnt

# Remote GlusterFS server node's login password. This is not required
# if 'glusterfs_path_to_private_key' is configured. (string value)
#glusterfs_server_password = <None>

# Path of Manila host's private SSH key file. (string value)
#glusterfs_path_to_private_key = <None>

# List of GlusterFS servers that can be used to create shares. Each
# GlusterFS server should be of the form [remoteuser@]<volserver>, and
# they are assumed to belong to distinct Gluster clusters. (list
# value)
# Deprecated group/name - [DEFAULT]/glusterfs_targets
#glusterfs_servers =

# Remote GlusterFS server node's login password. This is not required
# if 'glusterfs_native_path_to_private_key' is configured. (string
# value)
#glusterfs_native_server_password = <None>

# Path of Manila host's private SSH key file. (string value)
#glusterfs_native_path_to_private_key = <None>

# Regular expression template used to filter GlusterFS volumes for
# share creation. The regex template can optionally (ie. with support
# of the GlusterFS backend) contain the #{size} parameter which
# matches an integer (sequence of digits) in which case the value
# shall be interpreted as size of the volume in GB. Examples: "manila-
# share-volume-\d+$", "manila-share-volume-#{size}G-\d+$"; with
# matching volume names, respectively: "manila-share-volume-12",
# "manila-share-volume-3G-13". In latter example, the number that
# matches "#{size}", that is, 3, is an indication that the size of
# volume is 3G. (string value)
#glusterfs_volume_pattern = <None>

# The IP of the HDFS namenode. (string value)
#hdfs_namenode_ip = <None>

# The port of HDFS namenode service. (integer value)
#hdfs_namenode_port = 9000

# HDFS namenode SSH port. (integer value)
#hdfs_ssh_port = 22

# HDFS namenode ssh login name. (string value)
#hdfs_ssh_name = <None>

# HDFS namenode SSH login password, This parameter is not necessary,
# if 'hdfs_ssh_private_key' is configured. (string value)
#hdfs_ssh_pw = <None>

# Path to HDFS namenode SSH private key for login. (string value)
#hdfs_ssh_private_key = <None>

# HNAS management interface IP for communication between Manila
# controller and HNAS. (string value)
#hds_hnas_ip = <None>

# HNAS username Base64 String in order to perform tasks such as create
# file-systems and network interfaces. (string value)
#hds_hnas_user = <None>

# HNAS user password. Required only if private key is not provided.
# (string value)
#hds_hnas_password = <None>

# Specify which EVS this backend is assigned to. (string value)
#hds_hnas_evs_id = <None>

# Specify IP for mounting shares. (string value)
#hds_hnas_evs_ip = <None>

# Specify file-system name for creating shares. (string value)
#hds_hnas_file_system_name = <None>

# RSA/DSA private key value used to connect into HNAS. Required only
# if password is not provided. (string value)
#hds_hnas_ssh_private_key = <None>

# The IP of the clusters admin node. Only set in HNAS multinode
# clusters. (string value)
#hds_hnas_cluster_admin_ip0 = <None>

# The time (in seconds) to wait for stalled HNAS jobs before aborting.
# (integer value)
#hds_hnas_stalled_job_timeout = 30

# 3PAR WSAPI Server Url like https://<3par ip>:8080/api/v1 (string
# value)
#hp3par_api_url =

# 3PAR username with the 'edit' role (string value)
#hp3par_username =

# 3PAR password for the user specified in hp3par_username (string
# value)
#hp3par_password =

# IP address of SAN controller (string value)
#hp3par_san_ip =

# Username for SAN controller (string value)
#hp3par_san_login =

# Password for SAN controller (string value)
#hp3par_san_password =

# SSH port to use with SAN (integer value)
#hp3par_san_ssh_port = 22

# The File Provisioning Group (FPG) to use (string value)
#hp3par_fpg = OpenStack

# The IP address for shares not using a share server (string value)
#hp3par_share_ip_address =

# Use one filestore per share (boolean value)
#hp3par_fstore_per_share = false

# Enable HTTP debugging to 3PAR (boolean value)
#hp3par_debug = false

# The configuration file for the Manila Huawei driver. (string value)
#manila_huawei_conf_file = /etc/manila/manila_huawei_conf.xml

# The storage family type used on the storage system; valid values
# include ontap_cluster for using clustered Data ONTAP. (string value)
#netapp_storage_family = ontap_cluster

# The hostname (or IP address) for the storage system. (string value)
# Deprecated group/name - [DEFAULT]/netapp_nas_server_hostname
#netapp_server_hostname = <None>

# The TCP port to use for communication with the storage system or
# proxy server. If not specified, Data ONTAP drivers will use 80 for
# HTTP and 443 for HTTPS. (integer value)
#netapp_server_port = <None>

# The transport protocol used when communicating with the storage
# system or proxy server. Valid values are http or https. (string
# value)
# Deprecated group/name - [DEFAULT]/netapp_nas_transport_type
#netapp_transport_type = http

# Administrative user account name used to access the storage system.
# (string value)
# Deprecated group/name - [DEFAULT]/netapp_nas_login
#netapp_login = <None>

# Password for the administrative user account specified in the
# netapp_login option. (string value)
# Deprecated group/name - [DEFAULT]/netapp_nas_password
#netapp_password = <None>

# NetApp volume name template. (string value)
# Deprecated group/name - [DEFAULT]/netapp_nas_volume_name_template
#netapp_volume_name_template = share_%(share_id)s

# Name template to use for new Vserver. (string value)
#netapp_vserver_name_template = os_%s

# Pattern for overriding the selection of network ports on which to
# create Vserver LIFs. (string value)
#netapp_port_name_search_pattern = (.*)

# Logical interface (LIF) name template (string value)
#netapp_lif_name_template = os_%(net_allocation_id)s

# Pattern for searching available aggregates for provisioning. (string
# value)
#netapp_aggregate_name_search_pattern = (.*)

# Name of aggregate to create Vserver root volumes on. This option
# only applies when the option driver_handles_share_servers is set to
# True. (string value)
#netapp_root_volume_aggregate = <None>

# Root volume name. (string value)
# Deprecated group/name - [DEFAULT]/netapp_root_volume_name
#netapp_root_volume = root

# URL of the Quobyte API server (http or https) (string value)
#quobyte_api_url = <None>

# The X.509 CA file to verify the server cert. (string value)
#quobyte_api_ca = <None>

# Actually deletes shares (vs. unexport) (boolean value)
#quobyte_delete_shares = false

# Username for Quobyte API server. (string value)
#quobyte_api_username = admin

# Password for Quobyte API server (string value)
#quobyte_api_password = quobyte

# Name of volume configuration used for new shares. (string value)
#quobyte_volume_configuration = BASE

# Default owning user for new volumes. (string value)
#quobyte_default_volume_user = root

# Default owning group for new volumes. (string value)
#quobyte_default_volume_group = root

# User in service instance that will be used for authentication.
# (string value)
#service_instance_user = <None>

# Password for service instance user. (string value)
#service_instance_password = <None>

# Path to host's private key. (string value)
#path_to_private_key = ~/.ssh/id_rsa

# Maximum time in seconds to wait for creating service instance.
# (integer value)
#max_time_to_build_instance = 300

# Name or ID of service instance in Nova to use for share exports.
# Used only when share servers handling is disabled. (string value)
#service_instance_name_or_id = <None>

# Can be either name of network that is used by service instance
# within Nova to get IP address or IP address itself for managing
# shares there. Used only when share servers handling is disabled.
# (string value)
#service_net_name_or_ip = <None>

# Can be either name of network that is used by service instance
# within Nova to get IP address or IP address itself for exporting
# shares. Used only when share servers handling is disabled. (string
# value)
#tenant_net_name_or_ip = <None>

# Name of image in Glance, that will be used for service instance
# creation. (string value)
#service_image_name = manila-service-image

# Name of service instance. (string value)
#service_instance_name_template = manila_service_instance_%s

# Keypair name that will be created and used for service instances.
# (string value)
#manila_service_keypair_name = manila-service

# Path to hosts public key. (string value)
#path_to_public_key = ~/.ssh/id_rsa.pub

# Security group name, that will be used for service instance
# creation. (string value)
#service_instance_security_group = manila-service

# ID of flavor, that will be used for service instance creation.
# (integer value)
#service_instance_flavor_id = 100

# Name of manila service network. Used only with Neutron. (string
# value)
#service_network_name = manila_service_network

# CIDR of manila service network. Used only with Neutron. (string
# value)
#service_network_cidr = 10.254.0.0/16

# This mask is used for dividing service network into subnets, IP
# capacity of subnet with this mask directly defines possible amount
# of created service VMs per tenant's subnet. Used only with Neutron.
# (integer value)
#service_network_division_mask = 28

# Vif driver. Used only with Neutron. (string value)
#interface_driver = manila.network.linux.interface.OVSInterfaceDriver

# Attach share server directly to share network. Used only with
# Neutron. (boolean value)
#connect_share_server_to_tenant_network = false

# Allowed values are ['nova', 'neutron']. (string value)
#service_instance_network_helper_type = neutron

# Path to the x509 certificate used for accessing the serviceinstance.
# (string value)
#winrm_cert_pem_path = ~/.ssl/cert.pem

# Path to the x509 certificate key. (string value)
#winrm_cert_key_pem_path = ~/.ssl/key.pem

# Use x509 certificates in order to authenticate to theservice
# instance. (boolean value)
#winrm_use_cert_based_auth = false

# WinRM connection timeout. (integer value)
#winrm_conn_timeout = 60

# WinRM operation timeout. (integer value)
#winrm_operation_timeout = 60

# WinRM retry count. (integer value)
#winrm_retry_count = 3

# WinRM retry interval in seconds (integer value)
#winrm_retry_interval = 5

# ZFSSA management IP address. (string value)
#zfssa_host = <None>

# IP address for data. (string value)
#zfssa_data_ip = <None>

# ZFSSA management authorized username. (string value)
#zfssa_auth_user = <None>

# ZFSSA management authorized userpassword. (string value)
#zfssa_auth_password = <None>

# ZFSSA storage pool name. (string value)
#zfssa_pool = <None>

# ZFSSA project name. (string value)
#zfssa_project = <None>

# Controls checksum used for data blocks. (string value)
#zfssa_nas_checksum = fletcher4

# Data compression-off, lzjb, gzip-2, gzip, gzip-9. (string value)
#zfssa_nas_compression = off

# Controls behavior when servicing synchronous writes. (string value)
#zfssa_nas_logbias = latency

# Location of project in ZFS/SA. (string value)
#zfssa_nas_mountpoint =

# Controls whether a share quota includes snapshot. (string value)
#zfssa_nas_quota_snap = true

# Controls whether file ownership can be changed. (string value)
#zfssa_nas_rstchown = true

# Controls whether the share is scanned for viruses. (string value)
#zfssa_nas_vscan = false

# REST connection timeout (in seconds). (string value)
#zfssa_rest_timeout = <None>

# Whether to enable pre hooks or not. (boolean value)
# Deprecated group/name - [DEFAULT]/enable_pre_hooks
#enable_pre_hooks = false

# Whether to enable post hooks or not. (boolean value)
# Deprecated group/name - [DEFAULT]/enable_post_hooks
#enable_post_hooks = false

# Whether to enable periodic hooks or not. (boolean value)
# Deprecated group/name - [DEFAULT]/enable_periodic_hooks
#enable_periodic_hooks = false

# Whether to suppress pre hook errors (allow driver perform actions)
# or not. (boolean value)
# Deprecated group/name - [DEFAULT]/suppress_pre_hooks_errors
#suppress_pre_hooks_errors = false

# Whether to suppress post hook errors (allow driver's results to pass
# through) or not. (boolean value)
# Deprecated group/name - [DEFAULT]/suppress_post_hooks_errors
#suppress_post_hooks_errors = false

# Interval in seconds between execution of periodic hooks. Used when
# option 'enable_periodic_hooks' is set to True. Default is 300.
# (floating point value)
# Deprecated group/name - [DEFAULT]/periodic_hooks_interval
#periodic_hooks_interval = 300.0

# Driver to use for share creation. (string value)
#share_driver = manila.share.drivers.generic.GenericShareDriver

# Driver(s) to perform some additional actions before and after share
# driver actions and on a periodic basis. Default is []. (list value)
# Deprecated group/name - [DEFAULT]/hook_drivers
#hook_drivers =

# Whether share servers will be deleted on deletion of the last share.
# (boolean value)
#delete_share_server_with_last_share = false

# If set to True, then manila will deny access and remove all access
# rules on share unmanage.If set to False - nothing will be changed.
# (boolean value)
#unmanage_remove_access_rules = false

# If set to True, then Manila will delete all share servers which were
# unused more than specified time .If set to False - automatic
# deletion of share servers will be disabled. (boolean value)
# Deprecated group/name - [DEFAULT]/automatic_share_server_cleanup
#automatic_share_server_cleanup = true

# Unallocated share servers reclamation time interval (minutes).
# Minimum value is 10 minutes, maximum is 60 minutes. The reclamation
# function is run every 10 minutes and delete share servers which were
# unused more than unused_share_server_cleanup_interval option
# defines. This value reflects the shortest time Manila will wait for
# a share server to go unutilized before deleting it. (integer value)
# Deprecated group/name - [DEFAULT]/unused_share_server_cleanup_interval
#unused_share_server_cleanup_interval = 10

# The full class name of the Volume API class to use. (string value)
#volume_api_class = manila.volume.cinder.API

# Info to match when looking for cinder in the service catalog. Format
# is separated values of the form:
# <service_type>:<service_name>:<endpoint_type> (string value)
#cinder_catalog_info = volume:cinder:publicURL

# Region name of this node. (string value)
#os_region_name = <None>

# Location of CA certificates file to use for cinder client requests.
# (string value)
#cinder_ca_certificates_file = <None>

# Number of cinderclient retries on failed HTTP calls. (integer value)
#cinder_http_retries = 3

# Allow to perform insecure SSL requests to cinder. (boolean value)
#cinder_api_insecure = false

# Allow attaching between instances and volumes in different
# availability zones. (boolean value)
#cinder_cross_az_attach = true

# Cinder admin username. (string value)
#cinder_admin_username = cinder

# Cinder admin password. (string value)
#cinder_admin_password = <None>

# Cinder admin tenant name. (string value)
#cinder_admin_tenant_name = service

# Identity service URL. (string value)
#cinder_admin_auth_url = http://localhost:5000/v2.0

# Maximum line size of message headers to be accepted. Option
# max_header_line may need to be increased when using large tokens
# (typically those generated by the Keystone v3 API with big service
# catalogs). (integer value)
#max_header_line = 16384

# Timeout for client connections socket operations. If an incoming
# connection is idle for this number of seconds it will be closed. A
# value of '0' means wait forever. (integer value)
#client_socket_timeout = 900

# If False, closes the client socket connection explicitly. Setting it
# to True to maintain backward compatibility. Recommended setting is
# set it to False. (boolean value)
#wsgi_keep_alive = true

# Number of backlog requests to configure the socket with. (integer
# value)
#backlog = 4096

# Sets the value of TCP_KEEPALIVE (True/False) for each server socket.
# (boolean value)
#tcp_keepalive = true

# Sets the value of TCP_KEEPIDLE in seconds for each server socket.
# Not supported on OS X. (integer value)
#tcp_keepidle = 600

# Sets the value of TCP_KEEPINTVL in seconds for each server socket.
# Not supported on OS X. (integer value)
#tcp_keepalive_interval = <None>

# Sets the value of TCP_KEEPCNT for each server socket. Not supported
# on OS X. (integer value)
#tcp_keepalive_count = <None>

# CA certificate file to use to verify connecting clients. (string
# value)
#ssl_ca_file = <None>

# Certificate file to use when starting the server securely. (string
# value)
#ssl_cert_file = <None>

# Private key file to use when starting the server securely. (string
# value)
#ssl_key_file = <None>

#
# From manila
#

# Print debugging output (set logging level to DEBUG instead of
# default INFO level). (boolean value)
#debug = false

# If set to false, will disable INFO logging level, making WARNING the
# default. (boolean value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#verbose = true

# The name of a logging configuration file. This file is appended to
# any existing logging configuration files. For details about logging
# configuration files, see the Python logging module documentation.
# (string value)
# Deprecated group/name - [DEFAULT]/log_config
#log_config_append = <None>

# DEPRECATED. A logging.Formatter log message format string which may
# use any of the available logging.LogRecord attributes. This option
# is deprecated.  Please use logging_context_format_string and
# logging_default_format_string instead. (string value)
#log_format = <None>

# Format string for %%(asctime)s in log records. Default: %(default)s
# . (string value)
#log_date_format = %Y-%m-%d %H:%M:%S

# (Optional) Name of log file to output to. If no default is set,
# logging will go to stdout. (string value)
# Deprecated group/name - [DEFAULT]/logfile
#log_file = <None>

# (Optional) The base directory used for relative --log-file paths.
# (string value)
# Deprecated group/name - [DEFAULT]/logdir
#log_dir = <None>

# Use syslog for logging. Existing syslog format is DEPRECATED and
# will be changed later to honor RFC5424. (boolean value)
#use_syslog = false

# (Optional) Enables or disables syslog rfc5424 format for logging. If
# enabled, prefixes the MSG part of the syslog message with APP-NAME
# (RFC5424). The format without the APP-NAME is deprecated in Kilo,
# and will be removed in Mitaka, along with this option. (boolean
# value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#use_syslog_rfc_format = true

# Syslog facility to receive log lines. (string value)
#syslog_log_facility = LOG_USER

# Log output to standard error. (boolean value)
#use_stderr = true

# Format string to use for log messages with context. (string value)
#logging_context_format_string = %(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [%(request_id)s %(user_identity)s] %(instance)s%(message)s

# Format string to use for log messages without context. (string
# value)
#logging_default_format_string = %(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [-] %(instance)s%(message)s

# Data to append to log format when level is DEBUG. (string value)
#logging_debug_format_suffix = %(funcName)s %(pathname)s:%(lineno)d

# Prefix each line of exception output with this format. (string
# value)
#logging_exception_prefix = %(asctime)s.%(msecs)03d %(process)d ERROR %(name)s %(instance)s

# List of logger=LEVEL pairs. (list value)
#default_log_levels = amqp=WARN,amqplib=WARN,boto=WARN,qpid=WARN,sqlalchemy=WARN,suds=INFO,oslo.messaging=INFO,iso8601=WARN,requests.packages.urllib3.connectionpool=WARN,urllib3.connectionpool=WARN,websocket=WARN,requests.packages.urllib3.util.retry=WARN,urllib3.util.retry=WARN,keystonemiddleware=WARN,routes.middleware=WARN,stevedore=WARN,taskflow=WARN

# Enables or disables publication of error events. (boolean value)
#publish_errors = false

# The format for an instance that is passed with the log message.
# (string value)
#instance_format = "[instance: %(uuid)s] "

# The format for an instance UUID that is passed with the log message.
# (string value)
#instance_uuid_format = "[instance: %(uuid)s] "

# Enables or disables fatal status of deprecations. (boolean value)
#fatal_deprecations = false

#
# From oslo.messaging
#

# Size of RPC connection pool. (integer value)
# Deprecated group/name - [DEFAULT]/rpc_conn_pool_size
#rpc_conn_pool_size = 30

# ZeroMQ bind address. Should be a wildcard (*), an ethernet
# interface, or IP. The "host" option should point or resolve to this
# address. (string value)
#rpc_zmq_bind_address = *

# MatchMaker driver. (string value)
#rpc_zmq_matchmaker = local

# ZeroMQ receiver listening port. (integer value)
#rpc_zmq_port = 9501

# Number of ZeroMQ contexts, defaults to 1. (integer value)
#rpc_zmq_contexts = 1

# Maximum number of ingress messages to locally buffer per topic.
# Default is unlimited. (integer value)
#rpc_zmq_topic_backlog = <None>

# Directory for holding IPC sockets. (string value)
#rpc_zmq_ipc_dir = /var/run/openstack

# Name of this node. Must be a valid hostname, FQDN, or IP address.
# Must match "host" option, if running Nova. (string value)
#rpc_zmq_host = localhost

# Seconds to wait before a cast expires (TTL). Only supported by
# impl_zmq. (integer value)
#rpc_cast_timeout = 30

# Heartbeat frequency. (integer value)
#matchmaker_heartbeat_freq = 300

# Heartbeat time-to-live. (integer value)
#matchmaker_heartbeat_ttl = 600

# Size of executor thread pool. (integer value)
# Deprecated group/name - [DEFAULT]/rpc_thread_pool_size
#executor_thread_pool_size = 64

# The Drivers(s) to handle sending notifications. Possible values are
# messaging, messagingv2, routing, log, test, noop (multi valued)
#notification_driver =

# AMQP topic used for OpenStack notifications. (list value)
# Deprecated group/name - [rpc_notifier2]/topics
#notification_topics = notifications

# Seconds to wait for a response from a call. (integer value)
#rpc_response_timeout = 60

# A URL representing the messaging driver to use and its full
# configuration. If not set, we fall back to the rpc_backend option
# and driver specific configuration. (string value)
#transport_url = <None>

# The messaging driver to use, defaults to rabbit. Other drivers
# include qpid and zmq. (string value)
#rpc_backend = rabbit

# The default exchange under which topics are scoped. May be
# overridden by an exchange name specified in the transport_url
# option. (string value)
#control_exchange = openstack


[cors]

#
# From manila
#

# Indicate whether this resource may be shared with the domain
# received in the requests "origin" header. (string value)
#allowed_origin = <None>

# Indicate that the actual request can include user credentials
# (boolean value)
allow_credentials = true

# Indicate which headers are safe to expose to the API. Defaults to
# HTTP Simple Headers. (list value)
#expose_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma

# Maximum cache age of CORS preflight requests. (integer value)
#max_age = 3600

# Indicate which methods can be used during the actual request. (list
# value)
#allow_methods = GET,POST,PUT,DELETE,OPTIONS

# Indicate which header field names may be used during the actual
# request. (list value)
#allow_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma


[cors.subdomain]

#
# From manila
#

# Indicate whether this resource may be shared with the domain
# received in the requests "origin" header. (string value)
#allowed_origin = <None>

# Indicate that the actual request can include user credentials
# (boolean value)
#allow_credentials = true

# Indicate which headers are safe to expose to the API. Defaults to
# HTTP Simple Headers. (list value)
#expose_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma

# Maximum cache age of CORS preflight requests. (integer value)
#max_age = 3600

# Indicate which methods can be used during the actual request. (list
# value)
#allow_methods = GET,POST,PUT,DELETE,OPTIONS

# Indicate which header field names may be used during the actual
# request. (list value)
#allow_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma


[database]

#
# From oslo.db
#

# The file name to use with SQLite. (string value)
# Deprecated group/name - [DEFAULT]/sqlite_db
#sqlite_db = oslo.sqlite

# If True, SQLite uses synchronous mode. (boolean value)
# Deprecated group/name - [DEFAULT]/sqlite_synchronous
#sqlite_synchronous = true

# The back end to use for the database. (string value)
# Deprecated group/name - [DEFAULT]/db_backend
#backend = sqlalchemy

# The SQLAlchemy connection string to use to connect to the database.
# (string value)
# Deprecated group/name - [DEFAULT]/sql_connection
# Deprecated group/name - [DATABASE]/sql_connection
# Deprecated group/name - [sql]/connection
#connection = <None>

# The SQLAlchemy connection string to use to connect to the slave
# database. (string value)
#slave_connection = <None>

# The SQL mode to be used for MySQL sessions. This option, including
# the default, overrides any server-set SQL mode. To use whatever SQL
# mode is set by the server configuration, set this to no value.
# Example: mysql_sql_mode= (string value)
#mysql_sql_mode = TRADITIONAL

# Timeout before idle SQL connections are reaped. (integer value)
# Deprecated group/name - [DEFAULT]/sql_idle_timeout
# Deprecated group/name - [DATABASE]/sql_idle_timeout
# Deprecated group/name - [sql]/idle_timeout
#idle_timeout = 3600

# Minimum number of SQL connections to keep open in a pool. (integer
# value)
# Deprecated group/name - [DEFAULT]/sql_min_pool_size
# Deprecated group/name - [DATABASE]/sql_min_pool_size
#min_pool_size = 1

# Maximum number of SQL connections to keep open in a pool. (integer
# value)
# Deprecated group/name - [DEFAULT]/sql_max_pool_size
# Deprecated group/name - [DATABASE]/sql_max_pool_size
#max_pool_size = <None>

# Maximum number of database connection retries during startup. Set to
# -1 to specify an infinite retry count. (integer value)
# Deprecated group/name - [DEFAULT]/sql_max_retries
# Deprecated group/name - [DATABASE]/sql_max_retries
#max_retries = 10

# Interval between retries of opening a SQL connection. (integer
# value)
# Deprecated group/name - [DEFAULT]/sql_retry_interval
# Deprecated group/name - [DATABASE]/reconnect_interval
#retry_interval = 10

# If set, use this value for max_overflow with SQLAlchemy. (integer
# value)
# Deprecated group/name - [DEFAULT]/sql_max_overflow
# Deprecated group/name - [DATABASE]/sqlalchemy_max_overflow
#max_overflow = <None>

# Verbosity of SQL debugging information: 0=None, 100=Everything.
# (integer value)
# Deprecated group/name - [DEFAULT]/sql_connection_debug
#connection_debug = 0

# Add Python stack traces to SQL as comment strings. (boolean value)
# Deprecated group/name - [DEFAULT]/sql_connection_trace
#connection_trace = false

# If set, use this value for pool_timeout with SQLAlchemy. (integer
# value)
# Deprecated group/name - [DATABASE]/sqlalchemy_pool_timeout
#pool_timeout = <None>

# Enable the experimental use of database reconnect on connection
# lost. (boolean value)
#use_db_reconnect = false

# Seconds between retries of a database transaction. (integer value)
#db_retry_interval = 1

# If True, increases the interval between retries of a database
# operation up to db_max_retry_interval. (boolean value)
#db_inc_retry_interval = true

# If db_inc_retry_interval is set, the maximum seconds between retries
# of a database operation. (integer value)
#db_max_retry_interval = 10

# Maximum retries in case of connection error or deadlock error before
# error is raised. Set to -1 to specify an infinite retry count.
# (integer value)
#db_max_retries = 20

#
# From oslo.db.concurrency
#

# Enable the experimental use of thread pooling for all DB API calls
# (boolean value)
# Deprecated group/name - [DEFAULT]/dbapi_use_tpool
#use_tpool = false


[keystone_authtoken]

#
# From keystonemiddleware.auth_token
#

# Complete public Identity API endpoint. (string value)
#auth_uri = <None>

# API version of the admin Identity API endpoint. (string value)
#auth_version = <None>

# Do not handle authorization requests within the middleware, but
# delegate the authorization decision to downstream WSGI components.
# (boolean value)
#delay_auth_decision = false

# Request timeout value for communicating with Identity API server.
# (integer value)
#http_connect_timeout = <None>

# How many times are we trying to reconnect when communicating with
# Identity API Server. (integer value)
#http_request_max_retries = 3

# Env key for the swift cache. (string value)
#cache = <None>

# Required if identity server requires client certificate (string
# value)
#certfile = <None>

# Required if identity server requires client certificate (string
# value)
#keyfile = <None>

# A PEM encoded Certificate Authority to use when verifying HTTPs
# connections. Defaults to system CAs. (string value)
#cafile = <None>

# Verify HTTPS connections. (boolean value)
#insecure = false

# The region in which the identity server can be found. (string value)
#region_name = <None>

# Directory used to cache files related to PKI tokens. (string value)
#signing_dir = <None>

# Optionally specify a list of memcached server(s) to use for caching.
# If left undefined, tokens will instead be cached in-process. (list
# value)
# Deprecated group/name - [DEFAULT]/memcache_servers
#memcached_servers = <None>

# In order to prevent excessive effort spent validating tokens, the
# middleware caches previously-seen tokens for a configurable duration
# (in seconds). Set to -1 to disable caching completely. (integer
# value)
#token_cache_time = 300

# Determines the frequency at which the list of revoked tokens is
# retrieved from the Identity service (in seconds). A high number of
# revocation events combined with a low cache duration may
# significantly reduce performance. (integer value)
#revocation_cache_time = 10

# (Optional) If defined, indicate whether token data should be
# authenticated or authenticated and encrypted. Acceptable values are
# MAC or ENCRYPT.  If MAC, token data is authenticated (with HMAC) in
# the cache. If ENCRYPT, token data is encrypted and authenticated in
# the cache. If the value is not one of these options or empty,
# auth_token will raise an exception on initialization. (string value)
#memcache_security_strategy = <None>

# (Optional, mandatory if memcache_security_strategy is defined) This
# string is used for key derivation. (string value)
#memcache_secret_key = <None>

# (Optional) Number of seconds memcached server is considered dead
# before it is tried again. (integer value)
#memcache_pool_dead_retry = 300

# (Optional) Maximum total number of open connections to every
# memcached server. (integer value)
#memcache_pool_maxsize = 10

# (Optional) Socket timeout in seconds for communicating with a
# memcached server. (integer value)
#memcache_pool_socket_timeout = 3

# (Optional) Number of seconds a connection to memcached is held
# unused in the pool before it is closed. (integer value)
#memcache_pool_unused_timeout = 60

# (Optional) Number of seconds that an operation will wait to get a
# memcached client connection from the pool. (integer value)
#memcache_pool_conn_get_timeout = 10

# (Optional) Use the advanced (eventlet safe) memcached client pool.
# The advanced pool will only work under python 2.x. (boolean value)
#memcache_use_advanced_pool = false

# (Optional) Indicate whether to set the X-Service-Catalog header. If
# False, middleware will not ask for service catalog on token
# validation and will not set the X-Service-Catalog header. (boolean
# value)
#include_service_catalog = true

# Used to control the use and type of token binding. Can be set to:
# "disabled" to not check token binding. "permissive" (default) to
# validate binding information if the bind type is of a form known to
# the server and ignore it if not. "strict" like "permissive" but if
# the bind type is unknown the token will be rejected. "required" any
# form of token binding is needed to be allowed. Finally the name of a
# binding method that must be present in tokens. (string value)
#enforce_token_bind = permissive

# If true, the revocation list will be checked for cached tokens. This
# requires that PKI tokens are configured on the identity server.
# (boolean value)
#check_revocations_for_cached = false

# Hash algorithms to use for hashing PKI tokens. This may be a single
# algorithm or multiple. The algorithms are those supported by Python
# standard hashlib.new(). The hashes will be tried in the order given,
# so put the preferred one first for performance. The result of the
# first hash will be stored in the cache. This will typically be set
# to multiple values only while migrating from a less secure algorithm
# to a more secure one. Once all the old tokens are expired this
# option should be set to a single value for better performance. (list
# value)
#hash_algorithms = md5

# Prefix to prepend at the beginning of the path. Deprecated, use
# identity_uri. (string value)
#auth_admin_prefix =

# Host providing the admin Identity API endpoint. Deprecated, use
# identity_uri. (string value)
#auth_host = 127.0.0.1

# Port of the admin Identity API endpoint. Deprecated, use
# identity_uri. (integer value)
#auth_port = 35357

# Protocol of the admin Identity API endpoint (http or https).
# Deprecated, use identity_uri. (string value)
#auth_protocol = https

# Complete admin Identity API endpoint. This should specify the
# unversioned root endpoint e.g. https://localhost:35357/ (string
# value)
#identity_uri = <None>

# This option is deprecated and may be removed in a future release.
# Single shared secret with the Keystone configuration used for
# bootstrapping a Keystone installation, or otherwise bypassing the
# normal authentication process. This option should not be used, use
# `admin_user` and `admin_password` instead. (string value)
#admin_token = <None>

# Service username. (string value)
#admin_user = <None>

# Service user password. (string value)
#admin_password = <None>

# Service tenant name. (string value)
#admin_tenant_name = admin


[matchmaker_redis]

#
# From oslo.messaging
#

# Host to locate redis. (string value)
#host = 127.0.0.1

# Use this port to connect to redis host. (integer value)
#port = 6379

# Password for Redis server (optional). (string value)
#password = <None>


[matchmaker_ring]

#
# From oslo.messaging
#

# Matchmaker ring file (JSON). (string value)
# Deprecated group/name - [DEFAULT]/matchmaker_ringfile
#ringfile = /etc/oslo/matchmaker_ring.json


[oslo_concurrency]

#
# From manila
#

# Enables or disables inter-process locks. (boolean value)
# Deprecated group/name - [DEFAULT]/disable_process_locking
#disable_process_locking = false

# Directory to use for lock files.  For security, the specified
# directory should only be writable by the user running the processes
# that need locking. Defaults to environment variable OSLO_LOCK_PATH.
# If external locks are used, a lock path must be set. (string value)
# Deprecated group/name - [DEFAULT]/lock_path
#lock_path = <None>


[oslo_messaging_amqp]

#
# From oslo.messaging
#

# address prefix used when sending to a specific server (string value)
# Deprecated group/name - [amqp1]/server_request_prefix
#server_request_prefix = exclusive

# address prefix used when broadcasting to all servers (string value)
# Deprecated group/name - [amqp1]/broadcast_prefix
#broadcast_prefix = broadcast

# address prefix when sending to any server in group (string value)
# Deprecated group/name - [amqp1]/group_request_prefix
#group_request_prefix = unicast

# Name for the AMQP container (string value)
# Deprecated group/name - [amqp1]/container_name
#container_name = <None>

# Timeout for inactive connections (in seconds) (integer value)
# Deprecated group/name - [amqp1]/idle_timeout
#idle_timeout = 0

# Debug: dump AMQP frames to stdout (boolean value)
# Deprecated group/name - [amqp1]/trace
#trace = false

# CA certificate PEM file to verify server certificate (string value)
# Deprecated group/name - [amqp1]/ssl_ca_file
#ssl_ca_file =

# Identifying certificate PEM file to present to clients (string
# value)
# Deprecated group/name - [amqp1]/ssl_cert_file
#ssl_cert_file =

# Private key PEM file used to sign cert_file certificate (string
# value)
# Deprecated group/name - [amqp1]/ssl_key_file
#ssl_key_file =

# Password for decrypting ssl_key_file (if encrypted) (string value)
# Deprecated group/name - [amqp1]/ssl_key_password
#ssl_key_password = <None>

# Accept clients using either SSL or plain TCP (boolean value)
# Deprecated group/name - [amqp1]/allow_insecure_clients
#allow_insecure_clients = false


[oslo_messaging_qpid]

#
# From oslo.messaging
#

# Use durable queues in AMQP. (boolean value)
# Deprecated group/name - [DEFAULT]/amqp_durable_queues
# Deprecated group/name - [DEFAULT]/rabbit_durable_queues
#amqp_durable_queues = false

# Auto-delete queues in AMQP. (boolean value)
# Deprecated group/name - [DEFAULT]/amqp_auto_delete
#amqp_auto_delete = false

# Send a single AMQP reply to call message. The current behaviour
# since oslo-incubator is to send two AMQP replies - first one with
# the payload, a second one to ensure the other have finish to send
# the payload. We are going to remove it in the N release, but we must
# keep backward compatible at the same time. This option provides such
# compatibility - it defaults to False in Liberty and can be turned on
# for early adopters with a new installations or for testing. Please
# note, that this option will be removed in the Mitaka release.
# (boolean value)
#send_single_reply = false

# Qpid broker hostname. (string value)
# Deprecated group/name - [DEFAULT]/qpid_hostname
#qpid_hostname = localhost

# Qpid broker port. (integer value)
# Deprecated group/name - [DEFAULT]/qpid_port
#qpid_port = 5672

# Qpid HA cluster host:port pairs. (list value)
# Deprecated group/name - [DEFAULT]/qpid_hosts
#qpid_hosts = $qpid_hostname:$qpid_port

# Username for Qpid connection. (string value)
# Deprecated group/name - [DEFAULT]/qpid_username
#qpid_username =

# Password for Qpid connection. (string value)
# Deprecated group/name - [DEFAULT]/qpid_password
#qpid_password =

# Space separated list of SASL mechanisms to use for auth. (string
# value)
# Deprecated group/name - [DEFAULT]/qpid_sasl_mechanisms
#qpid_sasl_mechanisms =

# Seconds between connection keepalive heartbeats. (integer value)
# Deprecated group/name - [DEFAULT]/qpid_heartbeat
#qpid_heartbeat = 60

# Transport to use, either 'tcp' or 'ssl'. (string value)
# Deprecated group/name - [DEFAULT]/qpid_protocol
#qpid_protocol = tcp

# Whether to disable the Nagle algorithm. (boolean value)
# Deprecated group/name - [DEFAULT]/qpid_tcp_nodelay
#qpid_tcp_nodelay = true

# The number of prefetched messages held by receiver. (integer value)
# Deprecated group/name - [DEFAULT]/qpid_receiver_capacity
#qpid_receiver_capacity = 1

# The qpid topology version to use.  Version 1 is what was originally
# used by impl_qpid.  Version 2 includes some backwards-incompatible
# changes that allow broker federation to work.  Users should update
# to version 2 when they are able to take everything down, as it
# requires a clean break. (integer value)
# Deprecated group/name - [DEFAULT]/qpid_topology_version
#qpid_topology_version = 1


[oslo_messaging_rabbit]

#
# From oslo.messaging
#

# Use durable queues in AMQP. (boolean value)
# Deprecated group/name - [DEFAULT]/amqp_durable_queues
# Deprecated group/name - [DEFAULT]/rabbit_durable_queues
#amqp_durable_queues = false

# Auto-delete queues in AMQP. (boolean value)
# Deprecated group/name - [DEFAULT]/amqp_auto_delete
#amqp_auto_delete = false

# Send a single AMQP reply to call message. The current behaviour
# since oslo-incubator is to send two AMQP replies - first one with
# the payload, a second one to ensure the other have finish to send
# the payload. We are going to remove it in the N release, but we must
# keep backward compatible at the same time. This option provides such
# compatibility - it defaults to False in Liberty and can be turned on
# for early adopters with a new installations or for testing. Please
# note, that this option will be removed in the Mitaka release.
# (boolean value)
#send_single_reply = false

# SSL version to use (valid only if SSL enabled). Valid values are
# TLSv1 and SSLv23. SSLv2, SSLv3, TLSv1_1, and TLSv1_2 may be
# available on some distributions. (string value)
# Deprecated group/name - [DEFAULT]/kombu_ssl_version
#kombu_ssl_version =

# SSL key file (valid only if SSL enabled). (string value)
# Deprecated group/name - [DEFAULT]/kombu_ssl_keyfile
#kombu_ssl_keyfile =

# SSL cert file (valid only if SSL enabled). (string value)
# Deprecated group/name - [DEFAULT]/kombu_ssl_certfile
#kombu_ssl_certfile =

# SSL certification authority file (valid only if SSL enabled).
# (string value)
# Deprecated group/name - [DEFAULT]/kombu_ssl_ca_certs
#kombu_ssl_ca_certs =

# How long to wait before reconnecting in response to an AMQP consumer
# cancel notification. (floating point value)
# Deprecated group/name - [DEFAULT]/kombu_reconnect_delay
#kombu_reconnect_delay = 1.0

# How long to wait before considering a reconnect attempt to have
# failed. This value should not be longer than rpc_response_timeout.
# (integer value)
#kombu_reconnect_timeout = 60

# The RabbitMQ broker address where a single node is used. (string
# value)
# Deprecated group/name - [DEFAULT]/rabbit_host
#rabbit_host = localhost

# The RabbitMQ broker port where a single node is used. (integer
# value)
# Deprecated group/name - [DEFAULT]/rabbit_port
#rabbit_port = 5672

# RabbitMQ HA cluster host:port pairs. (list value)
# Deprecated group/name - [DEFAULT]/rabbit_hosts
#rabbit_hosts = $rabbit_host:$rabbit_port

# Connect over SSL for RabbitMQ. (boolean value)
# Deprecated group/name - [DEFAULT]/rabbit_use_ssl
#rabbit_use_ssl = false

# The RabbitMQ userid. (string value)
# Deprecated group/name - [DEFAULT]/rabbit_userid
#rabbit_userid = guest

# The RabbitMQ password. (string value)
# Deprecated group/name - [DEFAULT]/rabbit_password
#rabbit_password = guest

# The RabbitMQ login method. (string value)
# Deprecated group/name - [DEFAULT]/rabbit_login_method
#rabbit_login_method = AMQPLAIN

# The RabbitMQ virtual host. (string value)
# Deprecated group/name - [DEFAULT]/rabbit_virtual_host
#rabbit_virtual_host = /

# How frequently to retry connecting with RabbitMQ. (integer value)
#rabbit_retry_interval = 1

# How long to backoff for between retries when connecting to RabbitMQ.
# (integer value)
# Deprecated group/name - [DEFAULT]/rabbit_retry_backoff
#rabbit_retry_backoff = 2

# Maximum number of RabbitMQ connection retries. Default is 0
# (infinite retry count). (integer value)
# Deprecated group/name - [DEFAULT]/rabbit_max_retries
#rabbit_max_retries = 0

# Use HA queues in RabbitMQ (x-ha-policy: all). If you change this
# option, you must wipe the RabbitMQ database. (boolean value)
# Deprecated group/name - [DEFAULT]/rabbit_ha_queues
#rabbit_ha_queues = false

# Number of seconds after which the Rabbit broker is considered down
# if heartbeat's keep-alive fails (0 disable the heartbeat).
# EXPERIMENTAL (integer value)
#heartbeat_timeout_threshold = 60

# How often times during the heartbeat_timeout_threshold we check the
# heartbeat. (integer value)
#heartbeat_rate = 2

# Deprecated, use rpc_backend=kombu+memory or rpc_backend=fake
# (boolean value)
# Deprecated group/name - [DEFAULT]/fake_rabbit
#fake_rabbit = false


[oslo_middleware]

#
# From manila
#

# The maximum body size for each  request, in bytes. (integer value)
# Deprecated group/name - [DEFAULT]/osapi_max_request_body_size
# Deprecated group/name - [DEFAULT]/max_request_body_size
#max_request_body_size = 114688

#
# From manila
#

# The HTTP Header that will be used to determine what the original
# request protocol scheme was, even if it was hidden by an SSL
# termination proxy. (string value)
#secure_proxy_ssl_header = X-Forwarded-Proto


[oslo_policy]

#
# From manila
#

# The JSON file that defines policies. (string value)
# Deprecated group/name - [DEFAULT]/policy_file
#policy_file = policy.json

# Default rule. Enforced when a requested rule is not found. (string
# value)
# Deprecated group/name - [DEFAULT]/policy_default_rule
#policy_default_rule = default

# Directories where policy configuration files are stored. They can be
# relative to any directory in the search path defined by the
# config_dir option, or absolute paths. The file defined by
# policy_file must exist for these directories to be searched.
# Missing or empty directories are ignored. (multi valued)
# Deprecated group/name - [DEFAULT]/policy_dirs
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#policy_dirs = policy.d
"""

MANILA_DOC = """
[DEFAULT]
osapi_max_limit = 1000
osapi_share_base_URL = <None>
use_forwarded_for = false
api_paste_config = api-paste.ini
state_path = /var/lib/manila
scheduler_topic = manila-scheduler
share_topic = manila-share
share_driver = manila.share.drivers.generic.GenericShareDriver
enable_v1_api = false
enable_v2_api = false

[cors]
allowed_origin = <None>
allow_credentials = true
expose_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma
allow_methods = GET,POST,PUT,DELETE,OPTIONS
allow_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma
""".strip()

osp = OSP()
osp.role = "Controller"


def test_doc_examples():
    failed_count, tests = doctest.testmod(
        manila_conf,
        globs={'conf': manila_conf.ManilaConf(context_wrap(MANILA_DOC))}
    )
    assert failed_count == 0


def test_match():
    result = manila_conf.ManilaConf(context_wrap(MANILA_CONTENT, osp=osp))
    assert result.data.get("DEFAULT", "share_topic") == "manila-share"
    assert result.data.get("DEFAULT", "scheduler_topic") == "manila-scheduler"
    assert result.data.get("DEFAULT", "enable_v2_api") == "false"

    assert result.data.get("cors", "allow_credentials") == "true"
