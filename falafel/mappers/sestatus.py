from falafel.core.plugins import mapper
from falafel.core import MapperOutput


@mapper('sestatus')
class SEStatus(MapperOutput):

    @staticmethod
    def parse_content(content):
        '''
        Return the 'sestatus -b' information as a dict.
        Input:
        ------------------
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
        ...
        ------------------
        The output will look like:
        {
            "loaded_policy_name": "targeted",
            "policy_booleans": {
                "antivirus_use_jit": False,
                "abrt_anon_write": False,
                "abrt_upload_watch_anon_write": True,
                "antivirus_can_scan_system": False,
                "abrt_handle_event": False,
                "auditadm_exec_content": True,
            },
            "mode_from_config_file": "enforcing",
            "current_mode": "enforcing",
            "policy_mls_status": "enabled",
            "policy_deny_unknown_status": "allowed",
            "max_kernel_policy_version": "30"
        }
        '''
        sestatus_info = {}
        booleans = {}

        for line in content:
            if ":" in line:
                if 'Policy booleans' in line:
                    sestatus_info['policy_booleans'] = {}
                else:
                    key, val = line.split(":", 1)
                    sestatus_info[key.strip().lower().replace(" ", "_")] = val.strip()
            else:
                if line.strip():
                    key, val = line.split()
                    #  convert 'on' and 'off' strings to actual boolean values
                    booleans[key] = val == 'on'

        if 'policy_booleans' in sestatus_info:
            sestatus_info['policy_booleans'] = booleans

        return sestatus_info
