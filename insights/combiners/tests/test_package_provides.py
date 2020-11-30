import doctest

from insights.tests import context_wrap
from insights.combiners import package_provides
from insights.parsers.package_provides import PackageProvidesJava, PackageProvidesHttpd
from insights.combiners.package_provides import PackageProvidesHttpdAll, PackageProvidesJavaAll

PACKAGE_COMMAND_MATCH_JAVA_1 = """
/usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
"""
PACKAGE_COMMAND_MATCH_JAVA_2 = """
/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
"""

PACKAGE_COMMAND_MATCH_JAVA_3 = """
java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
"""

PACKAGE_COMMAND_MATCH_HTTPD_1 = """
/opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64
"""

PACKAGE_COMMAND_MATCH_HTTPD_2 = """
/usr/sbin/httpd httpd-2.4.6-88.el7.x86_64
"""

PACKAGE_COMMAND_MATCH_HTTPD_3 = """
/opt/rh/jbcs-httpd24/root/usr/sbin/httpd jbcs-httpd24-httpd-2.4.34-7.el7.x86_64
"""


def test_packages_provide_java():
    pack1 = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_MATCH_JAVA_1))
    pack2 = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_MATCH_JAVA_2))
    pack3 = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_MATCH_JAVA_3))
    result = PackageProvidesJavaAll([pack1, pack2, pack3])
    assert sorted(result.running_javas) == sorted(
        ['/usr/lib/jvm/jre/bin/java',
         '/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java', 'java'])
    assert result["/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java"] == "java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64"
    assert result.get("/usr/lib/jvm/jre/bin/java") == "java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64"
    assert result.get("/usr/lib/jre/bin/java") is None
    assert "java" in result.running_javas
    assert "java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64" in result.packages


def test_packages_provide_httpd():
    pack1 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_HTTPD_1))
    pack2 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_HTTPD_2))
    pack3 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_HTTPD_3))
    result = PackageProvidesHttpdAll([pack1, pack2, pack3])
    assert sorted(result.running_httpds) == sorted(
        ['/opt/rh/httpd24/root/usr/sbin/httpd',
         '/usr/sbin/httpd', '/opt/rh/jbcs-httpd24/root/usr/sbin/httpd'])
    assert result["/usr/sbin/httpd"] == "httpd-2.4.6-88.el7.x86_64"
    assert result.get("/opt/rh/httpd24/root/usr/sbin/httpd") == "httpd24-httpd-2.4.34-7.el7.x86_64"
    assert result.get("/usr/lib/httpd") is None
    assert "/opt/rh/httpd24/root/usr/sbin/httpd" in result.running_httpds
    assert "jbcs-httpd24-httpd-2.4.34-7.el7.x86_64" in result.packages


def test_doc_examples():
    java_pack1 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_JAVA_1))
    java_pack2 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_JAVA_2))
    httpd_pack1 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_HTTPD_1))
    httpd_pack2 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_HTTPD_2))
    env = {
        'httpd_packages': PackageProvidesHttpdAll([httpd_pack1, httpd_pack2]),
        'java_packages': PackageProvidesJavaAll([java_pack1, java_pack2]),
    }
    failed, _ = doctest.testmod(package_provides, globs=env)
    assert failed == 0
