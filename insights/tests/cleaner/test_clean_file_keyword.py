import os

from pytest import mark

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.cleaner import Cleaner

test_file_data = 'test\nabcd\n1234\npwd: p4ssw0rd\n'


@mark.parametrize("obfuscate", [True, False])
def test_clean_file_keyword_empty_not_change(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)
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
def test_clean_file_keyword_changed_keyword(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)
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
def test_clean_file_keyword_no_such_keyword_to_change(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)
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
def test_clean_file_keyword_disabled_by_no_obfuacate(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, {'keywords': 'test'})
    pp.clean_file(test_file, ['keyword'])
    # file is NOT changed
    with open(test_file, 'r') as t:
        assert test_file_data == ''.join(t.readlines())
    arch.delete_archive_dir()
