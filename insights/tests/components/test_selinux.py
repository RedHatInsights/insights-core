import pytest

from insights import SkipComponent
from insights.components.selinux import SELinuxEnabled, SELinuxDisabled
from insights.parsers.selinux_config import SelinuxConfig
from insights.parsers.sestatus import SEStatus
from insights.tests import context_wrap

SESTATUS_ENFORCING = """
SELinux status:                 enabled
Current mode:                   enforcing
"""

SESTATUS_PERMISSIVE = """
SELinux status:                 enabled
Current mode:                   permissive
"""

SESTATUS_DISABLED = """
SELinux status:                 disabled
"""

SELINUX_CONFIG = """
SELINUX=enforcing
SELINUXTYPE=targeted
"""
SELINUX_CONFIG_DISABLED = """
SELINUX=disabled
SELINUXTYPE=targeted
"""


def test_selinux_enabled():
    conf = SelinuxConfig(context_wrap(SELINUX_CONFIG))
    result = SELinuxEnabled(None, conf)
    assert isinstance(result, SELinuxEnabled)

    conf = SelinuxConfig(context_wrap(SELINUX_CONFIG_DISABLED))
    with pytest.raises(SkipComponent):
        SELinuxEnabled(None, conf)

    conf = SelinuxConfig(context_wrap(SELINUX_CONFIG_DISABLED))
    with pytest.raises(SkipComponent):
        SELinuxEnabled(None, conf)

    ses = SEStatus(context_wrap(SESTATUS_ENFORCING))
    result = SELinuxEnabled(ses, conf)
    assert isinstance(result, SELinuxEnabled)

    ses = SEStatus(context_wrap(SESTATUS_PERMISSIVE))
    result = SELinuxEnabled(ses, conf)
    assert isinstance(result, SELinuxEnabled)

    ses = SEStatus(context_wrap(SESTATUS_DISABLED))
    with pytest.raises(SkipComponent):
        SELinuxEnabled(ses, conf)


def test_selinux_disabled():
    conf = SelinuxConfig(context_wrap(SELINUX_CONFIG_DISABLED))
    result = SELinuxDisabled(None, conf)
    assert isinstance(result, SELinuxDisabled)

    ses = SEStatus(context_wrap(SESTATUS_ENFORCING))
    with pytest.raises(SkipComponent):
        SELinuxDisabled(ses, conf)

    ses = SEStatus(context_wrap(SESTATUS_PERMISSIVE))
    with pytest.raises(SkipComponent):
        SELinuxDisabled(ses, conf)

    ses = SEStatus(context_wrap(SESTATUS_DISABLED))
    result = SELinuxDisabled(ses, conf)
    assert isinstance(result, SELinuxDisabled)
