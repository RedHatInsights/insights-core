import pytest
import doctest

from insights.parsers import SkipException, tuned
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

TUNED_OUTPUT3 = '''
Available profiles:
- balanced                    - General non-specialized tuned profile
- desktop                     - Optimize for the desktop use-case
- hpc-compute                 - Optimize for HPC compute workloads
- latency-performance         - Optimize for deterministic performance at the cost of increased power consumption
- network-latency             - Optimize for deterministic performance at the cost of increased power consumption, focused on low latency network performance
- network-throughput          - Optimize for streaming network throughput, generally only necessary on older CPUs or 40G+ networks
- powersave                   - Optimize for low power consumption
- sap-netweaver               - Optimize for SAP NetWeaver
- throughput-performance      - Broadly applicable tuning that provides excellent performance across a variety of common server workloads
- virtual-guest               - Optimize for running inside a virtual guest
- virtual-guest-vmware
- virtual-host                - Optimize for running KVM guests
Current active profile: virtual-guest-vmware
'''.strip()

TUNED_OUTPUT4 = '''
'''.strip()


def test_active_profile():
    tuned_output = Tuned(context_wrap(TUNED_OUTPUT))
    assert len(tuned_output.get('available')) == 9
    assert tuned_output.get('active') == 'virtual-guest'
    assert tuned_output.get('available') == ['balanced',
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
    assert len(tuned_output.get('available')) == 9
    assert tuned_output.get('preset') == 'virtual-guest'
    assert tuned_output.get('available') == ['balanced',
                                             'desktop',
                                             'latency-performance',
                                             'network-latency',
                                             'network-throughput',
                                             'powersave',
                                             'throughput-performance',
                                             'virtual-guest',
                                             'virtual-host']


def test_tuned_profile():
    tuned_output = Tuned(context_wrap(TUNED_OUTPUT3))
    assert len(tuned_output.get('available')) == 12
    assert tuned_output.get('preset') is None
    assert tuned_output.get('active') == 'virtual-guest-vmware'
    assert 'sap-netweaver' in tuned_output.get('available')
    assert 'virtual-guest-vmware' in tuned_output.get('available')

    with pytest.raises(SkipException):
        Tuned(context_wrap(''))


def test_doc_example():
    env = {'tuned': Tuned(context_wrap(TUNED_OUTPUT))}
    failed, total = doctest.testmod(tuned, globs=env)
    assert failed == 0
