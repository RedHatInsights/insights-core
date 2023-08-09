import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import named_conf
from insights.parsers.named_conf import NamedConf
from insights.tests import context_wrap


CONFIG_NORMAL_SECTIONS = """
logging {
    channel "default_debug" {
        file "data/named.run";
        severity dynamic;
    };
};
options {
    directory "/var/named";
    dump-file "/var/named/data/cache_dump.db";
    listen-on port 53 {
        127.0.0.1/32;
    };
    listen-on-v6 port 53 {
        ::1/128;
    };
    managed-keys-directory "/var/named/dynamic";
    memstatistics-file "/var/named/data/named_mem_stats.txt";
    allow-recursion { localnets; localhost; 192.168.10.1/24; };
    pid-file "/run/named/named.pid";
    recursing-file "/var/named/data/named.recursing";
    secroots-file "/var/named/data/named.secroots";
    session-keyfile "/run/named/session.key";
    statistics-file "/var/named/data/named_stats.txt";
    disable-algorithms "." {
        "RSAMD5";
        "DSA";
    };
    disable-ds-digests "." {
        "GOST";
    };
    dnssec-enable yes;
    dnssec-validation yes;
    recursion yes;
    allow-query {
        "localhost";
    };

    include "/etc/crypto-policies/back-ends/bind.config";
};
"""

CONFIG_INVALID_SECTIONS = """
logging {
    channel "default_debug" {
        file "data/named.run";
        severity dynamic;
    };
};
options {
    directory "/var/named";
    dump-file "/var/named/data/cache_dump.db";
    listen-on port 53 {
        127.0.0.1/32;
    };
    listen-on-v6 port 53 {
        ::1/128;
    };
    managed-keys-directory "/var/named/dynamic";
    memstatistics-file "/var/named/data/named_mem_stats.txt";
    pid-file "/run/named/named.pid";
    recursing-file "/var/named/data/named.recursing";
    secroots-file "/var/named/data/named.secroots";
    session-keyfile "/run/named/session.key";
    statistics-file "/var/named/data/named_stats.txt";
    disable-algorithms "." {
        "RSAMD5";
        "DSA";
    };
    disable-ds-digests "." {
        "GOST";
    };
    dnssec-enable yes;
    dnssec-validation yes;
    recursion yes;
    allow-query {
        "localhost";
    };

    include "";
};
"""

CONFIG_COMPLEX_SECTIONS = """
include "/tmp/test-unix"; # Unix style

logging {
    channel "default_debug" {
        file "data/named.run";
        severity dynamic;
    };
};
options {
    directory "/var/named";
    dump-file "/var/named/data/cache_dump.db";
    listen-on port 53 {
        127.0.0.1/32;
    };
    listen-on-v6 port 53 {
        ::1/128;
    };
    managed-keys-directory "/var/named/dynamic";
    memstatistics-file "/var/named/data/named_mem_stats.txt";
    allow-recursion { localnets; localhost; 192.168.10.1/24; };
    pid-file "/run/named/named.pid";
    recursing-file "/var/named/data/named.recursing";
    secroots-file "/var/named/data/named.secroots";
    session-keyfile "/run/named/session.key";
    statistics-file "/var/named/data/named_stats.txt";
    disable-algorithms "." {
        "RSAMD5";
        "DSA";
    };
    disable-ds-digests "." {
        "GOST";
    };
    dnssec-enable yes;
    dnssec-validation yes;
    recursion yes;
    allow-query {
        "localhost";
    };

    include "/etc/crypto-policies/back-ends/bind.config";
};
managed-keys {
    "." initial-key 257 3 8 "AwEAAagAIKlVZrpC6Ia7gEzahOR+9W29euxhJhVVLOyQbSEW0O8gcCjF
                FVQUTf6v58fLjwBd0YI0EzrAcQqBGCzh/RStIoO8g0NfnfL2MTJRkxoX
                bfDaUeVPQuYEhg37NZWAJQ9VnMVDxP/VHL496M/QZxkjf5/Efucp2gaD
                X6RS6CXpoY68LsvPVjR0ZSwzz1apAzvN9dlzEheX7ICJBBtuA6G3LQpz
                W5hOA2hzCTMjJPJ8LbqF6dsV6DoBQzgul0sGIcGOYl7OyQdXfZ57relS
                Qageu+ipAdTTJ25AsRTAoub8ONGcLmqrAmRLKBP1dfwhYB4N7knNnulq
                QxA+Uk1ihz0=";
    "." initial-key 257 3 8 "AwEAAaz/tAm8yTn4Mfeh5eyI96WSVexTBAvkMgJzkKTOiW1vkIbzxeF3
                +/4RgWOq7HrxRixHlFlExOLAJr5emLvN7SWXgnLh4+B5xQlNVz8Og8kv
                ArMtNROxVQuCaSnIDdD5LKyWbRd2n9WGe2R8PzgCmr3EgVLrjyBxWezF
                0jLHwVN8efS3rCj/EWgvIWgb9tarpVUDK/b58Da+sqqls3eNbuv7pr+e
                oZG+SrDK6nWeL3c6H5Apxz7LjVc1uTIdsIXxuOLYA4/ilBmSVIzuDWfd
                RUfhHdY6+cn8HFRm+2hM8AnXGXws9555KrUB5qihylGa8subX2Nn6UwN
                R1AkUTV74bU=";
};
zone "." IN {
    type hint;
    file "named.ca";
};
zone "localhost.localdomain" IN {
    type master;
    file "named.localhost";
    allow-update {
        "none";
    };
};
zone "localhost" IN {
    type master;
    file "named.localhost";
    allow-update {
        "none";
    };
};
zone "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa" IN {
    type master;
    file "named.loopback";
    allow-update {
        "none";
    };
};
zone "1.0.0.127.in-addr.arpa" IN {
    type master;
    file "named.loopback";
    allow-update {
        "none";
    };
};
zone "0.in-addr.arpa" IN {
    type master;
    file "named.empty";
    allow-update {
        "none";
    };

include "/etc/crypto-policies/back-ends/bind.config-c"; /* c style */
};

    include "/etc/crypto-policies/back-ends/bind.config-c-plus"; // C++ style
include "/etc/crypto-policies/back-ends/bind.config"; // the sname line
"""


def test_config_no_data():
    with pytest.raises(SkipComponent):
        NamedConf(context_wrap(""))


def test_config_invalid_data():
    with pytest.raises(SkipComponent):
        NamedConf(context_wrap(CONFIG_INVALID_SECTIONS))


def test_config_include_sections():
    include_sections = NamedConf(context_wrap(CONFIG_COMPLEX_SECTIONS))
    assert len(include_sections.includes) == 5
    assert include_sections.includes[0] == '/tmp/test-unix'
    assert include_sections.includes[1] == '/etc/crypto-policies/back-ends/bind.config'
    assert include_sections.includes[2] == '/etc/crypto-policies/back-ends/bind.config-c'
    assert include_sections.includes[3] == '/etc/crypto-policies/back-ends/bind.config-c-plus'
    assert include_sections.includes[4] == '/etc/crypto-policies/back-ends/bind.config'
    assert include_sections.allow_recursion_address == ['localnets', 'localhost', '192.168.10.1/24']


def test_doc_examples():
    env = {
        "named_conf": NamedConf(context_wrap(CONFIG_NORMAL_SECTIONS)),
    }
    failed, total = doctest.testmod(named_conf, globs=env)
    assert failed == 0
