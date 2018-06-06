from .. import parser, LegacyItemAccess, CommandParser
from insights.specs import Specs


@parser(Specs.sestatus)
class SEStatus(LegacyItemAccess, CommandParser):
    """Class to parse the ``sestatus -b`` command

    Attributes:
        data (dict): A dict likes
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

    ---Sample---
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
    """

    def parse_content(self, content):
        # Default to disabled if not found
        sestatus_info = {
            'loaded_policy_name': None,
            'current_mode': 'disabled',
            'mode_from_config_file': 'disabled',
            'policy_mls_status': 'disabled',
            'policy_deny_unknown_status': 'disabled',
            'max_kernel_policy_version': None,
            'policy_booleans': {},
        }

        for line in content:
            if ":" in line:
                if 'Policy booleans' in line:
                    pass
                else:
                    key, val = [s.strip() for s in line.split(":", 1)]
                    sestatus_info[key.lower().replace(" ", "_")] = val
            else:
                if line.strip():
                    key, val = line.split()
                    #  convert 'on' and 'off' strings to actual boolean values
                    sestatus_info['policy_booleans'][key] = val == 'on'

        # When SELinux is disabled, sestatus has simply 'SELinux status: disabled'
        # in its output.  But 'SELinux status' is not included in the output
        # when SELinux is enabled.  So we include it as a nicety.
        if sestatus_info['current_mode'] != 'disabled' and 'selinux_status' not in sestatus_info:
            sestatus_info['selinux_status'] = sestatus_info['current_mode']

        self.data = sestatus_info
