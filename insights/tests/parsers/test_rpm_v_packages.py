import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import rpm_v_packages
from insights.parsers.rpm_v_packages import RpmVPackage
from insights.tests import context_wrap


TEST_RPM_V_PACKAGE_1 = """
..?......  c /etc/sudoers
..?......    /usr/bin/sudo
..?......    /usr/bin/sudoreplay
missing     /var/db/sudo/lectured (Permission denied)
"""

TEST_RPM_V_PACKAGE_2 = """
package sudo is not installed
"""

CONTEXT_PATH_1 = "insights_commands/rpm_-V_sudo"


def test_rpm_pkg():
    line = [
        {
            'attributes': '..?......',
            'file': '/etc/sudoers',
            'line': '..?......  c /etc/sudoers',
            'mark': 'c',
        },
        {
            'attributes': '..?......',
            'file': '/usr/bin/sudo',
            'line': '..?......    /usr/bin/sudo',
            'mark': None,
        },
        {
            'attributes': '..?......',
            'file': '/usr/bin/sudoreplay',
            'line': '..?......    /usr/bin/sudoreplay',
            'mark': None,
        },
        {
            'attributes': None,
            'file': None,
            'line': 'missing     /var/db/sudo/lectured (Permission denied)',
            'mark': None,
        },
    ]

    rpm_pkg = RpmVPackage(context_wrap(TEST_RPM_V_PACKAGE_1, CONTEXT_PATH_1))
    for index in range(4):
        assert rpm_pkg.discrepancies[index] == line[index]
    assert rpm_pkg.package_name == 'sudo'


def test_rpm_pkg_empty():
    with pytest.raises(SkipComponent) as exc:
        RpmVPackage(context_wrap([], CONTEXT_PATH_1))
    assert 'Empty result' in str(exc)


def test_rpm_pkg_not_installed():
    with pytest.raises(SkipComponent) as exc:
        RpmVPackage(context_wrap(TEST_RPM_V_PACKAGE_2, CONTEXT_PATH_1))
    assert 'Invalid Contents' in str(exc)


def test_doc_examples():
    env = {"rpm_v_pkg": RpmVPackage(context_wrap(TEST_RPM_V_PACKAGE_1, CONTEXT_PATH_1))}
    failed, total = doctest.testmod(rpm_v_packages, globs=env)
    assert failed == 0
