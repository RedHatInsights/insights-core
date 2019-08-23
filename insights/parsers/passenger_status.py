"""
passenger-status command
========================
This module provides processing for the ``passenger-status`` command using the
following parsers:
"""
from insights.parsers import SkipException
from insights.specs import Specs
from insights import CommandParser, parser


@parser(Specs.passenger_status)
class PassengerStatus(CommandParser, dict):
    """
    Parse the passenger-status command output.

    Produces a simple dictionary of keys and values from the command output
    contents.

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

    Examples:
        >>> passenger_status["Version"]
        '4.0.18'
        >>> 'rack_default' in passenger_status
        True
        >>> len(passenger_status['foreman_default']['p_list'])
        3

    Raises:
        SkipException: When input content is empty or there is no useful data.
    """

    def parse_content(self, content):
        if len(content) <= 1:
            raise SkipException("Empty content")

        group = ''
        data = {}
        for line in content:
            line = line.strip()
            if not group and ":" in line and not line.endswith(':'):
                key, val = [i.strip() for i in line.split(':', 1)]
                data[key] = val
            elif line.startswith(("/usr/share/foreman#default", "/etc/puppet/rack#default")):
                # set the group which the following pid will belong to
                group = line.strip(':').split('/')[-1].replace('#', '_')
                data[group] = group_list = {}
            elif group:
                if line.startswith(("* PID:", "CPU")):
                    if line.strip().startswith("* PID:"):
                        p_dict = {}
                        if 'p_list' not in group_list:
                            group_list['p_list'] = []
                        group_list['p_list'].append(p_dict)
                    l = line.lstrip('* ')
                    # parse each key: value pair
                    while(':' in l and l.index(':') != l.rindex(':')):
                        k, l = [i.strip() for i in l.split(':', 1)]
                        v, l = [i.strip() for i in l.split(None, 1)]
                        p_dict[k] = v
                    # for the last key: value pair
                    if l and ':' in l:
                        k, v = [i.strip() for i in l.split(':')]
                        p_dict[k] = v
                elif ':' in line:
                    key, val = [i.strip() for i in line.split(':', 1)]
                    group_list[key] = val

        if not data:
            raise SkipException("No useful data")
        self.update(data)

    @property
    def data(self):
        """
        (dict): A simple dictionary of keys and values from the command output contents
        """
        return self
