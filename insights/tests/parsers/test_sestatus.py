from insights.parsers.sestatus import SEStatus
from insights.tests import context_wrap


SESTATUS_ENFORCING = '''
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
Policy MLS status:              enabled
Policy deny_unknown status:     allowed
Max kernel policy version:      30

Policy booleans:
abrt_anon_write                             off
abrt_handle_event                           off
abrt_upload_watch_anon_write                on
antivirus_can_scan_system                   off
antivirus_use_jit                           off
auditadm_exec_content                       on
'''

SESTATUS_PERMISSIVE = '''
SELinux status:                 enabled
SELinuxfs mount:                /sys/fs/selinux
SELinux root directory:         /etc/selinux
Loaded policy name:             targeted
Current mode:                   permissive
Mode from config file:          permissive
Policy MLS status:              enabled
Policy deny_unknown status:     allowed
Max kernel policy version:      28

Policy booleans:
abrt_anon_write                             off
abrt_handle_event                           off
abrt_upload_watch_anon_write                on
antivirus_can_scan_system                   off
antivirus_use_jit                           off
auditadm_exec_content                       on
authlogin_nsswitch_use_ldap                 on
authlogin_radius                            off
authlogin_yubikey                           off
awstats_purge_apache_log_files              off
'''

SESTATUS_DISABLED = '''
SELinux status:                 disabled
'''


def test_sestatus():
    sestatus_info = SEStatus(context_wrap(SESTATUS_ENFORCING)).data

    assert sestatus_info['loaded_policy_name'] == 'targeted'
    assert sestatus_info['current_mode'] == 'enforcing'
    assert sestatus_info['mode_from_config_file'] == 'enforcing'
    assert sestatus_info['policy_mls_status'] == 'enabled'
    assert sestatus_info['policy_deny_unknown_status'] == 'allowed'
    assert sestatus_info['max_kernel_policy_version'] == '30'
    assert sestatus_info['selinux_status'] == 'enforcing'
    assert sestatus_info['policy_booleans'] == {'abrt_anon_write': False,
                                                'abrt_handle_event': False,
                                                'abrt_upload_watch_anon_write': True,
                                                'antivirus_can_scan_system': False,
                                                'antivirus_use_jit': False,
                                                'auditadm_exec_content': True}
    assert sorted(sestatus_info) == sorted([
        'loaded_policy_name', 'current_mode', 'mode_from_config_file',
        'policy_mls_status', 'policy_deny_unknown_status',
        'max_kernel_policy_version', 'policy_booleans', 'selinux_status'
    ])

    perm_info = SEStatus(context_wrap(SESTATUS_PERMISSIVE))
    assert perm_info is not None
    assert perm_info.data
    assert 'selinux_status' in perm_info.data
    assert perm_info.data['selinux_status'] == 'enabled'
    assert perm_info.data['selinuxfs_mount'] == '/sys/fs/selinux'
    assert perm_info.data['selinux_root_directory'] == '/etc/selinux'
    assert perm_info.data['loaded_policy_name'] == 'targeted'
    assert perm_info.data['current_mode'] == 'permissive'
    assert perm_info.data['mode_from_config_file'] == 'permissive'
    assert perm_info.data['policy_mls_status'] == 'enabled'
    assert perm_info.data['policy_deny_unknown_status'] == 'allowed'
    assert perm_info.data['max_kernel_policy_version'] == '28'
    assert perm_info.data['policy_booleans'] == {
        'abrt_anon_write': False,
        'abrt_handle_event': False,
        'abrt_upload_watch_anon_write': True,
        'antivirus_can_scan_system': False,
        'antivirus_use_jit': False,
        'auditadm_exec_content': True,
        'authlogin_nsswitch_use_ldap': True,
        'authlogin_radius': False,
        'authlogin_yubikey': False,
        'awstats_purge_apache_log_files': False,
    }

    disabled_info = SEStatus(context_wrap(SESTATUS_DISABLED))
    assert disabled_info is not None
    assert disabled_info.data
    assert disabled_info.data['loaded_policy_name'] is None
    assert disabled_info.data['current_mode'] == 'disabled'
    assert disabled_info.data['mode_from_config_file'] == 'disabled'
    assert disabled_info.data['policy_mls_status'] == 'disabled'
    assert disabled_info.data['policy_deny_unknown_status'] == 'disabled'
    assert disabled_info.data['max_kernel_policy_version'] is None
    assert 'selinux_status' in disabled_info.data
    assert disabled_info.data['selinux_status'] == 'disabled'
    assert disabled_info.data['policy_booleans'] == {}
