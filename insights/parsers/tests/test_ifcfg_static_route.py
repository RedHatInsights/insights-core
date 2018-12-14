import doctest
from insights.parsers import ifcfg_static_route
from insights.parsers.ifcfg_static_route import IfCFGStaticRoute
from insights.tests import context_wrap
import pytest

CONTEXT_PATH_DEVICE_1 = "etc/sysconfig/network-scripts/route-test-net"

STATIC_ROUTE_1="""
ADDRESS0=10.65.223.0
NETMASK0=255.255.254.0
GATEWAY0=10.65.223.1
""".strip()

CONTEXT_PATH_DEVICE_2 = "etc/sysconfig/network-scripts/route-test-net-11"

STATIC_ROUTE_2="""
ADDRESS0=
NETMASK0=255.255.254.0
GATEWAY0=10.65.223.1
""".strip()

CONTEXT_PATH_DEVICE_3 = "etc/sysconfig/network-scripts/ifcfg-eth0"

def test_static_route_connection_1():
    context = context_wrap(STATIC_ROUTE_1, CONTEXT_PATH_DEVICE_1)
    r = IfCFGStaticRoute(context)
    assert r.static_route == 'test-net'
    assert r.data == {'ADDRESS0': '10.65.223.0', 'NETMASK0': '255.255.254.0', 'GATEWAY0': '10.65.223.1'}
    assert r.data['ADDRESS0'] ==  '10.65.223.0'

def test_static_route_connection_2():
    context = context_wrap(STATIC_ROUTE_1, CONTEXT_PATH_DEVICE_2)
    r = IfCFGStaticRoute(context)
    assert r.static_route == 'test-net-11'
    assert r.data == {'ADDRESS0': '10.65.223.0', 'NETMASK0': '255.255.254.0', 'GATEWAY0': '10.65.223.1'}

def test_missing_columns():
    with pytest.raises(AssertionError):
        context = context_wrap(STATIC_ROUTE_2, CONTEXT_PATH_DEVICE_1)
        r = IfCFGStaticRoute(context)
        assert r.data['ADDRESS0'] ==  '10.65.223.0'

def test_missing_index():
    with pytest.raises(IndexError):
        context = context_wrap(STATIC_ROUTE_2, CONTEXT_PATH_DEVICE_3)
        r = IfCFGStaticRoute(context)
        assert r.static_route == 'eth0'

def test_ifcfg_static_route_doc_examples():
    env = {
        'conn_info': IfCFGStaticRoute(context_wrap(STATIC_ROUTE_1, CONTEXT_PATH_DEVICE_1)),
    }
    failed, total = doctest.testmod(ifcfg_static_route, globs=env)
    assert failed == 0