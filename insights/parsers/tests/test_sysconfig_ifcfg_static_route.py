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

from insights.parsers.sysconfig import IfCFGStaticRoute
from insights.tests import context_wrap
import pytest

CONTEXT_PATH_DEVICE_1 = "etc/sysconfig/network-scripts/route-test-net"

STATIC_ROUTE_1 = """
ADDRESS0=10.65.223.0
NETMASK0=255.255.254.0
GATEWAY0=10.65.223.1
""".strip()

CONTEXT_PATH_DEVICE_2 = "etc/sysconfig/network-scripts/route-test-net-11"

STATIC_ROUTE_2 = """
ADDRESS0=
NETMASK0=255.255.254.0
GATEWAY0=10.65.223.1
""".strip()

CONTEXT_PATH_DEVICE_3 = "etc/sysconfig/network-scripts/ifcfg-eth0"


def test_static_route_connection_1():
    context = context_wrap(STATIC_ROUTE_1, path=CONTEXT_PATH_DEVICE_1)
    r = IfCFGStaticRoute(context)
    assert r.static_route_name == 'test-net'
    assert r.data == {'ADDRESS0': '10.65.223.0', 'NETMASK0': '255.255.254.0', 'GATEWAY0': '10.65.223.1'}


def test_static_route_connection_2():
    context = context_wrap(STATIC_ROUTE_1, CONTEXT_PATH_DEVICE_2)
    r = IfCFGStaticRoute(context)
    assert r.static_route_name == 'test-net-11'
    assert r.data == {'ADDRESS0': '10.65.223.0', 'NETMASK0': '255.255.254.0', 'GATEWAY0': '10.65.223.1'}


def test_missing_index():
    with pytest.raises(IndexError):
        context = context_wrap(STATIC_ROUTE_2, CONTEXT_PATH_DEVICE_3)
        r = IfCFGStaticRoute(context)
        assert r.static_route_name == 'eth0'
