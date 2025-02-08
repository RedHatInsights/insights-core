from pytest import mark

from insights.cleaner import Cleaner
from insights.client.config import InsightsConfig

test_data = 'test\nabcd\n \n\n1234\npwd: p4ssw0rd\n'.splitlines()


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_patterns_exclude_regex(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    rm_conf = {'patterns': {'regex': ['12.*4', '^abcd']}}
    pp = Cleaner(conf, rm_conf)
    ret = pp.clean_content(test_data, [])
    # content IS changed
    assert test_data != ret
    assert '1234' not in ret
    assert 'abcd' not in ret


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_result_empty(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    rm_conf = {'patterns': {'regex': [' ', '12.*4', '^abcd', 'test', 'pwd', 'w0rd']}}
    pp = Cleaner(conf, rm_conf)
    ret = pp.clean_content(test_data, [])
    # result content is Empty
    assert len(ret) == 0


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_patterns_exclude_no_regex(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    rm_conf = {'patterns': ['1234', 'abcde']}
    pp = Cleaner(conf, rm_conf)
    ret = pp.clean_content(test_data, [])
    # content IS changed
    assert test_data != ret
    assert '1234' not in ret
    assert 'abcd' in ret


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_patterns_exclude_empty(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    rm_conf = {'patterns': []}
    pp = Cleaner(conf, rm_conf)
    ret = pp.clean_content(test_data, [])
    # file is NOT changed
    assert test_data == ret


@mark.parametrize("obfuscate", [True, False])
def test_clean_content_exclude_none(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)

    pp = Cleaner(conf, None)
    ret = pp.clean_content(test_data, [])
    # file is NOT changed
    assert test_data == ret


@mark.parametrize(
    ("line", "expected"),
    [
        (
            "what's your name? what day is today?",
            "what's your keyword0? what keyword1 is tokeyword1?",
        ),
    ],
)
@mark.parametrize("obfuscate", [True, False])
def test_clean_content_keyword_extract_cases(obfuscate, line, expected):
    conf = InsightsConfig(obfuscate=obfuscate)
    pp = Cleaner(conf, {'keywords': ['name', 'day']})
    actual = pp.clean_content(line)
    assert actual == expected


@mark.parametrize(
    ("line", "expected"),
    [
        ("test1.abc.com: it's myserver? what is yours?", None),
        ("testabc: it's mykey? what is yours?", None),
        (
            "testabc: it's my1key? what is yours?",
            "testabc: it's my1key? what is yours?",
        ),
    ],
)
def test_clean_content_exclude_patterns(line, expected):
    c = InsightsConfig()
    pp = Cleaner(c, {'patterns': ['myserver', 'mykey']})
    actual = pp.clean_content(line)
    assert actual == expected


@mark.parametrize(
    ("line", "expected"),
    [
        ("test.abc.com: it's myserver? what is yours?", None),
        ("testabc: it's mykey? what is yours?", None),
        ("testabc: it's my1key? what is yours?", None),
        ("test1: it's my-key? what is yours?", "test1: it's my-key? what is yours?"),
    ],
)
def test_clean_content_patterns_regex(line, expected):
    c = InsightsConfig()
    pp = Cleaner(c, {'patterns': {'regex': ['myserver', r'my(\w*)key']}})
    actual = pp.clean_content(line)
    assert actual == expected


@mark.parametrize(
    ("line", "expected"),
    [
        ("test.abc.com: it's myserver? what is yours?", None),
        ("testabc: it's mykey? what is yours?", None),
        ("testabc: it's my1key? what is yours?", None),
        ("test1: it's my-key? what is yours?", None),
        ("test: it's my-key? what is yours?", "test: it's my-key? what is yours?"),
    ],
)
def test_clean_content_patterns_posix_regex(line, expected):
    c = InsightsConfig()
    pp = Cleaner(c, {'patterns': {'regex': ['myserver', r'my(\w*)key', 'test[[:digit:]]']}})
    actual = pp.clean_content(line)
    assert actual == expected
