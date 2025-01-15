from pytest import mark

from insights.cleaner import Cleaner
from insights.client.config import InsightsConfig

test_data_sensitive = 'test \n\n\nabcd\n1234\npassword: p4ssw0rd\n'.splitlines()


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_password_line_changed_password(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {})
    ret = pp.clean_content(test_data_sensitive, [])
    # content IS changed
    assert test_data_sensitive != ret
    assert 'p4ssw0rd' not in ret[-1]
    assert '********' in ret[-1]


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_password_disabled_by_no_obfuscate(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {})
    ret = pp.clean_content(test_data_sensitive, ['password'])
    # content is NOT changed
    assert test_data_sensitive == ret


@mark.parametrize(
    ("line", "expected"),
    [
        ("password: p@ss_W0rd ?", "password: ******** ?"),
        ("password = p@ss_W0rd ?", "password = ******** ?"),
        ("password=p@ss_W0-d", "password=********"),
    ],
)
def test_clean_content_password(line, expected):
    c = InsightsConfig()
    pp = Cleaner(c, {'patterns': {'regex': ['myserver', r'my(\w*)key']}})
    actual = pp.clean_content(line)
    assert actual == expected
