from insights.tests import context_wrap
from insights.parsers.sysconfig import SbdSysconfig

SBD_SYSCONFIG = """
SBD_DEVICE="/dev/disk/by-path/ip-198.20.25.163:3260-iscsi-iqn.2022-09.com.epmpttest:rhel85-lun-0"
SBD_DELAY_START=no
SBD_OPTS="-n emptytest"
SBD_PACEMAKER=yes
SBD_STARTMODE=always
SBD_WATCHDOG_DEV=/dev/watchdog
SBD_WATCHDOG_TIMEOUT=5
""".strip()


def test_sysconfig_sbd():
    result = SbdSysconfig(context_wrap(SBD_SYSCONFIG))
    assert result["SBD_DELAY_START"] == 'no'
    assert result.get("SBD_PACEMAKER") == 'yes'
    assert 'SBD_WATCHDOG_TIMEOUT' in result
    assert result.get('SBD_WATCHDOG_TIMEOUT') == '5'
    assert "OPTIONS1" not in result
