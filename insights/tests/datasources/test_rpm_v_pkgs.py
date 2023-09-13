import pytest

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.specs import Specs
from insights.specs.datasources.rpm_v_pkgs import list_with_pkgs


def setup_function(func):
    if func is test_pkgs_list_empty:
        pass
    if func is test_rpm_v_pkgs:
        filters.add_filter(Specs.rpm_V_package_list, ['coreutils', 'procps', 'procps-ng', 'shadow-utils', 'passwd', 'sudo', 'chrony', 'findutils', 'glibc'])


def teardown_function(func):
    if Specs.rpm_V_package_list in filters._CACHE:
        del filters._CACHE[Specs.rpm_V_package_list]


def test_pkgs_list_empty():
    with pytest.raises(SkipComponent):
        list_with_pkgs({})


def test_rpm_v_pkgs():
    ret = list_with_pkgs({})
    assert ret == ['chrony', 'coreutils', 'findutils', 'glibc', 'passwd', 'procps', 'procps-ng', 'shadow-utils', 'sudo']
