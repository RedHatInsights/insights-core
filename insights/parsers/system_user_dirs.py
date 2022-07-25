"""
SystemUserDirs - datasource ``system_user_dirs``
================================================

Parser for CVE-2021-35937, CVE-2021-35938, and CVE-2021-35939.
For more information, see the ``system_user_dirs`` datasource.
"""

from insights import Parser, parser
from insights.specs import Specs


@parser(Specs.system_user_dirs)
class SystemUserDirs(Parser):
    """
    Class for enabling the data from the ``system_user_dirs`` datasource.

    Sample output of this datasource is::

        ["ca-certificates", "kmod", "sssd-ldap"]

    Examples:

        >>> type(system_user_dirs)
        <class 'insights.parsers.system_user_dirs.SystemUserDirs'>
        >>> system_user_dirs.packages
        ['ca-certificates', 'kmod', 'sssd-ldap']
    """

    def parse_content(self, content):
        self.packages = content
