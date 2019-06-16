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

"""
KeystoneConf - file ``/etc/keystone/keystone.conf``
===================================================

The ``KeystoneConf`` class parses the information in the file
``/etc/keystone/keystone.conf``.  See the ``IniConfigFile`` class for more
information on attributes and methods.

Sample input data looks like::

    [DEFAULT]

    #
    # From keystone
    #
    admin_token = ADMIN
    compute_port = 8774

    [identity]

    # From keystone
    default_domain_id = default
    #domain_specific_drivers_enabled = false
    domain_configurations_from_database = false

    [identity_mapping]

    driver = keystone.identity.mapping_backends.sql.Mapping
    generator = keystone.identity.id_generators.sha256.Generator
    #backward_compatible_ids = true

Examples:

    >>> kconf = shared[KeystoneConf]
    >>> kconf.defaults()
    {'admin_token': 'ADMIN', 'compute_port': '8774'}
    >>> 'identity' in kconf
    True
    >>> kconf.has_option('identity', 'default_domain_id')
    True
    >>> kconf.has_option('identity', 'domain_specific_drivers_enabled')
    False
    >>> kconf.get('identity', 'default_domain_id')
    'default'
    >>> kconf.items('identity_mapping')
    {'driver': 'keystone.identity.mapping_backends.sql.Mapping',
     'generator': 'keystone.identity.id_generators.sha256.Generator'}
"""
from .. import IniConfigFile, parser
from insights.specs import Specs


@parser(Specs.keystone_conf)
class KeystoneConf(IniConfigFile):
    """Parse contents of file ``/etc/keystone/keystone.conf``."""
    pass
