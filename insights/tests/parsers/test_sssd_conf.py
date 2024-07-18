import pytest

from insights.parsers.sssd_conf import SSSDConf, SSSDConfd
from insights.tests import context_wrap

sssd_conf_cnt = """
[sssd]
config_file_version = 2
domains = example.com
debug_level = 0xfff0

[domain/example.com]
id_provider = ldap
enumerate = {0}
"""


@pytest.mark.parametrize("cls", [SSSDConf, SSSDConfd])
@pytest.mark.parametrize(
    "bool_val", ["True", "true", "TRUE", "False", "false", "FALSE"]
)
def test_sssd_conf(cls, bool_val):
    result = cls(
        context_wrap(sssd_conf_cnt.format(bool_val), path="/etc/sssd/sssd.conf")
    )

    assert result.file_name == "sssd.conf"
    assert result.file_path == "/etc/sssd/sssd.conf"

    assert "sssd" in result
    assert "domain/example.com" in result
    assert result.sections() == ["sssd", "domain/example.com"]

    assert result.getint("sssd", "config_file_version") == 2
    assert result.get("sssd", "domains") == "example.com"
    assert result.get("sssd", "debug_level") == "0xfff0"

    expected = bool_val.lower() == "true"
    assert result.get("domain/example.com", "id_provider") == "ldap"
    assert result.getboolean("domain/example.com", "enumerate") == expected
