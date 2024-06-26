import os

from mock.mock import patch, Mock
from pytest import mark

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.core.spec_cleaner import Cleaner

test_file_data = 'test\nabcd\n1234\npwd: p4ssw0rd\n'
test_file_data_sensitive = 'test\nabcd\n1234\npassword: p4ssw0rd here\npassword=  p4ssw0rd here\npassword'


@patch('insights.client.archive.InsightsArchive', Mock())
@patch('insights.client.insights_spec.InsightsCommand', Mock())
@patch('insights.client.insights_spec.InsightsFile', Mock())
@patch('insights.client.data_collector.DataCollector._parse_command_spec', Mock())
@patch('insights.client.data_collector.DataCollector._parse_file_spec', Mock())
@patch('insights.client.data_collector.DataCollector._parse_glob_spec', Mock())
def test_redact_classic():
    '''
    Verify redact is filled during classic collection
    '''
    conf = InsightsConfig()
    rm_conf = {'test': 'test'}
    pp = Cleaner(conf, rm_conf)
    assert pp.redact['exclude'] == []
    assert pp.redact['regex'] is False


@patch('insights.client.archive.InsightsArchive', Mock())
@patch('insights.client.core_collector.CoreCollector._write_branch_info', Mock())
@patch('insights.client.core_collector.CoreCollector._write_display_name', Mock())
@patch('insights.client.core_collector.CoreCollector._write_version_info', Mock())
@patch('insights.client.core_collector.CoreCollector._write_tags', Mock())
@patch('insights.client.core_collector.CoreCollector._write_blacklist_report', Mock())
@patch('insights.client.core_collector.collect.collect', Mock(return_value=('/var/tmp/testarchive/insights-test', {})))
def test_redact_core():
    conf = InsightsConfig(core_collect=True)
    rm_conf = {'test': 'test'}
    pp = Cleaner(conf, rm_conf)
    assert pp.redact['exclude'] == []
    assert pp.redact['regex'] is False


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_line_changed_password(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data_sensitive)
    old_data = test_file_data_sensitive.splitlines()

    pp = Cleaner(conf, {})
    pp.clean_file(test_file, [])
    # file is changed
    pwd_line_cnt = 0
    with open(test_file, 'r') as t:
        new_data = t.readlines()
        for idx, line in enumerate(old_data):
            if 'p4ssw0rd' in line:
                pwd_line_cnt += 1
                assert 'p4ssw0rd' not in new_data[idx]
                assert '********' in new_data[idx]
            if line.endswith('password'):
                pwd_line_cnt += 1
                assert line == new_data[idx]
    assert pwd_line_cnt == 3
    arch.delete_archive_dir()


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_keyword_empty_not_change(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, {})  # empty keywords
    pp.clean_file(test_file, [])
    # file is NOT changed
    with open(test_file, 'r') as t:
        assert test_file_data == ''.join(t.readlines())
    arch.delete_archive_dir()


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_keyword_changed_keyword(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, {'keywords': ['test']})
    pp.clean_file(test_file, [])
    # file is changed
    with open(test_file, 'r') as t:
        data = t.readlines()
        assert 'test' not in data[0]
        assert 'keyword0' in data[0]
    arch.delete_archive_dir()


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_keyword_no_such_keyword_to_change(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, {'keywords': ['t_e_s_t']})  # no such keyword
    pp.clean_file(test_file, [])
    # file is NOT changed
    with open(test_file, 'r') as t:
        assert test_file_data == ''.join(t.readlines())
    arch.delete_archive_dir()


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_keyword_disabled_by_no_redact(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, {'keywords': 'test'})
    pp.clean_file(test_file, [], no_redact=True)
    # file is NOT changed
    with open(test_file, 'r') as t:
        assert test_file_data == ''.join(t.readlines())
    arch.delete_archive_dir()


@mark.parametrize(("line", "expected"), [
    (
        "what's your name? what day is today?",
        "what's your keyword0? what keyword1 is tokeyword1?"
    ),
])
@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_line_keyword_extract_cases(core_collect, obfuscate, line, expected):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    pp = Cleaner(conf, {'keywords': ['name', 'day']})
    actual = pp._redact_line(line)
    assert actual == expected


