import os

from pytest import mark

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.cleaner import Cleaner

test_file_data_sensitive = (
    'test\nabcd\n1234\npassword: p4ssw0rd here\npassword=  p4ssw0rd here\npassword'
)


@mark.parametrize("obfuscate", [True, False])
def test_clean_file_line_changed_password(obfuscate):
    conf = InsightsConfig(obfuscate=obfuscate)
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
