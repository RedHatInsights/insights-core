import doctest

from insights.combiners import package_provides_httpd
from insights.parsers.package_provides_httpd import PackageProvidesHttpd
from insights.combiners.package_provides_httpd import PackageProvidesHttpdAll
from insights.tests import context_wrap


PACKAGE_COMMAND_MATCH_1 = """
/opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64
"""

PACKAGE_COMMAND_MATCH_2 = """
/usr/sbin/httpd httpd-2.4.6-88.el7.x86_64
"""

PACKAGE_COMMAND_MATCH_3 = """
/opt/rh/jbcs-httpd24/root/usr/sbin/httpd jbcs-httpd24-httpd-2.4.34-7.el7.x86_64
"""


def test_packages_provide_httpd():
    pack1 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_1))
    pack2 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_2))
    pack3 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_3))
    result = PackageProvidesHttpdAll([pack1, pack2, pack3])
    assert sorted(result.running_httpds) == sorted(
        ['/opt/rh/httpd24/root/usr/sbin/httpd',
         '/usr/sbin/httpd', '/opt/rh/jbcs-httpd24/root/usr/sbin/httpd'])
    assert result["/usr/sbin/httpd"] == "httpd-2.4.6-88.el7.x86_64"
    assert result.get_package("/opt/rh/httpd24/root/usr/sbin/httpd") == "httpd24-httpd-2.4.34-7.el7.x86_64"
    assert result.get("/opt/rh/httpd24/root/usr/sbin/httpd") == "httpd24-httpd-2.4.34-7.el7.x86_64"
    assert result.get_package("/usr/lib/httpd") is None
    assert result.get("/usr/lib/httpd") is None


def test_doc_examples():
    pack1 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_1))
    pack2 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_2))
    env = {
        'packages': package_provides_httpd.PackageProvidesHttpdAll([pack1, pack2]),
    }
    failed, _ = doctest.testmod(package_provides_httpd, globs=env)
    assert failed == 0
