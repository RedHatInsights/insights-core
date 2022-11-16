"""
SystemUserPkgs - datasource ``system_user_pkgs``
================================================

Parser for CVE-2021-35937, CVE-2021-35938, and CVE-2021-35939.
For more information, see the ``system_user_pkgs`` datasource.
"""

from insights import Parser, parser
from insights.specs import Specs


@parser(Specs.system_user_pkgs)
class SystemUserPkgs(Parser):
    """
    Class for enabling the data from the ``system_user_pkgs`` datasource.

    Sample output of this datasource is::

        ["httpd-core"]

    Examples:

        >>> type(system_user_pkgs)
        <class 'insights.parsers.system_user_pkgs.SystemUserPkgs'>
        >>> system_user_pkgs.packages
        ['httpd-core']
    """

    def parse_content(self, content):
        self.packages = content
