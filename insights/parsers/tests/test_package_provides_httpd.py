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

import pytest
import doctest

from insights.parsers import package_provides_httpd
from insights.parsers.package_provides_httpd import PackageProvidesHttpd
from insights.tests import context_wrap
from ...parsers import SkipException


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
