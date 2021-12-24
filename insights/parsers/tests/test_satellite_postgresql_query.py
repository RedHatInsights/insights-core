import doctest
import pytest

from insights.parsers import (
    satellite_postgresql_query, ParseException, SkipException)
from insights.core.plugins import ContentException
from insights.tests import context_wrap


SATELLITE_POSTGRESQL_WRONG_1 = '''
-bash: psql: command not found
'''

SATELLITE_POSTGRESQL_WRONG_2 = '''
su: user postgres does not exist
'''

SATELLITE_POSTGRESQL_WRONG_3 = '''
psql: FATAL:  database "foreman" does not exist
'''

SATELLITE_POSTGRESQL_WRONG_4 = '''
'''

SATELLITE_POSTGRESQL_WRONG_5 = '''
name,default,value
'''.strip()

test_data_1 = '''
name
fix_db_cache
foreman_tasks_sync_task_timeout
dynflow_enable_console
dynflow_console_require_auth
foreman_tasks_proxy_action_retry_count
'''

test_data_2 = '''
id,name,created_at,updated_at
1,project-receptor.satellite_receptor_installer,2021-01-30 01:14:22.848735,2021-01-30 01:14:22.848735
2,theforeman.foreman_scap_client,2021-01-30 01:14:22.916142,2021-01-30 01:14:22.91614
'''

test_data_3 = '''
name,url,value
abc,,test
abcdef,,test2
def,http://xx.com,
'''

SATELLITE_SETTINGS_1 = '''
name,value,default
unregister_delete_host,"--- true
...","--- false
..."
destroy_vm_on_host_delete,,"--- true
..."
'''

SATELLITE_SETTINGS_2 = '''
name,value,default
unregister_delete_host,,"--- false
..."
destroy_vm_on_host_delete,,"--- true
..."
'''

SATELLITE_SETTINGS_3 = '''
name,value,default
unregister_delete_host,"--- false
...","--- true
..."
destroy_vm_on_host_delete,"--- false
...","--- true
..."
'''

SATELLITE_SETTINGS_WITH_DIFFERENT_TYPES = '''
name,value,default
http_proxy_except_list,,--- []
trusted_hosts,,--- []
oidc_audience,,--- []
ignored_interface_identifiers,,"---
- lo
- en*v*
- usb*
- vnet*
- macvtap*
- _vdsmdummy_
- veth*
- docker*
- tap*
- qbr*
- qvb*
- qvo*
- qr-*
- qg-*
- vlinuxbr*
- vovsbr*"
dns_timeout,,"---
- 5
- 10
- 15
- 20"
foreman_tasks_troubleshooting_url,,"--- https://access.redhat.com/solutions/satellite6-tasks#%{label}
..."
remote_execution_ssh_user,,"--- root
..."
foreman_tasks_sync_task_timeout,,"--- 120
..."
foreman_tasks_proxy_action_retry_count,,"--- 4
..."
'''

SATELLITE_SETTINGS_BAD_1 = '''
name,value
unregister_delete_host,"--- true
..."
destroy_vm_on_host_delete,
'''

SATELLITE_SETTINGS_BAD_2 = '''
name,value,default
unregister_delete_host,"--- true:: def
...","--- false
..."
destroy_vm_on_host_delete,,"--- true
..."
'''

SATELLITE_COMPUTE_RESOURCE_1 = '''
name,type
test_compute_resource1,Foreman::Model::Libvirt
test_compute_resource2,Foreman::Model::RHV
'''

SATELLITE_SCA_INFO_1 = '''
displayname,content_access_mode
Default Organization,entitlement
Orgq,org_environment
'''

SATELLITE_SCA_INFO_2 = '''
displayname,content_access_mode
Default Organization,entitlement
Orgq,entitlement
'''

SATELLITE_KATELLO_ROOT_REPOSITORIES = """
id,name
54,testa
55,testb
"""

SATELLITE_TASK_RESERVERDRESOURCE_CONTENT = """
count
0
"""

SATELLITE_QUERY_DATA1 = """
logname: no login name
/etc/profile.d/hkuser.sh: line 40: HISTFILE: readonly variable
id,name
1,Puppet_Base
""".strip()

SATELLITE_QUERY_DATA2 = """
logname: no login name
/etc/profile.d/hkuser.sh: line 40: HISTFILE: readonly variable
id,name
""".strip()

SATELLITE_QUERY_DATA3 = """
logname: no login name
/etc/profile.d/hkuser.sh: line 40: HISTFILE: readonly variable
""".strip()


