import doctest
from insights.parsers import neutron_metadata_agent_conf
from insights.parsers.neutron_metadata_agent_conf import NeutronMetadataAgentIni
from insights.tests import context_wrap


METADATA_AGENT_INI = """
[DEFAULT]
# Show debugging output in log (sets DEBUG log level output)
# debug = True
debug = False

# The Neutron user information for accessing the Neutron API.
auth_url = http://localhost:35357/v2.0
# Turn off verification of the certificate for ssl
# auth_insecure = False
auth_insecure = False
# Certificate Authority public key (CA cert) file for ssl
# auth_ca_cert =
admin_tenant_name = service
admin_user = neutron
admin_password = *********

# Network service endpoint type to pull from the keystone catalog
# endpoint_type = adminURL

# IP address used by Nova metadata server
# nova_metadata_ip = 127.0.0.1
nova_metadata_ip = 127.0.0.1

# TCP Port used by Nova metadata server
# nova_metadata_port = 8775
nova_metadata_port = 8775

# Which protocol to use for requests to Nova metadata server, http or https
# nova_metadata_protocol = http
nova_metadata_protocol = http

# Whether insecure SSL connection should be accepted for Nova metadata server
# requests
# nova_metadata_insecure = False

# Client certificate for nova api, needed when nova api requires client
# certificates
# nova_client_cert =

# Private key for nova client certificate
# nova_client_priv_key =

# When proxying metadata requests, Neutron signs the Instance-ID header with a
# shared secret to prevent spoofing.  You may select any string for a secret,
# but it must match here and in the configuration used by the Nova Metadata
# Server. NOTE: Nova uses the same config key, but in [neutron] section.
# metadata_proxy_shared_secret =
metadata_proxy_shared_secret =*********

# Location of Metadata Proxy UNIX domain socket
# metadata_proxy_socket = $state_path/metadata_proxy

# Metadata Proxy UNIX domain socket mode, 4 values allowed:
# 'deduce': deduce mode from metadata_proxy_user/group values,
# 'user': set metadata proxy socket mode to 0o644, to use when
# metadata_proxy_user is agent effective user or root,
# 'group': set metadata proxy socket mode to 0o664, to use when
# metadata_proxy_group is agent effective group,
# 'all': set metadata proxy socket mode to 0o666, to use otherwise.
# metadata_proxy_socket_mode = deduce

# Number of separate worker processes for metadata server. Defaults to
# half the number of CPU cores
# metadata_workers =
metadata_workers =0

# Number of backlog requests to configure the metadata server socket with
# metadata_backlog = 4096
metadata_backlog = 4096

# URL to connect to the cache backend.
# default_ttl=0 parameter will cause cache entries to never expire.
# Otherwise default_ttl specifies time in seconds a cache entry is valid for.
# No cache is used in case no value is passed.
# cache_url = memory://?default_ttl=5
cache_url = memory://?default_ttl=5

[AGENT]
# Log agent heartbeats from this Metadata agent
log_agent_heartbeats = False
""".strip()


def test_neutron_metadata_agent_ini():
    nmda_ini = NeutronMetadataAgentIni(context_wrap(METADATA_AGENT_INI))
    assert nmda_ini.has_option('AGENT', 'log_agent_heartbeats')
    assert nmda_ini.get("DEFAULT", "auth_url") == 'http://localhost:35357/v2.0'
    assert nmda_ini.getint("DEFAULT", "metadata_backlog") == 4096


def test_doc():
    env = {'metadata_agent_ini': NeutronMetadataAgentIni(context_wrap(METADATA_AGENT_INI, path='/etc/neutron/metadata_agent.ini'))}
    failed, total = doctest.testmod(neutron_metadata_agent_conf, globs=env)
    assert failed == 0
