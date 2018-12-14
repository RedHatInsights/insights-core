#/etc/sysconfig/network-scripts/route-*

from insights.parsers.ifcfg_static_route import IfCFGStaticRoute
from insights.tests import context_wrap

CONTEXT_PATH_DEVICE = "etc/sysconfig/network-scripts/route-test-net"

STATIC_ROUTE="""
ADDRESS0=10.65.223.0
NETMASK0=255.255.254.0
GATEWAY0=10.65.223.1
""".strip()

def test_static_route_connection():
    context = context_wrap(STATIC_ROUTE, CONTEXT_PATH_DEVICE)
    r = IfCFGStaticRoute(context)
    assert r.static_route == 'test-net'
    assert r.data == {'ADDRESS0': '10.65.223.0', 'NETMASK0': '255.255.254.0', 'GATEWAY0': '10.65.223.1'}
