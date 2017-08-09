from insights.parsers.tuned import Tuned
from insights.tests import context_wrap

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

TUNED_OUTPUT2 = '''
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
It seems that tuned daemon is not running, preset profile is not activated.
Preset profile: virtual-guest
'''.strip()


def test_active_profile():
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


def test_preset_profile():
    tuned_output = Tuned(context_wrap(TUNED_OUTPUT2))
    assert len(tuned_output.data.get('available')) == 9
    assert tuned_output.data.get('preset') == 'virtual-guest'
    assert tuned_output.data.get('available') == ['balanced',
                                                  'desktop',
                                                  'latency-performance',
                                                  'network-latency',
                                                  'network-throughput',
                                                  'powersave',
                                                  'throughput-performance',
                                                  'virtual-guest',
                                                  'virtual-host']
