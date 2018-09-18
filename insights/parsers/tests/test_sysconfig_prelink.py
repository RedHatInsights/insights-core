from insights.tests import context_wrap
from insights.parsers.sysconfig import PrelinkSysconfig

PRELINK_SYSCONFIG = """
# Set this to no to disable prelinking altogether
# (if you change this from yes to no prelink -ua
# will be run next night to undo prelinking)
PRELINKING=no

# Options to pass to prelink
# -m    Try to conserve virtual memory by allowing overlapping
#       assigned virtual memory slots for libraries which
#       never appear together in one binary
# -R    Randomize virtual memory slot assignments for libraries.
#       This makes it slightly harder for various buffer overflow
#       attacks, since library addresses will be different on each
#       host using -R.
PRELINK_OPTS=-mR

# How often should full prelink be run (in days)
# Normally, prelink will be run in quick mode, every
# $PRELINK_FULL_TIME_INTERVAL days it will be run
# in normal mode.  Comment it out if it should be run
# in normal mode always.
PRELINK_FULL_TIME_INTERVAL=14

# How often should prelink run (in days) even if
# no packages have been upgraded via rpm.
# If $PRELINK_FULL_TIME_INTERVAL days have not elapsed
# yet since last normal mode prelinking, last
# quick mode prelinking happened less than
# $PRELINK_NONRPM_CHECK_INTERVAL days ago
# and no packages have been upgraded by rpm
# since last quick mode prelinking, prelink
# will not do anything.
# Change to
# PRELINK_NONRPM_CHECK_INTERVAL=0
# if you want to disable the rpm database timestamp
# check (especially if you don't use rpm/up2date/yum/apt-rpm
# exclusively to upgrade system libraries and/or binaries).
PRELINK_NONRPM_CHECK_INTERVAL=7
""".strip()


def test_sysconfig_prelink():
    result = PrelinkSysconfig(context_wrap(PRELINK_SYSCONFIG))
    assert result["PRELINKING"] == 'no'
    assert result.get("PRELINK_OPTS") == '-mR'
    assert result.get("OPTIONS1") is None
    assert result['PRELINK_NONRPM_CHECK_INTERVAL'] == "7"
