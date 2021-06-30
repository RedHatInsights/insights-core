import doctest
import pytest
from insights.parsers import ansible_tower_settings, SkipException
from insights.tests import context_wrap


ANSIBLE_TOWER_CONFIG_CUSTOM = '''
AWX_CLEANUP_PATHS = False
LOGGING['handlers']['tower_warnings']['level'] = 'DEBUG'
'''.strip()

ANSIBLE_TOWER_CONFIG_CUSTOM_INVALID1 = '''
'''.strip()

ANSIBLE_TOWER_CONFIG_CUSTOM_INVALID2 = '''
AWX_CLEANUP_PATHS
'''.strip()


def test_ansible_tower_settings():
    conf = ansible_tower_settings.AnsibleTowerSettings(context_wrap(ANSIBLE_TOWER_CONFIG_CUSTOM))
    assert conf['AWX_CLEANUP_PATHS'] == 'False'

    with pytest.raises(SkipException) as exc:
        ansible_tower_settings.AnsibleTowerSettings(context_wrap(ANSIBLE_TOWER_CONFIG_CUSTOM_INVALID1))
    assert 'No Valid Configuration' in str(exc)

    with pytest.raises(SkipException) as exc:
        ansible_tower_settings.AnsibleTowerSettings(context_wrap(ANSIBLE_TOWER_CONFIG_CUSTOM_INVALID2))
    assert 'No Valid Configuration' in str(exc)


def test_ansible_tower_settings_documentation():
    failed_count, tests = doctest.testmod(
        ansible_tower_settings,
        globs={'conf': ansible_tower_settings.AnsibleTowerSettings(context_wrap(ANSIBLE_TOWER_CONFIG_CUSTOM))}
    )
    assert failed_count == 0
