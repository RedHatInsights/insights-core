"""
passenger-status command
========================
This module provides processing for the ``passenger-status`` command using the
following parsers:
"""
from insights.parsers import ParseException
from insights.specs import Specs

from .. import CommandParser, get_active_lines, parser


class Statuslist(CommandParser):
    """Base class implementing shared code."""

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for row in self.data:
            yield row

    def parse_content(self, content):
        new_content = get_active_lines(content, '-----------')
        if len(content) <= 1:
            raise ParseException("Input content is empty or there is no useful parsed data.")
        return new_content


@parser(Specs.passenger_status)
class PassengerStatus(Statuslist):
    """
    Parse the passenger-status command output.

    Produces a simple dictionary of keys and values from the command output
    contents , stored in the ``data`` attribute.

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
            'foreman-default': {
                'App root': '/usr/share/foreman',
                'Requests in queue': '192',
                'p-list': [
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
            'rack-default': {
                'App root': '/etc/puppet/rack',
                'Requests in queue': '0',
                'p-list': [
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
        >>> 'rack-default' in passenger_status.data
        True
        >>> len(passenger_status.data['foreman-default']['p-list'])
        3

    Raises:
        ParseException: When there is no usefull data or the input content is
        empty,  or does contain the header line.
    """

    def parse_content(self, content):
        content = super(PassengerStatus, self).parse_content(content)
        if not content[0].startswith('Version'):
            raise ParseException("Cannot find the header line.")
        returndic = {}
        normal_line_l = ['Version', 'Date', 'Instance', 'Max pool size', 'Processes', 'Requests in top-level queue']
        group_bit = ''
        for line in content:
            for i in normal_line_l:
                if line.startswith(i):
                    returndic[line.split(":")[0].strip()] = line.split(":")[1].strip()
                    break

            if line.startswith("/usr/share/foreman#default"):
                # set the group which the following pid will belong to
                group_bit = "foreman-default"
                returndic["foreman-default"] = {}

            elif line.startswith("/etc/puppet/rack#default"):
                # set the group which the following pid will belong to
                group_bit = "rack-default"
                returndic["rack-default"] = {}

            elif line.startswith("App root") or line.startswith("Requests in queue"):
                # set the entry to the current group
                returndic[group_bit][line.split(":")[0].strip()] = line.split(":")[1].strip()

            elif line.startswith("* PID:") or line.startswith("CPU:"):
                p_dic = {}
                linesplit = line.split("   ")
                for i in linesplit:
                    if i == '':
                        continue
                    elif i.split(":")[0].strip() == '* PID':
                        p_dic['PID'] = i.split(":")[1].strip()
                    else:
                        p_dic[i.split(":")[0].strip()] = i.split(":")[1].strip()
                # if this is the first process of this group the create the p-lists key
                if 'p-list' not in returndic[group_bit]:
                    returndic[group_bit]['p-list'] = [p_dic]
                else:
                    # if this is PID line, then create new one in p-lists
                    if line.startswith("* PID:"):
                        returndic[group_bit]['p-list'].append(p_dic)
                    # if this is CPU line, then insert this to the last one's tail in p-list
                    else:
                        returndic[group_bit]['p-list'][-1].update(p_dic)

        self.data = returndic
