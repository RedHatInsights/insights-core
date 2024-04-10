import os

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.core.spec_cleaner import Cleaner

test_file_data = 'test\nabcd\n1234\npwd: p4ssw0rd\n'
test_data = test_file_data.splitlines()


def test_clean_filter_no_filters():
    conf = InsightsConfig()
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, {})
    pp.clean_file(test_file, filters=[])
    # file is NOT changed
    with open(test_file, 'r') as t:
        assert test_file_data == ''.join(t.readlines())

    arch.delete_archive_dir()

    ret = pp.clean_content(test_data, filters=[])
    assert ret == test_data


def test_clean_filter_w_filters():
    conf = InsightsConfig()
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, {})
    pp.clean_file(test_file, filters=['test', 'abc'])
    # file is changed
    with open(test_file, 'r') as t:
        assert 'test\nabcd\n' == ''.join(t.readlines())

    arch.delete_archive_dir()

    ret = pp.clean_content(test_data, filters=['test', '23'])
    assert ret == ['test', '1234']
