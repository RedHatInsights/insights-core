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

from insights.parsers.dnsmasq_config import DnsmasqConf
from insights.tests import context_wrap

DNSMASQ_CONF_MAIN = """
# Listen on this specific port instead of the standard DNS port
# (53). Setting this to zero completely disables DNS function,
# leaving only DHCP and/or TFTP.
port=5353

no-resolv
domain-needed
no-negcache
max-cache-ttl=1
enable-dbus
dns-forward-max=5000
cache-size=5000
bind-dynamic
except-interface=lo
server=/in-addr.arpa/127.0.0.1
server=/cluster.local/127.0.0.1
# End of config
""".strip()

DNSMASQ_CONF_FILE_1 = """
server=/in-addr.arpa/127.0.0.1
server=/cluster.local/127.0.0.1
""".strip()


def test_dnsmasq_conf():
    result = DnsmasqConf(context_wrap(DNSMASQ_CONF_MAIN, path="/etc/dnsmasq.conf"))
    assert "no-resolv" in result
    assert result.find("port").value == 5353
    assert len(result.find_all("server")) == 2
    assert result.find_all("server")[0].value == '/in-addr.arpa/127.0.0.1'
    assert result.find("bind-dynamic").name == 'bind-dynamic'
    assert "# End of config" not in result


def test_dnsmasq_conf_file():
    result = DnsmasqConf(context_wrap(DNSMASQ_CONF_FILE_1, path="/etc/dnsmasq.d/dns-origin.conf"))
    assert len(result["server"]) == 2
    assert result["server"][-1].value == "/cluster.local/127.0.0.1"
