import doctest

from insights.parsers import ceilometer_conf
from insights.tests import context_wrap

CEILOMETER_CONTENT = """
[DEFAULT]
#
# From ceilometer
#
# To reduce polling agent load, samples are sent to the notification
# agent in a batch. To gain higher throughput at the cost of load set
# this to False. (boolean value)
#batch_polled_samples = true
# To reduce large requests at same time to Nova or other components
# from different compute agents, shuffle start time of polling task.
# (integer value)
#shuffle_time_before_polling_task = 0
# Configuration file for WSGI definition of API. (string value)
#api_paste_config = api_paste.ini
# Polling namespace(s) to be used while resource polling (unknown
# type)
#polling_namespaces = ['compute', 'central']
# List of pollsters (or wildcard templates) to be used while polling
# (unknown type)
#pollster_list = []
# Exchange name for Nova notifications. (string value)
#nova_control_exchange = nova
# List of metadata prefixes reserved for metering use. (list value)
#reserved_metadata_namespace = metering.
# Limit on length of reserved metadata values. (integer value)
#reserved_metadata_length = 256
# List of metadata keys reserved for metering use. And these keys are
# additional to the ones included in the namespace. (list value)
#reserved_metadata_keys =
# Inspector to use for inspecting the hypervisor layer. Known
# inspectors are libvirt, hyperv, vmware, xenapi and powervm. (string
# value)
#hypervisor_inspector = libvirt
# Libvirt domain type. (string value)
# Allowed values: kvm, lxc, qemu, uml, xen
#libvirt_type = kvm
# Override the default libvirt URI (which is dependent on
# libvirt_type). (string value)
#libvirt_uri =
# Dispatcher to process data. (multi valued)
# Deprecated group/name - [collector]/dispatcher
#dispatcher = database
# Number of items to request in each paginated Glance API request
# (parameter used by glancecelient). If this is less than or equal to
# 0, page size is not specified (default value in glanceclient is
# used). (integer value)
#glance_page_size = 0
# Exchange name for Ironic notifications. (string value)
#ironic_exchange = ironic
# Exchanges name to listen for notifications. (multi valued)
#http_control_exchanges = nova
#http_control_exchanges = glance
#http_control_exchanges = neutron
#http_control_exchanges = cinder
# Exchange name for Neutron notifications. (string value)
# Deprecated group/name - [DEFAULT]/quantum_control_exchange
#neutron_control_exchange = neutron
# Allow novaclient's debug log output. (boolean value)
#nova_http_log_debug = false
# Swift reseller prefix. Must be on par with reseller_prefix in proxy-
# server.conf. (string value)
#reseller_prefix = AUTH_
# Configuration file for pipeline definition. (string value)
#pipeline_cfg_file = pipeline.yaml
# Configuration file for event pipeline definition. (string value)
#event_pipeline_cfg_file = event_pipeline.yaml
# Refresh Pipeline configuration on-the-fly. (boolean value)
#refresh_pipeline_cfg = false
# Refresh Event Pipeline configuration on-the-fly. (boolean value)
#refresh_event_pipeline_cfg = false
# Polling interval for pipeline file configuration in seconds.
# (integer value)
#pipeline_polling_interval = 20
# Source for samples emitted on this instance. (string value)
# Deprecated group/name - [DEFAULT]/counter_source
#sample_source = openstack
# Name of this node, which must be valid in an AMQP key. Can be an
# opaque identifier. For ZeroMQ only, must be a valid host name, FQDN,
# or IP address. (string value)
# Timeout seconds for HTTP requests. Set it to None to disable
# timeout. (integer value)
#http_timeout = 600
http_timeout = 600
# DEPRECATED - Database connection string. (string value)
#database_connection = <None>
# Path to the rootwrap configuration file touse for running commands
# as root (string value)
#rootwrap_config = /etc/ceilometer/rootwrap.conf
#
# From oslo.log
#
# Print debugging output (set logging level to DEBUG instead of
# default INFO level). (boolean value)
#debug = false
debug = False
# If set to false, will disable INFO logging level, making WARNING the
# default. (boolean value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#verbose = true
verbose = False
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
log_dir = /var/log/ceilometer
# Use syslog for logging. Existing syslog format is DEPRECATED and
# will be changed later to honor RFC5424. (boolean value)
#use_syslog = false
use_syslog = False
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
syslog_log_facility = LOG_USER
# Log output to standard error. (boolean value)
#use_stderr = true
use_stderr = True
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
notification_topics = notifications
# Seconds to wait for a response from a call. (integer value)
#rpc_response_timeout = 60
# A URL representing the messaging driver to use and its full
# configuration. If not set, we fall back to the rpc_backend option
# and driver specific configuration. (string value)
#transport_url = <None>
# The messaging driver to use, defaults to rabbit. Other drivers
# include qpid and zmq. (string value)
#rpc_backend = rabbit
rpc_backend = rabbit
# The default exchange under which topics are scoped. May be
# overridden by an exchange name specified in the transport_url
# option. (string value)
#control_exchange = openstack
#
# From oslo.service.service
#
# Enable eventlet backdoor.  Acceptable values are 0, <port>, and
# <start>:<end>, where 0 results in listening on a random tcp port
# number; <port> results in listening on the specified port number
# (and not enabling backdoor if that port is in use); and
# <start>:<end> results in listening on the smallest unused port
# number within the specified range of port numbers.  The chosen port
# is displayed in the service's log file. (string value)
#backdoor_port = <None>
# Enables or disables logging values of all registered options when
# starting a service (at DEBUG level). (boolean value)
#log_options = true
meter_dispatcher=database
event_dispatcher=database
[alarm]
#
# From ceilometer
#
# SSL Client certificate for REST notifier. (string value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#rest_notifier_certificate_file =
# SSL Client private key for REST notifier. (string value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#rest_notifier_certificate_key =
# Whether to verify the SSL Server certificate when calling alarm
# action. (boolean value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#rest_notifier_ssl_verify = true
# Number of retries for REST notifier (integer value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#rest_notifier_max_retries = 0
# Period of evaluation cycle, should be >= than configured pipeline
# interval for collection of underlying meters. (integer value)
# Deprecated group/name - [alarm]/threshold_evaluation_interval
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#evaluation_interval = 60
evaluation_interval = 60
# The topic that ceilometer uses for alarm notifier messages. (string
# value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#notifier_rpc_topic = alarm_notifier
# URL to Gnocchi. (string value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#gnocchi_url = http://localhost:8041
# Record alarm change events. (boolean value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#record_history = true
record_history = True
# Maximum number of alarms defined for a user. (integer value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#user_alarm_quota = <None>
# Maximum number of alarms defined for a project. (integer value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#project_alarm_quota = <None>
# Maximum count of actions for each state of an alarm, non-positive
# number means no limit. (integer value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#alarm_max_actions = -1
evaluation_service=ceilometer.alarm.service.SingletonAlarmService
partition_rpc_topic=alarm_partition_coordination
[api]
#
# From ceilometer
#
# The port for the ceilometer API server. (integer value)
# Minimum value: 1
# Maximum value: 65535
# Deprecated group/name - [DEFAULT]/metering_api_port
#port = 8777
port = 8777
# The listen IP for the ceilometer API server. (string value)
#host = 0.0.0.0
host = 192.0.2.10
# Toggle Pecan Debug Middleware. (boolean value)
#pecan_debug = false
# Default maximum number of items returned by API request. (integer
# value)
# Minimum value: 1
#default_api_return_limit = 100
# Number of workers for api, default value is 1. (integer value)
# Minimum value: 1
# Deprecated group/name - [DEFAULT]/api_workers
#workers = 1
[central]
#
# From ceilometer
#
# To reduce polling agent load, samples are sent to the notification
# agent in a batch. To gain higher throughput at the cost of load set
# this to False. (boolean value)
#batch_polled_samples = true
# To reduce large requests at same time to Nova or other components
# from different compute agents, shuffle start time of polling task.
# (integer value)
#shuffle_time_before_polling_task = 0
[collector]
#
# From ceilometer
#
# Address to which the UDP socket is bound. Set to an empty string to
# disable. (string value)
#udp_address = 0.0.0.0
udp_address = 0.0.0.0
# Port to which the UDP socket is bound. (integer value)
# Minimum value: 1
# Maximum value: 65535
#udp_port = 4952
udp_port = 4952
# Requeue the sample on the collector sample queue when the collector
# fails to dispatch it. This is only valid if the sample come from the
# notifier publisher. (boolean value)
#requeue_sample_on_dispatcher_error = false
# Requeue the event on the collector event queue when the collector
# fails to dispatch it. (boolean value)
#requeue_event_on_dispatcher_error = false
# Enable the RPC functionality of collector. This functionality is now
# deprecated in favour of notifier publisher and queues. (boolean
# value)
#enable_rpc = false
# Number of workers for collector service. default value is 1.
# (integer value)
# Minimum value: 1
# Deprecated group/name - [DEFAULT]/collector_workers
#workers = 1
[compute]
#
# From ceilometer
#
# Enable work-load partitioning, allowing multiple compute agents to
# be run simultaneously. (boolean value)
#workload_partitioning = false
[coordination]
#
# From ceilometer
#
# The backend URL to use for distributed coordination. If left empty,
# per-deployment central agent and per-host compute agent won't do
# workload partitioning and will only function correctly if a single
# instance of that service is running. (string value)
#backend_url = <None>
backend_url = redis://:chDWmHdH8dyjsmpCWfCEpJR87@192.0.2.7:6379/
# Number of seconds between heartbeats for distributed coordination.
# (floating point value)
#heartbeat = 1.0
# Number of seconds between checks to see if group membership has
# changed (floating point value)
#check_watchers = 10.0
[database]
#
# From ceilometer
#
# Number of seconds that samples are kept in the database for (<= 0
# means forever). (integer value)
# Deprecated group/name - [database]/time_to_live
#metering_time_to_live = -1
metering_time_to_live = -1
# Number of seconds that events are kept in the database for (<= 0
# means forever). (integer value)
#event_time_to_live = -1
event_time_to_live = -1
# The connection string used to connect to the metering database. (if
# unset, connection is used) (string value)
#metering_connection = <None>
# The connection string used to connect to the alarm database. (if
# unset, connection is used) (string value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#alarm_connection = <None>
# Number of seconds that alarm histories are kept in the database for
# (<= 0 means forever). (integer value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#alarm_history_time_to_live = -1
alarm_history_time_to_live = -1
# The connection string used to connect to the event database. (if
# unset, connection is used) (string value)
#event_connection = <None>
# The max length of resources id in DB2 nosql, the value should be
# larger than len(hostname) * 2 as compute node's resource id is
# <hostname>_<nodename>. (integer value)
#db2nosql_resource_id_maxlen = 512
# The name of the replica set which is used to connect to MongoDB
# database. Add "?replicaSet=myreplicatset" in your connection URI
# instead. (string value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#mongodb_replica_set =
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
connection = mongodb://192.0.2.11:27017,192.0.2.10:27017,192.0.2.12:27017/ceilometer?replicaSet=tripleo
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
idle_timeout = 3600
# Minimum number of SQL connections to keep open in a pool. (integer
# value)
# Deprecated group/name - [DEFAULT]/sql_min_pool_size
# Deprecated group/name - [DATABASE]/sql_min_pool_size
#min_pool_size = 1
min_pool_size = 1
# Maximum number of SQL connections to keep open in a pool. (integer
# value)
# Deprecated group/name - [DEFAULT]/sql_max_pool_size
# Deprecated group/name - [DATABASE]/sql_max_pool_size
#max_pool_size = <None>
max_pool_size = 10
# Maximum number of database connection retries during startup. Set to
# -1 to specify an infinite retry count. (integer value)
# Deprecated group/name - [DEFAULT]/sql_max_retries
# Deprecated group/name - [DATABASE]/sql_max_retries
#max_retries = 10
max_retries = 10
# Interval between retries of opening a SQL connection. (integer
# value)
# Deprecated group/name - [DEFAULT]/sql_retry_interval
# Deprecated group/name - [DATABASE]/reconnect_interval
#retry_interval = 10
retry_interval = 10
# If set, use this value for max_overflow with SQLAlchemy. (integer
# value)
# Deprecated group/name - [DEFAULT]/sql_max_overflow
# Deprecated group/name - [DATABASE]/sqlalchemy_max_overflow
#max_overflow = <None>
max_overflow = 20
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
time_to_live=-1
[dispatcher_file]
#
# From ceilometer
#
# Name and the location of the file to record meters. (string value)
#file_path = <None>
# The max size of the file. (integer value)
#max_bytes = 0
# The max number of the files to keep. (integer value)
#backup_count = 0
[event]
#
# From ceilometer
#
# Configuration file for event definitions. (string value)
#definitions_cfg_file = event_definitions.yaml
# Drop notifications if no event definition matches. (Otherwise, we
# convert them with just the default traits) (boolean value)
#drop_unmatched_notifications = false
# Store the raw notification for select priority levels (info and/or
# error). By default, raw details are not captured. (multi valued)
#store_raw =
[exchange_control]
#
# From ceilometer
#
# Exchange name for Heat notifications (string value)
#heat_control_exchange = heat
# Exchange name for Glance notifications. (string value)
#glance_control_exchange = glance
# Exchange name for Magnetodb notifications. (string value)
#magnetodb_control_exchange = magnetodb
# Exchange name for Keystone notifications. (string value)
#keystone_control_exchange = keystone
# Exchange name for Cinder notifications. (string value)
#cinder_control_exchange = cinder
# Exchange name for Data Processing notifications. (string value)
#sahara_control_exchange = sahara
# Exchange name for Swift notifications. (string value)
#swift_control_exchange = swift
# Exchange name for Magnum notifications. (string value)
#magnum_control_exchange = magnum
# Exchange name for DBaaS notifications. (string value)
#trove_control_exchange = trove
# Exchange name for Messaging service notifications. (string value)
#zaqar_control_exchange = zaqar
"""

