"""
KeystoneConf - file ``/etc/keystone/keystone.conf``
===================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.keystone_conf)
class KeystoneConf(IniConfigFile):
    """
    The ``KeystoneConf`` class parses the information in the file
    ``/etc/keystone/keystone.conf``.  See the ``IniConfigFile`` class for more
    information on attributes and methods.

    Sample input data looks like::

        [DEFAULT]
        admin_token = ADMIN
        compute_port = 8774

        [identity]
        default_domain_id = default
        domain_configurations_from_database = false

        [identity_mapping]
        driver = keystone.identity.mapping_backends.sql.Mapping
        generator = keystone.identity.id_generators.sha256.Generator

    Examples:
        >>> type(conf)
        <class 'insights.parsers.keystone.KeystoneConf'>
        >>> 'identity' in conf
        True
        >>> conf.has_option('identity', 'default_domain_id')
        True
        >>> conf.has_option('identity', 'domain_specific_drivers_enabled')
        False
        >>> conf.get('identity', 'default_domain_id')
        'default'
    """
    pass
