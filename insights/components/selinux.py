"""
SELinux related Components
==========================

This module provides components which check the SELinux status.

SELinuxEnabled - If SELinux is enabled
--------------------------------------

SELinuxDisabled - If SELinux is disabled
----------------------------------------
"""

from insights.core.exceptions import SkipComponent
from insights.core.plugins import component
from insights.parsers.selinux_config import SelinuxConfig
from insights.parsers.sestatus import SEStatus


@component([SEStatus, SelinuxConfig])
class SELinuxEnabled(object):
    """
    This ``SELinuxEnabled`` component will be skipped when SELinux is disabled,
    which means the SELinux is enabled in "enforcing" or "permissive" mode.

    Raises:
        SkipComponent: When SELinux is disabled
    """

    def __init__(self, ses, seconf):
        if ses:
            self.selinux = ses.get('selinux_status')
        else:
            self.selinux = seconf.get('SELINUX', 'disabled')

        if self.selinux == 'disabled':
            raise SkipComponent('SELinux not enabled')


@component([SEStatus, SelinuxConfig])
class SELinuxDisabled(object):
    """
    This ``SELinuxDisabled`` component will be skipped when SELinux is enabled
    in "enforcing" or "permissive" mode, which means the SELinux is disabled.

    Raises:
        SkipComponent: When SELinux is "enforcing" or "permissive".
    """

    def __init__(self, ses, seconf):
        if ses:
            self.selinux = ses.get('selinux_status')
        else:
            self.selinux = seconf.get('SELINUX', 'disabled')

        if self.selinux != 'disabled':
            raise SkipComponent('SELinux is enabled')
