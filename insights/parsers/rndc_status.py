"""
RndcStatus - Command ``rndc status``
=====================================
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.rndc_status)
class RndcStatus(CommandParser, dict):
    """
    Class for parsing the output of `rndc status` command.

    Typical output of the command is::

        version: BIND 9.11.4-P2-RedHat-9.11.4-9.P2.el7 (Extended Support Version) <id:7107deb>
        running on rhel7: Linux x86_64 3.10.0-957.10.1.el7.x86_64 #1 SMP Thu Feb 7 07:12:53 UTC 2019
        boot time: Mon, 26 Aug 2019 02:17:03 GMT
        last configured: Mon, 26 Aug 2019 02:17:03 GMT
        configuration file: /etc/named.conf
        CPUs found: 4
        worker threads: 4
        UDP listeners per interface: 3
        number of zones: 103 (97 automatic)
        debug level: 0
        xfers running: 0
        xfers deferred: 0
        soa queries in progress: 0
        query logging is OFF
        recursive clients: 0/900/1000
        tcp clients: 1/150
        server is up and running

    Raises:
        SkipComponent: When input is empty.
        ParseException: When input cannot be parsed.

    Examples:
        >>> type(rndc_status)
        <class 'insights.parsers.rndc_status.RndcStatus'>
        >>> rndc_status['CPUs found']
        '4'
        >>> rndc_status['server']
        'up and running'
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty content")
        for line in content:
            if ':' in line:
                k, v = line.split(':', 1)
            elif ' is ' in line:
                k, v = line.split(' is ', 1)
            else:
                raise ParseException("Incorrect content: '{0}'".format(content))
            self[k.strip()] = v.strip()
