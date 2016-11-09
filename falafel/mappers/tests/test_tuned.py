import unittest
from falafel.mappers.tuned import Tuned
from falafel.tests import context_wrap

TUNED_OUTPUT = '''
Available profiles:
- balanced
- desktop
- latency-performance
- network-latency
- network-throughput
- powersave
- throughput-performance
- virtual-guest
- virtual-host
Current active profile: virtual-guest
'''.strip()


class CheckTuned(unittest.TestCase):

    def test_active_profile(self):
        tuned_output = Tuned(context_wrap(TUNED_OUTPUT))
        assert len(tuned_output.data.get('available')) == 9
        assert tuned_output.data.get('active') == 'virtual-guest'
        assert tuned_output.data.get('available') == ['balanced',
                                                 'desktop',
                                                 'latency-performance',
                                                 'network-latency',
                                                 'network-throughput',
                                                 'powersave',
                                                 'throughput-performance',
                                                 'virtual-guest',
                                                 'virtual-host']
