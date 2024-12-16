"""
Rpm -V Packages Parsers - command ``/bin/rpm -V <packages>``
============================================================

Parsers provided in this module includes:

RpmVPackage - command ``/bin/rpm -V <package>``
-----------------------------------------------
"""

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


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
                entry = {
                    "line": line.strip(),
                    "attributes": line_parts[0],
                    "mark": line_parts[1],
                    "file": line_parts[2],
                }
            else:
                entry = {
                    "line": line.strip(),
                    "attributes": line_parts[0],
                    "mark": None,
                    "file": line_parts[1],
                }
            self.discrepancies.append(entry)

        if not self.discrepancies:
            raise SkipComponent("Empty result")
