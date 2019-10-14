"""
CpupowerFrequencyInfo - Commands ``cpupower frequency-info``
============================================================
"""
from insights import parser, CommandParser, LegacyItemAccess
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.cpupower_frequency_info)
class CpupowerFrequencyInfo(CommandParser, LegacyItemAccess):
    """
    Class for parsing the output of `cpupower frequency-info` command.

    Typical output of the command is::

        analyzing CPU 0:
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
        if len(content) < 10 or not ('analyzing CPU 0' in content[0]):
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
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    current_data[key.strip()] = value.strip()
                else:
                    key = 'dummy_key'
                    if key in current_data:
                        current_data[key].append(line.strip())
                    else:
                        current_data[key] = [line.strip()]
                prev_shift = shift
                prev_key = key
        self.data = power_frequency_info
