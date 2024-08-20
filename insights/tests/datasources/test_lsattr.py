import pytest

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.specs import Specs
from insights.specs.datasources.lsattr import paths_to_lsattr


def setup_function(func):
    if func is test_lsattr_empty:
        return
    if func is test_lsattr_one_file:
        filters.add_filter(Specs.lsattr_files_or_dirs, ["/etc/default/grub"])
    if func is test_lsattr_more_files:
        filters.add_filter(Specs.lsattr_files_or_dirs, ["/etc/default/grub", "/etc/httpd/httpd.conf"])


def teardown_function(func):
    if Specs.lsattr_files_or_dirs in filters._CACHE:
        del filters._CACHE[Specs.lsattr_files_or_dirs]


def test_lsattr_empty():
    with pytest.raises(SkipComponent):
        paths_to_lsattr({})


def test_lsattr_one_file():
    attr_files = paths_to_lsattr({})
    assert attr_files == '/etc/default/grub'


def test_lsattr_more_files():
    attr_files = paths_to_lsattr({})
    assert attr_files == '/etc/default/grub /etc/httpd/httpd.conf'
