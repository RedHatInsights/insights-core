"""
redhat-release - File ``/etc/redhat-release``
=============================================

This module provides plugins access to file ``/etc/redhat-release``

Typical content of file ``/etc/redhat-release`` is::

    Red Hat Enterprise Linux Server release 7.2 (Maipo)

This module parses the file content and stores data in the dict ``self.parsed``.
The version info can also be get via ``obj.major`` and ``obj.minor``.
Property ``is_rhel`` and ``is_hypervisor`` specifies the host type.

Examples:
    >>> rh_rls_content = '''
    ... Red Hat Enterprise Linux Server release 7.2 (Maipo)
    ... '''.strip()
    >>> from insights.tests import context_wrap
    >>> shared = {RedhatRelease: RedhatRelease(context_wrap(rh_rls_content))}
    >>> release = shared[RedhatRelease]
    >>> assert release.raw == rh_rls_content
    >>> assert release.major == 7
    >>> assert release.minor == 2
    >>> assert release.version == "7.2"
    >>> assert release.is_rhel
    >>> assert release.product == "Red Hat Enterprise Linux Server"
"""
from .. import Parser, parser
from ..specs import Specs


@parser(Specs.redhat_release)
class RedhatRelease(Parser):
    """Parses the content of file ``/etc/redhat-release``."""

    def parse_content(self, content):
        self.raw = content[0]
        product, _, version_name = [v.strip() for v in content[0].partition("release")]
        version_name_split = [v.strip() for v in version_name.split(None, 1)]
        code_name = (version_name_split[1].strip("()")
                        if len(version_name_split) > 1 else None)
        self.parsed = {
            "product": product,
            "version": version_name_split[0],
            "code_name": code_name
        }

    @property
    def major(self):
        """int: the major version of this OS."""
        return int(self.parsed["version"].split(".")[0])

    @property
    def minor(self):
        """int: the minor version of this OS."""
        s = self.parsed["version"].split(".")
        if len(s) > 1:
            return int(s[1])

    @property
    def version(self):
        """string: version of this OS."""
        return self.parsed["version"]

    @property
    def is_rhel(self):
        """bool: True if this OS belong to RHEL, else False."""
        return "Red Hat Enterprise Linux" in self.parsed["product"]

    @property
    def product(self):
        """string: product of this OS."""
        return self.parsed["product"]
