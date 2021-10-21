import pytest

from insights.tests import context_wrap
from insights.parsers.postgresql_conf import PostgreSQLConf

postgresql_conf_cnt = """

# -----------------------------
# PostgreSQL configuration file
# -----------------------------
#
# This file consists of lines of the form:
#
#   name = value
#
# (The "=" is optional.)  Whitespace may be used.  Comments are introduced with
# "#" anywhere on a line.  The complete list of parameter names and allowed
# values can be found in the PostgreSQL documentation.
#
# The commented-out settings shown in this file represent the default values.
# Re-commenting a setting is NOT sufficient to revert it to the default value;
# you need to reload the server.
#
# This file is read on server startup and when the server receives a SIGHUP
# signal.  If you edit the file on a running system, you have to SIGHUP the
# server for the changes to take effect, or use "pg_ctl reload".  Some
# parameters, which are marked below, require a server shutdown and restart to
# take effect.
#
# Any parameter can also be given as a command-line option to the server, e.g.,
# "postgres -c log_connections=on".  Some parameters can be changed at run time
# with the "SET" SQL command.
#
# Memory units:  kB = kilobytes        Time units:  ms  = milliseconds
#                MB = megabytes                     s   = seconds
#                GB = gigabytes                     min = minutes
#                                                   h   = hours
#                                                   d   = days


#------------------------------------------------------------------------------
# FILE LOCATIONS
#------------------------------------------------------------------------------

# The default values of these variables are driven from the -D command-line
# option or PGDATA environment variable, represented here as ConfigDir.

#data_directory = 'ConfigDir'		# use data in another directory
#hba_file = 'ConfigDir/pg_hba.conf'	# host-based authentication file
#ident_file = 'ConfigDir/pg_ident.conf'	# ident configuration file

# If external_pid_file is not explicitly set, no extra PID file is written.
#external_pid_file = '(none)'		# write an extra PID file


#------------------------------------------------------------------------------
# CONNECTIONS AND AUTHENTICATION
#------------------------------------------------------------------------------

# - Connection Settings -

#listen_addresses = 'localhost'		# what IP address(es) to listen on;
#port = 5432				# (change requires restart)
### next line has been commented out by spacewalk-setup-postgresql ###
##max_connections = 100			# (change requires restart)
# Note:  Increasing max_connections costs ~400 bytes of shared memory per
# connection slot, plus lock space (see max_locks_per_transaction).
#superuser_reserved_connections = 3	# (change requires restart)
#unix_socket_directory = ''		# (change requires restart)
#unix_socket_group = ''			# (change requires restart)
#unix_socket_permissions = 0777		# begin with 0 to use octal notation
#bonjour_name = ''			# defaults to the computer name

# - Security and Authentication -

#authentication_timeout = 1min		# 1s-600s
#ssl = off				# (change requires restart)
#ssl_ciphers = 'ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH'	# allowed SSL ciphers
#ssl_renegotiation_limit = 512MB	# amount of data between renegotiations
#password_encryption = on
#db_user_namespace = off

# Kerberos and GSSAPI
#krb_server_keyfile = ''
#krb_srvname = 'postgres'		# (Kerberos only)
#krb_caseins_users = off

# - TCP Keepalives -
# see "man 7 tcp" for details

#tcp_keepalives_idle = 0		# TCP_KEEPIDLE, in seconds;
#tcp_keepalives_interval = 0		# TCP_KEEPINTVL, in seconds;
#tcp_keepalives_count = 0		# TCP_KEEPCNT;

#------------------------------------------------------------------------------
# RESOURCE USAGE (except WAL)
#------------------------------------------------------------------------------

# - Memory -

### next line has been commented out by spacewalk-setup-postgresql ###
##shared_buffers = 32MB			# min 128kB
#temp_buffers = 8MB			# min 800kB
#max_prepared_transactions = 0		# zero disables the feature
# Note:  Increasing max_prepared_transactions costs ~600 bytes of shared memory
# per transaction slot, plus lock space (see max_locks_per_transaction).
# It is not advisable to set max_prepared_transactions nonzero unless you
# actively intend to use prepared transactions.
#work_mem = 1MB				# min 64kB
#maintenance_work_mem = 16MB		# min 1MB
#max_stack_depth = 2MB			# min 100kB

# - Kernel Resource Usage -

#max_files_per_process = 1000		# min 25
#shared_preload_libraries = ''		# (change requires restart)

# - Cost-Based Vacuum Delay -

#vacuum_cost_delay = 0ms		# 0-100 milliseconds
#vacuum_cost_page_hit = 1		# 0-10000 credits
#vacuum_cost_page_miss = 10		# 0-10000 credits
#vacuum_cost_page_dirty = 20		# 0-10000 credits
#vacuum_cost_limit = 200		# 1-10000 credits

# - Background Writer -

#bgwriter_delay = 200ms			# 10-10000ms between rounds
#bgwriter_lru_maxpages = 100		# 0-1000 max buffers written/round
#bgwriter_lru_multiplier = 2.0		# 0-10.0 multipler on buffers scanned/round

# - Asynchronous Behavior -

#effective_io_concurrency = 1		# 1-1000. 0 disables prefetching

# These are only used if logging_collector is on:
log_directory = 'pg_log'		# directory where log files are written,
log_filename = 'postgresql-%a.log'	# log file name pattern,
log_truncate_on_rotation = on		# If on, an existing log file of the
checkpoint_completion_target = 0.7
checkpoint_segments = 8
effective_cache_size = 1152MB
log_line_prefix = '%m '
maintenance_work_mem = 96MB
max_connections = 600
shared_buffers = 384MB
wal_buffers = 4MB
work_mem = 2560kB

password_encryption on
db_user_namespace = off

bgwriter_delay = 200ms			# 10-10000ms between rounds
checkpoint_timeout = 5min
tcp_keepalives_interval 300

max_stack_depth = 2048576       # Test of as_memory_bytes with string of digits

test_strange_quoting '''strange quoting\\''
""".strip()


