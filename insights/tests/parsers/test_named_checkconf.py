import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import named_checkconf
from insights.parsers.named_checkconf import NamedCheckconf
from insights.tests import context_wrap


CONFIG_DNSSEC_ENABLED = """
options {
    bindkeys-file "/etc/named.iscdlv.key";
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
    statistics-file "/var/named/data/named_stats.txt";
    dnssec-enable yes;
    dnssec-validation yes;
    recursion yes;
    allow-query {
        "localhost";
    };
};
"""

CONFIG_DNSSEC_DISABLED = """
options {
    bindkeys-file "/etc/named.iscdlv.key";
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
    statistics-file "/var/named/data/named_stats.txt";
    dnssec-enable no;
    dnssec-validation yes;
    recursion yes;
    allow-query {
        "localhost";
    };
};
"""

CONFIG_DNSSEC_DEFAULT = """
options {
    bindkeys-file "/etc/named.iscdlv.key";
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
    statistics-file "/var/named/data/named_stats.txt";
    dnssec-validation yes;
    recursion yes;
    allow-query {
        "localhost";
    };
};
"""

CONFIG_DISABLED_SECTIONS = """
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
};
"""


def test_config_no_data():
    with pytest.raises(SkipComponent):
        NamedCheckconf(context_wrap(""))


def test_config_dnssec():
    dnssec_disabled = NamedCheckconf(context_wrap(CONFIG_DNSSEC_DISABLED))
    assert dnssec_disabled.is_dnssec_disabled
    assert dnssec_disabled.dnssec_line == "dnssec-enable no;"
    assert dnssec_disabled.disable_algorithms == {}
    assert dnssec_disabled.disable_ds_digests == {}

    dnssec_enabled = NamedCheckconf(context_wrap(CONFIG_DNSSEC_ENABLED))
    assert not dnssec_enabled.is_dnssec_disabled
    assert dnssec_enabled.dnssec_line is None
    assert dnssec_enabled.disable_algorithms == {}
    assert dnssec_enabled.disable_ds_digests == {}

    # dnssec line is not preset - dnssec is enabled by default
    dnssec_default = NamedCheckconf(context_wrap(CONFIG_DNSSEC_DEFAULT))
    assert not dnssec_default.is_dnssec_disabled
    assert dnssec_default.dnssec_line is None
    assert dnssec_default.disable_algorithms == {}
    assert dnssec_default.disable_ds_digests == {}


def test_config_disabled_sections():
    disabled_sections = NamedCheckconf(context_wrap(CONFIG_DISABLED_SECTIONS))
    assert not disabled_sections.is_dnssec_disabled
    assert disabled_sections.dnssec_line is None
    assert disabled_sections.disable_algorithms == {".": ["RSAMD5", "DSA"]}
    assert disabled_sections.disable_ds_digests == {".": ["GOST"]}


def test_doc_examples():
    env = {
        "named_checkconf": NamedCheckconf(context_wrap(CONFIG_DISABLED_SECTIONS)),
    }
    failed, total = doctest.testmod(named_checkconf, globs=env)
    assert failed == 0
