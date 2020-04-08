"""
RpmVPackages - command ``/bin/rpm -V coreutils procps procps-ng shadow-utils passwd sudo``
==========================================================================================
"""

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.rpm_V_packages)
class RpmVPackages(CommandParser):
    """
    Class for parsing ``/bin/rpm -V coreutils procps procps-ng shadow-utils passwd sudo`` command.

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
