"""
SaMBa status commands
=====================

This module provides processing for the ``smbstatus`` command.Parsers included in this module are:

SmbstatusS - command ``smbstatus -S``
-------------------------------------

Class ``SmbstatusS`` parses the output of the ``smbstatus -S`` command.

Sample output of this command looks like::

    Service      pid     Machine       Connected at                     Encryption   Signing
    ----------------------------------------------------------------------------------------
    share_test   13668   10.66.208.149 Wed Sep 27 10:33:55 AM 2017 CST  -            -

Smbstatusp - command ``smbstatus -p``
-------------------------------------

Class ``Smbstatusp`` parses the output of the ``smbstatus -p`` command.

Sample output of this command looks like::

    Samba version 4.6.2
    PID     Username     Group        Machine                                   Protocol Version  Encryption           Signing
    --------------------------------------------------------------------------------------------------------------------------
    12668   testsmb       testsmb       10.66.208.149 (ipv4:10.66.208.149:44376)  SMB2_02           -                    -

Examples:
    >>> smbstatusS_info = shared[SmbstatusS]
    >>> smbstatusS_info.data[0]
    {'Signing': '-', 'Service': 'share_test1', 'Encryption': '-', 'pid': '12668', 'Machine': '10.66.208.149', 'Connected': 'Wed Sep 27', 'at': '10:33:55 AM 2017 CST'}
    >>> smbstatusS_info.data[0]['PID']
    '13668'
"""

from .. import parser, Parser, get_active_lines
from . import parse_fixed_table


class Statuslist(Parser):
    """Base class implementing shared code."""

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for row in self.data:
            yield row


@parser('smbstatus_S')
class SmbstatusS(Statuslist):
    """
        Class for ``smbstatus -S`` command.

        The format of ``smbstatus -S`` is like table, and function `parse_fixed_table`
        could parse it.

        Attributes:
            data (list): List of dicts, where the keys in each dict are the column
                headers and each item in the list represents a connection.
    """

    def parse_content(self, content):
        self.data = parse_fixed_table(get_active_lines(content, '-----------'), header_substitute=[('Connected at', 'Connected_at')])


@parser('smbstatus_p')
class Smbstatusp(Statuslist):
    """
        Class for ``smbstatus -p`` command.

        The format of ``smbstatus -p`` is like table, and function `parse_fixed_table`
        could parse it.

        Attributes:
            data (list): List of dicts, where the keys in each dict are the column
                headers and each item in the list represents a connection.
    """

    def parse_content(self, content):
        self.data = parse_fixed_table(get_active_lines(content, '-----------'), heading_ignore=["PID     Username"], header_substitute=[('Protocol Version', 'Protocol_Version')])
