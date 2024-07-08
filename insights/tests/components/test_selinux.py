import pytest

from insights import SkipComponent
from insights.components.selinux import SELinuxEnabled
from insights.parsers.selinux_config import SelinuxConfig
from insights.tests import context_wrap

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
    result = SELinuxEnabled(conf)
    assert isinstance(result, SELinuxEnabled)

    conf = SelinuxConfig(context_wrap(SELINUX_CONFIG_DISABLED))
    with pytest.raises(SkipComponent):
        SELinuxEnabled(conf)
