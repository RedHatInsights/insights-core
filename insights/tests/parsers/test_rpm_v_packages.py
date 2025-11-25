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
error: db5 error(-30973) from dbenv->failchk: BDB0087 DB_RUNRECOVERY: Fatal error, run database recovery
"""

TEST_RPM_V_PACKAGE_2 = """
package sudo is not installed
"""

TEST_RPM_V_PACKAGE_3 = """
error: rpmdb: BDB0113 Thread/process 259/139 failed: BDB1507 Thread died in Berkeley DB library
error: db5 error(-30973) from dbenv->failchk: BDB0087 DB_RUNRECOVERY: Fatal error, run database recovery
error: cannot open Packages index using db5 - (-30973)
"""

TEST_RPM_V_PACKAGE_4 = """
error: rpmdb: BDB0113 Thread/process 259/139 failed: BDB1507 Thread died in Berkeley DB library
error: db5 error(-30973) from dbenv->failchk: BDB0087 DB_RUNRECOVERY: Fatal error, run database recovery
error: cannot open Packages index using db5 - (-30973)

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


def test_rpm_pkg_erros():
    rpm_pkg = RpmVPackage(context_wrap(TEST_RPM_V_PACKAGE_3, CONTEXT_PATH_1))
    assert rpm_pkg.package_name == 'sudo'
    assert rpm_pkg.error_lines is not None
    assert len(rpm_pkg.error_lines) == 3


def test_rpm_pkg_erros_other_lines():
    rpm_pkg = RpmVPackage(context_wrap(TEST_RPM_V_PACKAGE_4, CONTEXT_PATH_1))
    assert rpm_pkg.package_name == 'sudo'
    assert rpm_pkg.discrepancies == []
    assert len(rpm_pkg.error_lines) == 3
    assert "package sudo is not installed" not in rpm_pkg.error_lines


def test_rpm_pkg_not_installed():
    with pytest.raises(SkipComponent) as exc:
        RpmVPackage(context_wrap(TEST_RPM_V_PACKAGE_2, CONTEXT_PATH_1))
    assert 'Package is not installed' in str(exc)


def test_doc_examples():
    env = {"rpm_v_pkg": RpmVPackage(context_wrap(TEST_RPM_V_PACKAGE_1, CONTEXT_PATH_1))}
    failed, total = doctest.testmod(rpm_v_packages, globs=env)
    assert failed == 0
