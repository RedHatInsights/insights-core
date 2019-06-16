#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
