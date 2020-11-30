import pytest
import doctest

from insights.tests import context_wrap
from insights.parsers import SkipException
from insights.parsers import package_provides
from insights.parsers.package_provides import PackageProvidesJava, PackageProvidesHttpd

PACKAGE_COMMAND_JAVA = """
/usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
"""

PACKAGE_COMMAND_ERROR = """
"""

PACKAGE_COMMAND_NOT_MATCH_JAVA = """
jdk-9/bin/java file /root/jdk-9/bin/java is not owned by any package
"""

PACKAGE_COMMAND_HTTPD = """
/opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64
"""

PACKAGE_COMMAND_NOT_MATCH_HTTPD = """
bin/httpd file /root/bin/httpd is not owned by any package
"""


def test_package_provides_java_match():
    package = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_JAVA))
    assert package.command == "/usr/lib/jvm/jre/bin/java"
    assert package.package == "java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64"


def test_package_provides_java_AB():
    with pytest.raises(SkipException):
        PackageProvidesJava(context_wrap(PACKAGE_COMMAND_ERROR))

    with pytest.raises(SkipException):
        PackageProvidesJava(context_wrap(PACKAGE_COMMAND_NOT_MATCH_JAVA))


def test_package_provides_httpd_match():
    package = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_HTTPD))
    assert package.command == "/opt/rh/httpd24/root/usr/sbin/httpd"
    assert package.package == "httpd24-httpd-2.4.34-7.el7.x86_64"


def test_package_provides_httpd_AB():
    with pytest.raises(SkipException):
        PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_ERROR))

    with pytest.raises(SkipException):
        PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_NOT_MATCH_HTTPD))


def test_doc_examples():
    env = {
        'httpd_package': PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_HTTPD)),
        'java_package': PackageProvidesJava(context_wrap(PACKAGE_COMMAND_JAVA)),
    }
    failed, _ = doctest.testmod(package_provides, globs=env)
    assert failed == 0
