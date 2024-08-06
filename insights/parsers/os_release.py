"""
OsRelease - file ``/etc/os-release``
====================================

This module provides plugins access to file ``/etc/os-release``.

.. note::

    The /etc/os-release is not exist in RHEL6 and prior versions.

"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.os_release)
class OsRelease(Parser, dict):
    """
    Parses the content of file ``/etc/os-release`` and stores it as a `dict`.

    Sample content of this file::

            NAME="Red Hat Enterprise Linux Server"
            VERSION="7.2 (Maipo)"
            ID="rhel"
            ID_LIKE="fedora"
            VERSION_ID="7.2"
            PRETTY_NAME="Employee SKU"
            ANSI_COLOR="0;31"
            CPE_NAME="cpe:/o:redhat:enterprise_linux:7.2:GA:server"
            HOME_URL="https://www.redhat.com/"
            BUG_REPORT_URL="https://bugzilla.redhat.com/"
            REDHAT_BUGZILLA_PRODUCT="Red Hat Enterprise Linux 7"
            REDHAT_BUGZILLA_PRODUCT_VERSION=7.2
            REDHAT_SUPPORT_PRODUCT="Red Hat Enterprise Linux"
            REDHAT_SUPPORT_PRODUCT_VERSION="7.2"


    Raises:
        SkipComponent: When nothing is parsed.

    Examples:
        >>> type(rls)
        <class 'insights.parsers.os_release.OsRelease'>
        >>> rls.get("VARIANT_ID") is None
        True
        >>> rls.get("VERSION") == "7.2 (Maipo)"
        True
    """
    def parse_content(self, content):
        data = {}
        for line in get_active_lines(content):
            k, _, v = line.partition("=")
            if _ == "=" and k:
                data[k] = v.strip('"\'') if v else None
        if not data:
            raise SkipComponent
        self.update(data)

    @property
    def data(self):
        """
        .. warning::
            Deprecated, it will be removed from 3.7.0
        """
        return self
