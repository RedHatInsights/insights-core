from falafel.core import MapperOutput
from falafel.core.plugins import mapper
import os
import re

"""
    Mapper for output of smartctl -a for each drive in system.
    This returns a dict with keys:
     * 'device' - the name of the device after /dev/ - e.g. sda
     * 'info' - the -i info (vendor, product, etc)
     * 'health' - overall health assessment (-H)
     * 'values' - the SMART values (-c) - SMART config on drive firmware
     * 'attributes' - the SMART attributes (-A) - run time data
"""
@mapper('smartctl')
def SMARTctl(context):
    """
        This function gets called once per detected file, so we don't have to
        deal with file changes within this process.
    """
    filename_re =   re.compile(r'smartctl_-a_\.dev\.(?P<device>\w+)$')
    info_line_re =  re.compile(r'(?P<key>\w+(?:\s\w+)*):\s+(?P<value>\S.*?)\s*$')

    match = filename_re.search(context.path)
    if not match:
        return {}

    drive_info = {
        'device'    : match.group('device'),
        'info'      : {},
        'health'    : 'not parsed',
        'values'    : {},
        'attributes': {},
    }

    for line in context.content:
        # Parse info section until 'Error Counter logging not supported'
        if line.startswith('Error Counter logging not supported'):
            break
        match = info_line_re.search(line)
        if match:
            drive_info['info'][match.group('key')] = match.group('value')

    # Continue parsing the values and attributes sections

    return drive_info
