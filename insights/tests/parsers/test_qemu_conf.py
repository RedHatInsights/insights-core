from insights.tests import context_wrap
from insights.parsers.qemu_conf import QemuConf

qemu_conf_content = """
   vnc_listen = "0.0.0.0"

   vnc_auto_unix_socket = 1
   vnc_tls = 1
   # comment line
   vnc_tls_x509_cert_dir = "/etc/pki/libvirt-vnc"
   security_driver = "selinux"    #inline comment
   cgroup_device_acl = [
    "/dev/null", "/dev/full", "/dev/zero",
    "/dev/random", "/dev/urandom",
    "/dev/ptmx", "/dev/kvm", "/dev/kqemu",
    "/dev/rtc","/dev/hpet", "/dev/vfio/vfio"
    ]
"""

qemu_conf_comment = """
    # comment line
    # comment line
"""


def test_sssd_conf():
    result = QemuConf(context_wrap(qemu_conf_content))
    assert result.get("vnc_listen") == '0.0.0.0'
    assert result.get("vnc_tls") == '1'
    assert "/dev/zero" in result.get('cgroup_device_acl')
    assert result.get('security_driver') == 'selinux'
    assert isinstance(result.get('cgroup_device_acl'), list)

    result = QemuConf(context_wrap(qemu_conf_comment))
    assert result.data == {}
