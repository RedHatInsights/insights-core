import os

from pytest import mark

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.cleaner import Cleaner

test_file_data = 'test\nabcd\n1234\npwd: p4ssw0rd\n'


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
def test_clean_file_patterns_exclude_regex(obfuscate, line, expected):
    conf = InsightsConfig(obfuscate=obfuscate)
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
def test_clean_file_patterns_empty_result(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)
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
def test_clean_file_patterns_exclude_no_regex(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)
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
def test_clean_file_patterns_exclude_empty(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)
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
def test_clean_file_patterns_exclude_none(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)
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
