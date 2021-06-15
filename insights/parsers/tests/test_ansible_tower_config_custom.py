import doctest
import pytest
from insights.parsers import ansible_tower_config_custom, SkipException
from insights.tests import context_wrap


ANSIBLE_TOWER_CONFIG_CUSTOM = '''
AWX_CLEANUP_PATHS = False
AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_REFERRALS: False,
}
LOGGING['handlers']['tower_warnings']['level'] = 'DEBUG'
'''

ANSIBLE_TOWER_CONFIG_CUSTOM_INVALID = '''
AWX_CLEANUP_PATHS = False
AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_REFERRALS = False,
}
'''


def test_ansible_tower_config_custom():
    conf = ansible_tower_config_custom.AnsibleTowerConfigCustom(context_wrap(ANSIBLE_TOWER_CONFIG_CUSTOM))
    assert conf["LOGGING['handlers']['tower_warnings']['level']"] == 'DEBUG'
    assert not conf['AUTH_LDAP_GLOBAL_OPTIONS']['ldap.OPT_REFERRALS']
    assert not conf['AWX_CLEANUP_PATHS']

    with pytest.raises(SkipException) as exc:
        conf_invalid = ansible_tower_config_custom.AnsibleTowerConfigCustom(context_wrap(ANSIBLE_TOWER_CONFIG_CUSTOM_INVALID))
        assert conf_invalid is not None
    assert 'Syntax error' in str(exc)


def test_ansible_tower_config_custom_conf_documentation():
    failed_count, tests = doctest.testmod(
        ansible_tower_config_custom,
        globs={'conf': ansible_tower_config_custom.AnsibleTowerConfigCustom(context_wrap(ANSIBLE_TOWER_CONFIG_CUSTOM))}
    )
    assert failed_count == 0
