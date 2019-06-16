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
