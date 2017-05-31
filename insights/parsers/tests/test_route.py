from insights.parsers.route import Route
from insights.tests import context_wrap


ROUTE = '''
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
10.66.208.0     0.0.0.0         255.255.255.0   U     0      0        0 eth0
169.254.0.0     0.0.0.0         255.255.0.0     U     1002   0        0 eth0
0.0.0.0         10.66.208.254   0.0.0.0         UG    0      0        0 eth0
'''


def test_route():
    route_info = Route(context_wrap(ROUTE))

    for route in route_info:
        assert route == {'Destination': '10.66.208.0',
                             'Gateway': '0.0.0.0',
                             'Genmask': '255.255.255.0',
                             'Flags': 'U',
                             'Metric': '0',
                             'Ref': '0',
                             'Use': '0',
                             'Iface': 'eth0'}
        break
    assert '169.254.0.0' in route_info
