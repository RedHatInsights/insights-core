from falafel.mappers.sestatus import SEStatus
from falafel.tests import context_wrap


SESTATUS = '''
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


def test_sestatus():
    sestatus_info = SEStatus(context_wrap(SESTATUS)).data

    assert sestatus_info['loaded_policy_name'] == 'targeted'
    assert sestatus_info['current_mode'] == 'enforcing'
    assert sestatus_info['mode_from_config_file'] == 'enforcing'
    assert sestatus_info['policy_mls_status'] == 'enabled'
    assert sestatus_info['policy_deny_unknown_status'] == 'allowed'
    assert sestatus_info['max_kernel_policy_version'] == '30'
    assert sestatus_info['policy_booleans'] == {'abrt_anon_write': False,
                                                'abrt_handle_event': False,
                                                'abrt_upload_watch_anon_write': True,
                                                'antivirus_can_scan_system': False,
                                                'antivirus_use_jit': False,
                                                'auditadm_exec_content': True}
