from insights.parsers import getsebool
from insights.tests import context_wrap


GETSEBOOL = """
varnishd_connect_any --> off
virt_read_qemu_ga_data --> off
virt_rw_qemu_ga_data --> off
virt_sandbox_use_all_caps --> on
virt_sandbox_use_audit --> on
virt_sandbox_use_fusefs --> off
virt_sandbox_use_mknod --> off
virt_sandbox_use_netlink --> off
virt_sandbox_use_sys_admin --> off
virt_transition_userdomain --> off
virt_use_comm --> off
virt_use_execmem --> off
virt_use_fusefs --> off
virt_use_glusterd --> off
virt_use_nfs --> on
virt_use_rawip --> off
virt_use_samba --> off
virt_use_sanlock --> off
virt_use_usb --> on
virt_use_xserver --> off
""".strip()


def test_getsebool():
    result = getsebool.Getsebool(context_wrap(GETSEBOOL))
    assert result["varnishd_connect_any"] == 'off'
    assert result["virt_use_nfs"] == 'on'
    assert "virt_use_xserver" in result
    assert "not_exist_key" not in result
