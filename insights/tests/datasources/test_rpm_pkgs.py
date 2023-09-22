import mock
import pytest

from mock.mock import Mock

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.rpm_pkgs import LocalSpecs, pkgs_with_writable_dirs, rpm_v_pkg_list
from insights.specs import Specs

RPM_CMD = """
httpd-core; httpd-core-2.4.53-7.el9.x86_64; /usr/share/doc/httpd-core; drwxr-xr-x; apache; root; Red Hat, Inc.
httpd-core; httpd-core-2.4.53-7.el9.x86_64; /usr/share/doc/httpd-core/CHANGES; -rw-r--r--; root; root; Red Hat, Inc.
postgresql-server; postgresql-server-13.7-1.el9_0.x86_64; /var/lib/pgsql; drwx------; postgres; postgres; Red Hat, Inc.
polkit; polkit-0.117-10.el9_0.x86_64; /usr/lib/polkit-1; drwxrwxr-x; polkitd; polkitd; Red Hat, Inc.
polkit; polkit-0.117-10.el9_0.x86_64; /usr/lib/polkit-1/polkitd; -rwxr-xr-x; root; root; Red Hat, Inc.
""".strip()

RPM_EXPECTED = ["httpd-core|httpd-core-2.4.53-7.el9.x86_64|Red Hat, Inc."]

RPM_BAD_CMD = "bash: rpm: command not found..."

RPM_EMPTY_CMD = ""

RELATIVE_PATH = "insights_commands/rpm_pkgs"


def get_users():
    return ["apache", "postgres"]


def get_groups(users):
    return ["apache", "postgres"]


@mock.patch("insights.specs.datasources.rpm_pkgs.get_users", get_users)
@mock.patch("insights.specs.datasources.rpm_pkgs.get_groups", get_groups)
def test_rpm():
    rpm_args = Mock()
    rpm_args.content = RPM_CMD.splitlines()
    broker = {LocalSpecs.rpm_args: rpm_args}

    result = pkgs_with_writable_dirs(broker)
    expected = DatasourceProvider(content=RPM_EXPECTED, relative_path=RELATIVE_PATH)
    assert result
    assert isinstance(result, DatasourceProvider)
    assert sorted(result.content) == sorted(expected.content)
    assert result.relative_path == expected.relative_path


@pytest.mark.parametrize("no_rpm", [RPM_BAD_CMD, RPM_EMPTY_CMD])
def test_no_rpm(no_rpm):
    rpm_args = Mock()
    rpm_args.content = no_rpm.splitlines()
    broker = {LocalSpecs.rpm_args: rpm_args}

    with pytest.raises(SkipComponent):
        pkgs_with_writable_dirs(broker)


def setup_function(func):
    if func is test_pkgs_list_empty:
        pass
    if func is test_rpm_v_pkgs:
        filters.add_filter(Specs.rpm_V_package_list, ['coreutils', 'procps', 'procps-ng', 'shadow-utils', 'passwd', 'sudo', 'chrony', 'findutils', 'glibc'])


def teardown_function():
    if Specs.rpm_V_package_list in filters._CACHE:
        del filters._CACHE[Specs.rpm_V_package_list]


def test_pkgs_list_empty():
    with pytest.raises(SkipComponent):
        rpm_v_pkg_list({})


def test_rpm_v_pkgs():
    ret = rpm_v_pkg_list({})
    assert ret == ['chrony', 'coreutils', 'findutils', 'glibc', 'passwd', 'procps', 'procps-ng', 'shadow-utils', 'sudo']
