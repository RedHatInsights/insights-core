"""
passenger-status command
========================
This module provides processing for the ``passenger-status`` command using the
following parsers:
"""
from insights.parsers import ParseException
from insights.specs import Specs

from .. import CommandParser, get_active_lines, parser


@parser(Specs.passenger_status)
class PassengerStatus(CommandParser):
    """
    Parse the passenger-status command output.

    Produces a simple dictionary of keys and values from the command output
    contents, stored in the ``data`` attribute.

    Sample command output::

        Version : 4.0.18
        Date    : 2018-10-23 15:42:04 +0800
        Instance: 1265
        ----------- General information -----------
        Max pool size : 12
        Processes     : 2
        Requests in top-level queue : 0

        ----------- Application groups -----------
        /usr/share/foreman#default:
        App root: /usr/share/foreman
        Requests in queue: 192
        * PID: 30131   Sessions: 1       Processed: 991     Uptime: 2h 9m 8s
        CPU: 3%      Memory  : 562M    Last used: 1h 53m 51s
        * PID: 32450   Sessions: 1       Processed: 966     Uptime: 2h 8m 15s
        CPU: 4%      Memory  : 463M    Last used: 1h 48m 17
        * PID: 4693    Sessions: 1       Processed: 939     Uptime: 2h 6m 32s
        CPU: 3%      Memory  : 470M    Last used: 1h 50m 48

        /etc/puppet/rack#default:
        App root: /etc/puppet/rack
        Requests in queue: 0
        * PID: 21934   Sessions: 1       Processed: 380     Uptime: 1h 33m 34s
        CPU: 1%      Memory  : 528M    Last used: 1h 29m 4
        * PID: 26194   Sessions: 1       Processed: 544     Uptime: 1h 31m 34s
        CPU: 2%      Memory  : 490M    Last used: 1h 23m 5
        * PID: 32384   Sessions: 1       Processed: 36      Uptime: 1h 0m 29s
        CPU: 0%      Memory  : 561M    Last used: 1h 0m 3s


    Example data structure produced::

        {
            'Version': '4.0.18',
            'Date': '2018-10-23 15',
            'Instance': '1265',
            'Max pool size': '12',
            'Processes': '2',
            'Requests in top-level queue': '0',
            'foreman_default': {
                'App root': '/usr/share/foreman',
                'Requests in queue': '192',
                'p_list': [
                    {
                        'Uptime': '2h 9m 8s', 'Processed': '991', 'Sessions': '1', 'Memory': '562M',
                        'PID': '30131', 'CPU': '3%', 'Last used': '1h 53m 51s'
                    }, {
                        'Uptime': '2h 8m 15s', 'Processed': '966', 'Sessions': '1', 'Memory': '463M',
                        'PID': '32450', 'CPU': '4%', 'Last used': '1h 48m 17'
                    }, {
                        'Uptime': '2h 6m 32s', 'Processed': '939', 'Sessions': '1', 'Memory': '470M',
                        'PID': '4693', 'CPU': '3%', 'Last used': '1h 50m 48'
                    }
                ]
            },
            'rack_default': {
                'App root': '/etc/puppet/rack',
                'Requests in queue': '0',
                'p_list': [
                    {
                        'Uptime': '1h 33m 34s', 'Processed': '380', 'Sessions': '1', 'Memory': '528M',
                        'PID': '21934', 'CPU': '1%', 'Last used': '1h 29m 4'
                    }, {
                        'Uptime': '1h 31m 34s', 'Processed': '544', 'Sessions': '1', 'Memory': '490M',
                        'PID': '26194', 'CPU': '2%', 'Last used': '1h 23m 5'
                    }, {
                        'Uptime': '1h 0m 29s', 'Processed': '36', 'Sessions': '1', 'Memory': '561M',
                        'PID': '32384', 'CPU': '0%', 'Last used': '1h 0m 3s'
                    }
                ]
            }
        }


    Examples:
        >>> passenger_status.data["Version"]
        '4.0.18'
        >>> 'rack_default' in passenger_status.data
        True
        >>> len(passenger_status.data['foreman_default']['p_list'])
        3

    Raises:
        ParseException: When there is no useful data or the input content is
            empty, or does contain the header line.
    """

    def parse_content(self, content):
        content = get_active_lines(content, '-----------')
        if len(content) <= 1:
            raise ParseException("Input content is empty or there is no useful parsed data.")

        if not content or not content[0].startswith('Version'):
            raise ParseException("Cannot find the header line.")
        returndic = {}
        group_bit = None
        for line in content:
            if not group_bit and ":" in line and not line.endswith(':'):
                returndic[line.split(":")[0].strip()] = line.split(":")[1].strip()
                continue

            if line.startswith(("/usr/share/foreman#default", "/etc/puppet/rack#default")):
                # set the group which the following pid will belong to
                group_bit = line.strip(':').split('/')[-1].replace('#', '_')
                returndic[group_bit] = {}
                continue

            if group_bit:
                if line.strip().startswith(("* PID:", "CPU")):
                    if line.strip().startswith("* PID:"):
                        p_dic = {}
                        # if this is the first process of this group the create the p_lists key
                        if 'p_list' not in returndic[group_bit]:
                            returndic[group_bit]['p_list'] = []
                        returndic[group_bit]['p_list'].append(p_dic)
                    linesplit = line.split("    ")
                    for i in linesplit:
                        if ':' in i:
                            si1, si2 = i.split(':', 1)
                            p_dic[si1.strip(' \t*')] = si2.strip()
                elif ':' in line:
                    # set the entry to the current group
                    returndic[group_bit][line.split(":")[0].strip()] = line.split(":")[1].strip()

        self.data = returndic
