"""
Rpm -V Packages Parsers - command ``/bin/rpm -V <packages>``
============================================================

Parsers provided in this module includes:

RpmVPackages - command ``/bin/rpm -V <packages>``
-------------------------------------------------

RpmVPackage - command ``/bin/rpm -V <package>``
-----------------------------------------------

"""

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.rpm_V_packages)
class RpmVPackages(CommandParser):
    """
    Class for parsing ``/bin/rpm -V <packages>`` command.

    .. warning::
        This class is deprecated and will be removed from 3.5.0.

        For Insights Advisor Rules, it's recommended to use the
        :class:`insights.parsers.rpm_v_packages.RpmVPackage` and add the
        ``'coreutils', 'procps', 'procps-ng', 'shadow-utils', 'passwd', 'sudo', 'chrony', 'findutils', 'glibc'``
        to the filter list of `Specs.rpm_V_package_list` instead.

    Attributes:
        packages_list (list of dictionaries): every dictionary contains information about one entry

    Sample output of this command is::

        package procps is not installed
        ..?......  c /etc/sudoers
        ..?......    /usr/bin/sudo
        ..?......    /usr/bin/sudoreplay
        missing     /var/db/sudo/lectured (Permission denied)

    Examples:
        >>> type(rpm_v_packages)
        <class 'insights.parsers.rpm_v_packages.RpmVPackages'>
        >>> len(rpm_v_packages.packages_list)
        5
        >>> sorted(rpm_v_packages.packages_list[0].items())
        [('attributes', None), ('file', None), ('line', 'package procps is not installed'), ('mark', None)]
        >>> sorted(rpm_v_packages.packages_list[1].items())
        [('attributes', '..?......'), ('file', '/etc/sudoers'), ('line', '..?......  c /etc/sudoers'), ('mark', 'c')]
"""

    def __init__(self, *args, **kwargs):
        deprecated(RpmVPackages, "Please use the :class:`insights.parsers.rpm_v_packages.RpmVPackage` instead.", "3.5.0")
        super(RpmVPackages, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        self.packages_list = []

        for line in content:
            line_parts = line.split()
            if "package" in line_parts[0] or "missing" in line_parts[0]:
                entry = {"line": line.strip(), "attributes": None, "mark": None, "file": None}
            elif len(line_parts) == 3:
                entry = {"line": line.strip(), "attributes": line_parts[0], "mark": line_parts[1],
                         "file": line_parts[2]}
            else:
                entry = {"line": line.strip(), "attributes": line_parts[0], "mark": None,
                         "file": line_parts[1]}
            self.packages_list.append(entry)


@parser(Specs.rpm_V_package)
class RpmVPackage(CommandParser):
    """
    Class for parsing ``/bin/rpm -V <package>`` command.

    Attributes:
        package_name (String): The name of package
        discrepancies (list of dictionaries): Every dictionary contains information about one entry

    Sample output of this command is::

        ..?......  c /etc/sudoers
        ..?......    /usr/bin/sudo
        ..?......    /usr/bin/sudoreplay
        missing     /var/db/sudo/lectured (Permission denied)

    Examples:
        >>> type(rpm_v_pkg)
        <class 'insights.parsers.rpm_v_packages.RpmVPackage'>
        >>> rpm_v_pkg.package_name
        'sudo'
        >>> len(rpm_v_pkg.discrepancies)
        4
        >>> sorted(rpm_v_pkg.discrepancies[0].items())
        [('attributes', '..?......'), ('file', '/etc/sudoers'), ('line', '..?......  c /etc/sudoers'), ('mark', 'c')]
"""

    def parse_content(self, content):
        self.discrepancies = []
        self.package_name = self.file_name.split('_')[-1] if self.file_name else None

        for line in content:
            line_parts = line.split()
            if not line_parts:
                continue

            if "package" in line_parts[0]:
                raise SkipComponent("Invalid Contents")

            if "missing" in line_parts[0]:
                entry = {"line": line.strip(), "attributes": None, "mark": None, "file": None}
            elif len(line_parts) == 3:
                entry = {"line": line.strip(), "attributes": line_parts[0], "mark": line_parts[1],
                         "file": line_parts[2]}
            else:
                entry = {"line": line.strip(), "attributes": line_parts[0], "mark": None,
                         "file": line_parts[1]}
            self.discrepancies.append(entry)

        if not self.discrepancies:
            raise SkipComponent("Empty result")
