from insights.parsers.package_provides_java import PackageProvidesJava
from insights.tests import context_wrap
from ...parsers import ParseException, SkipException
import pytest

PACKAGE_COMMAND_MATCH = """
/usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
"""

PACKAGE_COMMAND_ERROR = """
"""

PACKAGE_COMMAND_NOT_MATCH = """
jdk-9/bin/java file /root/jdk-9/bin/java is not owned by any package
"""


def test_package_provides_java_match():
    package = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_MATCH))
    assert package.command == "/usr/lib/jvm/jre/bin/java"
    assert package.package == "java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64"


def test_package_provides_java_err():
    with pytest.raises(ParseException) as pe:
        PackageProvidesJava(context_wrap(PACKAGE_COMMAND_ERROR))
        assert "there is not java application running" in str(pe)


def test_package_provides_java_not_match():
    with pytest.raises(SkipException) as pe:
        PackageProvidesJava(context_wrap(PACKAGE_COMMAND_NOT_MATCH))
        assert "current running java command is not provided by package installed through yum or rpm" in str(pe)
