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
        error_lines (list of strings): The error messages from the command `rpm -V <package>`

    Raises:
        SkipComponents: When a package is not installed and no error is reported.

    Sample output of this command is::

        ..?......  c /etc/sudoers
        ..?......    /usr/bin/sudo
        ..?......    /usr/bin/sudoreplay
        missing     /var/db/sudo/lectured (Permission denied)

    OR::

        error: rpmdb: BDB0113 Thread/process 259/139 failed: BDB1507 Thread died in Berkeley DB library
        error: db5 error(-30973) from dbenv->failchk: BDB0087 DB_RUNRECOVERY: Fatal error, run database recovery
        error: cannot open Packages index using db5 - (-30973)

    Examples:
        >>> type(rpm_v_pkg)
        <class 'insights.parsers.rpm_v_packages.RpmVPackage'>
        >>> rpm_v_pkg.package_name
        'sudo'
        >>> len(rpm_v_pkg.discrepancies)
        4
        >>> sorted(rpm_v_pkg.discrepancies[0].items())
        [('attributes', '..?......'), ('file', '/etc/sudoers'), ('line', '..?......  c /etc/sudoers'), ('mark', 'c')]
        >>> "error: db5 error(-30973) from dbenv->failchk: BDB0087 DB_RUNRECOVERY: Fatal error, run database recovery" in rpm_v_pkg.error_lines
        True
    """

    def parse_content(self, content):
        self.error_lines = []
        self.discrepancies = []
        self.package_name = self.file_name.split('_')[-1] if self.file_name else None

        for line in content:
            if line.startswith("error: "):
                self.error_lines.append(line)
                continue

            line_parts = line.split()
            if not line_parts:
                continue

            entry = {}
            if "package" in line_parts[0]:
                if not self.error_lines:
                    # Skip the parser only when:
                    # - The package is not installed
                    # - No error is reported
                    raise SkipComponent("Package is not installed")

            if "missing" in line_parts[0]:
                entry = {"line": line.strip(), "attributes": None, "mark": None, "file": None}
            elif len(line_parts) == 3:
                entry = {
                    "line": line.strip(),
                    "attributes": line_parts[0],
                    "mark": line_parts[1],
                    "file": line_parts[2],
                }
            elif len(line_parts) == 2:
                entry = {
                    "line": line.strip(),
                    "attributes": line_parts[0],
                    "mark": None,
                    "file": line_parts[1],
                }
            if entry:
                self.discrepancies.append(entry)

        if not self.discrepancies and not self.error_lines:
            raise SkipComponent("Empty result")
