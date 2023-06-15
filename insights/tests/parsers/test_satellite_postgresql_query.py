import doctest
import pytest

from insights.core.exceptions import ContentException, ParseException, SkipComponent
from insights.parsers import satellite_postgresql_query
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

SATELLITE_CAPSULES_WITH_BACKGROUND_DOWNLOADPOLICY = """
name
capsule1.test.com
capsule2.test.com
"""

SATELLITE_CAPSULES_WITH_BACKGROUND_DOWNLOADPOLICY_2 = """
name
Last login: Sun May  8 01:51:06 EDT 2022
"""

SATELLITE_REPOS_INFO = """
id,name,url,download_policy
2,Red Hat Satellite Tools 6.8 for RHEL 7 Server RPMs x86_64,,on_demand
3,Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8,https://xx.xx.com/rhel8/8/x86_64/appstream/os,background
4,Red Hat Enterprise Linux 7 Server RPMs x86_64 7Server,https://xx.xx.com/server/7/7Server/x86_64/os,background
"""

SATELLITE_KATELLO_REPOS_WITH_MULTI_REF = """
repository_href,count
/pulp/api/v3/repositories/rpm/rpm/64e1ddf8-025e-45f2-b2f0-04b874674671/,3
/pulp/api/v3/repositories/rpm/rpm/sfwrsrw45sfse-45f2-b2f0-04b874675688/,2
""".strip()

SATELLITE_PROVISION_PARAMETERS_HIT_1 = """
name,value
package_upgrade,"--- false
...
"
"""

SATELLITE_PROVISION_PARAMETERS_HIT_2 = """
name,value
"""

SATELLITE_LOGS_TABLE_SIZE1 = """
logs_size
565248
""".strip()

SATELLITE_LOGS_TABLE_SIZE2 = """
logs_size
578813952
""".strip()

SATELLITE_LOGS_TABLE_SIZE3 = """
logs_size
abc
""".strip()

SATELLITE_RHV_HOSTS_COUNT = """
count
2
""".strip()

SATELLITE_IGNORE_SOURCE_RPMS_REPOS = """
id,name
4,Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8
7,Red Hat Enterprise Linux 8 for x86_64 - BaseOS RPMs 8
""".strip()


def test_HTL_doc_examples():
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_1))
    resources_table = satellite_postgresql_query.SatelliteComputeResources(context_wrap(SATELLITE_COMPUTE_RESOURCE_1))
    sat_sca_info = satellite_postgresql_query.SatelliteSCAStatus(context_wrap(SATELLITE_SCA_INFO_1))
    tasks = satellite_postgresql_query.SatelliteCoreTaskReservedResourceCount(context_wrap(SATELLITE_TASK_RESERVERDRESOURCE_CONTENT))
    capsules = satellite_postgresql_query.SatelliteQualifiedCapsules(context_wrap(SATELLITE_CAPSULES_WITH_BACKGROUND_DOWNLOADPOLICY))
    repos = satellite_postgresql_query.SatelliteQualifiedKatelloRepos(context_wrap(SATELLITE_REPOS_INFO))
    multi_ref_katello_repos = satellite_postgresql_query.SatelliteKatellloReposWithMultipleRef(context_wrap(SATELLITE_KATELLO_REPOS_WITH_MULTI_REF))
    param_settings = satellite_postgresql_query.SatelliteProvisionParamSettings(context_wrap(SATELLITE_PROVISION_PARAMETERS_HIT_1))
    logs_table = satellite_postgresql_query.SatelliteLogsTableSize(context_wrap(SATELLITE_LOGS_TABLE_SIZE1))
    rhv_hosts = satellite_postgresql_query.SatelliteRHVHostsCount(context_wrap(SATELLITE_RHV_HOSTS_COUNT))
    ignore_srpm_repos = satellite_postgresql_query.SatelliteIgnoreSourceRpmsRepos(context_wrap(SATELLITE_IGNORE_SOURCE_RPMS_REPOS))
    globs = {
        'table': settings,
        'resources_table': resources_table,
        'sat_sca_info': sat_sca_info,
        'tasks': tasks,
        'capsules': capsules,
        'repos': repos,
        'multi_ref_katello_repos': multi_ref_katello_repos,
        'param_settings': param_settings,
        'logs_table': logs_table,
        'rhv_hosts': rhv_hosts,
        'i_srpm_repos': ignore_srpm_repos
    }
    failed, _ = doctest.testmod(satellite_postgresql_query, globs=globs)
    assert failed == 0


