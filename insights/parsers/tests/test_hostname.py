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
from insights.parsers.hostname import Hostname
from insights.tests import context_wrap

HOSTNAME = "rhel7.example.com"
HOSTNAME_MULTILINE = """
rhel7.example.com
"""

HOSTNAME_SHORT = "rhel7"
HOSTNAME_SHORT_MULTILINE = """
rhel7
"""


def test_full_hostname():
    data = Hostname(context_wrap(HOSTNAME))
    assert data.fqdn == "rhel7.example.com"
    assert data.hostname == "rhel7"
    assert data.domain == "example.com"
    assert "{0}".format(data) == "<hostname: rhel7, domain: example.com>"


def test_full_multiline_hostname():
    data = Hostname(context_wrap(HOSTNAME_MULTILINE, strip=False))
    assert data.fqdn == "rhel7.example.com"
    assert data.hostname == "rhel7"
    assert data.domain == "example.com"
    assert "{0}".format(data) == "<hostname: rhel7, domain: example.com>"


def test_short_hostname():
    data = Hostname(context_wrap(HOSTNAME_SHORT))
    assert data.fqdn == "rhel7"
    assert data.hostname == "rhel7"
    assert data.domain == ""


def test_short_multiline_hostname():
    data = Hostname(context_wrap(HOSTNAME_SHORT_MULTILINE, strip=False))
    assert data.fqdn == "rhel7"
    assert data.hostname == "rhel7"
    assert data.domain == ""


def test_empty_hostname():
    with pytest.raises(Exception):
        Hostname(context_wrap(""))
