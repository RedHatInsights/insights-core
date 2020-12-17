import pytest
import doctest

from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException
from insights.parsers import package_provides
from insights.parsers.package_provides import PackageProvidesCommand

PACKAGE_COMMAND = """
/usr/bin/java java-11-openjdk-11.0.9.11-2.el8_3.x86_64
/usr/sbin/httpd httpd-2.4.22-7.el7.x86_64
/usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64
/opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64
"""

PACKAGE_COMMAND_EMPTY = """
"""

PACKAGE_COMMAND_NOT_MATCH = """
jdk-9/bin/java file /root/jdk-9/bin/java is not owned by any package
bin/httpd file /root/bin/httpd is not owned by any package
"""


def test_package_provides_command():
    package = PackageProvidesCommand(context_wrap(PACKAGE_COMMAND))
    assert len(package.commands) == 4
    assert len(package.packages) == 4
    assert '/usr/bin/java' in package
    assert '/usr/sbin/httpd' in package.commands
    assert package['/usr/bin/java'] == 'java-11-openjdk-11.0.9.11-2.el8_3.x86_64'
    assert package['/opt/rh/httpd24/root/usr/sbin/httpd'] == 'httpd24-httpd-2.4.34-7.el7.x86_64'


def test_package_provides_command_AB():
    with pytest.raises(SkipException):
        PackageProvidesCommand(context_wrap(PACKAGE_COMMAND_EMPTY))

    with pytest.raises(ParseException):
        PackageProvidesCommand(context_wrap(PACKAGE_COMMAND_NOT_MATCH))


def test_doc_examples():
    env = {
        'cmd_package': PackageProvidesCommand(context_wrap(PACKAGE_COMMAND)),
    }
    failed, _ = doctest.testmod(package_provides, globs=env)
    assert failed == 0
