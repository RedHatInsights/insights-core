import pytest
import os
from collections import defaultdict

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.core import dr
from insights.specs import Specs
from insights.specs.datasources.ls import files_dirs_number


TEST_DIR1 = "/tmp/test_files_number1/"
TEST_DIR2 = "/tmp/test_files_number2"
TEST_DIR3 = "/tmp/test_files_number3"
TEST_DIR4 = "/tmp/test_files_number4"
CREATE_TEST_FILES = "touch " + TEST_DIR1 + "file1" + " " + TEST_DIR1 + "file2"
REMOVE_DIR = "rm -rf " + TEST_DIR1 + " " + TEST_DIR2


def setup_function(func):
    if func is test_module_filters:
        filters.add_filter(Specs.files_dirs_number_filter, [TEST_DIR1, TEST_DIR2, TEST_DIR3])
    if func is test_module_filters_empty:
        filters.add_filter(Specs.files_dirs_number_filter, [])
    if func is test_module_no_target_dir_empty:
        filters.add_filter(Specs.files_dirs_number_filter, [TEST_DIR4])


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)


def test_module_filters():
    broker = dr.Broker()
    os.makedirs(TEST_DIR1)
    os.makedirs(TEST_DIR2)
    os.makedirs(TEST_DIR1 + "test_dir1")
    os.system(CREATE_TEST_FILES)
    result = files_dirs_number(broker)
    os.system(REMOVE_DIR)
    assert result.content == [
        '{"/tmp/test_files_number1/": {"dirs_number": 1, "files_number": 2}, "/tmp/test_files_number2/": {"dirs_number": 0, "files_number": 0}}'
    ]


def test_module_filters_empty():
    broker = dr.Broker()
    with pytest.raises(SkipComponent):
        files_dirs_number(broker)


def test_module_no_target_dir_empty():
    broker = dr.Broker()
    with pytest.raises(SkipComponent):
        files_dirs_number(broker)
