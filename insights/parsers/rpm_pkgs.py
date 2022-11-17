"""
RpmPkgs - datasource ``rpm_pkgs``
=================================

Parser for CVE-2021-35937, CVE-2021-35938, and CVE-2021-35939.
For more information, see the ``rpm_pkgs`` datasource.
"""

from insights import Parser, parser
from insights.specs import Specs


@parser(Specs.rpm_pkgs)
class RpmPkgs(Parser):
    """
    Class for enabling the data from the ``rpm_pkgs`` datasource.

    Sample output of this datasource is::

        ["httpd-core"]

    Examples:

        >>> type(rpm_pkgs)
        <class 'insights.parsers.rpm_pkgs.RpmPkgs'>
        >>> rpm_pkgs.packages
        ['httpd-core']
    """

    def parse_content(self, content):
        self.packages = content
