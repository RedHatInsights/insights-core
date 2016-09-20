from falafel.core import MapperOutput
from falafel.core.plugins import mapper

import os
import re

# Make our own iterator across the content, which doesn't go back to the
# start when we read it later...
pos_for_list = {}
def lines(l):
    global pos_for_list
    idl = id(l)
    if idl not in pos_for_list:
        pos_for_list[idl] = 0
    while pos_for_list[idl] < len(l):
        yield l[pos_for_list[idl]]
        pos_for_list[idl] += 1

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
    value_line_re = re.compile(r'(?P<key>\w[A-Za-z _.-]+):\s+\(\s*(?P<value>\S.*?)\)')
    attr_line_re =  re.compile(r'^\s*(?P<id>\d+)\s(?P<name>\w+)\s+' +
     r'(?P<flag>0x[0-9a-fA-F]{4})\s+(?P<value>\d{3})\s+(?P<worst>\d{3})\s+' + 
     r'(?P<threshold>\d{3})\s+(?P<type>[A-Za-z_-]+)\s+(?P<updated>[A-Za-z_-]+)\s+' + 
     r'(?P<when_failed>\S+)\s+(?P<raw_value>\S.*)$')
    attr_keys = ['id', 'flag', 'value', 'worst', 'threshold', 'type', 'updated',
     'when_failed', 'raw_value']

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

    # Information section:
    for line in lines(context.content):
        # Exit parsing information section if we go into the next section
        if line.startswith('=== START OF READ SMART DATA SECTION ==='):
            break
        match = info_line_re.search(line)
        if match:
#            print "information matched key:", match.group('key'), "value:", match.group('value')
            drive_info['info'][match.group('key')] = match.group('value')
        else:
            # Translate some of the less structured information
            if   line == 'Device does not support SMART':
                drive_info['info']['SMART support is'] = 'Not supported'
            elif line == 'Device supports SMART and is Enabled':
                drive_info['info']['SMART support is'] = 'Enabled'
            elif line == 'Error Counter logging not supported':
                drive_info['info']['Error Counter logging'] = 'Not supported'
            elif line == 'Device does not support Self Test logging':
                drive_info['info']['Self Test logging'] = 'Not supported'
            elif line == 'Temperature Warning Disabled or Not Supported':
                drive_info['info']['Temperature Warning'] = 'Disabled or Not Supported'

    # Values section:
    full_line = ''
    for line in lines(context.content):
        if line.startswith('=== START OF READ SMART DATA SECTION ==='):
            continue
        if line.startswith('Vendor Specific SMART Attributes with Thresholds:'):
            break
        if line.startswith('SMART overall-health self-assessment test result'):
            drive_info['health'] = ''.join((line.split(': '))[1:])
            continue
        # Values section begins with this - ignore:
        if line.startswith('General SMART Values:'):
            continue

        # Lines starting with a space are continuations of the commentary on
        # the previous setting - ignore
        if len(line) == 0 or line[0] == ' ' or line[0] == "\t":
            continue
        # Otherwise, join this line to the full line
        if full_line:
            full_line += ' '
        full_line += line.strip()
        
        match = value_line_re.search(full_line)
        if match:
            # Handle the recommended polling time lines, which are joined
            # with the previous line and values are in minutes.
            (key, value) = match.group('key', 'value')
            drive_info['values'][key] = value
#            print "... matched, key =", key, "value =", value
            full_line = ''

    # Attributes sections
    for line in lines(context.content):
        if line.startswith('SMART Error Log Version:'):
            break
        if line.startswith('Vendor Specific SMART Attributes with Thresholds:'):
            continue
        if len(line) == 0:
            continue
        match = attr_line_re.match(line)
        if match:
            name = match.group('name')
            drive_info['attributes'][name] = { key: match.group(key) for key in attr_keys }

    return drive_info

