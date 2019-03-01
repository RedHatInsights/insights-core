"""
Samba status commands
=====================

This module provides processing for the ``smbstatus`` command using the
following parsers:

SmbstatusS - command ``/usr/bin/smbstatus -S``
----------------------------------------------

Smbstatusp - command ``/usr/bin/smbstatus -p``
----------------------------------------------
"""

from .. import parser, get_active_lines, CommandParser
from insights.parsers import ParseException, SkipException
from . import parse_fixed_table
from insights.specs import Specs


class Statuslist(CommandParser):
    """Base class implementing shared code."""

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for row in self.data:
            yield row

    def parse_content(self, content):
        new_content = get_active_lines(content, '-----------')
        if not content:
            raise SkipException("Empty content.")
        if len(content) == 1:
            raise ParseException("There is no useful parsed data in the content: '{0}'".format(content))
        return new_content


@parser(Specs.smbstatus_S)
class SmbstatusS(Statuslist):
    """
    Class ``SmbstatusS`` parses the output of the ``smbstatus -S`` command.

    Sample output of this command looks like::

        Service      pid     Machine       Connected at                     Encryption   Signing
        ----------------------------------------------------------------------------------------
        share_test   13668   10.66.208.149 Wed Sep 27 10:33:55 AM 2017 CST  -            -

    The format of ``smbstatus -S`` is like table, and function `parse_fixed_table`
    could parse it.

    Examples:
        >>> smbstatuss_info.data[0] == {'Signing': '-', 'Service': 'share_test', 'Encryption': '-', 'pid': '13668', 'Machine': '10.66.208.149', 'Connected_at': 'Wed Sep 27 10:33:55 AM 2017 CST'}
        True
        >>> smbstatuss_info.data[0]['pid']
        '13668'

    Raises:
        ParseException: When there is no usefull data or the input content is
            empty,  or does contain the header line.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a connection.
    """

    def parse_content(self, content):
        content = super(SmbstatusS, self).parse_content(content)
        if not content[0].startswith('Service '):
            raise ParseException("Cannot find the header line.")
        self.data = parse_fixed_table(content, header_substitute=[('Connected at', 'Connected_at')])


@parser(Specs.smbstatus_p)
class Smbstatusp(Statuslist):
    """
    Class ``Smbstatusp`` parses the output of the ``smbstatus -p`` command.

    Sample output of this command looks like::

        Samba version 4.6.2
        PID     Username     Group        Machine                                   Protocol Version  Encryption           Signing
        --------------------------------------------------------------------------------------------------------------------------
        12668   testsmb       testsmb       10.66.208.149 (ipv4:10.66.208.149:44376)  SMB2_02           -                    -

    The format of ``smbstatus -p`` is like table, and function `parse_fixed_table`
    could parse it.

    Examples:
        >>> smbstatusp_info.data[0] == {'Username': 'testsmb', 'Signing': '-', 'Group': 'testsmb', 'Encryption': '-', 'PID': '12668', 'Machine': '10.66.208.149 (ipv4:10.66.208.149:44376)', 'Protocol_Version': 'SMB2_02'}
        True
        >>> smbstatusp_info.data[0]['PID']
        '12668'

    Raises:
        ParseException: When there is no usefull data or the input content is
            empty,  or does contain the header line.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a connection.
    """

    def parse_content(self, content):
        content = super(Smbstatusp, self).parse_content(content)
        if not any(l.startswith('PID ') for l in content):
            raise ParseException("Cannot find the header line.")
        self.data = parse_fixed_table(content, heading_ignore=["PID     Username"],
                                      header_substitute=[('Protocol Version', 'Protocol_Version')])
