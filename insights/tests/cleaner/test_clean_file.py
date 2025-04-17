# -*- coding: utf-8 -*-
import os

from mock.mock import patch

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.cleaner import Cleaner


def test_clean_file_obfuscate():
    conf = InsightsConfig(obfuscate=True)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # netstat_-neopa
    line = "tcp6       0      0 10.0.0.1:23           10.0.0.110:63564   ESTABLISHED 0"
    ret = "tcp6       0      0 10.230.230.2:23       10.230.230.1:63564 ESTABLISHED 0"

    test_dir = os.path.join(arch.archive_dir, 'data', 'etc')
    os.makedirs(test_dir)
    pp = Cleaner(conf, {})

    # netstat
    test_file = os.path.join(arch.archive_dir, 'data', 'testfile.netstat_-neopa')
    with open(test_file, 'w') as t:
        t.write(line)
    pp.clean_file(test_file, no_obfuscate=[])
    # file is changed per netstat logic
    with open(test_file, 'r') as t:
        assert ret == ''.join(t.readlines())

    arch.delete_archive_dir()


def test_clean_file_obfuscate_disabled_by_no_obfuscate():
    conf = InsightsConfig(obfuscate=True)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # netstat_-neopa
    line = "tcp6       0      0 10.0.0.1:23           10.0.0.110:63564   ESTABLISHED 0"

    test_dir = os.path.join(arch.archive_dir, 'data', 'etc')
    os.makedirs(test_dir)
    pp = Cleaner(conf, {})

    # netstat
    test_file = os.path.join(arch.archive_dir, 'data', 'testfile.netstat_-neopa')
    with open(test_file, 'w') as t:
        t.write(line)
    pp.clean_file(test_file, no_obfuscate=['ipv4'])
    # file is NOT changed
    with open(test_file, 'r') as t:
        assert line == ''.join(t.readlines())

    arch.delete_archive_dir()


@patch("insights.cleaner.Cleaner.clean_content")
def test_clean_file_non_exist(func):
    conf = InsightsConfig(obfuscate=True)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    test_dir = os.path.join(arch.archive_dir, 'data', 'etc')
    os.makedirs(test_dir)
    pp = Cleaner(conf, {})

    pp.clean_file('non_existing_file', no_obfuscate=[])
    func.assert_not_called()

    # empty file
    test_file = os.path.join(arch.archive_dir, 'data', 'etc', 'x.conf')
    open(test_file, 'w').close()
    pp.clean_file(test_file, no_obfuscate=[])
    func.assert_called_once()

    arch.delete_archive_dir()
