from pytest import mark

from insights.client.config import InsightsConfig
from insights.core.spec_cleaner import Cleaner

test_data = 'test\nabcd\n \n\n1234\npwd: p4ssw0rd\n'.splitlines()
test_data_sensitive = 'test \n\n\nabcd\n1234\npassword: p4ssw0rd\n'.splitlines()


@mark.parametrize("obfuscate", [True, False])
def test_redact_line_changed_password(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {})
    ret = pp.clean_content(test_data_sensitive, [])
    # content IS changed
    assert test_data != ret
    assert 'p4ssw0rd' not in ret[-1]
    assert '********' in ret[-1]


@mark.parametrize("obfuscate", [True, False])
def test_redact_keyword_empty_not_change(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {})  # empty keywords
    ret = pp.clean_content(test_data, [])
    # content is NOT changed
    assert test_data == ret


@mark.parametrize("obfuscate", [True, False])
def test_redact_keyword_changed_keyword(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {'keywords': ['test']})
    ret = pp.clean_content(test_data, [])
    # content IS changed
    assert test_data != ret
    assert 'test' not in ret[0]
    assert 'keyword0' in ret[0]
    assert ret[1] == test_data[1]


@mark.parametrize("obfuscate", [True, False])
def test_redact_keyword_no_such_keyword_to_change(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {'keywords': ['t_e_s_t']})  # no such keyword
    ret = pp.clean_content(test_data, [])
    # content is NOT changed
    assert test_data == ret


@mark.parametrize("obfuscate", [True, False])
def test_redact_keyword_disabled_by_no_redact(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, {'keywords': 'test'})
    ret = pp.clean_content(test_data, [], no_redact=True)
    # content is NOT changed
    assert test_data == ret


@mark.parametrize("obfuscate", [True, False])
def test_redact_patterns_exclude_regex(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    rm_conf = {'patterns': {'regex': ['12.*4', '^abcd']}}
    pp = Cleaner(conf, rm_conf)
    ret = pp.clean_content(test_data, [])
    # content IS changed
    assert test_data != ret
    assert '1234' not in ret
    assert 'abcd' not in ret


@mark.parametrize("obfuscate", [True, False])
def test_redact_result_empty(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    rm_conf = {'patterns': {'regex': [' ', '12.*4', '^abcd', 'test', 'pwd', 'w0rd']}}
    pp = Cleaner(conf, rm_conf)
    ret = pp.clean_content(test_data, [])
    # result content is Empty
    assert len(ret) == 0


@mark.parametrize("obfuscate", [True, False])
def test_redact_patterns_exclude_no_regex(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    rm_conf = {'patterns': ['1234', 'abcde']}
    pp = Cleaner(conf, rm_conf)
    ret = pp.clean_content(test_data, [])
    # content IS changed
    assert test_data != ret
    assert '1234' not in ret
    assert 'abcd' in ret


@mark.parametrize("obfuscate", [True, False])
def test_redact_patterns_exclude_empty(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    rm_conf = {'patterns': []}
    pp = Cleaner(conf, rm_conf)
    ret = pp.clean_content(test_data, [])
    # file is NOT changed
    assert test_data == ret


@mark.parametrize("obfuscate", [True, False])
def test_redact_exclude_none(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, None)
    ret = pp.clean_content(test_data, [])
    # file is NOT changed
    assert test_data == ret
