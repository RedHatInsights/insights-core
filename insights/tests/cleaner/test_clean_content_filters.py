from pytest import mark

from insights.cleaner import Cleaner
from insights.client.config import InsightsConfig

test_data = 'testabc\nabcd\n \n\n1234\npwd: p4ssw0rd\ntest123\npwd:abc\n'.splitlines()


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_filters_allowlist(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, None)
    ret = pp.clean_content(test_data, allowlist={'test': 2, 'pwd': 1})
    # content IS changed
    assert test_data != ret
    assert 'testabc' in ret  # 1 of 2 matched
    assert 'test123' in ret  # 2 of 2 matched
    # lines are processed in reverse order
    assert 'pwd:abc' in ret  # 1 of 1 matched
    assert 'pwd: p4ssw0rd' not in ret  # Max count matched
    assert '1234' not in ret
    assert 'abcd' not in ret


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_filters_allowlist_empty(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, None)
    ret = pp.clean_content(test_data, allowlist={})
    # content IS changed
    assert test_data != ret
    assert ret == []


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_filters_allowlist_not(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, None)
    ret = pp.clean_content(test_data, allowlist=None)
    # content IS NOT changed
    assert test_data == ret
