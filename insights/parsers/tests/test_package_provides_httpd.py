from insights.parsers.package_provides_httpd import PackageProvidesHttpd
from insights.tests import context_wrap
from ...parsers import ParseException, SkipException
import pytest

PACKAGE_COMMAND_MATCH = """
/opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64
"""

PACKAGE_COMMAND_ERROR = """
"""

PACKAGE_COMMAND_NOT_MATCH = """
bin/httpd file /root/bin/httpd is not owned by any package
"""


def test_package_provides_httpd_match():
    package = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH))
    assert package.command == "/opt/rh/httpd24/root/usr/sbin/httpd"
    assert package.package == "httpd24-httpd-2.4.34-7.el7.x86_64"


def test_package_provides_httpd_err():
    with pytest.raises(ParseException) as pe:
        PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_ERROR))
        assert "there is not httpd application running" in str(pe)


def test_package_provides_httpd_not_match():
    with pytest.raises(SkipException) as pe:
        PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_NOT_MATCH))
        assert "current running httpd command is not provided by package installed through yum or rpm" in str(pe)
