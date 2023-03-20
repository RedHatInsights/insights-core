import doctest

from insights.parsers import keystone
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


def test_doc_examples():
    failed_count, tests = doctest.testmod(
        keystone,
        globs={'conf': keystone.KeystoneConf(context_wrap(KEYSTONE_CONF))}
    )
    assert failed_count == 0


def test_keystone():
    kconf = keystone.KeystoneConf(context_wrap(KEYSTONE_CONF))
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
