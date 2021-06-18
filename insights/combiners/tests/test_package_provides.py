import doctest
import pytest

from insights.combiners import package_provides
from insights.combiners.package_provides import PackageProvidesCommand
from insights.parsers import SkipComponent
from insights.parsers.package_provides_httpd import PackageProvidesHttpd
from insights.parsers.package_provides_java import PackageProvidesJava
from insights.tests import context_wrap


HTTPD_COMMANDS = """
/opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64
/usr/sbin/httpd httpd-2.4.6-88.el7.x86_64
/opt/rh/jbcs-httpd24/root/usr/sbin/httpd jbcs-httpd24-httpd-2.4.34-7.el7.x86_64
""".strip()

JAVA_COMMANDS = """
/usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
java ibm-java-1.8.0-jdk-headless-1.8.0.141-3.b16.el6_9.x86_64
""".strip()

NO_COMMANDS = """
/usr/bin/bash bash-1.1.1
"""

DOC_COMMANDS_JAVA = """
/usr/bin/java java-11-openjdk-11.0.9.11-2.el8_3.x86_64
/usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64
""".strip()

DOC_COMMANDS_HTTPD = """
/usr/sbin/httpd httpd-2.4.22-7.el7.x86_64
/opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64
""".strip()


def test_packages_provide_httpd():
    pp_httpd = [PackageProvidesHttpd(context_wrap(cmd)) for cmd in HTTPD_COMMANDS.splitlines()]
    result = PackageProvidesCommand(pp_httpd, None)
    assert result is not None
    assert sorted(result.commands) == sorted([
        '/opt/rh/httpd24/root/usr/sbin/httpd',
        '/usr/sbin/httpd',
        '/opt/rh/jbcs-httpd24/root/usr/sbin/httpd'
    ])
    assert result.command_names == set(['httpd', ])
    assert sorted(result.packages) == sorted([
        'httpd24-httpd-2.4.34-7.el7.x86_64',
        'httpd-2.4.6-88.el7.x86_64',
        'jbcs-httpd24-httpd-2.4.34-7.el7.x86_64'
    ])
    assert sorted(result.commands_by_name('httpd')) == sorted([
        '/opt/rh/httpd24/root/usr/sbin/httpd',
        '/usr/sbin/httpd',
        '/opt/rh/jbcs-httpd24/root/usr/sbin/httpd'
    ])
    assert result.commands_by_name('java') == []
    assert result.command_and_package_by_name('httpd') == {
        '/opt/rh/httpd24/root/usr/sbin/httpd': 'httpd24-httpd-2.4.34-7.el7.x86_64',
        '/usr/sbin/httpd': 'httpd-2.4.6-88.el7.x86_64',
        '/opt/rh/jbcs-httpd24/root/usr/sbin/httpd': 'jbcs-httpd24-httpd-2.4.34-7.el7.x86_64',
    }
    assert result.command_and_package_by_name('java') == {}
    assert result['/usr/sbin/httpd'] == 'httpd-2.4.6-88.el7.x86_64'
    assert '/opt/rh/httpd24/root/usr/sbin/httpd' in result
    assert result.get('java') is None


def test_packages_provide_java():
    pp_java = [PackageProvidesJava(context_wrap(cmd)) for cmd in JAVA_COMMANDS.splitlines()]
    result = PackageProvidesCommand(None, pp_java)
    assert result is not None
    assert sorted(result.commands) == sorted([
        '/usr/lib/jvm/jre/bin/java',
        '/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java',
        'java',
    ])
    assert result.command_names == set(['java', ])
    assert sorted(result.packages) == sorted([
        'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64',
        'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64',
        'ibm-java-1.8.0-jdk-headless-1.8.0.141-3.b16.el6_9.x86_64',
    ])
    assert sorted(result.commands_by_name('java')) == sorted([
        '/usr/lib/jvm/jre/bin/java',
        '/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java',
        'java',
    ])
    assert result.commands_by_name('httpd') == []
    assert result.command_and_package_by_name('java') == {
        '/usr/lib/jvm/jre/bin/java': 'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64',
        '/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java': 'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64',
        'java': 'ibm-java-1.8.0-jdk-headless-1.8.0.141-3.b16.el6_9.x86_64',
    }
    assert result.command_and_package_by_name('httpd') == {}
    assert result['/usr/lib/jvm/jre/bin/java'] == 'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'
    assert '/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java' in result
    assert result.get('httpd') is None


def test_package_provides_multiple():
    pp_httpd = [PackageProvidesHttpd(context_wrap(cmd)) for cmd in HTTPD_COMMANDS.splitlines()]
    pp_java = [PackageProvidesJava(context_wrap(cmd)) for cmd in JAVA_COMMANDS.splitlines()]
    result = PackageProvidesCommand(pp_httpd, pp_java)
    assert result is not None
    assert '/usr/lib/jvm/jre/bin/java' in result
    assert '/opt/rh/httpd24/root/usr/sbin/httpd' in result
    assert 'bash' not in result
    assert result.command_names == set(['httpd', 'java'])
    assert sorted(result.commands_by_name('httpd')) == sorted([
        '/opt/rh/httpd24/root/usr/sbin/httpd',
        '/usr/sbin/httpd',
        '/opt/rh/jbcs-httpd24/root/usr/sbin/httpd'
    ])
    assert sorted(result.commands_by_name('java')) == sorted([
        '/usr/lib/jvm/jre/bin/java',
        '/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java',
        'java',
    ])
    assert sorted(result.commands) == sorted([
        '/opt/rh/httpd24/root/usr/sbin/httpd',
        '/usr/sbin/httpd',
        '/opt/rh/jbcs-httpd24/root/usr/sbin/httpd',
        '/usr/lib/jvm/jre/bin/java',
        '/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java',
        'java',
    ])


def test_package_provides_none():
    with pytest.raises(SkipComponent) as e:
        PackageProvidesCommand(None, None)
    assert e is not None


def test_doc_examples():
    pp_httpd = [PackageProvidesHttpd(context_wrap(cmd)) for cmd in DOC_COMMANDS_HTTPD.splitlines()]
    pp_java = [PackageProvidesJava(context_wrap(cmd)) for cmd in DOC_COMMANDS_JAVA.splitlines()]
    result = PackageProvidesCommand(pp_httpd, pp_java)
    env = {
        'cmd_package': result,
    }
    failed, _ = doctest.testmod(package_provides, globs=env)
    assert failed == 0
