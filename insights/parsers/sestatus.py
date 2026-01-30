"""
SEStatus - command ``sestatus -b``
==================================
"""

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.sestatus)
class SEStatus(CommandParser, dict):
    """
    Class to parse the output of ``sestatus -b`` command into a Python dictionary
    with names mangled as below:
    - All characters are converted to lowercase
    - All blank spaces are converted to underline
    - All policy-booleans items are put as the value of "Policy booleans"

    Sample output of ``sestatus -b``::

        SELinux status:                 enabled
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

    Example:
        >>> type(sestatus)
        <class 'insights.parsers.sestatus.SEStatus'>
        >>> sestatus['selinux_status']
        'enabled'
        >>> sestatus['policy_booleans']['abrt_anon_write']
        False

    """

    def parse_content(self, content):
        # Backward compatible
        # - Default to disabled if not found
        self.update(
            loaded_policy_name=None,
            current_mode='disabled',
            mode_from_config_file='disabled',
            policy_mls_status='disabled',
            policy_deny_unknown_status='disabled',
            max_kernel_policy_version=None,
            policy_booleans={},
        )

        for line in content:
            line = line.strip()
            if ":" in line:
                if 'Policy booleans' in line:
                    self['policy_booleans'] = {}
                else:
                    key, val = [s.strip() for s in line.split(":", 1)]
                    self[key.lower().replace(" ", "_")] = val
            elif line:
                key, val = line.split()
                #  convert 'on' and 'off' strings to actual boolean values
                self['policy_booleans'][key] = val == 'on'

        # Backward compatible
        # - "SELinux status" now are always printed
        if 'selinux_status' not in self and 'current_mode' in self:
            self['selinux_status'] = self['current_mode']

    # Backward compatible
    data = property(lambda self: self)
