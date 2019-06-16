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

from insights.parsers.keystone import KeystoneConf
from insights.tests import context_wrap

KEYSTONE_CONF = """
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
""".strip()


def test_keystone():
    kconf = KeystoneConf(context_wrap(KEYSTONE_CONF))
    assert kconf is not None
    assert kconf.defaults() == {'admin_token': 'ADMIN',
                                'compute_port': '8774'}
    assert 'identity' in kconf
    assert 'identity_mapping' in kconf
    assert kconf.has_option('identity', 'default_domain_id')
    assert kconf.has_option('identity_mapping', 'driver')
    assert not kconf.has_option('identity', 'domain_specific_drivers_enabled')
    assert kconf.get('identity', 'default_domain_id') == 'default'
    assert kconf.items('DEFAULT') == {'admin_token': 'ADMIN',
                                      'compute_port': '8774'}
