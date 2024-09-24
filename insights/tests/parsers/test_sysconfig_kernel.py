from insights.parsers.sysconfig import KernelSysconfig
from insights.tests import context_wrap

SYSCONFIG_KERNEL = """
# UPDATEDEFAULT specifies if new-kernel-pkg should make
# new kernels the default
UPDATEDEFAULT=yes

# DEFAULTKERNEL specifies the default kernel package type
DEFAULTKERNEL=kernel

# MAKEDEBUG specifies if new-kernel-pkg should create non-default
# "debug" entries for new kernels.
MAKEDEBUG=yes
""".strip()


def test_sysconfig_nfs():
    result = KernelSysconfig(context_wrap(SYSCONFIG_KERNEL))
    assert result['UPDATEDEFAULT'] == 'yes'
    assert result.get('DEFAULTKERNEL') == 'kernel'
    assert result.get('MAKEDEBUG') == 'yes'
