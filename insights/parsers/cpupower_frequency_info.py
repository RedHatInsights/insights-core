"""
CpupowerFrequencyInfo - Commands ``cpupower -c all frequency-info``
===================================================================
"""
from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.cpupower_frequency_info)
class CpupowerFrequencyInfo(CommandParser, dict):
    """
    Class for parsing the output of `cpupower -c all frequency-info` command.

    Typical output of the command is::

        analyzing CPU 0:
          driver: pcc-cpufreq
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
        analyzing CPU 1:
          driver: pcc-cpufreq
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
        SkipException: When input is empty.
        ParseException: When input cannot be parsed.

    Examples:

        >>> type(cpupower_frequency_info)
        <class 'insights.parsers.cpupower_frequency_info.CpupowerFrequencyInfo'>
        >>> cpupower_frequency_info['analyzing CPU 0']['driver']
        'pcc-cpufreq'
        >>> cpupower_frequency_info['analyzing CPU 0']['boost state support']['Supported']
        'yes'
        >>> cpupower_frequency_info['analyzing CPU 0']['boost state support']['Active']
        'yes'
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty content")
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
                key, value = line, 'True'
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                current_data[key.strip()] = value.strip()
                prev_shift = shift
                prev_key = key
        self.update(power_frequency_info)
