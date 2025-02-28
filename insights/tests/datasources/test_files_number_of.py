import pytest
import os
from collections import defaultdict

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.core import dr
from insights.specs import Specs
from insights.specs.datasources.files_number_of import files_number_dir


TEST_DIR = "/tmp/test_files_number/"
CREATE_TEST_FILES = "touch " + TEST_DIR + "file1" + " " + TEST_DIR + "file2"
REMOVE_DIR = "rm -rf " + TEST_DIR


def setup_function(func):
    if func is test_module_filters:
        filters.add_filter(Specs.files_number_filter, [TEST_DIR])
    if func is test_module_filters_empty:
        filters.add_filter(Specs.files_number_filter, [])


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)


def test_module_filters():
    broker = dr.Broker()
    os.makedirs(TEST_DIR)
    os.system(CREATE_TEST_FILES)
    result = files_number_dir(broker)
    os.system(REMOVE_DIR)
    assert result.content == ['{"/tmp/test_files_number/": 2}']


def test_module_filters_empty():
    broker = dr.Broker()
    with pytest.raises(SkipComponent):
        files_number_dir(broker)