CEILOMETER_DOC_TEST = """
[DEFAULT]
#
# From ceilometer
http_timeout = 600
debug = False
verbose = False
log_dir = /var/log/ceilometer
meter_dispatcher=database
event_dispatcher=database
[alarm]
evaluation_interval = 60
evaluation_service=ceilometer.alarm.service.SingletonAlarmService
partition_rpc_topic=alarm_partition_coordination
[api]
port = 8777
host = 192.0.2.10
[central]
[collector]
udp_address = 0.0.0.0
udp_port = 4952
[compute]
[coordination]
backend_url = redis://:chDWmHdH8dyjsmpCWfCEpJR87@192.0.2.7:6379/
""".strip()


def test_doc_examples():
    env = {
        'config': ceilometer_conf.CeilometerConf(context_wrap(CEILOMETER_DOC_TEST))
    }
    failed, total = doctest.testmod(ceilometer_conf, globs=env)
    assert failed == 0


def test_match():
    result = ceilometer_conf.CeilometerConf(context_wrap(CEILOMETER_CONTENT))
    assert result.data.get("DEFAULT", "http_timeout") == "600"
    assert result.data.get("DEFAULT", "log_dir") == "/var/log/ceilometer"
    assert result.data.get("api", "host") == "192.0.2.10"

    assert result.data.get("coordination", "backend_url") == \
        "redis://:chDWmHdH8dyjsmpCWfCEpJR87@192.0.2.7:6379/"
    assert result.data.get("database", "metering_time_to_live") == "-1"
    assert result.data.get("database", "connection") == \
        "mongodb://192.0.2.11:27017,192.0.2.10:27017,192.0.2.12:27017/ceilometer?replicaSet=tripleo"
