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
