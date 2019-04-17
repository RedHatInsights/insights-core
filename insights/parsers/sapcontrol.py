"""
sapcontrol - Commands ``sapcontrol``
====================================
Shared parsers for parsing output of the ``sapcontrol [option]`` commands.

SAPControlSystemUpdateList- command ``sapcontrol -nr <NR> -function GetSystemUpdateList``
-----------------------------------------------------------------------------------------
"""
from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException, parse_delimited_table
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
        >>> rks.is_running
        True
        >>> rks.is_green
        True
        >>> rks.data[-1]['status'] == 'Running'
        True
        >>> rks.data[-1]['dispstatus'] == 'GREEN'
        True
        >>> rks.data[0]['instanceNr'] == '00'
        True

    Attributes:
        is_running (Boolean): The status of GetSystemUpdateList
        is_green (Boolean): The display status of GetSystemUpdateList
        data (list): List of dicts where keys are the lead name of header line and
            values are the string value.
    """
    def parse_content(self, content):
        if not content:
            raise SkipException("Empty output.")

        header = "hostname, instanceNr, status, starttime, endtime, dispstatus"
        if len(content) <= 3 or header not in content:
            raise ParseException("Incorrect content: '{0}'".format(content[-1]))

        header_sp = [i.strip() for i in header.split(',')]
        self.data = parse_delimited_table(
                content,
                delim=',',
                max_splits=5,
                strip=True,
                heading_ignore=header_sp)

        if not self.data:
            raise SkipException("Empty or useless output.")

        self.is_running = all(l['status'] == 'Running' for l in self.data)
        self.is_green = all(l['dispstatus'] == 'GREEN' for l in self.data)