def test_postgresql_conf():
    result = PostgreSQLConf(context_wrap(postgresql_conf_cnt))
    assert result.get("checkpoint_segments") == "8"
    # The bit before the hash mark should still be treated as valid:
    assert result.get("log_filename") == "postgresql-%a.log"
    # Quoting allows spaces at beginning or end of value
    assert result.get("log_line_prefix") == "%m "
    # Equals signs are optional
    assert result.get("password_encryption") == "on"
    # Values can include a quote with '' or \\' - both work.
    assert result.get("test_strange_quoting") == "'strange quoting'"

    # Default value tests
    # get method from LegacyItemAccess
    assert result.get(None) is None
    assert result.get('') is None
    assert 'listen_addresses' not in result
    assert result.get('listen_addresses', 'localhost') == 'localhost'


def test_postgresql_conf_conversions():
    result = PostgreSQLConf(context_wrap(postgresql_conf_cnt))
    assert result.as_duration('bgwriter_delay') == 0.2
    assert result.as_duration('checkpoint_timeout') == 300
    assert result.as_duration('tcp_keepalives_interval') == 300
    # Default value tests do conversions as well
    assert result.as_duration(None) is None
    assert 'vacuum_cost_delay' not in result
    assert result.as_duration('vacuum_cost_delay', '200ms') == 0.2
    assert result.as_duration('tcp_keepalives_idle', '0') == 0
    assert result.as_duration('tcp_keepalives_idle', 0) == 0

    assert result.as_boolean('password_encryption')
    assert not result.as_boolean('db_user_namespace')
    # Default value tests do conversions as well
    assert result.as_boolean(None) is None
    assert result.as_boolean('no_such_property', True)
    assert 'krb_caseins_users' not in result
    assert not result.as_boolean('krb_caseins_users', 'no')

    assert result.as_memory_bytes('work_mem') == 2560 * 1024
    assert result.as_memory_bytes('wal_buffers') == 4 * 1048576
    # No scaling necessary if no suffix but conversion to int done
    assert result.as_memory_bytes('max_stack_depth') == 2048576
    # Default value tests do conversions as well
    assert result.as_memory_bytes(None) is None
    assert 'temp_buffers' not in result
    assert result.as_memory_bytes('temp_buffers', '8MB') == 8192 * 1024
    assert result.as_memory_bytes('temp_buffers', '8388608') == 8192 * 1024
    assert result.as_memory_bytes('temp_buffers', 8388608) == 8192 * 1024


def test_postgresql_conf_conversion_errors():
    result = PostgreSQLConf(context_wrap(postgresql_conf_cnt))
    # Test that we raise the right errors for bad conversions
    # Can't chain them because the raised error aborts further checks.
    with pytest.raises(ValueError):
        assert result.as_duration('log_filename')
    with pytest.raises(ValueError):
        assert result.as_duration('db_user_namespace')
    with pytest.raises(ValueError):
        assert result.as_boolean('log_directory')
    with pytest.raises(ValueError):
        assert result.as_boolean('checkpoint_segments')
    with pytest.raises(ValueError):
        assert result.as_memory_bytes('log_line_prefix')
    with pytest.raises(ValueError):
        assert result.as_memory_bytes('checkpoint_timeout')
