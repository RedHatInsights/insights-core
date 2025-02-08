from pytest import mark

from insights.cleaner import Cleaner
from insights.cleaner.keyword import Keyword
from insights.client.config import InsightsConfig

test_data = 'test\nabcd\n \n\n1234\npwd: p4ssw0rd\n'.splitlines()


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_keyword_empty_not_change(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {})  # empty keywords
    ret = pp.clean_content(test_data, [])
    # content is NOT changed
    assert test_data == ret


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_keyword_changed_keyword(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {'keywords': ['test']})
    ret = pp.clean_content(test_data, [])
    # content IS changed
    assert test_data != ret
    assert 'test' not in ret[0]
    assert 'keyword0' in ret[0]
    assert ret[1] == test_data[1]


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_keyword_no_such_keyword_to_change(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {'keywords': ['t_e_s_t']})  # no such keyword
    ret = pp.clean_content(test_data, [])
    # content is NOT changed
    assert test_data == ret
    assert ret[1] == test_data[1]


def test_keyword_empty():
    kw = Keyword([])  # no keyword
    assert kw._kw_db == dict()
