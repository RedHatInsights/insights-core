import doctest
import pytest
from insights.parsers import cpupower_frequency_info, ParseException, SkipException
from insights.parsers.cpupower_frequency_info import CpupowerFrequencyInfo
from insights.tests import context_wrap

CPUPOWER_INFO = """
analyzing CPU 0:
  test:
    test_key1: value1
    test2:
      test_key2: value2
        test3:
          test_key3: value3
  driver: pcc-cpufreq
  CPUs which run at the same hardware frequency: 0
  CPUs which need to have their frequency coordinated by software: 0
  maximum transition latency:  Cannot determine or is not supported.
  hardware limits: 1.20 GHz - 2.20 GHz
  available cpufreq governors: conservative userspace powersave ondemand performance
  current policy: frequency should be within 1.20 GHz and 2.20 GHz.
                  The governor "performance" may decide which speed to use
                  within this range.
  current CPU frequency: 2.38 GHz (asserted by call to hardware)
  boost state support:
    Supported: yes
    Active: yes
    2700 MHz max turbo 4 active cores
    2800 MHz max turbo 3 active cores
    2900 MHz max turbo 2 active cores
    3000 MHz max turbo 1 active cores
""".strip()

CPUPOWER_INFO_MULTI = """
analyzing CPU 0:
  driver: intel_pstate
  CPUs which run at the same hardware frequency: 0
  CPUs which need to have their frequency coordinated by software: 0
  maximum transition latency:  Cannot determine or is not supported.
  hardware limits: 800 MHz - 3.00 GHz
  available cpufreq governors: performance powersave
  current policy: frequency should be within 800 MHz and 3.00 GHz.
                  The governor "performance" may decide which speed to use
                  within this range.
  current CPU frequency: Unable to call hardware
  current CPU frequency: 1.22 GHz (asserted by call to kernel)
  boost state support:
    Supported: yes
    Active: yes
    2700 MHz max turbo 4 active cores
    2800 MHz max turbo 3 active cores
    2900 MHz max turbo 2 active cores
    3000 MHz max turbo 1 active cores
analyzing CPU 1:
  driver: intel_pstate
  CPUs which run at the same hardware frequency: 1
  CPUs which need to have their frequency coordinated by software: 1
  maximum transition latency:  Cannot determine or is not supported.
  hardware limits: 800 MHz - 3.00 GHz
  available cpufreq governors: performance powersave
  current policy: frequency should be within 800 MHz and 3.00 GHz.
                  The governor "performance" may decide which speed to use
                  within this range.
  current CPU frequency: Unable to call hardware
  current CPU frequency: 1.22 GHz (asserted by call to kernel)
  boost state support:
    Supported: yes
    Active: yes
analyzing CPU 2:
  driver: intel_pstate
  CPUs which run at the same hardware frequency: 2
  CPUs which need to have their frequency coordinated by software: 2
  maximum transition latency:  Cannot determine or is not supported.
  hardware limits: 800 MHz - 3.00 GHz
  available cpufreq governors: performance powersave
  current policy: frequency should be within 800 MHz and 3.00 GHz.
                  The governor "performance" may decide which speed to use
                  within this range.
  current CPU frequency: Unable to call hardware
  current CPU frequency: 871 MHz (asserted by call to kernel)
  boost state support:
    Supported: yes
    Active: yes
analyzing CPU 3:
  driver: intel_pstate
  CPUs which run at the same hardware frequency: 3
  CPUs which need to have their frequency coordinated by software: 3
  maximum transition latency:  Cannot determine or is not supported.
  hardware limits: 800 MHz - 3.00 GHz
  available cpufreq governors: performance powersave
  current policy: frequency should be within 800 MHz and 3.00 GHz.
                  The governor "performance" may decide which speed to use
                  within this range.
  current CPU frequency: Unable to call hardware
  current CPU frequency: 868 MHz (asserted by call to kernel)
  boost state support:
    Supported: yes
    Active: yes
"""

CPUPOWER_INFO_INVALID = """
ERROR FIRST LINE:
  driver: pcc-cpufreq
  CPUs which run at the same hardware frequency: 0
  CPUs which need to have their frequency coordinated by software: 0
  maximum transition latency:  Cannot determine or is not supported.
  hardware limits: 1.20 GHz - 2.20 GHz
  available cpufreq governors: conservative userspace powersave ondemand performance
  current policy: frequency should be within 1.20 GHz and 2.20 GHz.
                  The governor "performance" may decide which speed to use
                  within this range.
  current CPU frequency: 2.38 GHz (asserted by call to hardware)
  boost state support:
    Supported: yes
    Active: yes
    2700 MHz max turbo 4 active cores
    2800 MHz max turbo 3 active cores
    2900 MHz max turbo 2 active cores
    3000 MHz max turbo 1 active cores
""".strip()

CPUPOWER_INFO_EMPTY = """
""".strip()


def test_cpupower_frequency_info():
    cpupower_info = CpupowerFrequencyInfo(context_wrap(CPUPOWER_INFO))
    assert cpupower_info['analyzing CPU 0']['boost state support']['Supported'] == 'yes'
    assert cpupower_info['analyzing CPU 0']['boost state support']['Active'] == 'yes'
    assert cpupower_info['analyzing CPU 0']['current policy'] == 'frequency should be within 1.20 GHz and 2.20 GHz. The governor "performance" may decide which speed to use within this range.'
    assert cpupower_info['analyzing CPU 0']['boost state support']['2700 MHz max turbo 4 active cores'] is True


def test_cpupower_frequency_info_multi():
    cpupower_info = CpupowerFrequencyInfo(context_wrap(CPUPOWER_INFO_MULTI))
    assert cpupower_info['analyzing CPU 3']['boost state support']['Supported'] == 'yes'
    assert cpupower_info['analyzing CPU 3']['boost state support']['Active'] == 'yes'
    assert cpupower_info['analyzing CPU 3']['current policy'] == 'frequency should be within 800 MHz and 3.00 GHz. The governor "performance" may decide which speed to use within this range.'


def test_invalid():
    with pytest.raises(ParseException) as e:
        CpupowerFrequencyInfo(context_wrap(CPUPOWER_INFO_INVALID))
    assert "Incorrect content" in str(e)


def test_empty():
    with pytest.raises(SkipException) as e:
        CpupowerFrequencyInfo(context_wrap(CPUPOWER_INFO_EMPTY))
    assert "Empty content" in str(e)


def test_cpupower_frequency_info_doc_examples():
    env = {
        'cpupower_frequency_info': CpupowerFrequencyInfo(
            context_wrap(CPUPOWER_INFO_MULTI)),
    }
    failed, total = doctest.testmod(cpupower_frequency_info, globs=env)
    assert failed == 0
