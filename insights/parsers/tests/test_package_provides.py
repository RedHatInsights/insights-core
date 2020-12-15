import pytest
import doctest

from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException
from insights.parsers import package_provides
from insights.parsers.package_provides import PackageProvidesJava, PackageProvidesHttpd

PACKAGE_COMMAND_JAVA = """
/usr/bin/java java-11-openjdk-11.0.9.11-2.el8_3.x86_64
/usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64
"""

PACKAGE_COMMAND_EMPTY = """
"""

PACKAGE_COMMAND_NOT_MATCH_JAVA = """
jdk-9/bin/java file /root/jdk-9/bin/java is not owned by any package
"""

PACKAGE_COMMAND_HTTPD = """
/usr/sbin/httpd httpd-2.4.22-7.el7.x86_64
/opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64
"""

PACKAGE_COMMAND_NOT_MATCH_HTTPD = """
bin/httpd file /root/bin/httpd is not owned by any package
"""


def test_package_provides_java_match():
    package = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_JAVA))
    assert sorted(package.commands) == sorted(['/usr/bin/java', '/usr/lib/jvm/jre/bin/java'])
    assert sorted(package.packages) == sorted(['java-11-openjdk-11.0.9.11-2.el8_3.x86_64', 'java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64'])
    assert package['/usr/bin/java'] == 'java-11-openjdk-11.0.9.11-2.el8_3.x86_64'


def test_package_provides_java_AB():
    with pytest.raises(SkipException):
        PackageProvidesJava(context_wrap(PACKAGE_COMMAND_EMPTY))

    with pytest.raises(ParseException):
        PackageProvidesJava(context_wrap(PACKAGE_COMMAND_NOT_MATCH_JAVA))


def test_package_provides_httpd_match():
    package = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_HTTPD))
    assert sorted(package.commands) == sorted(['/usr/sbin/httpd', '/opt/rh/httpd24/root/usr/sbin/httpd'])
    assert sorted(package.packages) == sorted(['httpd-2.4.22-7.el7.x86_64', 'httpd24-httpd-2.4.34-7.el7.x86_64'])


def test_package_provides_httpd_AB():
    with pytest.raises(SkipException):
        PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_EMPTY))

    with pytest.raises(ParseException):
        PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_NOT_MATCH_HTTPD))


def test_doc_examples():
    env = {
        'httpd_package': PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_HTTPD)),
        'java_package': PackageProvidesJava(context_wrap(PACKAGE_COMMAND_JAVA)),
    }
    failed, _ = doctest.testmod(package_provides, globs=env)
    assert failed == 0
