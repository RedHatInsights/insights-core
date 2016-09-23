from falafel.mappers.libvirtd_log import LibVirtdLog
from falafel.tests import context_wrap

LIBVIRTD_LOG = """
2013-10-23 17:32:19.909+0000: 14069: debug : virConnectOpen:1331 : name=qemu+tls://AA.BB.CC.DD/system
2013-10-23 17:32:19.909+0000: 14069: debug : virConnectGetConfigFile:953 : Loading config file '/etc/libvirt/libvirt.conf'
2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1127 : name "qemu+tls://AA.BB.CC.DD/system" to URI components:
  scheme qemu+tls
  server AA.BB.CC.DD
  user (null)
  port 0
  path /system

2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1174 : trying driver 0 (Test) ...
2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1180 : driver 0 Test returned DECLINED
2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1174 : trying driver 1 (ESX) ...
2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1180 : driver 1 ESX returned DECLINED
2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1174 : trying driver 2 (remote) ...
2013-10-23 17:32:19.957+0000: 14069: error : virNetTLSContextCheckCertDN:418 : Certificate [session] owner does not match the hostname AA.BB.CC.DD <============= IP Address
2013-10-23 17:32:19.957+0000: 14069: warning : virNetTLSContextCheckCertificate:1102 : Certificate check failed Certificate [session] owner does not match the hostname AA.BB.CC.DD
2013-10-23 17:32:19.957+0000: 14069: error : virNetTLSContextCheckCertificate:1105 : authentication failed: Failed to verify peer's certificate

"""


def test_libvirtd_log():
    log = LibVirtdLog.parse_context(context_wrap(LIBVIRTD_LOG))
    assert "Certificate check failed Certificate" in log

    assert log.get("authentication failed: Failed to verify peer's certificate") == ["2013-10-23 17:32:19.957+0000: 14069: error : virNetTLSContextCheckCertificate:1105 : authentication failed: Failed to verify peer's certificate"]