@mark.parametrize("core_collect", [True, False])
def test_redact_line_keyword_with_hostname_and_ip(core_collect):
    hostname = 'test1.abc.com'
    line = "test1.abc.com, 10.0.0.1, test1.abc.loc, 20.1.4.7, smtp.abc.com, what's your name?, what day is today?"
    conf = InsightsConfig(core_collect=core_collect, obfuscate=True, obfuscate_hostname=True, hostname=hostname)
    pp = Cleaner(conf, {'keywords': ['name', 'day']}, hostname)
    result = pp._redact_line(line)
    assert 'test1.abc.com' in result  # hostname is not processed in _redact_line
    assert '10.0.0.1' in result  # IP is not processed in _redact_line
    assert '20.1.4.7' in result  # IP is not processed in _redact_line
    assert 'name' not in result
    assert 'day' not in result
    assert 'keyword0' in result
    assert 'keyword1' in result


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_patterns_exclude_regex(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    rm_conf = {'patterns': {'regex': ['12.*4', '^abcd']}}
    pp = Cleaner(conf, rm_conf)
    pp.clean_file(test_file, [])
    with open(test_file, 'r') as t:
        data = [i.strip() for i in t.readlines()]
        assert '1234' not in data
        assert 'abcd' not in data
    arch.delete_archive_dir()


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_file_empty(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    rm_conf = {'patterns': {'regex': ['test', 'pwd', '12.*4', '^abcd']}}
    pp = Cleaner(conf, rm_conf)
    pp.clean_file(test_file)
    # file is cleaned to empty, hence it was removed
    assert not os.path.exists(test_file)
    arch.delete_archive_dir()


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_patterns_exclude_no_regex(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    rm_conf = {'patterns': ['1234', 'abcd']}
    pp = Cleaner(conf, rm_conf)
    pp.clean_file(test_file, [])
    with open(test_file, 'r') as t:
        data = [i.strip() for i in t.readlines()]
        assert '1234' not in data
        assert 'abcd' not in data
    arch.delete_archive_dir()


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_patterns_exclude_empty(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    rm_conf = {'patterns': []}
    pp = Cleaner(conf, rm_conf)
    pp.clean_file(test_file, [])
    # file is not changed
    with open(test_file, 'r') as t:
        assert test_file_data == ''.join(t.readlines())
    arch.delete_archive_dir()


@mark.parametrize("obfuscate", [True, False])
@mark.parametrize("core_collect", [True, False])
def test_redact_exclude_none(core_collect, obfuscate):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, None)
    pp.clean_file(test_file, [])
    # file is not changed
    with open(test_file, 'r') as t:
        assert test_file_data == ''.join(t.readlines())
    arch.delete_archive_dir()


@mark.parametrize(("line", "expected"), [
    ("test1.abc.com: it's myserver? what is yours?", None),
    ("testabc: it's mykey? what is yours?", None),
    (
        "testabc: it's my1key? what is yours?",
        "testabc: it's my1key? what is yours?",
    ),
])
def test_redact_exclude_patterns(line, expected):
    c = InsightsConfig()
    pp = Cleaner(c, {'patterns': ['myserver', 'mykey']})
    actual = pp._redact_line(line)
    assert actual == expected


@mark.parametrize(("line", "expected"), [
    ("test.abc.com: it's myserver? what is yours?", None),
    ("testabc: it's mykey? what is yours?", None),
    ("testabc: it's my1key? what is yours?", None),
    ("test1: it's my-key? what is yours?", "test1: it's my-key? what is yours?"),
])
def test_redact_patterns_regex(line, expected):
    c = InsightsConfig()
    pp = Cleaner(c, {'patterns': {'regex': ['myserver', r'my(\w*)key']}})
    actual = pp._redact_line(line)
    assert actual == expected


@mark.parametrize(("line", "expected"), [
    ("test.abc.com: it's myserver? what is yours?", None),
    ("testabc: it's mykey? what is yours?", None),
    ("testabc: it's my1key? what is yours?", None),
    ("test1: it's my-key? what is yours?", None),
    ("test: it's my-key? what is yours?", "test: it's my-key? what is yours?"),
])
def test_redact_patterns_posix_regex(line, expected):
    c = InsightsConfig()
    pp = Cleaner(c, {'patterns': {'regex': ['myserver', r'my(\w*)key', 'test[[:digit:]]']}})
    actual = pp._redact_line(line)
    assert actual == expected


@mark.parametrize(("line", "expected"), [
    ("password: p@ss_W0rd ?", "password: ******** ?"),
    ("password = p@ss_W0rd ?", "password = ******** ?"),
    ("password=p@ss_W0-d", "password=********"),
])
def test_redact_password(line, expected):
    c = InsightsConfig()
    pp = Cleaner(c, {'patterns': {'regex': ['myserver', r'my(\w*)key']}})
    actual = pp._redact_line(line)
    assert actual == expected