def test_HTL_doc_examples():
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_1))
    resources_table = satellite_postgresql_query.SatelliteComputeResources(context_wrap(SATELLITE_COMPUTE_RESOURCE_1))
    sat_sca_info = satellite_postgresql_query.SatelliteSCAStatus(context_wrap(SATELLITE_SCA_INFO_1))
    repositories = satellite_postgresql_query.SatelliteKatelloEmptyURLRepositories(context_wrap(SATELLITE_KATELLO_ROOT_REPOSITORIES))
    tasks = satellite_postgresql_query.SatelliteCoreTaskReservedResourceCount(context_wrap(SATELLITE_TASK_RESERVERDRESOURCE_CONTENT))
    globs = {
        'table': settings,
        'resources_table': resources_table,
        'sat_sca_info': sat_sca_info,
        'katello_root_repositories': repositories,
        'tasks': tasks
    }
    failed, tested = doctest.testmod(satellite_postgresql_query, globs=globs)
    assert failed == 0


def test_basic_output_with_satellite_admin_setting():
    with pytest.raises(ContentException):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_1))
    with pytest.raises(ValueError):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_2))
    with pytest.raises(ValueError):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_3))
    with pytest.raises(ValueError):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_4))
    with pytest.raises(SkipException):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_5))


def test_satellite_admin_settings():
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_2))
    assert(len(settings)) == 2
    assert not settings.get_setting('unregister_delete_host')
    assert settings.get_setting('destroy_vm_on_host_delete')

    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_3))
    assert(len(settings)) == 2
    assert not settings.get_setting('unregister_delete_host')
    assert not settings.get_setting('destroy_vm_on_host_delete')
    assert settings.get_setting('non_exist_column') is None

    table = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_WITH_DIFFERENT_TYPES))
    setting_value = table.get_setting('ignored_interface_identifiers')
    assert isinstance(setting_value, list)
    for item in ['lo', 'en*v*', 'usb*', 'vnet*', 'macvtap*', '_vdsmdummy_', 'veth*',
                 'docker*', 'tap*', 'qbr*', 'qvb*', 'qvo*', 'qr-*', 'qg-*',
                 'vlinuxbr*', 'vovsbr*']:
        assert item in setting_value
    setting_value = table.get_setting('foreman_tasks_troubleshooting_url')
    assert isinstance(setting_value, str)
    assert setting_value == 'https://access.redhat.com/solutions/satellite6-tasks#%{label}'
    setting_value = table.get_setting('foreman_tasks_sync_task_timeout')
    assert isinstance(setting_value, int)
    assert setting_value == 120


def test_satellite_admin_settings_exception():
    with pytest.raises(ValueError):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_BAD_1))
    with pytest.raises(ParseException):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_BAD_2))


def test_satellite_compute_resources():
    resources_table = satellite_postgresql_query.SatelliteComputeResources(context_wrap(SATELLITE_COMPUTE_RESOURCE_1))
    assert len(resources_table) == 2
    rows = resources_table.search(type='Foreman::Model::RHV')
    assert len(rows) == 1
    assert rows[0]['name'] == 'test_compute_resource2'


def test_satellite_sca():
    sat_sca_info = satellite_postgresql_query.SatelliteSCAStatus(context_wrap(SATELLITE_SCA_INFO_2))
    assert not sat_sca_info.sca_enabled


def test_satellite_katello_empty_url_repositories():
    repositories = satellite_postgresql_query.SatelliteKatelloEmptyURLRepositories(context_wrap(SATELLITE_KATELLO_ROOT_REPOSITORIES))
    assert repositories[1]['name'] == 'testb'

    table = satellite_postgresql_query.SatelliteKatelloEmptyURLRepositories(context_wrap(SATELLITE_QUERY_DATA1))
    assert len(table) == 1
    assert table[0]['id'] == '1'
    assert table[0]['name'] == 'Puppet_Base'

    with pytest.raises(SkipException):
        satellite_postgresql_query.SatelliteKatelloEmptyURLRepositories(context_wrap(SATELLITE_QUERY_DATA2))

    with pytest.raises(ValueError):
        satellite_postgresql_query.SatelliteKatelloEmptyURLRepositories(context_wrap(SATELLITE_QUERY_DATA3))


def test_satellite_taskreservedresource():
    tasks = satellite_postgresql_query.SatelliteCoreTaskReservedResourceCount(context_wrap(SATELLITE_TASK_RESERVERDRESOURCE_CONTENT))
    assert tasks[0]['count'] == '0'
