import pytest
import doctest

from insights.parsers import package_provides_httpd
from insights.parsers.package_provides_httpd import PackageProvidesHttpd
from insights.tests import context_wrap
from insights.parsers import SkipException


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
    with pytest.raises(SkipException) as pe:
        PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_ERROR))
        assert "there is not httpd application running" in str(pe)


def test_package_provides_httpd_not_match():
    with pytest.raises(SkipException) as pe:
        PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_NOT_MATCH))
        assert "current running httpd command is not provided by package installed through yum or rpm" in str(pe)


def test_doc_examples():
    env = {
        'package': package_provides_httpd.PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH)),
    }
    failed, _ = doctest.testmod(package_provides_httpd, globs=env)
    assert failed == 0
