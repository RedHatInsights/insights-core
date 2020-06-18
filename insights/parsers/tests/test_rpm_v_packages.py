import doctest

from insights.parsers import rpm_v_packages
from insights.parsers.rpm_v_packages import RpmVPackages
from insights.tests import context_wrap


TEST_RPM = """
package procps is not installed
..?......  c /etc/sudoers
..?......    /usr/bin/sudo
..?......    /usr/bin/sudoreplay
missing     /var/db/sudo/lectured (Permission denied)
"""

TEST_RPM_2 = """
package procps is not installed
S.5....T.  c /etc/sudoers
S.5....T.  c /etc/chrony.conf
"""


def test_rpm_empty():
    rpm_pkgs = RpmVPackages(context_wrap([]))
    assert rpm_pkgs.packages_list == []


def test_rpm():
    line_1 = {'attributes': None, 'file': None,
              'line': 'package procps is not installed', 'mark': None}
    line_2 = {'attributes': '..?......', 'file': '/etc/sudoers',
              'line': '..?......  c /etc/sudoers', 'mark': 'c'}
    line_3 = {'attributes': '..?......', 'file': '/usr/bin/sudo',
              'line': '..?......    /usr/bin/sudo', 'mark': None}
    line_4 = {'attributes': '..?......', 'file': '/usr/bin/sudoreplay',
              'line': '..?......    /usr/bin/sudoreplay', 'mark': None}
    line_5 = {'attributes': None, 'file': None,
              'line': 'missing     /var/db/sudo/lectured (Permission denied)', 'mark': None}

    rpm_pkgs = RpmVPackages(context_wrap(TEST_RPM))
    assert rpm_pkgs.packages_list[0] == line_1
    assert rpm_pkgs.packages_list[1] == line_2
    assert rpm_pkgs.packages_list[2] == line_3
    assert rpm_pkgs.packages_list[3] == line_4
    assert rpm_pkgs.packages_list[4] == line_5

    rpm_pkgs_2 = RpmVPackages(context_wrap(TEST_RPM_2))
    assert rpm_pkgs_2.packages_list[2].get('file', None) == '/etc/chrony.conf'


def test_doc_examples():
    env = {
        "rpm_v_packages": RpmVPackages(context_wrap(TEST_RPM))
    }
    failed, total = doctest.testmod(rpm_v_packages, globs=env)
    assert failed == 0
