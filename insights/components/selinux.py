"""
SELinuxEnabled
==============

The ``SELinuxEnabled`` component uses ``SelinuxConfig`` parser to determine if
SELinux is enabled or not.  The ``SkipComponent`` will be raised only when
"SELINUX=disabled" is set.
"""
from insights.core.exceptions import SkipComponent
from insights.core.plugins import component
from insights.parsers.selinux_config import SelinuxConfig


@component(SelinuxConfig)
class SELinuxEnabled(object):
    """
    Raises:
        SkipComponent: When ``SELINUX=disabled`` is set.
    """
    def __init__(self, seconf):
        self.selinux = seconf.get('SELINUX')
        if self.selinux == 'disabled':
            raise SkipComponent("SELinux not enabled")
