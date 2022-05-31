"""
redhat-release - File ``/etc/redhat-release``
=============================================

This module provides plugins access to file ``/etc/redhat-release``

Typical content of file ``/etc/redhat-release`` is::

    Red Hat Enterprise Linux Server release 7.2 (Maipo)

This module parses the file contents and stores data in the class
attributes described below.

Examples:
    >>> type(rh_release)
    <class 'insights.parsers.redhat_release.RedhatRelease'>
    >>> rh_release.raw
    'Red Hat Enterprise Linux Server release 7.2 (Maipo)'
    >>> rh_release.major
    7
    >>> rh_release.minor
    2
    >>> rh_release.version
    '7.2'
    >>> rh_release.is_rhel
    True
    >>> rh_release.product
    'Red Hat Enterprise Linux Server'
"""
from .. import Parser, parser
from ..specs import Specs


@parser(Specs.redhat_release)
class RedhatRelease(Parser):
    """Parses the content of file ``/etc/redhat-release``

    Attributes:
        is_alpha(bool): True if this is an Alpha release
        is_beta(bool): True if this is a Beta release
        is_centos(bool): True if this release is CentOS
        is_fedora(bool): True if this release is Fedora
        is_rhel(bool): True if this release is Red Hat Enterprise Linux
        major(int): Major release number or None
        minor(int): Minor release number or None
        parsed(dict): Dictionary containing the parsed strings for ``product``, ``version``, and ``code_name``
        raw(string): Unparsed redhat-release string
    """

    def parse_content(self, content):
        self.raw = content[0]
        self.is_beta = False
        self.is_alpha = False
        product, _, version_name = [v.strip() for v in content[0].partition("release")]
        if 'Alpha' in version_name:
            # Red Hat Enterprise Linux release 9 Alpha (Plow)
            version_number, code_name = version_name.split('Alpha', 1)
            self.is_alpha = True
        elif 'Beta' in version_name:
            # Red Hat Enterprise Linux release 8.5 Beta (Ootpa)
            version_number, code_name = version_name.split('Beta', 1)
            self.is_beta = True
        elif '(' in version_name:
            # Red Hat Enterprise Linux Workstation release 6.10(Santiago)
            # Red Hat Enterprise Linux Workstation release 6.10 (Santiago)
            version_number, code_name = version_name.split('(', 1)
        else:
            # Red Hat Enterprise Linux Workstation release 6.10
            version_number = version_name
            code_name = None

        self.parsed = {
            "product": product,
            "version": version_number.strip(),
            "code_name": code_name.strip().strip('()') if code_name is not None else None
        }

        self.is_rhel = 'red hat enterprise linux' in self.parsed['product'].lower()
        self.is_centos = 'centos' in self.parsed['product'].lower()
        self.is_fedora = 'fedora' in self.parsed['product'].lower()

        v_parts = self.parsed['version'].split('.')
        self.major = int(v_parts[0]) if v_parts[0].isdigit() else None
        if len(v_parts) >= 2:
            if '-' in v_parts[1]:
                minor = v_parts[1].split('-')[0]
            else:
                minor = v_parts[1]
            self.minor = int(minor) if minor.isdigit() else None
        else:
            self.minor = None

    @property
    def version(self):
        """string: version of this OS."""
        return self.parsed["version"]

    @property
    def product(self):
        """string: product of this OS."""
        return self.parsed["product"]

    @property
    def code_name(self):
        """string: code name of this OS or None."""
        return self.parsed["code_name"]
