from insights.tests import context_wrap
from insights.parsers.sysconfig import PcsdSysconfig

PCSD_SYSCONFIG = """
# Set PCSD_DEBUG to true for advanced pcsd debugging information
PCSD_DEBUG=false
# Set DISABLE_GUI to true to disable GUI frontend in pcsd
PCSD_DISABLE_GUI=false
# Set web UI sesions lifetime in seconds
PCSD_SESSION_LIFETIME=3600
# List of IP addresses pcsd should bind to delimited by ',' character
#PCSD_BIND_ADDR='::'
""".strip()


def test_sysconfig_virt_who():
    result = PcsdSysconfig(context_wrap(PCSD_SYSCONFIG))
    assert result["PCSD_DEBUG"] == 'false'
    assert result["PCSD_SESSION_LIFETIME"] == '3600'
    assert "NOSUCHOPTIONS" not in result
