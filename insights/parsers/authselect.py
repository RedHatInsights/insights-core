"""
AuthSelectCurrent - command ``authselect current``
==================================================
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.authselect_current)
class AuthSelectCurrent(CommandParser):
    """
    Class to parse the output of command "authselect current".

    Sample output of command ``authselect current``::

        Profile ID: sssd
        Enabled features:
        - with-sudo
        - with-mkhomedir
        - with-smartcard

    Attributes:
        profile_id (str): The enabled profile ID
        enabled_features (list): List of enabled features

    Examples:
        >>> asc.profile_id
        'sssd'
        >>> len(asc.enabled_features)
        3
        >>> 'with-sudo' in asc.enabled_features
        True
    """
    def parse_content(self, content):
        feature_flag = False
        self.profile_id = None
        self.enabled_features = []
        for line in content:
            if 'No existing configuration detected.' in line:
                raise SkipComponent
            line_sp = line.split()
            if line.startswith('Profile ID:'):
                self.profile_id = line_sp[-1]
            elif line.endswith('Enabled features:'):
                # Enabled features:
                # - ...
                feature_flag = True
            elif line.startswith('Enabled features:') and len(line_sp) > 2:
                # Enabled features: None
                feature_flag = True
                if line_sp[-1] != 'None':
                    self.enabled_features.append(line_sp[-1])
            elif line.startswith('-') and feature_flag:
                self.enabled_features.append(line_sp[-1])
        if self.profile_id is None:
            raise SkipComponent
