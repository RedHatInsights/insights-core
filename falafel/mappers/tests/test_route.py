from falafel.mappers import route
from falafel.tests import context_wrap


ROUTE = '''
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
10.66.208.0     0.0.0.0         255.255.255.0   U     0      0        0 eth0
169.254.0.0     0.0.0.0         255.255.0.0     U     1002   0        0 eth0
0.0.0.0         10.66.208.254   0.0.0.0         UG    0      0        0 eth0
'''


class TestRoute():
    def test_route(self):
        route_info = route.route(context_wrap(ROUTE))

        assert len(route_info) == 3
        assert route_info[0] == {'Destination': '10.66.208.0',
                                 'Gateway': '0.0.0.0',
                                 'Genmask': '255.255.255.0',
                                 'Flags': 'U',
                                 'Metric': '0',
                                 'Ref': '0',
                                 'Use': '0',
                                 'Iface': 'eth0'}
        assert route_info[1] == {'Destination': '169.254.0.0',
                                 'Gateway': '0.0.0.0',
                                 'Genmask': '255.255.0.0',
                                 'Flags': 'U',
                                 'Metric': '1002',
                                 'Ref': '0',
                                 'Use': '0',
                                 'Iface': 'eth0'}
        assert route_info[2] == {'Destination': '0.0.0.0',
                                 'Gateway': '10.66.208.254',
                                 'Genmask': '0.0.0.0',
                                 'Flags': 'UG',
                                 'Metric': '0',
                                 'Ref': '0',
                                 'Use': '0',
                                 'Iface': 'eth0'}