def test_no_headers():
    with pytest.raises(NotImplementedError):
        satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(SATELLITE_POSTGRESQL_WRONG_4))


def test_basic_output_with_satellite_admin_setting():
    with pytest.raises(ContentException):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_1))
    with pytest.raises(ValueError):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_2))
    with pytest.raises(ValueError):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_3))
    with pytest.raises(ValueError):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_4))
    with pytest.raises(SkipComponent):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_POSTGRESQL_WRONG_5))


def test_satellite_admin_settings():
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_2))
    assert (len(settings)) == 2
    assert not settings.get_setting('unregister_delete_host')
    assert settings.get_setting('destroy_vm_on_host_delete')

    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_3))
    assert (len(settings)) == 2
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


def test_satellite_taskreservedresource():
    tasks = satellite_postgresql_query.SatelliteCoreTaskReservedResourceCount(context_wrap(SATELLITE_TASK_RESERVERDRESOURCE_CONTENT))
    assert tasks[0]['count'] == '0'


def test_satellite_qulified_capsules():
    capsules = satellite_postgresql_query.SatelliteQualifiedCapsules(context_wrap(SATELLITE_CAPSULES_WITH_BACKGROUND_DOWNLOADPOLICY))
    assert len(capsules) == 2
    assert capsules[0]['name'] == 'capsule1.test.com'

    with pytest.raises(SkipComponent):
        satellite_postgresql_query.SatelliteQualifiedCapsules(context_wrap(SATELLITE_CAPSULES_WITH_BACKGROUND_DOWNLOADPOLICY_2))


def test_satellite_qulified_repos():
    repos = satellite_postgresql_query.SatelliteQualifiedKatelloRepos(context_wrap(SATELLITE_REPOS_INFO))
    assert len(repos) == 3
    assert repos[0]['name'] == 'Red Hat Satellite Tools 6.8 for RHEL 7 Server RPMs x86_64'
    background_repos = repos.search(download_policy='background')
    assert len(background_repos) == 2
    assert background_repos[0]['name'] == 'Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8'


def test_satellite_repos_with_multiptle_ref():
    repos = satellite_postgresql_query.SatelliteKatellloReposWithMultipleRef(context_wrap(SATELLITE_KATELLO_REPOS_WITH_MULTI_REF))
    assert len(repos) == 2
    assert repos[0]['repository_href'] == '/pulp/api/v3/repositories/rpm/rpm/64e1ddf8-025e-45f2-b2f0-04b874674671/'


def test_satellite_provision_params():
    param_settings = satellite_postgresql_query.SatelliteProvisionParamSettings(context_wrap(SATELLITE_PROVISION_PARAMETERS_HIT_1))
    assert len(param_settings) == 1
    assert not param_settings[0]['value']


def test_satellite_provision_params_excep():
    with pytest.raises(SkipComponent):
        satellite_postgresql_query.SatelliteProvisionParamSettings(context_wrap(SATELLITE_PROVISION_PARAMETERS_HIT_2))


def test_satellite_logs_table_size():
    logs_table = satellite_postgresql_query.SatelliteLogsTableSize(context_wrap(SATELLITE_LOGS_TABLE_SIZE2))
    assert len(logs_table) == 1
    assert logs_table[0]['logs_size'] == 552 * 1024 * 1024


def test_satelite_rhv_hosts():
    rhv_hosts = satellite_postgresql_query.SatelliteRHVHostsCount(context_wrap(SATELLITE_RHV_HOSTS_COUNT))
    assert len(rhv_hosts) == 1
    assert int(rhv_hosts[0]['count']) == 2


def test_satellite_logs_table_size_except():
    with pytest.raises(ParseException):
        satellite_postgresql_query.SatelliteLogsTableSize(context_wrap(SATELLITE_LOGS_TABLE_SIZE3))


def test_satellite_ignore_srpm_repos():
    i_srpms_repos = satellite_postgresql_query.SatelliteIgnoreSourceRpmsRepos(context_wrap(SATELLITE_IGNORE_SOURCE_RPMS_REPOS))
    assert len(i_srpms_repos) == 2
    assert i_srpms_repos[0]['id'] == '4'
    assert i_srpms_repos[0]['name'] == 'Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8'
    assert i_srpms_repos[1]['id'] == '7'
    assert i_srpms_repos[1]['name'] == 'Red Hat Enterprise Linux 8 for x86_64 - BaseOS RPMs 8'
