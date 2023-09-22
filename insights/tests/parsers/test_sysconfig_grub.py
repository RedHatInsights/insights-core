from insights.tests import context_wrap
from insights.parsers.sysconfig import GrubSysconfig

GRUB_SYSCONFIG = """

GRUB_TIMEOUT=1
GRUB_DISTRIBUTOR="$(sed 's, release .*$,,g' /etc/system-release)"
GRUB_DEFAULT=saved
GRUB_DISABLE_SUBMENU=true
GRUB_TERMINAL_OUTPUT="console"
GRUB_CMDLINE_LINUX="console=ttyS0 console=ttyS0,115200n8 no_timer_check net.ifnames=0 crashkernel=auto"
GRUB_DISABLE_RECOVERY="true"
GRUB_ENABLE_BLSCFG=true
""".strip()


def test_sysconfig_grub():
    result = GrubSysconfig(context_wrap(GRUB_SYSCONFIG))
    assert result["GRUB_ENABLE_BLSCFG"] == 'true'
    assert result.get("GRUB_ENABLE_BLSCFG") == 'true'
    assert result.get("NONEXISTENT_VAR") is None
    assert "NONEXISTENT_VAR" not in result
    assert "GRUB_ENABLE_BLSCFG" in result
