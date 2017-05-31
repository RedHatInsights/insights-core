from insights.core.context import OSP
from insights.parsers.cinder_conf import CinderConf
from insights.tests import context_wrap

cinder_content = """
[DEFAULT]

#
# Options defined in oslo.messaging
#

# ZeroMQ bind address. Should be a wildcard (*), an ethernet
# interface, or IP. The "host" option should point or resolve
# to this address. (string value)
#rpc_zmq_bind_address=*

# MatchMaker driver. (string value)
#rpc_zmq_matchmaker=local

# ZeroMQ receiver listening port. (integer value)
#rpc_zmq_port=9501

# Number of ZeroMQ contexts, defaults to 1. (integer value)
#rpc_zmq_contexts=1

# Maximum number of ingress messages to locally buffer per
# topic. Default is unlimited. (integer value)
#rpc_zmq_topic_backlog=<None>

# Directory for holding IPC sockets. (string value)
#rpc_zmq_ipc_dir=/var/run/openstack

# Name of this node. Must be a valid hostname, FQDN, or IP
# address. Must match "host" option, if running Nova. (string
# value)
#rpc_zmq_host=cinder

# Seconds to wait before a cast expires (TTL). Only supported
# by impl_zmq. (integer value)
#rpc_cast_timeout=30

# Heartbeat frequency. (integer value)
#matchmaker_heartbeat_freq=300

# Heartbeat time-to-live. (integer value)
#matchmaker_heartbeat_ttl=600

# Size of RPC thread pool. (integer value)
#rpc_thread_pool_size=64

# Driver or drivers to handle sending notifications. (multi
# valued)
#notification_driver=

# AMQP topic used for OpenStack notifications. (list value)
# Deprecated group/name - [rpc_notifier2]/topics
#notification_topics=notifications

# Seconds to wait for a response from a call. (integer value)
#rpc_response_timeout=60

# A URL representing the messaging driver to use and its full
# configuration. If not set, we fall back to the rpc_backend
# option and driver specific configuration. (string value)
#transport_url=<None>

# The messaging driver to use, defaults to rabbit. Other
# drivers include qpid and zmq. (string value)
#rpc_backend=rabbit
rpc_backend=cinder.openstack.common.rpc.impl_kombu

# The default exchange under which topics are scoped. May be
# overridden by an exchange name specified in the
# transport_url option. (string value)
#control_exchange=openstack
control_exchange=openstack


#
# Options defined in cinder.exception
#

# Make exception message format errors fatal. (boolean value)
#fatal_exception_format_errors=false


#
# Options defined in cinder.quota
#

# Number of volumes allowed per project (integer value)
#quota_volumes=10

# Number of volume snapshots allowed per project (integer
# value)
#quota_snapshots=10

# Number of consistencygroups allowed per project (integer
# value)
#quota_consistencygroups=10

# Total amount of storage, in gigabytes, allowed for volumes
# and snapshots per project (integer value)
#quota_gigabytes=1000

# Number of volume backups allowed per project (integer value)
#quota_backups=10

# Total amount of storage, in gigabytes, allowed for backups
# per project (integer value)
#quota_backup_gigabytes=1000

# Number of seconds until a reservation expires (integer
# value)
#reservation_expire=86400

# Count of reservations until usage is refreshed (integer
# value)
#until_refresh=0

# Number of seconds between subsequent usage refreshes
# (integer value)
#max_age=0

# Default driver to use for quota checks (string value)
#quota_driver=cinder.quota.DbQuotaDriver

# Enables or disables use of default quota class with default
# quota. (boolean value)
#use_default_quota_class=true


#
# Options defined in cinder.service
#

# Interval, in seconds, between nodes reporting state to
# datastore (integer value)
#report_interval=10

# Interval, in seconds, between running periodic tasks
# (integer value)
#periodic_interval=60

# Range, in seconds, to randomly delay when starting the
# periodic task scheduler to reduce stampeding. (Disable by
# setting to 0) (integer value)
#periodic_fuzzy_delay=60

# IP address on which OpenStack Volume API listens (string
# value)
#osapi_volume_listen=0.0.0.0
osapi_volume_listen=10.22.100.58

# Port on which OpenStack Volume API listens (integer value)
#osapi_volume_listen_port=8776

# Number of workers for OpenStack Volume API service. The
# default is equal to the number of CPUs available. (integer
# value)
#osapi_volume_workers=<None>
osapi_volume_workers=32


#
# Options defined in cinder.ssh_utils
#

# Option to enable strict host key checking.  When set to
# "True" Cinder will only connect to systems with a host key
# present in the configured "ssh_hosts_key_file".  When set to
# "False" the host key will be saved upon first connection and
# used for subsequent connections.  Default=False (boolean
# value)
#strict_ssh_host_key_policy=false

# File containing SSH host keys for the systems with which
# Cinder needs to communicate.  OPTIONAL:
# Default=$state_path/ssh_known_hosts (string value)
#ssh_hosts_key_file=$state_path/ssh_known_hosts
#
# Options defined in cinder.test
#

# File name of clean sqlite db (string value)
#sqlite_clean_db=clean.sqlite


#
# Options defined in cinder.wsgi
#

# Maximum line size of message headers to be accepted.
# max_header_line may need to be increased when using large
# tokens (typically those generated by the Keystone v3 API
# with big service catalogs). (integer value)
#max_header_line=16384

# Timeout for client connections' socket operations. If an
# incoming connection is idle for this number of seconds it
# will be closed. A value of '0' means wait forever. (integer
# value)
#client_socket_timeout=900

# If False, closes the client socket connection explicitly.
# Setting it to True to maintain backward compatibility.
# Recommended setting is set it to False. (boolean value)
#wsgi_keep_alive=true

# Sets the value of TCP_KEEPALIVE (True/False) for each server
# socket. (boolean value)
#tcp_keepalive=true

# Sets the value of TCP_KEEPIDLE in seconds for each server
# socket. Not supported on OS X. (integer value)
#tcp_keepidle=600

# Sets the value of TCP_KEEPINTVL in seconds for each server
# socket. Not supported on OS X. (integer value)
#tcp_keepalive_interval=<None>

# Sets the value of TCP_KEEPCNT for each server socket. Not
# supported on OS X. (integer value)
#tcp_keepalive_count=<None>

# CA certificate file to use to verify connecting clients
# (string value)
#ssl_ca_file=<None>

# Certificate file to use when starting the server securely
# (string value)
#ssl_cert_file=<None>

# Private key file to use when starting the server securely
# (string value)
#ssl_key_file=<None>


#
# Options defined in cinder.api.common
#

# The maximum number of items that a collection resource
# returns in a single response (integer value)
#osapi_max_limit=1000

# Base URL that will be presented to users in links to the
# OpenStack Volume API (string value)
# Deprecated group/name - [DEFAULT]/osapi_compute_link_prefix
#osapi_volume_base_URL=<None>


#
# Options defined in cinder.api.middleware.auth
#

# Treat X-Forwarded-For as the canonical remote address. Only
# enable this if you have a sanitizing proxy. (boolean value)
#use_forwarded_for=false


#
# Options defined in cinder.api.middleware.sizelimit
#

# Max size for body of a request (integer value)
#osapi_max_request_body_size=114688


#
# Options defined in cinder.api.views.versions
#

# Public url to use for versions endpoint. The default is
# None, which will use the request's host_url attribute to
# populate the URL base. If Cinder is operating behind a
# proxy, you will want to change this to represent the proxy's
# URL. (string value)
#public_endpoint=<None>


#
# Options defined in cinder.backup.chunkeddriver
#

# Compression algorithm (None to disable) (string value)
#backup_compression_algorithm=zlib


#
# Options defined in cinder.backup.driver
#

# Backup metadata version to be used when backing up volume
# metadata. If this number is bumped, make sure the service
# doing the restore supports the new version. (integer value)
#backup_metadata_version=2

# The number of chunks or objects, for which one Ceilometer
# notification will be sent (integer value)
#backup_object_number_per_notification=10

# Interval, in seconds, between two progress notifications
# reporting the backup status (integer value)
#backup_timer_interval=120


#
# Options defined in cinder.backup.drivers.ceph
#

# Ceph configuration file to use. (string value)
#backup_ceph_conf=/etc/ceph/ceph.conf

# The Ceph user to connect with. Default here is to use the
# same user as for Cinder volumes. If not using cephx this
# should be set to None. (string value)
#backup_ceph_user=cinder

# The chunk size, in bytes, that a backup is broken into
# before transfer to the Ceph object store. (integer value)
#backup_ceph_chunk_size=134217728

# The Ceph pool where volume backups are stored. (string
# value)
#backup_ceph_pool=backups

# RBD stripe unit to use when creating a backup image.
# (integer value)
#backup_ceph_stripe_unit=0

# RBD stripe count to use when creating a backup image.
# (integer value)
#backup_ceph_stripe_count=0

# If True, always discard excess bytes when restoring volumes
# i.e. pad with zeroes. (boolean value)
#restore_discard_excess_bytes=true


#
# Options defined in cinder.backup.drivers.nfs
#

# The maximum size in bytes of the files used to hold backups.
# If the volume being backed up exceeds this size, then it
# will be backed up into multiple files. (integer value)
#backup_file_size=1999994880

# The size in bytes that changes are tracked for incremental
# backups. backup_swift_object_size has to be multiple of
# backup_swift_block_size. (integer value)
#backup_sha_block_size_bytes=32768

# Enable or Disable the timer to send the periodic progress
# notifications to Ceilometer when backing up the volume to
# the backend storage. The default value is True to enable the
# timer. (boolean value)
#backup_enable_progress_timer=true

# Base dir containing mount point for NFS share. (string
# value)
#backup_mount_point_base=$state_path/backup_mount

# NFS share in fqdn:path, ipv4addr:path, or "[ipv6addr]:path"
# format. (string value)
#backup_share=<None>

# Mount options passed to the NFS client. See NFS man page for
# details. (string value)
#backup_mount_options=<None>

# Custom container to use for backups. (string value)
#backup_container=<None>


#
# Options defined in cinder.backup.drivers.swift
#

# The URL of the Swift endpoint (string value)
#backup_swift_url=<None>

# Info to match when looking for swift in the service catalog.
# Format is: separated values of the form:
# <service_type>:<service_name>:<endpoint_type> - Only used if
# backup_swift_url is unset (string value)
#swift_catalog_info=object-store:swift:publicURL

# Swift authentication mechanism (string value)
#backup_swift_auth=per_user

# Swift authentication version. Specify "1" for auth 1.0, or
# "2" for auth 2.0 (string value)
#backup_swift_auth_version=1

# Swift tenant/account name. Required when connecting to an
# auth 2.0 system (string value)
#backup_swift_tenant=<None>

# Swift user name (string value)
#backup_swift_user=<None>

# Swift key for authentication (string value)
#backup_swift_key=<None>

# The default Swift container to use (string value)
#backup_swift_container=volumebackups

# The size in bytes of Swift backup objects (integer value)
#backup_swift_object_size=52428800

# The size in bytes that changes are tracked for incremental
# backups. backup_swift_object_size has to be multiple of
# backup_swift_block_size. (integer value)
#backup_swift_block_size=32768

# The number of retries to make for Swift operations (integer
# value)
#backup_swift_retry_attempts=3

# The backoff time in seconds between Swift retries (integer
# value)
#backup_swift_retry_backoff=2

# Enable or Disable the timer to send the periodic progress
# notifications to Ceilometer when backing up the volume to
# the Swift backend storage. The default value is True to
# enable the timer. (boolean value)
#backup_swift_enable_progress_timer=true


#
# Options defined in cinder.backup.drivers.tsm
#

# Volume prefix for the backup id when backing up to TSM
# (string value)
#backup_tsm_volume_prefix=backup

# TSM password for the running username (string value)
#backup_tsm_password=password

# Enable or Disable compression for backups (boolean value)
#backup_tsm_compression=true


#
# Options defined in cinder.backup.manager
#

# Driver to use for backups. (string value)
# Deprecated group/name - [DEFAULT]/backup_service
#backup_driver=cinder.backup.drivers.swift


#
# Options defined in cinder.cmd.volume
#

# Backend override of host value. (string value)
# Deprecated group/name - [DEFAULT]/host
#backend_host=<None>


#
# Options defined in cinder.cmd.volume_usage_audit
#

# If this option is specified then the start time specified is
# used instead of the start time of the last completed audit
# period. (string value)
#start_time=<None>

# If this option is specified then the end time specified is
# used instead of the end time of the last completed audit
# period. (string value)
#end_time=<None>

# Send the volume and snapshot create and delete notifications
# generated in the specified period. (boolean value)
#send_actions=false


#
# Options defined in cinder.common.config
#

# File name for the paste.deploy config for cinder-api (string
# value)
#api_paste_config=api-paste.ini
api_paste_config=/etc/cinder/api-paste.ini

# Top-level directory for maintaining cinder's state (string
# value)
# Deprecated group/name - [DEFAULT]/pybasedir
#state_path=/var/lib/cinder

# IP address of this host (string value)
#my_ip=10.0.0.1

# Default glance host name or IP (string value)
#glance_host=$my_ip

# Default glance port (integer value)
#glance_port=9292

# A list of the glance API servers available to cinder
# ([hostname|ip]:port) (list value)
#glance_api_servers=$glance_host:$glance_port
glance_api_servers=http://10.22.120.50:9292

# Version of the glance API to use (integer value)
#glance_api_version=1
glance_api_version=2

# Number retries when downloading an image from glance
# (integer value)
#glance_num_retries=0
glance_num_retries=0

# Allow to perform insecure SSL (https) requests to glance
# (boolean value)
#glance_api_insecure=false
glance_api_insecure=False

# Enables or disables negotiation of SSL layer compression. In
# some cases disabling compression can improve data
# throughput, such as when high network bandwidth is available
# and you use compressed image formats like qcow2. (boolean
# value)
#glance_api_ssl_compression=false
glance_api_ssl_compression=False

# Location of ca certificates file to use for glance client
# requests. (string value)
#glance_ca_certificates_file=<None>

# http/https timeout value for glance operations. If no value
# (None) is supplied here, the glanceclient default value is
# used. (integer value)
#glance_request_timeout=<None>

# The topic that scheduler nodes listen on (string value)
#scheduler_topic=cinder-scheduler

# The topic that volume nodes listen on (string value)
#volume_topic=cinder-volume

# The topic that volume backup nodes listen on (string value)
#backup_topic=cinder-backup

# DEPRECATED: Deploy v1 of the Cinder API. (boolean value)
#enable_v1_api=true
enable_v1_api=True

# Deploy v2 of the Cinder API. (boolean value)
#enable_v2_api=true
enable_v2_api=True

# Enables or disables rate limit of the API. (boolean value)
#api_rate_limit=true

# Specify list of extensions to load when using
# osapi_volume_extension option with
# cinder.api.contrib.select_extensions (list value)
#osapi_volume_ext_list=

# osapi volume extension to load (multi valued)
#osapi_volume_extension=cinder.api.contrib.standard_extensions

# Full class name for the Manager for volume (string value)
#volume_manager=cinder.volume.manager.VolumeManager

# Full class name for the Manager for volume backup (string
# value)
#backup_manager=cinder.backup.manager.BackupManager

# Full class name for the Manager for scheduler (string value)
#scheduler_manager=cinder.scheduler.manager.SchedulerManager

# Name of this node.  This can be an opaque identifier. It is
# not necessarily a host name, FQDN, or IP address. (string
# value)
#host=cinder

# Availability zone of this node (string value)
#storage_availability_zone=nova
storage_availability_zone=nova

# Default availability zone for new volumes. If not set, the
# storage_availability_zone option value is used as the
# default for new volumes. (string value)
#default_availability_zone=<None>
default_availability_zone=nova

# Default volume type to use (string value)
#default_volume_type=<None>

# Time period for which to generate volume usages. The options
# are hour, day, month, or year. (string value)
#volume_usage_audit_period=month

# Path to the rootwrap configuration file to use for running
# commands as root (string value)
#rootwrap_config=/etc/cinder/rootwrap.conf

# Enable monkey patching (boolean value)
#monkey_patch=false

# List of modules/decorators to monkey patch (list value)
#monkey_patch_modules=

# Maximum time since last check-in for a service to be
# considered up (integer value)
#service_down_time=60

# The full class name of the volume API class to use (string
# value)
#volume_api_class=cinder.volume.api.API

# The full class name of the volume backup API class (string
# value)
#backup_api_class=cinder.backup.api.API

# The strategy to use for auth. Supports noauth, keystone, and
# deprecated. (string value)
#auth_strategy=noauth
auth_strategy=keystone

# A list of backend names to use. These backend names should
# be backed by a unique [CONFIG] group with its options (list
# value)
#enabled_backends=<None>
enabled_backends=tripleo_ceph

# Whether snapshots count against gigabyte quota (boolean
# value)
#no_snapshot_gb_quota=false

# The full class name of the volume transfer API class (string
# value)
#transfer_api_class=cinder.transfer.api.API

# The full class name of the volume replication API class
# (string value)
#replication_api_class=cinder.replication.api.API

# The full class name of the consistencygroup API class
# (string value)
#consistencygroup_api_class=cinder.consistencygroup.api.API

# OpenStack privileged account username. Used for requests to
# other services (such as Nova) that require an account with
# special rights. (string value)
#os_privileged_user_name=<None>

# Password associated with the OpenStack privileged account.
# (string value)
#os_privileged_user_password=<None>

# Tenant name associated with the OpenStack privileged
# account. (string value)
#os_privileged_user_tenant=<None>


#
# Options defined in cinder.compute
#

# The full class name of the compute API class to use (string
# value)
#compute_api_class=cinder.compute.nova.API


#
# Options defined in cinder.compute.nova
#

# Match this value when searching for nova in the service
# catalog. Format is: separated values of the form:
# <service_type>:<service_name>:<endpoint_type> (string value)
#nova_catalog_info=compute:Compute Service:publicURL
nova_catalog_info=compute:Compute Service:publicURL

# Same as nova_catalog_info, but for admin endpoint. (string
# value)
#nova_catalog_admin_info=compute:Compute Service:adminURL
nova_catalog_admin_info=compute:Compute Service:adminURL

# Override service catalog lookup with template for nova
# endpoint e.g. http://localhost:8774/v2/%(project_id)s
# (string value)
#nova_endpoint_template=<None>

# Same as nova_endpoint_template, but for admin endpoint.
# (string value)
#nova_endpoint_admin_template=<None>

# Region name of this node (string value)
#os_region_name=<None>

# Location of ca certificates file to use for nova client
# requests. (string value)
#nova_ca_certificates_file=<None>

# Allow to perform insecure SSL requests to nova (boolean
# value)
#nova_api_insecure=false


#
# Options defined in cinder.db.api
#

# Services to be added to the available pool on create
# (boolean value)
#enable_new_services=true

# Template string to be used to generate volume names (string
# value)
#volume_name_template=volume-%s

# Template string to be used to generate snapshot names
# (string value)
#snapshot_name_template=snapshot-%s

# Template string to be used to generate backup names (string
# value)
#backup_name_template=backup-%s


#
# Options defined in cinder.db.base
#

# Driver to use for database access (string value)
#db_driver=cinder.db
#
# Options defined in cinder.openstack.common.periodic_task
#

# Some periodic tasks can be run in a separate process. Should
# we run them here? (boolean value)
#run_external_periodic_tasks=true


#
# Options defined in cinder.openstack.common.policy
#

# The JSON file that defines policies. (string value)
#policy_file=policy.json

# Default rule. Enforced when a requested rule is not found.
# (string value)
#policy_default_rule=default

# Directories where policy configuration files are stored.
# They can be relative to any directory in the search path
# defined by the config_dir option, or absolute paths. The
# file defined by policy_file must exist for these directories
# to be searched.  Missing or empty directories are ignored.
# (multi valued)
#policy_dirs=policy.d
# Which filter class names to use for filtering hosts when not
# specified in the request. (list value)
#scheduler_default_filters=AvailabilityZoneFilter,CapacityFilter,CapabilitiesFilter

# Which weigher class names to use for weighing hosts. (list
# value)

# Cache volume availability zones in memory for the provided
# duration in seconds (integer value)
#az_cache_duration=3600

# Create volume from snapshot at the host where snapshot
# resides (boolean value)
#snapshot_same_host=true

# Ensure that the new volumes are the same AZ as snapshot or
# source volume (boolean value)
#cloned_volume_same_az=true


#
# Options defined in cinder.volume.driver
#

# The maximum number of times to rescan iSER targetto find
# volume (integer value)
#num_iser_scan_tries=3

# This option is deprecated and unused. It will be removed in
# the Liberty release. (integer value)
#iser_num_targets=<None>

# Prefix for iSER volumes (string value)
#iser_target_prefix=iqn.2010-10.org.openstack:

# The IP address that the iSER daemon is listening on (string
# value)
#iser_ip_address=$my_ip

# Prefix for iSCSI volumes (string value)
#iscsi_target_prefix=iqn.2010-10.org.openstack:

# The IP address that the iSCSI daemon is listening on (string
# value)
#iscsi_ip_address=$my_ip

# The list of secondary IP addresses of the iSCSI daemon (list
# value)
#iscsi_secondary_ip_addresses=

# The port that the iSCSI daemon is listening on (integer
# value)
#iscsi_port=3260

# The maximum number of times to rescan targets to find volume
# (integer value)
# Deprecated group/name - [DEFAULT]/num_iscsi_scan_tries
#num_volume_device_scan_tries=3

# The backend name for a given driver implementation (string
# value)
#volume_backend_name=<None>

# Do we attach/detach volumes in cinder using multipath for
# volume to image and image to volume transfers? (boolean
# value)
#use_multipath_for_image_xfer=false

# If this is set to True, attachment of volumes for image
# transfer will be aborted when multipathd is not running.
# Otherwise, it will fallback to single path. (boolean value)
#enforce_multipath_for_image_xfer=false

# Method used to wipe old volumes (string value)
#volume_clear=zero

# Size in MiB to wipe at start of old volumes. 0 => all
# (integer value)
#volume_clear_size=0

# The flag to pass to ionice to alter the i/o priority of the
# process used to zero a volume after deletion, for example
# "-c3" for idle only priority. (string value)
#volume_clear_ionice=<None>

# iSCSI target user-land tool to use. tgtadm is default, use
# lioadm for LIO iSCSI support, scstadmin for SCST target
# support, iseradm for the ISER protocol, ietadm for iSCSI
# Enterprise Target, iscsictl for Chelsio iSCSI Target or fake
# for testing. (string value)
#iscsi_helper=tgtadm

# Volume configuration file storage directory (string value)
#volumes_dir=$state_path/volumes

# IET configuration file (string value)
#iet_conf=/etc/iet/ietd.conf

# Chiscsi (CXT) global defaults configuration file (string
# value)
#chiscsi_conf=/etc/chelsio-iscsi/chiscsi.conf

# This option is deprecated and unused. It will be removed in
# the next release. (string value)
#lio_initiator_iqns=

# Sets the behavior of the iSCSI target to either perform
# blockio or fileio optionally, auto can be set and Cinder
# will autodetect type of backing device (string value)
#iscsi_iotype=fileio

# The default block size used when copying/clearing volumes
# (string value)
#volume_dd_blocksize=1M

# The blkio cgroup name to be used to limit bandwidth of
# volume copy (string value)
#volume_copy_blkio_cgroup_name=cinder-volume-copy

# The path to the client certificate key for verification, if
# the driver supports it. (string value)
#driver_client_cert_key=<None>

# Option to enable/disable CHAP authentication for targets.
# (boolean value)
# Deprecated group/name - [DEFAULT]/eqlx_use_chap
#use_chap_auth=false

# CHAP user name. (string value)
# Deprecated group/name - [DEFAULT]/eqlx_chap_login
#chap_username=

# Password for specified CHAP account name. (string value)
# Deprecated group/name - [DEFAULT]/eqlx_chap_password
#chap_password=

# Namespace for driver private data values to be saved in.
# (string value)
#driver_data_namespace=<None>

# String representation for an equation that will be used to
# filter hosts. Only used when the driver filter is set to be
# used by the Cinder scheduler. (string value)
#filter_function=<None>

# String representation for an equation that will be used to
# determine the goodness of a host. Only used when using the
# goodness weigher is set to be used by the Cinder scheduler.
# (string value)
#goodness_function=<None>


#
# Options defined in cinder.volume.drivers.block_device
#

# List of all available devices (list value)
#available_devices=


#
# Options defined in cinder.volume.drivers.cloudbyte.options
#

# These values will be used for CloudByte storage's addQos API
# call. (dict value)
#cb_add_qosgroup=latency:15,iops:10,graceallowed:false,iopscontrol:true,memlimit:0,throughput:0,tpcontrol:false,networkspeed:0

# Driver will use this API key to authenticate against the
# CloudByte storage's management interface. (string value)
#cb_apikey=None

# CloudByte storage specific account name. This maps to a
# project name in OpenStack. (string value)
#cb_account_name=None

# This corresponds to the name of Tenant Storage Machine (TSM)
# in CloudByte storage. A volume will be created in this TSM.
# (string value)
#cb_tsm_name=None

# A retry value in seconds. Will be used by the driver to
# check if volume creation was successful in CloudByte
# storage. (integer value)
#cb_confirm_volume_create_retry_interval=5

# Will confirm a successful volume creation in CloudByte
# storage by making this many number of attempts. (integer
# value)
#cb_confirm_volume_create_retries=3

# These values will be used for CloudByte storage's
# createVolume API call. (dict value)

# VNX authentication scope type. (string value)
#storage_vnx_authentication_type=global

# Directory path that contains the VNX security file. Make
# sure the security file is generated first. (string value)
#storage_vnx_security_file_dir=<None>

# Naviseccli Path. (string value)
#naviseccli_path=

# Storage pool name. (string value)
#storage_vnx_pool_name=<None>

# VNX secondary SP IP Address. (string value)
#san_secondary_ip=<None>

# Default timeout for CLI operations in minutes. For example,
# LUN migration is a typical long running operation, which
# depends on the LUN size and the load of the array. An upper
# bound in the specific deployment can be set to avoid
# unnecessary long wait. By default, it is 365 days long.
# (integer value)
#default_timeout=525600

# Default max number of LUNs in a storage group. By default,
# the value is 255. (integer value)
#max_luns_per_storage_group=255

# To destroy storage group when the last LUN is removed from
# it. By default, the value is False. (boolean value)
#destroy_empty_storage_group=false

# Mapping between hostname and its iSCSI initiator IP
# addresses. (string value)
#iscsi_initiators=

# Automatically register initiators. By default, the value is
# False. (boolean value)
#initiator_auto_registration=false

# Automatically deregister initiators after the related
# storage group is destroyed. By default, the value is False.
# (boolean value)
#initiator_auto_deregistration=false

# Report free_capacity_gb as 0 when the limit to maximum
# number of pool LUNs is reached. By default, the value is
# False. (boolean value)
#check_max_pool_luns_threshold=false

# Delete a LUN even if it is in Storage Groups. (boolean
# value)
#force_delete_lun_in_storagegroup=false
#
# Options defined in cinder.volume.drivers.emc.xtremio
#

# XMS cluster id in multi-cluster environment (string value)
#xtremio_cluster_name=


#
# Options defined in cinder.volume.drivers.eqlx
#

# Group name to use for creating volumes. Defaults to
# "group-0". (string value)
#eqlx_group_name=group-0

# Timeout for the Group Manager cli command execution. Default
# is 30. (integer value)
#eqlx_cli_timeout=30

# Maximum retry count for reconnection. Default is 5. (integer
# value)
#eqlx_cli_max_retries=5

# Use CHAP authentication for targets. Note that this option
# is deprecated in favour of "use_chap_auth" as specified in
# cinder/volume/driver.py and will be removed in next release.
# (boolean value)
eqlx_use_chap=false

# Existing CHAP account name. Note that this option is
# deprecated in favour of "chap_username" as specified in
# cinder/volume/driver.py and will be removed in next release.
# (string value)
#eqlx_chap_login=admin

# Password for specified CHAP account name. Note that this
# option is deprecated in favour of "chap_password" as
# specified in cinder/volume/driver.py and will be removed in
# the next release (string value)
#eqlx_chap_password=password

# Pool in which volumes will be created. Defaults to
# "default". (string value)
#eqlx_pool=default


#
# Options defined in cinder.volume.drivers.glusterfs
#

# File with the list of available gluster shares (string
# value)
#glusterfs_shares_config=/etc/cinder/glusterfs_shares

# Create volumes as sparsed files which take no space.If set
# to False volume is created as regular file.In such case
# volume creation takes a lot of time. (boolean value)
#glusterfs_sparsed_volumes=true

# Create volumes as QCOW2 files rather than raw files.
# (boolean value)
#glusterfs_qcow2_volumes=false

# Base dir containing mount points for gluster shares. (string
# value)
#glusterfs_mount_point_base=$state_path/mnt


#
# Options defined in cinder.volume.drivers.hds.hds
#

# The configuration file for the Cinder HDS driver for HUS
# (string value)
#hds_cinder_config_file=/opt/hds/hus/cinder_hus_conf.xml


#
# Options defined in cinder.volume.drivers.hds.iscsi
#

# Configuration file for HDS iSCSI cinder plugin (string
# value)
#hds_hnas_iscsi_config_file=/opt/hds/hnas/cinder_iscsi_conf.xml


#
# Options defined in cinder.volume.drivers.hds.nfs
#
# Interval to check copy (integer value)
#hitachi_copy_check_interval=3

# Interval to check copy asynchronously (integer value)
#hitachi_async_copy_check_interval=10

# Control port names for HostGroup or iSCSI Target (string
# value)
#hitachi_target_ports=<None>

# Range of group number (string value)
#hitachi_group_range=<None>

# Request for creating HostGroup or iSCSI Target (boolean
# value)
#hitachi_group_request=false


#
# Options defined in cinder.volume.drivers.hitachi.hbsd_fc
#

# Request for FC Zone creating HostGroup (boolean value)
#hitachi_zoning_request=false

# If False fully disable profiling feature. (boolean value)
#profiler_enabled=false

# If False doesn't trace SQL requests. (boolean value)
#trace_sqlalchemy=false

[lvm]
iscsi_helper=lioadm
volume_group=cinder-volumes
iscsi_ip_address=192.168.88.10
volume_driver=cinder.volume.drivers.lvm.LVMVolumeDriver
volumes_dir=/var/lib/cinder/volumes
iscsi_protocol=iscsi
volume_backend_name=lvm

"""

osp = OSP()
osp.role = "Controller"


def test_match():
    result = CinderConf(context_wrap(cinder_content, osp=osp))
    assert result.data.get("DEFAULT", "enabled_backends") == "tripleo_ceph"
    assert result.data.get("DEFAULT", "glance_api_ssl_compression") == "False"
    assert result.data.get("DEFAULT", "eqlx_use_chap") == "false"

    assert result.data.get("lvm", "iscsi_helper") == "lioadm"
    assert result.data.get("lvm", "volumes_dir") == "/var/lib/cinder/volumes"
    assert result.data.get("lvm", "volume_backend_name") == "lvm"
