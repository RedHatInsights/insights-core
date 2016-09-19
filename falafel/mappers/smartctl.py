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
        # Exit parsing information section if we go into the next section
        if (line.startswith('Error Counter logging not supported') or
           line.startswith('=== START OF READ SMART DATA SECTION ===')):
            break
        match = info_line_re.search(line)
        if match:
            drive_info['info'][match.group('key')] = match.group('value')
        else:
            # Translate some of the less structured information
            if   line == 'Device does not support SMART':
                drive_info[info]['SMART support is'] = 'Not supported'
            elif line == 'Device supports SMART and is Enabled':
                drive_info[info]['SMART support is'] = 'Enabled'
            elif line == 'Error Counter logging not supported':
                drive_info[info]['Error Counter logging'] = 'Not supported'
            elif line == 'Device does not support Self Test logging':
                drive_info[info]['Self Test logging'] = 'Not supported'
            elif line == 'Temperature Warning Disabled or Not Supported':
                drive_info[info]['Temperature Warning'] = 'Disabled or Not supported'

    # Continue parsing the values and attributes sections

    return drive_info

