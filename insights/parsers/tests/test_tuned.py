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
