"""
sapcontrol - Commands ``sapcontrol``
====================================
Shared parsers for parsing output of the ``sapcontrol [option]`` commands.

SAPControlSystemUpdateList- command ``sapcontrol -nr <NR> -function GetSystemUpdateList``
-----------------------------------------------------------------------------------------
"""
from insights import parser, CommandParser
from insights.parsers import SkipException, parse_delimited_table
from insights.specs import Specs


@parser(Specs.sapcontrol_getsystemupdatelist)
class SAPControlSystemUpdateList(CommandParser):
    """
    This class provides processing for the output of the
    ``sapcontrol -nr <NR> -function GetSystemUpdateList`` command on SAP system.

    Sample output of the command::
        29.01.2019 01:20:36
        GetSystemUpdateList
        OK
        hostname, instanceNr, status, starttime, endtime, dispstatus
        vm37-39, 00, Running, 29.01.2019 00:00:02, 29.01.2019 01:10:11, GREEN
        vm37-39, 02, Running, 29.01.2019 00:00:05, 29.01.2019 01:11:11, GREEN
        vm37-39, 03, Running, 29.01.2019 00:00:05, 29.01.2019 01:12:36, GREEN

    Examples:
        >>> rks.status
        'OK'
        >>> rks.data[-1]['status']
        'Running'
        >>> rks.data[-1]['dispstatus']
        'GREEN'
        >>> rks.data[0]['instanceNr']
        '00'

    Attributes:
        status (str): The status of GetSystemUpdateList
        data (list): List of dicts where keys are the lead name of header line and
            values are the string value.
    """
    def parse_content(self, content):
        if not content or len(content) <= 4:
            raise SkipException("Empty or useless output.")
        self.status = ''
        self.data = []
        for l in content:
            if l.startswith(('OK', 'FAIL')):
                self.status = l.strip()
                break
        self.data = parse_delimited_table(content,
                heading_ignore=['hostname,'],
                delim=',',
                strip=True)
