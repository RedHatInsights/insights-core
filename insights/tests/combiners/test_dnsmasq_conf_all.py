from insights.parsers.dnsmasq_config import DnsmasqConf
from insights.combiners.dnsmasq_conf_all import DnsmasqConfTree
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

DNSMASQ_CONF_MAIN_CONF_DIR = """
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
conf-dir=/etc/dnsmasq.d
# End of config
""".strip()

DNSMASQ_CONF_MAIN_EXCLUDE_CONF_DIR = """
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
conf-dir=/etc/dnsmasq.d,.conf
# End of config
""".strip()

DNSMASQ_CONF_MAIN_INCLUDE_CONF_DIR = """
enable-dbus
dns-forward-max=5000
cache-size=5000
bind-dynamic
except-interface=lo
server=/in-addr.arpa/127.0.0.1
server=/cluster.local/127.0.0.1
conf-dir=/etc/dnsmasq.d,*.conf
# End of config
""".strip()

DNSMASQ_CONF_FILE_1 = """
server=/in-addr.arpa/127.0.0.1
log-queries
txt-record=example.com,"v=spf1 a -all"
""".strip()

DNSMASQ_CONF_FILE_2 = """
dns-forward-max=10000
no-resolv
domain-needed
no-negcache
max-cache-ttl=1
enable-dbus
""".strip()


def test_no_conf_dir():
    # no conf-dir
    dnsmasq1 = DnsmasqConf(context_wrap(DNSMASQ_CONF_MAIN, path="/etc/dnsmasq.conf"))
    dnsmasq2 = DnsmasqConf(context_wrap(DNSMASQ_CONF_FILE_1, path="/etc/dnsmasq.d/origin-dns.conf"))
    result = DnsmasqConfTree([dnsmasq1, dnsmasq2])
    assert "domain-needed" in result
    assert "log-queries" not in result
    assert len(result["server"]) == 2


def test_conf_dir():
    dnsmasq1 = DnsmasqConf(context_wrap(DNSMASQ_CONF_MAIN_CONF_DIR, path="/etc/dnsmasq.conf"))
    dnsmasq2 = DnsmasqConf(context_wrap(DNSMASQ_CONF_FILE_1, path="/etc/dnsmasq.d/origin-dns.conf"))
    result = DnsmasqConfTree([dnsmasq1, dnsmasq2])
    assert "txt-record" in result
    assert len(result["server"]) == 3

    dnsmasq1 = DnsmasqConf(context_wrap(DNSMASQ_CONF_MAIN_CONF_DIR, path="/etc/dnsmasq.conf"))
    dnsmasq2 = DnsmasqConf(context_wrap(DNSMASQ_CONF_FILE_2, path="/etc/dnsmasq.d/dns-forward-max.conf"))
    result = DnsmasqConfTree([dnsmasq1, dnsmasq2])
    assert len(result["dns-forward-max"]) == 2
    assert result["dns-forward-max"][-1].value == 10000


def test_exclude_conf_dir():
    dnsmasq1 = DnsmasqConf(context_wrap(DNSMASQ_CONF_MAIN_EXCLUDE_CONF_DIR, path="/etc/dnsmasq.conf"))
    dnsmasq2 = DnsmasqConf(context_wrap(DNSMASQ_CONF_FILE_1, path="/etc/dnsmasq.d/origin-dns.conf"))
    result = DnsmasqConfTree([dnsmasq1, dnsmasq2])
    assert "txt-record" not in result
    assert len(result["server"]) == 2


def test_include_conf_dir():
    dnsmasq1 = DnsmasqConf(context_wrap(DNSMASQ_CONF_MAIN_INCLUDE_CONF_DIR, path="/etc/dnsmasq.conf"))
    dnsmasq2 = DnsmasqConf(context_wrap(DNSMASQ_CONF_FILE_2, path="/etc/dnsmasq.d/1id-dns.conf"))
    result = DnsmasqConfTree([dnsmasq1, dnsmasq2])
    assert len(result["dns-forward-max"]) == 2
