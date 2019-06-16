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

from insights.tests import context_wrap
from insights.parsers.multicast_querier import MulticastQuerier

MULTICAST_QUERIER = """
/sys/devices/virtual/net/br0/bridge/multicast_querier
0
/sys/devices/virtual/net/br1/bridge/multicast_querier
1
/sys/devices/virtual/net/br2/bridge/multicast_querier
0
"""


def test_mcast_queri():
    result = MulticastQuerier(context_wrap(MULTICAST_QUERIER))
    assert result.bri_val == {'br0': 0, 'br1': 1, 'br2': 0}
    assert result.bri_val['br1'] == 1
    assert len(result.bri_val) == 3
