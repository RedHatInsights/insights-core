#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

'''
NeutronMetadataAgentIni - file ``/etc/neutron/metadata_agent.ini``
==================================================================

The ``NeutronMetadataAgentIni`` class parses the metadata-agent configuration file.
See the ``IniConfigFile`` class for more usage information.
'''

from .. import add_filter, parser, IniConfigFile
from insights.specs import Specs

add_filter(Specs.neutron_metadata_agent_ini, ["["])


@parser(Specs.neutron_metadata_agent_ini)
class NeutronMetadataAgentIni(IniConfigFile):
    """
    Parse the ``/etc/neutron/metadata_agent.ini`` configuration file.

    Sample configuration::

        [DEFAULT]
        # Show debugging output in log (sets DEBUG log level output)
        # debug = True

        # The Neutron user information for accessing the Neutron API.
        auth_url = http://localhost:5000/v2.0
        auth_region = RegionOne
        # Turn off verification of the certificate for ssl
        # auth_insecure = False
        # Certificate Authority public key (CA cert) file for ssl
        # auth_ca_cert =
        admin_tenant_name = %SERVICE_TENANT_NAME%
        admin_user = %SERVICE_USER%
        admin_password = %SERVICE_PASSWORD%

        # Network service endpoint type to pull from the keystone catalog
        # endpoint_type = adminURL

        # IP address used by Nova metadata server
        # nova_metadata_ip = 127.0.0.1

        # TCP Port used by Nova metadata server
        # nova_metadata_port = 8775

        # Which protocol to use for requests to Nova metadata server, http or https
        # nova_metadata_protocol = http

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

        # Location of Metadata Proxy UNIX domain socket
        # metadata_proxy_socket = $state_path/metadata_proxy

        # Metadata Proxy UNIX domain socket mode, 3 values allowed:
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

        # Number of backlog requests to configure the metadata server socket with
        # metadata_backlog = 4096

        # URL to connect to the cache backend.
        # default_ttl=0 parameter will cause cache entries to never expire.
        # Otherwise default_ttl specifies time in seconds a cache entry is valid for.
        # No cache is used in case no value is passed.
        # cache_url = memory://?default_ttl=5

        [AGENT]
        # Log agent heartbeats from this Metadata agent
        # log_agent_heartbeats = False


    Examples:

        >>> metadata_agent_ini.has_option('AGENT', 'log_agent_heartbeats')
        True
        >>> metadata_agent_ini.get("DEFAULT", "auth_url") == 'http://localhost:35357/v2.0'
        True
        >>> metadata_agent_ini.getint("DEFAULT", "metadata_backlog")
        4096

    """
    pass
