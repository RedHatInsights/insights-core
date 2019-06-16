#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.parsers.libvirtd_log import LibVirtdLog
from insights.tests import context_wrap

from datetime import datetime

LIBVIRTD_LOG = """
2013-10-23 17:32:18.909+0000: 14069: debug : virConnectOpen:1331 : name=qemu+tls://AA.BB.CC.DD/system
2013-10-23 17:32:18.909+0000: 14069: debug : virConnectGetConfigFile:953 : Loading config file '/etc/libvirt/libvirt.conf'
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

""".strip()


def test_libvirtd_log():
    log = LibVirtdLog(context_wrap(LIBVIRTD_LOG))
    assert "Certificate check failed Certificate" in log

    assert log.get("authentication failed: Failed to verify peer's certificate")[0]['raw_message'] == \
            "2013-10-23 17:32:19.957+0000: 14069: error : virNetTLSContextCheckCertificate:1105 : authentication failed: Failed to verify peer's certificate"
    # Includes continuation of URI component expansion
    assert len(list(log.get_after(datetime(2013, 10, 23, 17, 32, 19)))) == 15
