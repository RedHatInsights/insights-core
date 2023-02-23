"""
RpmPkgs - datasource ``rpm_pkgs``
=================================

Parsers for CVE-2021-35937, CVE-2021-35938, and CVE-2021-35939.
For more information, see the ``rpm_pkgs`` datasource.
"""

from insights import Parser, parser
from insights.specs import Specs


@parser(Specs.rpm_pkgs)
class RpmPkgs(Parser):
    """
    .. warning::
        This class is deprecated, please use
        :py:class:`insights.parsers.rpm_pkgs.RpmPkgsWritable` instead.

    Class for enabling the data from the ``rpm_pkgs`` datasource.

    Sample output of this parser is::

        ["httpd-core"]

    Examples:

        >>> type(rpm_pkgs)
        <class 'insights.parsers.rpm_pkgs.RpmPkgs'>
        >>> rpm_pkgs.packages
        ['httpd-core']
    """

    def parse_content(self, content):
        self.packages = [pkg[0] for pkg in content]


@parser(Specs.rpm_pkgs)
class RpmPkgsWritable(Parser):
    """
    Class for enabling the data from the ``rpm_pkgs`` datasource.
    It replaces the original RpmPkgs parser.

    Sample output of this parser is::

        [("httpd-core", "httpd-core-2.4.53-7.el9.x86_64", "Red Hat, Inc.")]

    Examples:

        >>> type(rpm_pkgs_writable)
        <class 'insights.parsers.rpm_pkgs.RpmPkgsWritable'>
        >>> rpm_pkgs_writable.packages
        [('httpd-core', 'httpd-core-2.4.53-7.el9.x86_64', 'Red Hat, Inc.')]
    """

    def parse_content(self, content):
        self.packages = content
