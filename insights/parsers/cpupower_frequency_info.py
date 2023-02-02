"""
CpupowerFrequencyInfo - Commands ``cpupower -c all frequency-info``
===================================================================
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.cpupower_frequency_info)
class CpupowerFrequencyInfo(CommandParser, dict):
    """
    Class for parsing the output of `cpupower -c all frequency-info` command.

    Typical output of the command is::

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
          current CPU frequency: 871 MHz (asserted by call to kernel)
          boost state support:
            Supported: yes
            Active: yes

    Raises:
        SkipComponent: When input is empty.
        ParseException: When input cannot be parsed.

    Examples:

        >>> type(cpupower_frequency_info)
        <class 'insights.parsers.cpupower_frequency_info.CpupowerFrequencyInfo'>
        >>> cpupower_frequency_info['analyzing CPU 0']['driver']
        'intel_pstate'
        >>> cpupower_frequency_info['analyzing CPU 0']['boost state support']['Supported']
        'yes'
        >>> cpupower_frequency_info['analyzing CPU 0']['boost state support']['Active']
        'yes'
        >>> cpupower_frequency_info['analyzing CPU 1']['current policy']
        'frequency should be within 800 MHz and 3.00 GHz. The governor "performance" may decide which speed to use within this range.'
        >>> cpupower_frequency_info['analyzing CPU 0']['boost state support']['2700 MHz max turbo 4 active cores']
        True
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty content")
        if len(content) < 10 or not ('analyzing CPU' in content[0]):
            raise ParseException("Incorrect content: '{0}'".format(content))

        power_frequency_info = {}
        current_data = power_frequency_info
        parents = []
        prev_shift = 0
        prev_key = None

        for line in content:
            shift = (len(line) - len(line.lstrip()))
            if shift > prev_shift and (shift - prev_shift) > 2:
                current_data[prev_key] = ' '.join([current_data[prev_key], line.strip()])
            else:
                if shift > prev_shift:
                    current_data[prev_key] = {}
                    parents.append(current_data)
                    current_data = current_data[prev_key]
                elif shift < prev_shift:
                    while prev_shift - shift >= 2:
                        current_data = parents.pop()
                        prev_shift = prev_shift - 2
                key, value = line.strip(), True
                if ":" in line:
                    key, value = [l.strip() for l in line.strip().split(":", 1)]
                current_data[key] = value
                prev_shift = shift
                prev_key = key
        self.update(power_frequency_info)
