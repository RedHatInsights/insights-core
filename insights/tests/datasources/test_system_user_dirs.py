import mock
import pytest

from mock.mock import Mock

from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.system_user_dirs import LocalSpecs, system_user_dirs

RPM_CMD = """
sssd-ldap; drwxr-xr-x; apache; root
ca-certificates; drwxrwxr-x; root; apache
kmod; drwxr-xrwx; root; root
libbsd; dr-xr-xr-x; apache; root
libbsd; drwxr-xr-x; root; apache
libbsd; drwxrwxr-x; root; root
libbsd; -rwxr-xr-x; apache; root
libbsd; lrwxrwxrwx; apache; apache
""".strip()

RPM_EXPECTED = ["ca-certificates", "kmod", "sssd-ldap"]

RPM_BAD_CMD = "bash: rpm: command not found..."

RPM_EMPTY_CMD = ""

RELATIVE_PATH = "insights_commands/system_user_dirs"


def get_users():
    return ["apache"]


def get_groups(users):
    return ["apache"]


@mock.patch("insights.specs.datasources.system_user_dirs.get_users", get_users)
@mock.patch("insights.specs.datasources.system_user_dirs.get_groups", get_groups)
def test_rpm():
    rpm_args = Mock()
    rpm_args.content = RPM_CMD.splitlines()
    broker = {LocalSpecs.rpm_args: rpm_args}

    result = system_user_dirs(broker)
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
        system_user_dirs(broker)
