from falafel.core import MapperOutput
from falafel.core.plugins import mapper

import re

@mapper('smartctl')
class SMARTctl(MapperOutput):
    """
        Mapper for output of smartctl -a for each drive in system.
        This returns a dict with keys:
         * 'device' - the name of the device after /dev/ - e.g. sda
         * 'info' - the -i info (vendor, product, etc)
         * 'health' - overall health assessment (-H)
         * 'values' - the SMART values (-c) - SMART config on drive firmware
         * 'attributes' - the SMART attributes (-A) - run time data
        This function gets called once per detected file, so we don't have to
        deal with file changes within this process.
    """

    def __init__(self, data, path):
        filename_re = re.compile(r'smartctl_-a_\.dev\.(?P<device>\w+)$')
        match = filename_re.search(path)
        if match:
            data['device'] = match.group('device')
        # Else warn?  fail?

        super(SMARTctl, self).__init__(data, path)

    @staticmethod
    def parse_content(content):
        drive_info = {
            'info'          : {},
            'health'        : 'not parsed',
            'values'        : {},
            'attributes'    : {},
            'full_line'     : '', # hack for persistent line storage
        }

        info_line_re =  re.compile(r'(?P<key>\w+(?:\s\w+)*):\s+' +
         r'(?P<value>\S.*?)\s*$')
        value_line_re = re.compile(r'(?P<key>\w[A-Za-z _.-]+):\s+' +
         r'\(\s*(?P<value>\S.*?)\)')
        attr_line_re =  re.compile(r'^\s*(?P<id>\d+)\s(?P<name>\w+)\s+' +
         r'(?P<flag>0x[0-9a-fA-F]{4})\s+(?P<value>\d{3})\s+' +
         r'(?P<worst>\d{3})\s+(?P<threshold>\d{3})\s+' +
         r'(?P<type>[A-Za-z_-]+)\s+(?P<updated>[A-Za-z_-]+)\s+' +
         r'(?P<when_failed>\S+)\s+(?P<raw_value>\S.*)$')
        attr_keys = ['id', 'flag', 'value', 'worst', 'threshold', 'type',
         'updated', 'when_failed', 'raw_value']

        # Parsing using a state machine, sorry.  We use a state variable, and
        # functions to parse lines in each of the different states.  The function
        # returns the state as a result of reading that line, and we look up the
        # parse function out of an array based on the parse state.
        # parse state 0 = Reading 'key: value' drive information
        # parse state 1 = Reading freeform drive values
        # parse state 2 = Reading attributes information
        # parse state 3 = finished reading.
        parse_state = 0

        # Information section:
        def parse_information(line):
            # Exit parsing information section if we go into the next section
            if line.startswith('=== START OF READ SMART DATA SECTION ==='):
                return 1
            match = info_line_re.search(line)
            if match:
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
                    drive_info['info']['Temperature Warning'] =\
                        'Disabled or Not Supported'
            return 0

        # Values section:
        def parse_values(line):
            if line.startswith('=== START OF READ SMART DATA SECTION ==='):
                return 1
            if line.startswith('Vendor Specific SMART Attributes with Thresholds'):
                return 2
            if line.startswith('SMART overall-health self-assessment test result'):
                drive_info['health'] = ''.join((line.split(': '))[1:])
                return 1
            # Values section begins with this - ignore:
            if line.startswith('General SMART Values:'):
                return 1

            # Lines starting with a space are continuations of the commentary on
            # the previous setting - ignore
            if len(line) == 0 or line[0] == ' ' or line[0] == "\t":
                return 1
            # Otherwise, join this line to the full line
            if drive_info['full_line']:
                drive_info['full_line'] += ' '
            drive_info['full_line'] += line.strip()

            match = value_line_re.search(drive_info['full_line'])
            if match:
                # Handle the recommended polling time lines, which are joined
                # with the previous line and values are in minutes.
                (key, value) = match.group('key', 'value')
                drive_info['values'][key] = value
                drive_info['full_line'] = ''
            return 1

        # Attributes sections
        def parse_attributes(line):
            if line.startswith('SMART Error Log Version:'):
                return 3
            if line.startswith('Vendor Specific SMART Attributes with Thresholds'):
                return 2
            if len(line) == 0:
                return 2
            match = attr_line_re.match(line)
            if match:
                name = match.group('name')
                drive_info['attributes'][name] = {key: match.group(key)
                    for key in attr_keys}
            return 2

        parse_for_state = [
            parse_information,
            parse_values,
            parse_attributes,
        ]

        for line in content:
            parse_state = parse_for_state[parse_state](line)
            if parse_state == 3:
                break

        # Delete temporary full line storage
        del drive_info['full_line']

        return drive_info
